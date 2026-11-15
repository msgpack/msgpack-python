from pytest import mark, raises

from msgpack import Packer, packb, unpackb


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


@mark.skipif(
    Packer.__module__ == "msgpack.fallback",
    reason="reentrant guard is implemented in C extension only",
)
def test_packer_reentrant_default():
    def default(o):
        # touch the SAME packer, then return enough data to force a realloc
        o()
        return b"x" * (1 << 20)

    def export():
        memoryview(packer)

    def pack():
        packer.pack(1)

    packer = Packer(default=default, buf_size=1024)
    with raises(BufferError):
        packer.pack([b"A" * 512, export])
    with raises(BufferError):
        packer.pack_map_pairs([(1, export)])
    with raises(RuntimeError):
        packer.pack([b"A" * 512, pack])
    assert packer.pack([1, 2]) == b"\x92\x01\x02"
