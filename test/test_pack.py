#!/usr/bin/env python
# coding: utf-8

from nose import main
from nose.tools import *
from nose.plugins.skip import SkipTest

from msgpack import pack, packs, unpack, unpacks, Packer, Unpacker

from StringIO import StringIO

def check(data):
    re = unpacks(packs(data))
    assert_equal(re, data)

def testPack():
    test_data = [
            0, 1, 127, 128, 255, 256, 65535, 65536,
            -1, -32, -33, -128, -129, -32768, -32769,
            1.0,
        "", "a", "a"*31, "a"*32,
        None, True, False,
        (), ((),), ((), None,),
        {None: 0},
        (1<<23),
        ]
    for td in test_data:
        check(td)

def testPackUnicode():
    test_data = [
        u"", u"abcd", (u"defgh",), u"Русский текст",
        ]
    for td in test_data:
        re = unpacks(packs(td, encoding='utf-8'), encoding='utf-8')
        assert_equal(re, td)
        packer = Packer(encoding='utf-8')
        data = packer.pack(td)
        re = Unpacker(StringIO(data), encoding='utf-8').unpack()
        assert_equal(re, td)

def testPackUTF32():
    try:
        test_data = [
            u"", u"abcd", (u"defgh",), u"Русский текст",
            ]
        for td in test_data:
            re = unpacks(packs(td, encoding='utf-32'), encoding='utf-32')
            assert_equal(re, td)
    except LookupError:
        raise SkipTest

def testPackBytes():
    test_data = [
        "", "abcd", ("defgh",),
        ]
    for td in test_data:
        check(td)

def testPackNonSequenceObjects():
    test_objs = [1, 3.14, "Hello", [0, 1, 2], {'one': 1, 'two': 2}]
    out = StringIO()
    for obj in test_objs:
        pack(obj, out)
    out.seek(0)
    out_objs = []
    while 1:
        obj = unpack(out, use_list=True)
        if obj is None:
            break
        out_objs.append(obj)
    assert_equal(len(test_objs), len(out_objs))
    for a, b in zip(test_objs, out_objs):
        assert_equal(a, b)

def testIgnoreUnicodeErrors():
    re = unpacks(packs('abc\xeddef'),
        encoding='ascii', unicode_errors='ignore')
    assert_equal(re, "abcdef")

@raises(UnicodeDecodeError)
def testStrictUnicodeUnpack():
    unpacks(packs('abc\xeddef'), encoding='utf-8')

@raises(UnicodeEncodeError)
def testStrictUnicodePack():
    packs(u"abc\xeddef", encoding='ascii', unicode_errors='strict')

def testIgnoreErrorsPack():
    re = unpacks(
            packs(u"abcФФФdef", encoding='ascii', unicode_errors='ignore'),
            encoding='utf-8')
    assert_equal(re, u"abcdef")

@raises(TypeError)
def testNoEncoding():
    packs(u"abc", encoding=None)

def testDecodeBinary():
    re = unpacks(packs(u"abc"), encoding=None)
    assert_equal(re, "abc")

if __name__ == '__main__':
    main()
