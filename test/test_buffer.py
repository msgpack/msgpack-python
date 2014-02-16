#!/usr/bin/env python
# coding: utf-8

from msgpack import packb, unpackb
import sys


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
    expected_type = bytes if sys.version_info[0] == 3 else str
    assert all(type(s)==expected_type for s in obj)


