#!/usr/bin/env python
# coding: utf-8
import pytest

from msgpack import packb, unpackb, Packer


def test_integer():
    x = -(2 ** 63)
    assert unpackb(packb(x)) == x
    with pytest.raises(OverflowError):
        packb(x-1)

    x = 2 ** 64 - 1
    assert unpackb(packb(x)) == x
    with pytest.raises(OverflowError):
        packb(x+1)


def test_array_header():
    packer = Packer()
    packer.pack_array_header(2**32-1)
    with pytest.raises(ValueError):
        packer.pack_array_header(2**32)


def test_map_header():
    packer = Packer()
    packer.pack_map_header(2**32-1)
    with pytest.raises(ValueError):
        packer.pack_array_header(2**32)


@pytest.mark.skipif(True, reason="Requires very large memory.")
def test_binary():
    x = b'x' * (2**32 - 1)
    assert unpackb(packb(x)) == x
    del x
    x = b'x' * (2**32)
    with pytest.raises(ValueError):
        packb(x)


@pytest.mark.skipif(True, reason="Requires very large memory.")
def test_string():
    x = u'x' * (2**32 - 1)
    assert unpackb(packb(x)) == x
    x += u'y'
    with pytest.raises(ValueError):
        packb(x)


@pytest.mark.skipif(True, reason="Requires very large memory.")
def test_array():
    x = [0] * (2**32 - 1)
    assert unpackb(packb(x)) == x
    x.append(0)
    with pytest.raises(ValueError):
        packb(x)
