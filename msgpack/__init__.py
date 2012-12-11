# coding: utf-8
from msgpack._version import version
from msgpack.exceptions import *
from msgpack._packer import pack, packb, Packer, unpack, unpackb, Unpacker

# alias for compatibility to simplejson/marshal/pickle.
load = unpack
loads = unpackb

dump = pack
dumps = packb

