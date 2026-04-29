#!/usr/bin/env python

import datetime
import gc
import tracemalloc

from pytest import raises

from msgpack import ExtType, FormatError, OutOfData, StackError, Unpacker, packb, unpackb


class DummyException(Exception):
    pass


def test_raise_on_find_unsupported_value():
    with raises(TypeError):
        packb(datetime.datetime.now())


def test_raise_from_object_hook():
    def hook(obj):
        raise DummyException

    raises(DummyException, unpackb, packb({}), object_hook=hook)
    raises(DummyException, unpackb, packb({"fizz": "buzz"}), object_hook=hook)
    raises(DummyException, unpackb, packb({"fizz": "buzz"}), object_pairs_hook=hook)
    raises(DummyException, unpackb, packb({"fizz": {"buzz": "spam"}}), object_hook=hook)
    raises(
        DummyException,
        unpackb,
        packb({"fizz": {"buzz": "spam"}}),
        object_pairs_hook=hook,
    )


def test_raise_from_list_hook():
    def hook(lst: list) -> list:
        raise DummyException

    with raises(DummyException):
        unpackb(packb([1, 2, 3]), list_hook=hook)

    with raises(DummyException):
        unpacker = Unpacker(list_hook=hook)
        unpacker.feed(packb([1, 2, 3]))
        unpacker.unpack()


def test_raise_from_ext_hook():
    def hook(code: int, data: bytes) -> ExtType:
        raise DummyException

    packed = packb(ExtType(42, b"hello"))

    with raises(DummyException):
        unpackb(packed, ext_hook=hook)

    with raises(DummyException):
        unpacker = Unpacker(ext_hook=hook)
        unpacker.feed(packed)
        unpacker.unpack()


def test_invalidvalue():
    incomplete = b"\xd9\x97#DL_"  # raw8 - length=0x97
    with raises(ValueError):
        unpackb(incomplete)

    with raises(OutOfData):
        unpacker = Unpacker()
        unpacker.feed(incomplete)
        unpacker.unpack()

    with raises(FormatError):
        unpackb(b"\xc1")  # (undefined tag)

    with raises(FormatError):
        unpackb(b"\x91\xc1")  # fixarray(len=1) [ (undefined tag) ]

    with raises(StackError):
        unpackb(b"\x91" * 3000)  # nested fixarray(len=1)


def test_no_memory_leak_on_nested_invalid_tag() -> None:
    """Regression test: unpacking nested arrays containing an invalid tag must not leak objects."""

    kwargs: dict = {
        "raw": False,
        "strict_map_key": False,
        "max_array_len": 1 << 20,
        "max_map_len": 1 << 20,
    }
    n = 1000

    for depth in range(1, 15):
        data = bytes([0x91] * depth + [0xC1])

        gc.collect()
        tracemalloc.start()
        s1 = tracemalloc.take_snapshot()

        for _ in range(n):
            try:
                unpackb(data, **kwargs)
            except Exception:
                pass

        gc.collect()
        s2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        leaked = sum(s.count_diff for s in s2.compare_to(s1, "lineno") if s.count_diff > 0)
        per_call = leaked / n
        assert per_call < 1.0, f"depth={depth}: {per_call:.2f} leaked objects/call (expected < 1)"


def test_strict_map_key():
    valid = {"unicode": 1, b"bytes": 2}
    packed = packb(valid, use_bin_type=True)
    assert valid == unpackb(packed, raw=False, strict_map_key=True)

    invalid = {42: 1}
    packed = packb(invalid, use_bin_type=True)
    with raises(ValueError):
        unpackb(packed, raw=False, strict_map_key=True)
