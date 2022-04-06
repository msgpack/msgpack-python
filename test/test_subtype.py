#!/usr/bin/env python

# SPDX-FileCopyrightText: 2008-2022 INADA Naoki <songofacandy@gmail.com> and other contributors
#
# SPDX-License-Identifier: Apache-2.0

# coding: utf-8

from msgpack import packb, unpackb
from collections import namedtuple


class MyList(list):
    pass


class MyDict(dict):
    pass


class MyTuple(tuple):
    pass


MyNamedTuple = namedtuple("MyNamedTuple", "x y")


def test_types():
    assert packb(MyDict()) == packb(dict())
    assert packb(MyList()) == packb(list())
    assert packb(MyNamedTuple(1, 2)) == packb((1, 2))
