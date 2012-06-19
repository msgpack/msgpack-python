#!/usr/bin/env python
# coding: utf-8

from msgpack import Unpacker

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

if __name__ == '__main__':
    test_foobar()

