"""Test Unpacker's read_array_header and read_map_header methods"""

from io import BytesIO

from pytest import raises

from msgpack import OutOfData, Unpacker, packb

UnexpectedTypeException = ValueError


def test_read_array_header():
    unpacker = Unpacker()
    unpacker.feed(packb(["a", "b", "c"]))
    assert unpacker.read_array_header() == 3
    assert unpacker.unpack() == "a"
    assert unpacker.unpack() == "b"
    assert unpacker.unpack() == "c"
    try:
        unpacker.unpack()
        assert 0, "should raise exception"
    except OutOfData:
        assert 1, "okay"


def test_read_map_header():
    unpacker = Unpacker()
    unpacker.feed(packb({"a": "A"}))
    assert unpacker.read_map_header() == 1
    assert unpacker.unpack() == "a"
    assert unpacker.unpack() == "A"
    try:
        unpacker.unpack()
        assert 0, "should raise exception"
    except OutOfData:
        assert 1, "okay"


def test_incorrect_type_array():
    unpacker = Unpacker()
    unpacker.feed(packb(1))
    try:
        unpacker.read_array_header()
        assert 0, "should raise exception"
    except UnexpectedTypeException:
        assert 1, "okay"


def test_incorrect_type_map():
    unpacker = Unpacker()
    unpacker.feed(packb(1))
    try:
        unpacker.read_map_header()
        assert 0, "should raise exception"
    except UnexpectedTypeException:
        assert 1, "okay"


def test_correct_type_nested_array():
    unpacker = Unpacker()
    unpacker.feed(packb({"a": ["b", "c", "d"]}))
    try:
        unpacker.read_array_header()
        assert 0, "should raise exception"
    except UnexpectedTypeException:
        assert 1, "okay"


def test_incorrect_type_nested_map():
    unpacker = Unpacker()
    unpacker.feed(packb([{"a": "b"}]))
    try:
        unpacker.read_map_header()
        assert 0, "should raise exception"
    except UnexpectedTypeException:
        assert 1, "okay"


def test_incorrect_type_does_not_consume_object():
    packed = packb(1) + packb("abc") + packb({"a": 1}) + packb([2])
    unpackers = [Unpacker(), Unpacker(BytesIO(packed))]
    unpackers[0].feed(packed)
    for unpacker in unpackers:
        with raises(UnexpectedTypeException):
            unpacker.read_array_header()
        assert unpacker.tell() == 0
        assert unpacker.unpack() == 1

        with raises(UnexpectedTypeException):
            unpacker.read_map_header()
        assert unpacker.unpack() == "abc"

        # A map is not an array: the stream must stay in sync.
        with raises(UnexpectedTypeException):
            unpacker.read_array_header()
        assert unpacker.read_map_header() == 1
        assert unpacker.unpack() == "a"
        assert unpacker.unpack() == 1

        with raises(UnexpectedTypeException):
            unpacker.read_map_header()
        assert unpacker.read_array_header() == 1
        assert unpacker.unpack() == 2
        assert unpacker.tell() == len(packed)
