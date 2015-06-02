#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import pytest

from msgpack import packb, unpackb, Packer, Unpacker, ExtType


def test_integer():
    x = -(2 ** 63)
    assert unpackb(packb(x)) == x
    with pytest.raises((OverflowError, ValueError)):
        packb(x-1)

    x = 2 ** 64 - 1
    assert unpackb(packb(x)) == x
    with pytest.raises((OverflowError, ValueError)):
        packb(x+1)


def test_array_header():
    packer = Packer()
    packer.pack_array_header(2**32-1)
    with pytest.raises((OverflowError, ValueError)):
        packer.pack_array_header(2**32)


def test_map_header():
    packer = Packer()
    packer.pack_map_header(2**32-1)
    with pytest.raises((OverflowError, ValueError)):
        packer.pack_array_header(2**32)


def test_max_str_len():
    d = 'x' * 3
    packed = packb(d)

    unpacker = Unpacker(max_str_len=3, encoding='utf-8')
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_str_len=2, encoding='utf-8')
    with pytest.raises(ValueError):
        unpacker.feed(packed)
        unpacker.unpack()


def test_max_bin_len():
    d = b'x' * 3
    if sys.version_info[0] < 3:
        d = bytearray(d)
    packed = packb(d, use_bin_type=True)

    unpacker = Unpacker(max_bin_len=3)
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_bin_len=2)
    with pytest.raises(ValueError):
        unpacker.feed(packed)
        unpacker.unpack()


def test_max_array_len():
    d = [1,2,3]
    packed = packb(d)

    unpacker = Unpacker(max_array_len=3)
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_array_len=2)
    with pytest.raises(ValueError):
        unpacker.feed(packed)
        unpacker.unpack()


def test_max_map_len():
    d = {1: 2, 3: 4, 5: 6}
    packed = packb(d)

    unpacker = Unpacker(max_map_len=3)
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_map_len=2)
    with pytest.raises(ValueError):
        unpacker.feed(packed)
        unpacker.unpack()


def test_max_ext_len():
    d = ExtType(42, b"abc")
    packed = packb(d)

    unpacker = Unpacker(max_ext_len=3)
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_ext_len=2)
    with pytest.raises(ValueError):
        unpacker.feed(packed)
        unpacker.unpack()



# PyPy fails following tests because of constant folding?
# https://bugs.pypy.org/issue1721
#@pytest.mark.skipif(True, reason="Requires very large memory.")
#def test_binary():
#    x = b'x' * (2**32 - 1)
#    assert unpackb(packb(x)) == x
#    del x
#    x = b'x' * (2**32)
#    with pytest.raises(ValueError):
#        packb(x)
#
#
#@pytest.mark.skipif(True, reason="Requires very large memory.")
#def test_string():
#    x = 'x' * (2**32 - 1)
#    assert unpackb(packb(x)) == x
#    x += 'y'
#    with pytest.raises(ValueError):
#        packb(x)
#
#
#@pytest.mark.skipif(True, reason="Requires very large memory.")
#def test_array():
#    x = [0] * (2**32 - 1)
#    assert unpackb(packb(x)) == x
#    x.append(0)
#    with pytest.raises(ValueError):
#        packb(x)
