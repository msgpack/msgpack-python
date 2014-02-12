from io import BytesIO
from msgpack import Unpacker, packb, OutOfData
from pytest import raises


def test_unpack_array_header_from_file():
    f = BytesIO(packb([1,2,3,4]))
    unpacker = Unpacker(f)
    assert unpacker.read_array_header() == 4
    assert unpacker.unpack() == 1
    assert unpacker.unpack() == 2
    assert unpacker.unpack() == 3
    assert unpacker.unpack() == 4
    with raises(OutOfData):
        unpacker.unpack()


if __name__ == '__main__':
    test_unpack_array_header_from_file()
