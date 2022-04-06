# SPDX-FileCopyrightText: 2008-2022 INADA Naoki <songofacandy@gmail.com> and other contributors
#
# SPDX-License-Identifier: Apache-2.0

# coding: utf-8
from .exceptions import *
from .ext import ExtType, Timestamp

import os
import sys


version = (1, 0, 4, 'dev')
__version__ = "1.0.4dev"


if os.environ.get("MSGPACK_PUREPYTHON") or sys.version_info[0] == 2:
    from .fallback import Packer, unpackb, Unpacker
else:
    try:
        from ._cmsgpack import Packer, unpackb, Unpacker
    except ImportError:
        from .fallback import Packer, unpackb, Unpacker


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
