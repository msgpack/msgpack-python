from pytest import raises

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


def _c_extension():
    return Packer.__module__ == "msgpack._cmsgpack"


def test_getbuffer_during_default_is_rejected():
    # The default callback runs in the middle of pack(). Exporting the
    # internal buffer there lets a later realloc free the view.
    if not _c_extension():
        return

    class Unsupported:
        pass

    def default(obj):
        packer.getbuffer()
        return b"ok"

    packer = Packer(default=default, autoreset=False)
    with raises(BufferError):
        packer.pack(Unsupported())
    packer.pack(b"ok")
    assert bytes(packer.getbuffer()) == b"\xc4\x02ok"


def test_getbuffer_during_dict_items_is_rejected():
    if not _c_extension():
        return

    packer = Packer(autoreset=False)

    class EvilDict(dict):
        def items(self):
            packer.getbuffer()
            return [(b"k", b"v")]

    with raises(BufferError):
        packer.pack(EvilDict({b"x": 1}))
    assert bytes(packer.getbuffer()) == b""


def test_getbuffer_during_map_pairs_is_rejected():
    if not _c_extension():
        return

    packer = Packer(autoreset=False)

    class EvilPairs:
        def __len__(self):
            return 1

        def __iter__(self):
            packer.getbuffer()
            yield (b"k", b"v")

    with raises(BufferError):
        packer.pack_map_pairs(EvilPairs())
    packer.reset()
    packer.pack(b"ok")
    assert bytes(packer.bytes()) == b"\xc4\x02ok"
