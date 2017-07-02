#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import struct
from pytest import raises, xfail

from msgpack import packb, unpackb, Unpacker, Packer, Passthrough

from io import BytesIO

def check(data, use_list=False):
    re = unpackb(packb(data), use_list=use_list)
    assert re == data

def testPack():
    test_data = [
            0, 1, 127, 128, 255, 256, 65535, 65536, 4294967295, 4294967296,
            -1, -32, -33, -128, -129, -32768, -32769, -4294967296, -4294967297,
            1.0,
        b"", b"a", b"a"*31, b"a"*32,
        None, True, False,
        (), ((),), ((), None,),
        {None: 0},
        (1<<23),
        ]
    for td in test_data:
        check(td)

def testPackUnicode():
    test_data = ["", "abcd", ["defgh"], "Русский текст"]
    for td in test_data:
        re = unpackb(packb(td, encoding='utf-8'), use_list=1, encoding='utf-8')
        assert re == td
        packer = Packer(encoding='utf-8')
        data = packer.pack(td)
        re = Unpacker(BytesIO(data), encoding=str('utf-8'), use_list=1).unpack()
        assert re == td

def testPackUTF32():
    try:
        test_data = [
            "",
            "abcd",
            ["defgh"],
            "Русский текст",
            ]
        for td in test_data:
            re = unpackb(packb(td, encoding='utf-32'), use_list=1, encoding='utf-32')
            assert re == td
    except LookupError as e:
        xfail(e)

def testPackBytes():
    test_data = [
        b"", b"abcd", (b"defgh",),
        ]
    for td in test_data:
        check(td)

def testPackByteArrays():
    test_data = [
        bytearray(b""), bytearray(b"abcd"), (bytearray(b"defgh"),),
        ]
    for td in test_data:
        check(td)

def testIgnoreUnicodeErrors():
    re = unpackb(packb(b'abc\xeddef'), encoding='utf-8', unicode_errors='ignore', use_list=1)
    assert re == "abcdef"

def testStrictUnicodeUnpack():
    with raises(UnicodeDecodeError):
        unpackb(packb(b'abc\xeddef'), encoding='utf-8', use_list=1)

def testStrictUnicodePack():
    with raises(UnicodeEncodeError):
        packb("abc\xeddef", encoding='ascii', unicode_errors='strict')

def testIgnoreErrorsPack():
    re = unpackb(packb("abcФФФdef", encoding='ascii', unicode_errors='ignore'), encoding='utf-8', use_list=1)
    assert re == "abcdef"

def testNoEncoding():
    with raises(TypeError):
        packb("abc", encoding=None)

def testDecodeBinary():
    re = unpackb(packb(b"abc"), encoding=None, use_list=1)
    assert re == b"abc"

def testPackFloat():
    assert packb(1.0, use_single_float=True)  == b'\xca' + struct.pack(str('>f'), 1.0)
    assert packb(1.0, use_single_float=False) == b'\xcb' + struct.pack(str('>d'), 1.0)

def testArraySize(sizes=[0, 5, 50, 1000]):
    bio = BytesIO()
    packer = Packer()
    for size in sizes:
        bio.write(packer.pack_array_header(size))
        for i in range(size):
            bio.write(packer.pack(i))

    bio.seek(0)
    unpacker = Unpacker(bio, use_list=1)
    for size in sizes:
        assert unpacker.unpack() == list(range(size))

def test_manualreset(sizes=[0, 5, 50, 1000]):
    packer = Packer(autoreset=False)
    for size in sizes:
        packer.pack_array_header(size)
        for i in range(size):
            packer.pack(i)

    bio = BytesIO(packer.bytes())
    unpacker = Unpacker(bio, use_list=1)
    for size in sizes:
        assert unpacker.unpack() == list(range(size))

    packer.reset()
    assert packer.bytes() == b''

def testMapSize(sizes=[0, 5, 50, 1000]):
    bio = BytesIO()
    packer = Packer()
    for size in sizes:
        bio.write(packer.pack_map_header(size))
        for i in range(size):
            bio.write(packer.pack(i)) # key
            bio.write(packer.pack(i * 2)) # value

    bio.seek(0)
    unpacker = Unpacker(bio)
    for size in sizes:
        assert unpacker.unpack() == dict((i, i * 2) for i in range(size))


class odict(dict):
    """Reimplement OrderedDict to run test on Python 2.6"""
    def __init__(self, seq):
        self._seq = seq
        dict.__init__(self, seq)

    def items(self):
        return self._seq[:]

    def iteritems(self):
        return iter(self._seq)

    def keys(self):
        return [x[0] for x in self._seq]

def test_odict():
    seq = [(b'one', 1), (b'two', 2), (b'three', 3), (b'four', 4)]
    od = odict(seq)
    assert unpackb(packb(od), use_list=1) == dict(seq)
    def pair_hook(seq):
        return list(seq)
    assert unpackb(packb(od), object_pairs_hook=pair_hook, use_list=1) == seq


def test_pairlist():
    pairlist = [(b'a', 1), (2, b'b'), (b'foo', b'bar')]
    packer = Packer()
    packed = packer.pack_map_pairs(pairlist)
    unpacked = unpackb(packed, object_pairs_hook=list)
    assert pairlist == unpacked


def test_passthrough():
    map = {1: Passthrough(b'\x93\xa3foo\xa3bar\xa3baz')}
    packed = packb(map, passthrough=Passthrough)
    assert packed == b'\x81\x01' + b'\x93\xa3foo\xa3bar\xa3baz'
    unpacked = unpackb(packed)
    assert unpacked == {1: [b'foo', b'bar', b'baz']}


def test_passthrough_trailing():
    listing = [b'foo', Passthrough(b'\xa3bar'), b'baz']
    packed = packb(listing, passthrough=Passthrough)
    assert packed == b'\x93\xa3foo\xa3bar\xa3baz'
    unpacked = unpackb(packed)
    assert unpacked == [b'foo', b'bar', b'baz']
