"""Tests for cases where the user seeks to obtain packed msgpack objects"""

from nose import main
from nose.tools import *
import six
from msgpack import Unpacker, packb


def test_write_bytes():
    unpacker = Unpacker()
    unpacker.feed(b'abc')
    f = six.BytesIO()
    assert_equal(unpacker.unpack(f.write), ord('a'))
    assert_equal(f.getvalue(), b'a')
    f = six.BytesIO()
    assert unpacker.skip(f.write) is None
    assert_equal(f.getvalue(), b'b')
    f = six.BytesIO()
    assert unpacker.skip() is None
    assert_equal(f.getvalue(), b'')


def test_write_bytes_multi_buffer():
    long_val = (5) * 100
    expected = packb(long_val)
    unpacker = Unpacker(six.BytesIO(expected), read_size=3, max_buffer_size=3)

    f = six.BytesIO()
    unpacked = unpacker.unpack(f.write)
    assert_equal(unpacked, long_val)
    assert_equal(f.getvalue(), expected)

if __name__ == '__main__':
    main()
