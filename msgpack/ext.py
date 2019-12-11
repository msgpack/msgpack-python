# coding: utf-8
from collections import namedtuple
import datetime
import sys
import struct


try:
    _utc = datetime.timezone.utc
except AttributeError:
    _utc = datetime.timezone(datetime.timedelta(0))


PY2 = sys.version_info[0] == 2
if not PY2:
    long = int


class ExtType(namedtuple("ExtType", "code data")):
    """ExtType represents ext type in msgpack."""

    def __new__(cls, code, data):
        if not isinstance(code, int):
            raise TypeError("code must be int")
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if code == -1:
            return Timestamp.from_bytes(data)
        if not 0 <= code <= 127:
            raise ValueError("code must be 0~127")
        return super(ExtType, cls).__new__(cls, code, data)


class Timestamp(object):
    """Timestamp represents the Timestamp extension type in msgpack.

    When built with Cython, msgpack uses C methods to pack and unpack `Timestamp`. When using pure-Python
    msgpack, :func:`to_bytes` and :func:`from_bytes` are used to pack and unpack `Timestamp`.
    """

    __slots__ = ["seconds", "nanoseconds"]

    def __init__(self, seconds, nanoseconds=0):
        """Initialize a Timestamp object.

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
        if not isinstance(nanoseconds, (int, long)):
            raise TypeError("nanoseconds must be an integer")
        if nanoseconds:
            if nanoseconds < 0 or nanoseconds % 1 != 0 or nanoseconds > (1e9 - 1):
                raise ValueError(
                    "nanoseconds must be a non-negative integer less than 999999999."
                )
            if not isinstance(seconds, (int, long)):
                raise ValueError(
                    "seconds must be an integer if also providing nanoseconds."
                )
            self.nanoseconds = nanoseconds
        else:
            # round helps with floating point issues
            self.nanoseconds = int(round(seconds % 1 * 1e9, 0))
        self.seconds = int(seconds // 1)

    def __repr__(self):
        """String representation of Timestamp."""
        return "Timestamp(seconds={0}, nanoseconds={1})".format(
            self.seconds, self.nanoseconds
        )

    def __eq__(self, other):
        """Check for equality with another Timestamp object"""
        if type(other) is self.__class__:
            return (
                self.seconds == other.seconds and self.nanoseconds == other.nanoseconds
            )
        return False

    def __ne__(self, other):
        """not-equals method (see :func:`__eq__()`)"""
        return not self.__eq__(other)

    @staticmethod
    def from_bytes(b):
        """Unpack bytes into a `Timestamp` object.

        Used for pure-Python msgpack unpacking.

        :param b: Payload from msgpack ext message with code -1
        :type b: bytes

        :returns: Timestamp object unpacked from msgpack ext payload
        :rtype: Timestamp
        """
        if len(b) == 4:
            seconds = struct.unpack("!L", b)[0]
            nanoseconds = 0
        elif len(b) == 8:
            data64 = struct.unpack("!Q", b)[0]
            seconds = data64 & 0x00000003FFFFFFFF
            nanoseconds = data64 >> 34
        elif len(b) == 12:
            nanoseconds, seconds = struct.unpack("!Iq", b)
        else:
            raise ValueError(
                "Timestamp type can only be created from 32, 64, or 96-bit byte objects"
            )
        return Timestamp(seconds, nanoseconds)

    def to_bytes(self):
        """Pack this Timestamp object into bytes.

        Used for pure-Python msgpack packing.

        :returns data: Payload for EXT message with code -1 (timestamp type)
        :rtype: bytes
        """
        if (self.seconds >> 34) == 0:  # seconds is non-negative and fits in 34 bits
            data64 = self.nanoseconds << 34 | self.seconds
            if data64 & 0xFFFFFFFF00000000 == 0:
                # nanoseconds is zero and seconds < 2**32, so timestamp 32
                data = struct.pack("!L", data64)
            else:
                # timestamp 64
                data = struct.pack("!Q", data64)
        else:
            # timestamp 96
            data = struct.pack("!Iq", self.nanoseconds, self.seconds)
        return data

    def to_float(self):
        """Get the timestamp as a floating-point value.

        :returns: posix timestamp
        :rtype: float
        """
        return self.seconds + self.nanoseconds / 1e9

    @staticmethod
    def from_float(unix_float):
        seconds = int(unix_float)
        nanoseconds = int((unix_float % 1) * 1000_000_000)
        return Timestamp(seconds, nanoseconds)

    def to_unix_ns(self):
        """Get the timestamp as a unixtime in nanoseconds.

        :returns: posix timestamp in nanoseconds
        :rtype: int
        """
        return int(self.seconds * 1e9 + self.nanoseconds)

    if not PY2:

        def to_datetime(self):
            """Get the timestamp as a UTC datetime.

            :rtype: datetime.
            """
            return datetime.datetime.fromtimestamp(self.to_float(), _utc)

        @staticmethod
        def from_datetime(dt):
            return Timestamp.from_float(dt.timestamp())
