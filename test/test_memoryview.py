#!/usr/bin/env python
# coding: utf-8


from msgpack import packb, unpackb


def test_pack_memoryview():
    data = bytearray(range(256))
    view = memoryview(data)
    unpacked = unpackb(packb(view))
    assert data == unpacked
