"""Test Unpacker's read_array_header and read_map_header methods"""
from pytest import raises
from msgpack import packb, Unpacker, OutOfData
UnexpectedTypeException = ValueError

def test_read_array_header(size=3):
    unpacker = Unpacker()
    unpacker.feed(packb([i for i in xrange(size)]))
    assert unpacker.read_array_header() == size
    for i in range(size):
        assert unpacker.unpack() == i
    raises(OutOfData, unpacker.unpack)


def test_read_map_header(size=3):
    unpacker = Unpacker()
    unpacker.feed(packb(dict((str(i), i) for i in xrange(size))))
    assert unpacker.read_map_header() == size
    for i in xrange(size):
        key = unpacker.unpack()
        assert unpacker.unpack() == int(key)
    raises(OutOfData, unpacker.unpack)


def test_read_raw_header(size=3):
    unpacker = Unpacker()
    exp = B'!' * size
    unpacker.feed(packb(exp))
    print 'fed', len(packb(exp)), 'bytes', repr(packb(exp))
    assert unpacker.read_raw_header() == size
    assert unpacker.read_bytes(size) == exp
    raises(OutOfData, unpacker.unpack)


def test_read_various_sizes():
    for test in [test_read_array_header, test_read_map_header, test_read_raw_header]:
        for size in [0, 5, 20, 30, ]: # should also test 65536, but slow in fallback under CPython
            test(size)


def test_incorrect_type_array():
    unpacker = Unpacker()
    unpacker.feed(packb(1))
    raises(UnexpectedTypeException, unpacker.read_array_header)


def test_incorrect_type_map():
    unpacker = Unpacker()
    unpacker.feed(packb(1))
    raises(UnexpectedTypeException, unpacker.read_map_header)


def test_incorrect_type_raw():
    unpacker = Unpacker()
    unpacker.feed(packb(1))
    raises(UnexpectedTypeException, unpacker.read_raw_header)


def test_correct_type_nested_array():
    unpacker = Unpacker()
    unpacker.feed(packb({'a': ['b', 'c', 'd']}))
    raises(UnexpectedTypeException, unpacker.read_array_header)


def test_incorrect_type_nested_map():
    unpacker = Unpacker()
    unpacker.feed(packb([{'a': 'b'}]))
    raises(UnexpectedTypeException, unpacker.read_map_header)
