#!/usr/bin/env python
# coding: utf-8

from nose.tools import *
from msgpack import packb, unpackb

import datetime

class DummyException(Exception):
    pass


def test_raise_on_find_unsupported_value():
    assert_raises(TypeError, packb, datetime.datetime.now())


def test_raise_from_object_hook():
    def hook(obj):
        raise DummyException
    assert_raises(DummyException, unpackb, packb({}), object_hook=hook)
    assert_raises(DummyException, unpackb, packb({'fizz': 'buzz'}),
                  object_hook=hook)
    assert_raises(DummyException, unpackb, packb({'fizz': 'buzz'}),
                  object_pairs_hook=hook)
    assert_raises(DummyException, unpackb, packb({'fizz': {'buzz': 'spam'}}),
                  object_hook=hook)
    assert_raises(DummyException, unpackb, packb({'fizz': {'buzz': 'spam'}}),
                  object_pairs_hook=hook)


if __name__ == '__main__':
    from nose import main
    main()
