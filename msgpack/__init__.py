# coding: utf-8
from ._version import version
from .exceptions import *

from collections import namedtuple

import struct
import sys

if sys.version_info[0] > 2:
    long = int

class ExtType(namedtuple('ExtType', 'code data')):
    """ExtType represents ext type in msgpack."""
    def __new__(cls, code, data):
        if not isinstance(code, int):
            raise TypeError("code must be int")
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if code == -1:
            return TimestampType.from_bytes(data)
        if not 0 <= code <= 127:
            raise ValueError("code must be 0~127")
        return super(ExtType, cls).__new__(cls, code, data)


class TimestampType:
    """TimestampType represents the Timestamp extension type in msgpack.

    When built with Cython, msgpack-python uses C methods to pack and unpack `TimestampType`. When using pure-Python
    msgpack-python, :func:`to_bytes` and :func:`from_bytes` are used to pack and unpack `TimestampType`.
    """
    __slots__ = ["seconds", "nanoseconds"]

    def __init__(self, seconds, nanoseconds=0):
        """Initialize a TimestampType object.

        :param seconds: Number of seconds since the UNIX epoch (00:00:00 UTC Jan 1 1970, minus leap seconds). May be
            negative. If :code:`seconds` includes a fractional part, :code:`nanoseconds` must be 0.
        :type seconds: int or float

        :param nanoseconds: Number of nanoseconds to add to `seconds` to get fractional time. Maximum is 999_999_999.
            Default is 0.
        :type nanoseconds: int

        Note: Negative times (before the UNIX epoch) are represented as negative seconds + positive ns.
        """
        if not isinstance(seconds, (int, long, float)):
            raise TypeError("seconds must be numeric")
        if not isinstance(nanoseconds, int):
            raise TypeError("nanoseconds must be an integer")
        if nanoseconds:
            if nanoseconds < 0 or nanoseconds % 1 != 0 or nanoseconds > (1e9 - 1):
                raise ValueError("nanoseconds must be a non-negative integer less than 999999999.")
            if not isinstance(seconds, (int, long)):
                raise ValueError("seconds must be an integer if also providing nanoseconds.")
            self.nanoseconds = nanoseconds
        else:
            # round helps with floating point issues
            self.nanoseconds = int(round(seconds % 1 * 1e9, 0))
        self.seconds = long(seconds // 1)

    def __repr__(self):
        """String representation of TimestampType."""
        return str.format("TimestampType(seconds={0}, nanoseconds={1})", self.seconds, self.nanoseconds)

    def __eq__(self, other):
        """Check for equality with another TimestampType object"""
        if type(other) is self.__class__:
            return self.seconds == other.seconds and self.nanoseconds == other.nanoseconds
        return False

    def __ne__(self, other):
        """not-equals method (see :func:`__eq__()`)"""
        return not self.__eq__(other)

    @staticmethod
    def from_bytes(b):
        """Unpack bytes into a `TimestampType` object.

        Used for pure-Python msgpack unpacking.

        :param b: Payload from msgpack ext message with code -1
        :type b: bytes

        :returns: TimestampType object unpacked from msgpack ext payload
        :rtype: TimestampType
        """
        if len(b) == 4:
            seconds = struct.unpack("!L", b)[0]
            nanoseconds = 0
        elif len(b) == 8:
            data64 = struct.unpack("!Q", b)[0]
            seconds = data64 & 0x00000003ffffffff
            nanoseconds = data64 >> 34
        elif len(b) == 12:
            nanoseconds, seconds = struct.unpack("!Iq", b)
        else:
            raise ValueError("Timestamp type can only be created from 32, 64, or 96-bit byte objects")
        return TimestampType(seconds, nanoseconds)

    def to_bytes(self):
        """Pack this TimestampType object into bytes.

        Used for pure-Python msgpack packing.

        :returns data: Payload for EXT message with code -1 (timestamp type)
        :rtype: bytes
        """
        if (self.seconds >> 34) == 0:  # seconds is non-negative and fits in 34 bits
            data64 = self.nanoseconds << 34 | self.seconds
            if data64 & 0xffffffff00000000 == 0:
                # nanoseconds is zero and seconds < 2**32, so timestamp 32
                data = struct.pack("!L", data64)
            else:
                # timestamp 64
                data = struct.pack("!Q", data64)
        else:
            # timestamp 96
            data = struct.pack("!Iq", self.nanoseconds, self.seconds)
        return data

    def to_float_s(self):
        """Get the timestamp as a floating-point value.

        :returns: posix timestamp
        :rtype: float
        """
        return self.seconds + self.nanoseconds/1e9


import os
if os.environ.get('MSGPACK_PUREPYTHON'):
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
