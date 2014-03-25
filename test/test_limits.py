#!/usr/bin/env python
# coding: utf-8
import pytest

from msgpack import packb, unpackb


def test_integer():
    x = -(2 ** 63)
    assert unpackb(packb(x)) == x
    with pytest.raises(OverflowError):
        packb(x-1)

    x = 2 ** 64 - 1
    assert unpackb(packb(x)) == x
    with pytest.raises(OverflowError):
        packb(x+1)

@pytest.mark.skipif(True, "Requires very large memory.")
def test_binary():
    x = b'x' * (2**32 - 1)
    assert unpackb(packb(x)) == x
    x += b'y'
    with pytest.raises(ValueError):
        packb(x)


@pytest.mark.skipif(True, "Requires very large memory.")
def test_string():
    x = u'x' * (2**32 - 1)
    assert unpackb(packb(x)) == x
    x += u'y'
    with pytest.raises(ValueError):
        packb(x)


@pytest.mark.skipif(True, "Requires very large memory.")
def test_array():
    x = [0] * (2**32 - 1)
    assert unpackb(packb(x)) == x
    x.append(0)
    with pytest.raises(ValueError):
        packb(x)
