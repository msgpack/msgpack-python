from io import BytesIO
import sys
from msgpack import Unpacker, packb, OutOfData
from pytest import raises, mark


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


@mark.skipif(not hasattr(sys, 'getrefcount'),
             reason='sys.getrefcount() is needed to pass this test')
def test_unpacker_hook_refcnt():
    result = []

    def hook(x):
        result.append(x)
        return x

    basecnt = sys.getrefcount(hook)

    up = Unpacker(object_pairs_hook=hook, list_hook=hook)

    assert sys.getrefcount(hook) >= basecnt + 2

    up.feed(packb([{}]))
    up.feed(packb([{}]))
    assert up.unpack() == [{}]
    assert up.unpack() == [{}]
    assert result == [[{}], [{}]]

    del up

    assert sys.getrefcount(hook) == basecnt


if __name__ == '__main__':
    test_unpack_array_header_from_file()
    test_unpacker_hook_refcnt()
