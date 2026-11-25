from pytest import mark, raises

from msgpack import BufferFull, Packer, Unpacker, packb, unpackb


def test_unpack_buffer():
    from array import array

    buf = array("b")
    buf.frombytes(packb((b"foo", b"bar")))
    obj = unpackb(buf, use_list=1)
    assert [b"foo", b"bar"] == obj


def test_unpack_bytearray():
    buf = bytearray(packb((b"foo", b"bar")))
    obj = unpackb(buf, use_list=1)
    assert [b"foo", b"bar"] == obj
    expected_type = bytes
    assert all(type(s) is expected_type for s in obj)


def test_unpack_memoryview():
    buf = bytearray(packb((b"foo", b"bar")))
    view = memoryview(buf)
    obj = unpackb(view, use_list=1)
    assert [b"foo", b"bar"] == obj
    expected_type = bytes
    assert all(type(s) is expected_type for s in obj)


def test_packer_getbuffer():
    packer = Packer(autoreset=False)
    packer.pack_array_header(2)
    packer.pack(42)
    packer.pack("hello")
    buffer = packer.getbuffer()
    assert isinstance(buffer, memoryview)
    assert bytes(buffer) == b"\x92*\xa5hello"

    if Packer.__module__ == "msgpack._cmsgpack":  # only for Cython
        # cython Packer supports buffer protocol directly
        assert bytes(packer) == b"\x92*\xa5hello"

        with raises(BufferError):
            packer.pack(42)
        buffer.release()
        packer.pack(42)
        assert bytes(packer) == b"\x92*\xa5hello*"


@mark.parametrize("shape", [(2, 3), (3, 2), (1, 6)])
def test_unpack_multidimensional_buffer(shape):
    packed = packb(b"abcd")
    view = memoryview(packed).cast("B", shape)
    assert unpackb(view) == b"abcd"

    unpacker = Unpacker(max_buffer_size=len(packed))
    unpacker.feed(view)
    assert unpacker.unpack() == b"abcd"


def test_feed_multidimensional_buffer_limit():
    view = memoryview(packb(b"abcd")).cast("B", (2, 3))
    unpacker = Unpacker(max_buffer_size=5)
    unpacker.feed(packb(42))
    with raises(BufferFull):
        unpacker.feed(view)
    assert unpacker.unpack() == 42
    unpacker.feed(packb(43))
    assert unpacker.unpack() == 43


def test_unpack_scalar_buffer():
    view = memoryview(packb(42)).cast("B", ())
    assert unpackb(view) == 42
    unpacker = Unpacker()
    unpacker.feed(view)
    assert unpacker.unpack() == 42


def test_unpack_strided_multidimensional_buffer():
    packed = packb(b"abcd")
    padded = packed[:3] + b"xxx" + packed[3:] + b"xxx"
    view = memoryview(padded).cast("B", (4, 3))[::2]
    assert not view.contiguous
    assert unpackb(view) == b"abcd"
    unpacker = Unpacker(max_buffer_size=len(packed))
    unpacker.feed(view)
    assert unpacker.unpack() == b"abcd"
