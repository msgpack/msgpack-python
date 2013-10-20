# coding: utf-8
from msgpack._version import version
from msgpack.exceptions import *


class ExtType(object):
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
        if not isinstance(other, ExtType):
            return NotImplemented
        return self.code == other.code and self.data == other.data

    def __hash__(self):
        return self.code ^ hash(self.data)

    def __repr__(self):
        return "msgpack.ExtType(%r, %r)" % (self.code, self.data)


import os
if os.environ.get('MSGPACK_PUREPYTHON'):
    from msgpack.fallback import Packer, unpack, unpackb, Unpacker
else:
    try:
        from msgpack._packer import Packer
        from msgpack._unpacker import unpack, unpackb, Unpacker
    except ImportError:
        from msgpack.fallback import Packer, unpack, unpackb, Unpacker


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

# alias for compatibility to simplejson/marshal/pickle.
load = unpack
loads = unpackb

dump = pack
dumps = packb
