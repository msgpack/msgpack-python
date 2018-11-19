#!/usr/bin/env python
# coding: utf-8

from pytest import raises
from msgpack import packb, unpackb, Unpacker, FormatError, StackError, OutOfData

import datetime


class DummyException(Exception):
    pass


def test_raise_on_find_unsupported_value():
    with raises(TypeError):
        packb(datetime.datetime.now())


def test_raise_from_object_hook():
    def hook(obj):
        raise DummyException

    raises(DummyException, unpackb, packb({}), object_hook=hook)
    raises(DummyException, unpackb, packb({"fizz": "buzz"}), object_hook=hook)
    raises(DummyException, unpackb, packb({"fizz": "buzz"}), object_pairs_hook=hook)
    raises(DummyException, unpackb, packb({"fizz": {"buzz": "spam"}}), object_hook=hook)
    raises(
        DummyException,
        unpackb,
        packb({"fizz": {"buzz": "spam"}}),
        object_pairs_hook=hook,
    )


def test_invalidvalue():
    incomplete = b"\xd9\x97#DL_"  # raw8 - length=0x97
    with raises(ValueError):
        unpackb(incomplete)

    with raises(OutOfData):
        unpacker = Unpacker()
        unpacker.feed(incomplete)
        unpacker.unpack()

    with raises(FormatError):
        id(None)
        unpackb(b"\xc1")  # (undefined tag)

    with raises(FormatError):
        unpackb(b"\x91\xc1")  # fixarray(len=1) [ (undefined tag) ]

    with raises(StackError):
        unpackb(b"\x91" * 3000)  # nested fixarray(len=1)
