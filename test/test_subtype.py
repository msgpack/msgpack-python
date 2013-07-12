#!/usr/bin/env python
# coding: utf-8

from msgpack import packb, unpackb
from collections import namedtuple, Mapping, MutableMapping

class MyList(list):
    pass

class MyDict(dict):
    pass

class MyMapping(Mapping):
    
    def __init__(self):
        self._map = dict()

    def __getitem__(self, key):
        return self._map[key]

    def __iter__(self):
        return iter(self._map)

    def __len__(self):
        return len(self._map)

class MyMutableMapping(MutableMapping):
    
    def __init__(self):
        self._map = dict()

    def __getitem__(self, key):
        return self._map[key]

    def __setitem__(self, key, value):
        self._map[key] = value

    def __delitem__(self, key):
        del(self._map[key])

    def __iter__(self):
        return iter(self._map)

    def __len__(self):
        return len(self._map)

class MyTuple(tuple):
    pass

MyNamedTuple = namedtuple('MyNamedTuple', 'x y')

def test_types():
    assert packb(MyDict()) == packb(dict())
    assert packb(MyMapping()) == packb(dict())
    assert packb(MyMutableMapping()) == packb(dict())
    assert packb(MyList()) == packb(list())
    assert packb(MyNamedTuple(1, 2)) == packb((1, 2))
