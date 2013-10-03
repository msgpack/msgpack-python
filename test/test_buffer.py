#!/usr/bin/env python
# coding: utf-8

from msgpack import packb, unpackb


def test_unpack_buffer():
    from array import array
    buf = array('b')
    buf.fromstring(packb(('foo', 'bar')))
    obj = unpackb(buf, use_list=1)
    assert ['foo', 'bar'] == obj

