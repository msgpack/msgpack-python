#!/usr/bin/env python
# coding: utf-8

from nose.tools import *
from msgpack import packb, unpackb

import datetime

def test_raise_on_find_unsupported_value():
    assert_raises(TypeError, packb, datetime.datetime.now())

if __name__ == '__main__':
    from nose import main
    main()
