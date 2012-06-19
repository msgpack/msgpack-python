#!/usr/bin/env python
# coding: utf-8

from nose import main
from nose.tools import *
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
    assert_equal(packb(dict()), packb(MyDict()))
    assert_equal(packb(list()), packb(MyList()))
    assert_equal(packb(MyNamedTuple(1,2)), packb((1,2)))


if __name__ == '__main__':
    main()
