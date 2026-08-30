#!/usr/bin/env python
import io

import pytest
from pytest import raises

from msgpack import BufferFull, Unpacker, pack, packb
from msgpack.exceptions import OutOfData


def test_partialdata():
    unpacker = Unpacker()
    unpacker.feed(b"\xa5")
    with raises(StopIteration):
        next(iter(unpacker))
    unpacker.feed(b"h")
    with raises(StopIteration):
        next(iter(unpacker))
    unpacker.feed(b"a")
    with raises(StopIteration):
        next(iter(unpacker))
    unpacker.feed(b"l")
    with raises(StopIteration):
        next(iter(unpacker))
    unpacker.feed(b"l")
    with raises(StopIteration):
        next(iter(unpacker))
    unpacker.feed(b"o")
    assert next(iter(unpacker)) == "hallo"


def test_foobar():
    unpacker = Unpacker(read_size=3, use_list=1)
    unpacker.feed(b"foobar")
    assert unpacker.unpack() == ord(b"f")
    assert unpacker.unpack() == ord(b"o")
    assert unpacker.unpack() == ord(b"o")
    assert unpacker.unpack() == ord(b"b")
    assert unpacker.unpack() == ord(b"a")
    assert unpacker.unpack() == ord(b"r")
    with raises(OutOfData):
        unpacker.unpack()

    unpacker.feed(b"foo")
    unpacker.feed(b"bar")

    k = 0
    for o, e in zip(unpacker, "foobarbaz"):
        assert o == ord(e)
        k += 1
    assert k == len(b"foobar")


def test_foobar_skip():
    unpacker = Unpacker(read_size=3, use_list=1)
    unpacker.feed(b"foobar")
    assert unpacker.unpack() == ord(b"f")
    unpacker.skip()
    assert unpacker.unpack() == ord(b"o")
    unpacker.skip()
    assert unpacker.unpack() == ord(b"a")
    unpacker.skip()
    with raises(OutOfData):
        unpacker.unpack()


@pytest.mark.skipif(
    Unpacker.__module__ == "msgpack.fallback",
    reason="only the C extension keeps a stack frame across an incomplete read",
)
def test_skip_then_unpack_across_incomplete_container():
    # skip() opens the array's stack frame without ever populating its
    # object slot (it has nothing to build), so resuming with unpack()
    # used to reuse that slot as if it held a real list and crash. See
    # GH #734.
    unpacker = Unpacker()
    unpacker.feed(b"\x91")
    with raises(OutOfData):
        unpacker.skip()
    unpacker.feed(b"\x00")
    with raises(ValueError):
        unpacker.unpack()


@pytest.mark.skipif(
    Unpacker.__module__ == "msgpack.fallback",
    reason="only the C extension keeps a stack frame across an incomplete read",
)
def test_unpack_then_skip_across_incomplete_container():
    unpacker = Unpacker()
    unpacker.feed(b"\x91")
    with raises(OutOfData):
        unpacker.unpack()
    unpacker.feed(b"\x00")
    with raises(ValueError):
        unpacker.skip()


def test_skip_then_skip_across_incomplete_container_still_works():
    unpacker = Unpacker()
    unpacker.feed(b"\x91")
    with raises(OutOfData):
        unpacker.skip()
    unpacker.feed(b"\x00")
    assert unpacker.skip() is None


def test_unpack_then_unpack_across_incomplete_container_still_works():
    unpacker = Unpacker()
    unpacker.feed(b"\x91")
    with raises(OutOfData):
        unpacker.unpack()
    unpacker.feed(b"\x00")
    assert unpacker.unpack() == [0]


