#!/usr/bin/env python
# coding: utf-8

from msgpack import Unpacker, BufferFull
import nose

def test_foobar():
    unpacker = Unpacker(read_size=3)
    unpacker.feed(b'foobar')
    assert unpacker.unpack() == ord(b'f')
    assert unpacker.unpack() == ord(b'o')
    assert unpacker.unpack() == ord(b'o')
    assert unpacker.unpack() == ord(b'b')
    assert unpacker.unpack() == ord(b'a')
    assert unpacker.unpack() == ord(b'r')
    try:
        o = unpacker.unpack()
        assert 0, "should raise exception"
    except StopIteration:
        assert 1, "ok"

    unpacker.feed(b'foo')
    unpacker.feed(b'bar')

    k = 0
    for o, e in zip(unpacker, 'foobarbaz'):
        assert o == ord(e)
        k += 1
    assert k == len(b'foobar')


def test_maxbuffersize():
    nose.tools.assert_raises(ValueError, Unpacker, read_size=5, max_buffer_size=3)
    unpacker = Unpacker(read_size=3, max_buffer_size=3)
    unpacker.feed(b'fo')
    nose.tools.assert_raises(BufferFull, unpacker.feed, b'ob')
    unpacker.feed(b'o')
    assert ord('f') == next(unpacker)
    unpacker.feed(b'b')
    assert ord('o') == next(unpacker)
    assert ord('o') == next(unpacker)
    assert ord('b') == next(unpacker)


if __name__ == '__main__':
    nose.main()
