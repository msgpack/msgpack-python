# coding: utf-8
from msgpack._version import version
from msgpack.exceptions import *

try:
    from msgpack._packer import pack, packb, Packer
    from msgpack._unpacker import unpack, unpackb, Unpacker
except ImportError:
    from msgpack.fallback import pack, packb, Packer, unpack, unpackb, Unpacker

# alias for compatibility to simplejson/marshal/pickle.
load = unpack
loads = unpackb

dump = pack
dumps = packb

