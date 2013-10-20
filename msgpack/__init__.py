# coding: utf-8
from msgpack._version import version
from msgpack.exceptions import *

from collections import namedtuple

ExtType = namedtuple('ExtType', 'code data')

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