@pytest.mark.skipif(
    Unpacker.__module__ != "msgpack.fallback",
    reason="the C extension is the one that needs to reject this mix, see the tests above",
)
def test_fallback_skip_then_unpack_across_incomplete_container_still_works():
    # The fallback never keeps a stack frame across an OutOfData; an
    # incomplete read rolls the buffer position back to where the call
    # started, so the next call just reparses the array header from
    # scratch regardless of which method it uses. No corruption risk here,
    # so unlike the C extension it doesn't need to reject the mix.
    unpacker = Unpacker()
    unpacker.feed(b"\x91")
    with raises(OutOfData):
        unpacker.skip()
    unpacker.feed(b"\x00")
    assert unpacker.unpack() == [0]


@pytest.mark.skipif(
    Unpacker.__module__ != "msgpack.fallback",
    reason="the C extension is the one that needs to reject this mix, see the tests above",
)
def test_fallback_unpack_then_skip_across_incomplete_container_still_works():
    unpacker = Unpacker()
    unpacker.feed(b"\x91")
    with raises(OutOfData):
        unpacker.unpack()
    unpacker.feed(b"\x00")
    assert unpacker.skip() is None


def test_maxbuffersize():
    with raises(ValueError):
        Unpacker(read_size=5, max_buffer_size=3)
    unpacker = Unpacker(read_size=3, max_buffer_size=3, use_list=1)
    unpacker.feed(b"fo")
    with raises(BufferFull):
        unpacker.feed(b"ob")
    unpacker.feed(b"o")
    assert ord("f") == next(unpacker)
    unpacker.feed(b"b")
    assert ord("o") == next(unpacker)
    assert ord("o") == next(unpacker)
    assert ord("b") == next(unpacker)


def test_maxbuffersize_file():
    buff = io.BytesIO(packb(b"a" * 10) + packb([b"a" * 20] * 2))
    unpacker = Unpacker(buff, read_size=1, max_buffer_size=19, max_bin_len=20)
    assert unpacker.unpack() == b"a" * 10
    # assert unpacker.unpack() == [b"a" * 20]*2
    with raises(BufferFull):
        print(unpacker.unpack())


def test_readbytes():
    unpacker = Unpacker(read_size=3)
    unpacker.feed(b"foobar")
    assert unpacker.unpack() == ord(b"f")
    assert unpacker.read_bytes(3) == b"oob"
    assert unpacker.unpack() == ord(b"a")
    assert unpacker.unpack() == ord(b"r")

    # Test buffer refill
    unpacker = Unpacker(io.BytesIO(b"foobar"), read_size=3)
    assert unpacker.unpack() == ord(b"f")
    assert unpacker.read_bytes(3) == b"oob"
    assert unpacker.unpack() == ord(b"a")
    assert unpacker.unpack() == ord(b"r")

    # Issue 352
    u = Unpacker()
    u.feed(b"x")
    assert bytes(u.read_bytes(1)) == b"x"
    with raises(StopIteration):
        next(u)
    u.feed(b"\1")
    assert next(u) == 1


def test_issue124():
    unpacker = Unpacker()
    unpacker.feed(b"\xa1?\xa1!")
    assert tuple(unpacker) == ("?", "!")
    assert tuple(unpacker) == ()
    unpacker.feed(b"\xa1?\xa1")
    assert tuple(unpacker) == ("?",)
    assert tuple(unpacker) == ()
    unpacker.feed(b"!")
    assert tuple(unpacker) == ("!",)
    assert tuple(unpacker) == ()


def test_unpack_tell():
    stream = io.BytesIO()
    messages = [2**i - 1 for i in range(65)]
    messages += [-(2**i) for i in range(1, 64)]
    messages += [
        b"hello",
        b"hello" * 1000,
        list(range(20)),
        {i: bytes(i) * i for i in range(10)},
        {i: bytes(i) * i for i in range(32)},
    ]
    offsets = []
    for m in messages:
        pack(m, stream)
        offsets.append(stream.tell())
    stream.seek(0)
    unpacker = Unpacker(stream, strict_map_key=False)
    for m, o in zip(messages, offsets):
        m2 = next(unpacker)
        assert m == m2
        assert o == unpacker.tell()
