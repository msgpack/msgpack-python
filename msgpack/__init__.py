# coding: utf-8
from msgpack._version import version
from msgpack.exceptions import *
import itertools

chain = itertools.chain
if hasattr(itertools, 'filterfalse'):
    filterfalse = itertools.filterfalse
else:
    filterfalse = itertools.ifilterfalse


class ExtType(object):
    """ExtType represents ext type in msgpack."""
    def __init__(self, code, data):
        if not isinstance(code, int):
            raise TypeError("code must be int")
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if not 0 <= code <= 127:
            raise ValueError("code must be 0~127")
        self.code = code
        self.data = data

    def __eq__(self, other):
        return isinstance(other, ExtType) and \
        self.code == other.code and self.data == other.data

    def __hash__(self):
        return hash((ExtType, self.code, self.data))


# Automatic detection of Ext subtypes
def _filter_unique(iterable):
    seen = set()
    seen_add = seen.add  # this is just to prevent excessive lookups
    for x in filterfalse(seen.__contains__, iterable):
        seen_add(x)
        yield x


def _subclasses(cls, unique=True):
    """Iterates over the set of all subclasses of an object. Unlike
    class.__subclasses__(), this returns all subclasses, not just direct ones.
    Note: though issubclass(cls, cls) returns True, we do not yield cls"""
    if unique:
        for x in _filter_unique(_subclasses(cls, unique=False)):
            yield x
    else:
        sub = tuple(x for x in cls.__subclasses__() if x is not type)
        for x in sub:
            yield x
        for x in chain.from_iterable(_subclasses(x, unique=False) for x in sub):
            yield x


import os
if os.environ.get('MSGPACK_PUREPYTHON'):
    from msgpack.fallback import Packer, unpackb, Unpacker
else:
    try:
        from msgpack._packer import Packer
        from msgpack._unpacker import unpackb, Unpacker
    except ImportError:
        from msgpack.fallback import Packer, unpackb, Unpacker


def pack(o, stream, **kwargs):
    """
    Pack object `o` and write it to `stream`

    See :class:`Packer` for options.
    """
    packer = Packer(**kwargs)
    stream.write(packer.pack(o))


def packb(o, **kwargs):
    """
    Pack object `o` and return packed bytes

    See :class:`Packer` for options.
    """
    return Packer(**kwargs).pack(o)


def unpack(stream, **kwargs):
    """
    Unpack an object from `stream`.

    Raises `ExtraData` when `stream` contains extra bytes.
    See :class:`Unpacker` for options.
    """
    data = stream.read()
    return unpackb(data, **kwargs)


# alias for compatibility to simplejson/marshal/pickle.
load = unpack
loads = unpackb

dump = pack
dumps = packb

# alias for compatbiliity to umsgpack
Ext = ExtType
