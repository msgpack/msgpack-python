# coding: utf-8
from ._version import version
from .exceptions import *

from collections import namedtuple
from numbers import Number, Integral


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

class TimestampType(namedtuple('TimestampType', 'seconds, nanoseconds')):
    """TimestampType represents the Timestamp extension type in msgpack."""
    def __new__(cls, seconds, nanoseconds=0):
        """Create TimestampType namedtuple.

        seconds: numeric
            Number of seconds since the UNIX epoch (00:00:00 UTC Jan 1 1970, minus leap seconds).
            May be negative.
        nanoseconds: int
            Number of nanoseconds to add to `seconds` to get fractional time. Maximum is 999_999_999

        Note: Negative times (before the UNIX epoch) are represented as negative seconds + positive ns.
        """
        if not isinstance(seconds, Number):
            raise TypeError("seconds must be numeric")
        if not isinstance(nanoseconds, Number):
            raise TypeError("nanoseconds must be numeric")
        if nanoseconds:
            if nanoseconds < 0 or nanoseconds % 1 != 0 or nanoseconds > (1e9 - 1):
                raise ValueError("nanoseconds must be a non-negative integer less than 999999999.")
            if not isinstance(seconds, Integral):
                raise ValueError("seconds must be an integer if also providing nanoseconds.")
        else:
            # round helps with floating point issues
            nanoseconds = int(round(seconds % 1 * 1e9, 0))
        seconds = int(seconds // 1)
        return super(TimestampType, cls).__new__(cls, seconds, nanoseconds)

    @staticmethod
    def from_bytes(b):
        """Unpack bytes into a TimestampType."""
        if len(b) == 4:
            seconds_ = int.from_bytes(b, "big", signed=False)
            nanoseconds_ = 0
        elif len(b) == 8:
            data64 = int.from_bytes(b, "big", signed=False)
            seconds_ = data64 & 0x00000003ffffffff
            nanoseconds_ = data64 >> 34
        elif len(b) == 12:
            nanoseconds_, seconds_ = struct.unpack("!Iq", b)
        else:
            raise ValueError("Timestamp type can only be created from 32, 64, or 96-bit byte objects")
        return TimestampType(seconds_, nanoseconds_)

    def to_bytes(self):
        """Pack TimestampType into bytes."""
        if 0 <= self.seconds < 17179869184:  # seconds is nonnegative and fits in 34 bits
            data64 = self.nanoseconds << 34 | self.seconds
            if data64 & 0xffffffff00000000 == 0:
                # nanoseconds is zero and seconds < 2**32, so timestamp 32
                data = self.seconds.to_bytes(4, "big", signed=False)
            else:
                # timestamp 64
                data = data64.to_bytes(8, "big", signed=False)
        else:
            # timestamp 96
            data = struct.pack("!Iq", self.nanoseconds, self.seconds)
        return data

    def to_float_s(self):
        """Return a floating-point posix timestamp"""
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
