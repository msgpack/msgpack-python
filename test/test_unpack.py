import gc
import sys
import weakref
from io import BytesIO

from pytest import mark, raises

from msgpack import (
    ExtraData,
    ExtType,
    OutOfData,
    Unpacker,
    packb,
    unpack,
    unpackb,
)


def test_unpack_array_header_from_file():
    f = BytesIO(packb([1, 2, 3, 4]))
    unpacker = Unpacker(f)
    assert unpacker.read_array_header() == 4
    assert unpacker.unpack() == 1
    assert unpacker.unpack() == 2
    assert unpacker.unpack() == 3
    assert unpacker.unpack() == 4
    with raises(OutOfData):
        unpacker.unpack()


@mark.skipif(
    "not hasattr(sys, 'getrefcount') == True",
    reason="sys.getrefcount() is needed to pass this test",
)
def test_unpacker_hook_refcnt():
    result = []

    def hook(x):
        result.append(x)
        return x

    basecnt = sys.getrefcount(hook)

    up = Unpacker(object_hook=hook, list_hook=hook)

    assert sys.getrefcount(hook) >= basecnt + 2

    up.feed(packb([{}]))
    up.feed(packb([{}]))
    assert up.unpack() == [{}]
    assert up.unpack() == [{}]
    assert result == [{}, [{}], {}, [{}]]

    del up

    assert sys.getrefcount(hook) == basecnt


def test_unpacker_ext_hook():
    class MyUnpacker(Unpacker):
        def __init__(self):
            super().__init__(ext_hook=self._hook, raw=False)

        def _hook(self, code, data):
            if code == 1:
                return int(data)
            else:
                return ExtType(code, data)

    unpacker = MyUnpacker()
    unpacker.feed(packb({"a": 1}))
    assert unpacker.unpack() == {"a": 1}
    unpacker.feed(packb({"a": ExtType(1, b"123")}))
    assert unpacker.unpack() == {"a": 123}
    unpacker.feed(packb({"a": ExtType(2, b"321")}))
    assert unpacker.unpack() == {"a": ExtType(2, b"321")}


def test_unpacker_tell():
    objects = 1, 2, "abc", "def", "ghi"
    packed = b"\x01\x02\xa3abc\xa3def\xa3ghi"
    positions = 1, 2, 6, 10, 14
    unpacker = Unpacker(BytesIO(packed))
    for obj, unp, pos in zip(objects, unpacker, positions):
        assert obj == unp
        assert pos == unpacker.tell()


def test_unpacker_tell_read_bytes():
    objects = 1, "abc", "ghi"
    packed = b"\x01\x02\xa3abc\xa3def\xa3ghi"
    raw_data = b"\x02", b"\xa3def", b""
    lenghts = 1, 4, 999
    positions = 1, 6, 14
    unpacker = Unpacker(BytesIO(packed))
    for obj, unp, pos, n, raw in zip(objects, unpacker, positions, lenghts, raw_data):
        assert obj == unp
        assert pos == unpacker.tell()
        assert unpacker.read_bytes(n) == raw


@mark.skipif(
    Unpacker.__module__ == "msgpack.fallback",
    reason="specific to C extension reinit leak",
)
def test_unpacker_reinit_clears_partial_state():
    refs = []

    class Marker:
        pass

    def hook(code, data):
        obj = Marker()
        refs.append(weakref.ref(obj))
        return obj

    unpacker = Unpacker(ext_hook=hook, strict_map_key=False)
    # Keep parser state mid-map with a live key object from ext_hook.
    # Encodes: [ {ExtType(1, b"a"): <missing value>} ].
    unpacker.feed(b"\x91\x81\xd4\x01a")
    with raises(OutOfData):
        unpacker.unpack()
    assert len(refs) == 1
    assert refs[0]() is not None

    unpacker.__init__()
    gc.collect()
    assert refs[0]() is None
    with raises(OutOfData):
        unpacker.unpack()

    unpacker.feed(packb({"a": 1}))
    assert unpacker.unpack() == {"a": 1}


@mark.skipif(
    Unpacker.__module__ == "msgpack.fallback",
    reason="reentrant guard is implemented in C extension only",
)
def test_unpacker_reentrant_feed():
    import struct

    def ext_hook(code, data):
        # re-entrant feed on the SAME unpacker, large enough to force a buffer realloc
        up.feed(b"\xc0" * 100)
        return 0

    up = Unpacker(ext_hook=ext_hook, max_buffer_size=64 * 1024 * 1024)
    # array(11): [ ExtType(code=5, data=b'A') (fires the re-entrant hook), then 10 more elements ]
    up.feed(b"\xdc" + struct.pack(">H", 11) + b"\xd4\x05A" + b"\x2a" * 10)
    with raises(RuntimeError):
        up.unpack()


def test_unpackb_raises_extra_data_with_trailing_bytes():
    packed = packb(42) + packb("trailing")
    with raises(ExtraData) as exc_info:
        unpackb(packed)
    err = exc_info.value
    assert err.unpacked == 42
    assert err.extra == packb("trailing")


def test_unpack_raises_extra_data_on_stream_with_trailing_bytes():
    stream = BytesIO(packb(100) + packb(200))
    with raises(ExtraData) as exc_info:
        unpack(stream)
    assert exc_info.value.unpacked == 100
    assert exc_info.value.extra == packb(200)
