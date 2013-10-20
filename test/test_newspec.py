# coding: utf-8

from msgpack import packb, unpackb


def test_str8():
    header = b'\xd9'
    data = b'x' * 32
    b = packb(data.decode(), use_bin_type=True)
    assert len(b) == len(data) + 2
    assert b[0:2] == header + b'\x20'
    assert b[2:] == data
    assert unpackb(b) == data

    data = b'x' * 255
    b = packb(data.decode(), use_bin_type=True)
    assert len(b) == len(data) + 2
    assert b[0:2] == header + b'\xff'
    assert b[2:] == data
    assert unpackb(b) == data


def test_bin8():
    header = b'\xc4'
    data = b''
    b = packb(data, use_bin_type=True)
    assert len(b) == len(data) + 2
    assert b[0:2] == header + b'\x00'
    assert b[2:] == data
    assert unpackb(b) == data

    data = b'x' * 255
    b = packb(data, use_bin_type=True)
    assert len(b) == len(data) + 2
    assert b[0:2] == header + b'\xff'
    assert b[2:] == data
    assert unpackb(b) == data


def test_bin16():
    header = b'\xc5'
    data = b'x' * 256
    b = packb(data, use_bin_type=True)
    assert len(b) == len(data) + 3
    assert b[0:1] == header
    assert b[1:3] == b'\x01\x00'
    assert b[3:] == data
    assert unpackb(b) == data

    data = b'x' * 65535
    b = packb(data, use_bin_type=True)
    assert len(b) == len(data) + 3
    assert b[0:1] == header
    assert b[1:3] == b'\xff\xff'
    assert b[3:] == data
    assert unpackb(b) == data


def test_bin32():
    header = b'\xc6'
    data = b'x' * 65536
    b = packb(data, use_bin_type=True)
    assert len(b) == len(data) + 5
    assert b[0:1] == header
    assert b[1:5] == b'\x00\x01\x00\x00'
    assert b[5:] == data
    assert unpackb(b) == data


