# coding: utf-8
from msgpack._version import version
from msgpack.exceptions import *

from collections import namedtuple


class ExtType(namedtuple('ExtType', 'code data')):
    """ExtType represents ext type in msgpack."""
    def __new__(cls, code, data):
        if not isinstance(code, int):
            raise TypeError("code must be int")
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if not 0 <= code <= 127:
            raise ValueError("code must be 0~127")
        return super(ExtType, cls).__new__(cls, code, data)


import os
if os.environ.get('MSGPACK_PUREPYTHON'):
    from msgpack.fallback import StreamingPacker, unpackb, Unpacker
else:
    try:
        from msgpack._cmsgpack import StreamingPacker, unpackb, Unpacker
    except ImportError:
        from msgpack.fallback import StreamingPacker, unpackb, Unpacker

from .compat import StringIO, USING_STRINGBUILDER, PY2


class Packer(StreamingPacker):
    """
    MessagePack Packer

    usage:

        packer = Packer()
        astream.write(packer.pack(a))
        astream.write(packer.pack(b))

    Packer's constructor has some keyword arguments:

    :param callable default:
        Convert user type to builtin type that Packer supports.
        See also simplejson's document.

    :param bool use_single_float:
        Use single precision float type for float. (default: False)

    :param bool autoreset:
        Reset buffer after each pack and return its content as `bytes`. (default: True).
        If set this to false, use `bytes()` to get content and `.reset()` to clear buffer.

    :param bool use_bin_type:
        Use bin type introduced in msgpack spec 2.0 for bytes.
        It also enables str8 type for unicode.

    :param bool strict_types:
        If set to true, types will be checked to be exact. Derived classes
        from serializable types will not be serialized and will be
        treated as unsupported type and forwarded to default.
        Additionally tuples will not be serialized as lists.
        This is useful when trying to implement accurate serialization
        for python types.

    :param str encoding:
        (deprecated) Convert unicode to bytes with this encoding. (default: 'utf-8')

    :param str unicode_errors:
        Error handler for encoding unicode. (default: 'strict')
    """
    def __init__(self, default=None, encoding=None, unicode_errors=None,
                 use_single_float=False, autoreset=True, use_bin_type=False,
                 strict_types=False):
        self._buffer = StringIO()
        self._autoreset = autoreset
        super(Packer, self).__init__(self._write, default=default, encoding=encoding, unicode_errors=unicode_errors,
                                     use_single_float=use_single_float, use_bin_type=use_bin_type,
                                     strict_types=strict_types)

    def pack(self, obj):
        try:
            super(Packer, self).pack(obj)
        except:
            self._buffer = StringIO()  # force reset
            raise
        if self._autoreset:
            return self._reset()

    def pack_map_pairs(self, pairs):
        super(Packer, self).pack_map_pairs(pairs)
        if self._autoreset:
            return self._reset()

    def pack_array_header(self, n):
        super(Packer, self).pack_array_header(n)
        if self._autoreset:
            return self._reset()

    def pack_map_header(self, n):
        super(Packer, self).pack_map_header(n)
        if self._autoreset:
            return self._reset()

    def _write(self, data):
        self._buffer.write(data)

    def _reset(self):
        ret = self._buffer.getvalue()
        self._buffer = StringIO()
        return ret

    def bytes(self):
        """Return internal buffer contents as bytes object"""
        return self._buffer.getvalue()

    def reset(self):
        """Reset internal buffer.

        This method is useful only when autoreset=False.
        """
        self._buffer = StringIO()

    def getbuffer(self):
        """Return view of internal buffer."""
        if USING_STRINGBUILDER or PY2:
            return memoryview(self.bytes())
        else:
            return self._buffer.getbuffer()


def pack(o, stream, **kwargs):
    """
    Pack object `o` and write it to `stream`

    See :class:`Packer` for options.
    """
    return StreamingPacker(stream.write, **kwargs).pack(o)


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
