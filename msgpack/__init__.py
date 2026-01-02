# ruff: noqa: F401
# pyright: reportUnusedImport = none
import os
import typing as t

from .exceptions import *  # noqa: F403
from .ext import ExtType, Timestamp

version = (1, 1, 2)
__version__ = "1.1.2"


if os.environ.get("MSGPACK_PUREPYTHON") or t.TYPE_CHECKING:
    from .fallback import Packer, Unpacker, unpackb
else:
    try:
        from ._cmsgpack import Packer, Unpacker, unpackb
    except ImportError:
        from .fallback import Packer, Unpacker, unpackb


def pack(o: t.Any, stream: t.BinaryIO, **kwargs: dict[str, t.Any]):
    """
    Pack object `o` and write it to `stream`

    See :class:`Packer` for options.
    """
    packer = Packer(autoreset=True, **kwargs) # type: ignore
    stream.write(t.cast(bytes, packer.pack(o)))


def packb(o: t.Any, **kwargs: dict[str, t.Any]):
    """
    Pack object `o` and return packed bytes

    See :class:`Packer` for options.
    """
    return Packer(autoreset=True, **kwargs).pack(o) # type: ignore


def unpack(stream: t.BinaryIO, **kwargs: dict[str, t.Any]):
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
