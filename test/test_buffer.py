#!/usr/bin/env python
# coding: utf-8

from msgpack import packb, unpackb


def test_unpack_buffer():
    from array import array
    buf = array('b')
    buf.fromstring(packb(('foo', 'bar')))
    obj = unpackb(buf, use_list=1)
    assert [b'foo', b'bar'] == obj


def test_unpack_bytearray():
    buf = bytearray(packb(('foo', 'bar')))
    obj = unpackb(buf, use_list=1)
    assert [b'foo', b'bar'] == obj
    assert all(type(s)==str for s in obj)

