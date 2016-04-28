#!/usr/bin/env python
# coding: utf-8


from array import array
from msgpack import packb, unpackb
import sys


# For Python < 3:
#  - array type only supports old buffer interface
#  - array.frombytes is not available, must use deprecated array.fromstring
if sys.version_info[0] < 3:
    def __memoryview(obj):
        return memoryview(buffer(obj))

    def __make_array(f, data):
        a = array(f)
        a.fromstring(data)
        return a

    def __get_data(a):
        return a.tostring()
else:
    __memoryview = memoryview

    def __make_array(f, data):
        a = array(f)
        a.frombytes(data)
        return a

    def __get_data(a):
        return a.tobytes()


def __run_test(format, nbytes, expected_header, expected_prefix, use_bin_type):
    # create a new array
    original_array = array(format)
    original_array.fromlist([255] * (nbytes // original_array.itemsize))
    original_data = __get_data(original_array)
    view = __memoryview(original_array)

    # pack, unpack, and reconstruct array
    packed = packb(view, use_bin_type=use_bin_type)
    unpacked = unpackb(packed)
    reconstructed_array = __make_array(format, unpacked)

    # check that we got the right amount of data
    assert len(original_data) == nbytes
    # check packed header
    assert packed[:1] == expected_header
    # check packed length prefix, if any
    assert packed[1:1+len(expected_prefix)] == expected_prefix
    # check packed data
    assert packed[1+len(expected_prefix):] == original_data
    # check array unpacked correctly
    assert original_array == reconstructed_array


# -----------
# test fixstr
# -----------


def test_memoryview_byte_fixstr():
    __run_test('B', 31, b'\xbf', b'', False)


def test_memoryview_float_fixstr():
    __run_test('f', 28, b'\xbc', b'', False)


# ----------
# test str16
# ----------


def test_memoryview_byte_str16():
    __run_test('B', 2**8, b'\xda', b'\x01\x00', False)


def test_memoryview_float_str16():
    __run_test('f', 2**8, b'\xda', b'\x01\x00', False)


# ----------
# test str32
# ----------


def test_memoryview_byte_str32():
    __run_test('B', 2**16, b'\xdb', b'\x00\x01\x00\x00', False)


def test_memoryview_float_str32():
    __run_test('f', 2**16, b'\xdb', b'\x00\x01\x00\x00', False)


# ---------
# test bin8
# ---------


def test_memoryview_byte_bin8():
    __run_test('B', 1, b'\xc4', b'\x01', True)


def test_memoryview_float_bin8():
    __run_test('f', 4, b'\xc4', b'\x04', True)


# ----------
# test bin16
# ----------


def test_memoryview_byte_bin16():
    __run_test('B', 2**8, b'\xc5', b'\x01\x00', True)


def test_memoryview_float_bin16():
    __run_test('f', 2**8, b'\xc5', b'\x01\x00', True)


# ----------
# test bin32
# ----------


def test_memoryview_byte_bin32():
    __run_test('B', 2**16, b'\xc6', b'\x00\x01\x00\x00', True)


def test_memoryview_float_bin32():
    __run_test('f', 2**16, b'\xc6', b'\x00\x01\x00\x00', True)
