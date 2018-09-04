# coding: utf-8
from msgpack._version import version
from msgpack.exceptions import *

from collections import namedtuple


class ExtType(object):
    """ExtType represents ext type in msgpack."""
    __slots__ = ('code', 'data')
    
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
