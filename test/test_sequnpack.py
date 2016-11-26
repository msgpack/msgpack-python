#!/usr/bin/env python
# coding: utf-8

import io
from msgpack import Unpacker, BufferFull
from msgpack.exceptions import OutOfData
from pytest import raises


def test_partialdata():
    unpacker = Unpacker()
    unpacker.feed(b'\xa5')
    with raises(StopIteration): next(iter(unpacker))
    unpacker.feed(b'h')
    with raises(StopIteration): next(iter(unpacker))
    unpacker.feed(b'a')
    with raises(StopIteration): next(iter(unpacker))
    unpacker.feed(b'l')
    with raises(StopIteration): next(iter(unpacker))
    unpacker.feed(b'l')
    with raises(StopIteration): next(iter(unpacker))
    unpacker.feed(b'o')
    assert next(iter(unpacker)) == b'hallo'

def test_foobar():
    unpacker = Unpacker(read_size=3, use_list=1)
    unpacker.feed(b'foobar')
    assert unpacker.unpack() == ord(b'f')
    assert unpacker.unpack() == ord(b'o')
    assert unpacker.unpack() == ord(b'o')
    assert unpacker.unpack() == ord(b'b')
    assert unpacker.unpack() == ord(b'a')
    assert unpacker.unpack() == ord(b'r')
    with raises(OutOfData):
        unpacker.unpack()

    unpacker.feed(b'foo')
    unpacker.feed(b'bar')

    k = 0
    for o, e in zip(unpacker, 'foobarbaz'):
        assert o == ord(e)
        k += 1
    assert k == len(b'foobar')

def test_foobar_skip():
    unpacker = Unpacker(read_size=3, use_list=1)
    unpacker.feed(b'foobar')
    assert unpacker.unpack() == ord(b'f')
    unpacker.skip()
    assert unpacker.unpack() == ord(b'o')
    unpacker.skip()
    assert unpacker.unpack() == ord(b'a')
    unpacker.skip()
    with raises(OutOfData):
        unpacker.unpack()

def test_maxbuffersize():
    with raises(ValueError):
        Unpacker(read_size=5, max_buffer_size=3)
    unpacker = Unpacker(read_size=3, max_buffer_size=3, use_list=1)
    unpacker.feed(b'fo')
    with raises(BufferFull):
        unpacker.feed(b'ob')
    unpacker.feed(b'o')
    assert ord('f') == next(unpacker)
    unpacker.feed(b'b')
    assert ord('o') == next(unpacker)
    assert ord('o') == next(unpacker)
    assert ord('b') == next(unpacker)


def test_readbytes():
    unpacker = Unpacker(read_size=3)
    unpacker.feed(b'foobar')
    assert unpacker.unpack() == ord(b'f')
    assert unpacker.read_bytes(3) == b'oob'
    assert unpacker.unpack() == ord(b'a')
    assert unpacker.unpack() == ord(b'r')

    # Test buffer refill
    unpacker = Unpacker(io.BytesIO(b'foobar'), read_size=3)
    assert unpacker.unpack() == ord(b'f')
    assert unpacker.read_bytes(3) == b'oob'
    assert unpacker.unpack() == ord(b'a')
    assert unpacker.unpack() == ord(b'r')

def test_issue124():
    unpacker = Unpacker()
    unpacker.feed(b'\xa1?\xa1!')
    assert tuple(unpacker) == (b'?', b'!')
    assert tuple(unpacker) == ()
    unpacker.feed(b"\xa1?\xa1")
    assert tuple(unpacker) == (b'?',)
    assert tuple(unpacker) == ()
    unpacker.feed(b"!")
    assert tuple(unpacker) == (b'!',)
    assert tuple(unpacker) == ()


def test_offset():
    unpacker= Unpacker()
    unpacker.feed(b'\x81\x01\x02')
    assert unpacker.offset == 0
    assert unpacker.unpack() == {1: 2}
    assert unpacker.offset == 0
    unpacker.feed(b'\x81\x03\x04')
    assert unpacker.offset == 0
    assert unpacker.unpack() == {3: 4}
    assert unpacker.offset == 3


def test_offset2():
    unpacker = Unpacker()
    unpacker.feed(b'\x81\x01\x02\x81')
    assert unpacker.offset == 0
    assert unpacker.unpack() == {1: 2}
    assert unpacker.offset == 0
    with raises(OutOfData):
        unpacker.unpack()
    unpacker.feed(b'\x03\x04\x81')
    assert unpacker.offset == 0
    assert unpacker.unpack() == {3: 4}
    assert unpacker.offset == 3
    with raises(OutOfData):
        unpacker.unpack()
    assert unpacker.offset == 3
    unpacker.feed(b'\x05\x06')
    assert unpacker.offset == 3
    assert unpacker.unpack() == {5: 6}
    assert unpacker.offset == 6


def test_offset3():
    unpacker = Unpacker()
    unpacker.feed(b'\x81\x01\x02\x81')
    for obj in unpacker:
        assert obj == {1: 2}
        assert unpacker.offset == 0
    assert unpacker.offset == 0
    for obj in unpacker:
        assert False
    unpacker.feed(b'\x03\x04\x81')
    assert unpacker.offset == 0
    for obj in unpacker:
        assert obj == {3: 4}
        assert unpacker.offset == 3
    unpacker.feed(b'\x05\x06')
    assert unpacker.offset == 3
    for obj in unpacker:
        assert obj == {5: 6}
        assert unpacker.offset == 6
