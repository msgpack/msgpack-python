#!/usr/bin/env python
# coding: utf-8

import six
import struct
from nose import main
from nose.tools import *
from nose.plugins.skip import SkipTest

from msgpack import packb, unpackb, Unpacker, Packer

from io import BytesIO

def check(data):
    re = unpackb(packb(data))
    assert_equal(re, data)

def testPack():
    test_data = [
            0, 1, 127, 128, 255, 256, 65535, 65536,
            -1, -32, -33, -128, -129, -32768, -32769,
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
    test_data = [
        six.u(""), six.u("abcd"), (six.u("defgh"),), six.u("Русский текст"),
        ]
    for td in test_data:
        re = unpackb(packb(td, encoding='utf-8'), encoding='utf-8')
        assert_equal(re, td)
        packer = Packer(encoding='utf-8')
        data = packer.pack(td)
        re = Unpacker(BytesIO(data), encoding='utf-8').unpack()
        assert_equal(re, td)

def testPackUTF32():
    try:
        test_data = [
            six.u(""),
            six.u("abcd"),
            (six.u("defgh"),),
            six.u("Русский текст"),
            ]
        for td in test_data:
            re = unpackb(packb(td, encoding='utf-32'), encoding='utf-32')
            assert_equal(re, td)
    except LookupError:
        raise SkipTest

def testPackBytes():
    test_data = [
        b"", b"abcd", (b"defgh",),
        ]
    for td in test_data:
        check(td)

def testIgnoreUnicodeErrors():
    re = unpackb(packb(b'abc\xeddef'),
        encoding='utf-8', unicode_errors='ignore')
    assert_equal(re, "abcdef")

@raises(UnicodeDecodeError)
def testStrictUnicodeUnpack():
    unpackb(packb(b'abc\xeddef'), encoding='utf-8')

@raises(UnicodeEncodeError)
def testStrictUnicodePack():
    packb(six.u("abc\xeddef"), encoding='ascii', unicode_errors='strict')

def testIgnoreErrorsPack():
    re = unpackb(packb(six.u("abcФФФdef"), encoding='ascii', unicode_errors='ignore'), encoding='utf-8')
    assert_equal(re, six.u("abcdef"))

@raises(TypeError)
def testNoEncoding():
    packb(six.u("abc"), encoding=None)

def testDecodeBinary():
    re = unpackb(packb("abc"), encoding=None)
    assert_equal(re, b"abc")

def testPackFloat():
    assert_equal(packb(1.0, use_single_float=True),  b'\xca' + struct.pack('>f', 1.0))
    assert_equal(packb(1.0, use_single_float=False), b'\xcb' + struct.pack('>d', 1.0))

def testArraySize(sizes=[0, 5, 50, 1000]):
    bio = six.BytesIO()
    packer = Packer()
    for size in sizes:
        bio.write(packer.pack_array_header(size))
        for i in range(size):
            bio.write(packer.pack(i))

    bio.seek(0)
    unpacker = Unpacker(bio)
    for size in sizes:
        assert unpacker.unpack() == tuple(range(size))

def testMapSize(sizes=[0, 5, 50, 1000]):
    bio = six.BytesIO()
    packer = Packer()
    for size in sizes:
        bio.write(packer.pack_map_header(size))
        for i in range(size):
            bio.write(packer.pack(i)) # key
            bio.write(packer.pack(i * 2)) # value

    bio.seek(0)
    unpacker = Unpacker(bio)
    for size in sizes:
        assert unpacker.unpack() == {i: i * 2 for i in range(size)}




class odict(dict):
    '''Reimplement OrderedDict to run test on Python 2.6'''
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
    assert_equal(unpackb(packb(od)), dict(seq))
    # After object_pairs_hook is implemented.
    #def pair_hook(seq):
    #    return seq
    #assert_equal(unpackb(packb(od), object_pairs_hook=pair_hook), seq)


if __name__ == '__main__':
    main()
