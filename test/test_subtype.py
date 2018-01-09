#!/usr/bin/env python
# coding: utf-8

from msgpack import packb, unpackb
from collections import namedtuple

class MyList(list):
    pass

class MyDict(dict):
    pass

class MyTuple(tuple):
    pass

MyNamedTuple = namedtuple('MyNamedTuple', 'x y')

def test_types():
    assert packb(MyDict(), use_bin_type=True) == packb(dict(), use_bin_type=True)
    assert packb(MyList(), use_bin_type=True) == packb(list(), use_bin_type=True)
    assert packb(MyNamedTuple(1, 2), use_bin_type=True) == packb((1, 2), use_bin_type=True)
