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

if __name__ == '__main__':
    main()
