import array

import pytest

import msgpack
from msgpack import ExtType


@pytest.mark.parametrize("ext_hook", [None, 0, "hook", []])
def test_unpackb_invalid_ext_hook(ext_hook):
    with pytest.raises(TypeError, match="ext_hook.*callable"):
        msgpack.unpackb(b"\xc0", ext_hook=ext_hook)


@pytest.mark.parametrize("ext_hook", [None, 0, "hook", []])
def test_unpacker_invalid_ext_hook(ext_hook):
    with pytest.raises(TypeError, match="ext_hook.*callable"):
        msgpack.Unpacker(ext_hook=ext_hook)


@pytest.mark.parametrize("ext_hook", [None, 0, "hook", []])
def test_unpacker_reinit_invalid_ext_hook(ext_hook):
    unpacker = msgpack.Unpacker(ext_hook=lambda code, data: (code, data))
    unpacker.feed(b"\xd4\x42A")
    assert unpacker.unpack() == (0x42, b"A")

    with pytest.raises(TypeError, match="ext_hook.*callable"):
        unpacker.__init__(ext_hook=ext_hook)

    unpacker.__init__()
    unpacker.feed(b"\xd4\x42A")
    assert unpacker.unpack() == ExtType(0x42, b"A")


def test_pack_ext_type():
    def p(s):
        packer = msgpack.Packer(autoreset=False)
        packer.pack_ext_type(0x42, s)
        return packer.bytes()

    assert p(b"A") == b"\xd4\x42A"  # fixext 1
    assert p(b"AB") == b"\xd5\x42AB"  # fixext 2
    assert p(b"ABCD") == b"\xd6\x42ABCD"  # fixext 4
    assert p(b"ABCDEFGH") == b"\xd7\x42ABCDEFGH"  # fixext 8
    assert p(b"A" * 16) == b"\xd8\x42" + b"A" * 16  # fixext 16
    assert p(b"ABC") == b"\xc7\x03\x42ABC"  # ext 8
    assert p(b"A" * 0x0123) == b"\xc8\x01\x23\x42" + b"A" * 0x0123  # ext 16
    assert p(b"A" * 0x00012345) == b"\xc9\x00\x01\x23\x45\x42" + b"A" * 0x00012345  # ext 32


def test_pack_ext_type_autoreset():
    packer = msgpack.Packer()

    assert packer.pack_ext_type(0x42, b"A") == b"\xd4\x42A"
    assert packer.bytes() == b""
    assert packer.pack_ext_type(0x42, b"ABC") == b"\xc7\x03\x42ABC"
    assert packer.bytes() == b""


def test_unpack_ext_type():
    def check(b, expected):
        assert msgpack.unpackb(b) == expected

    check(b"\xd4\x42A", ExtType(0x42, b"A"))  # fixext 1
    check(b"\xd5\x42AB", ExtType(0x42, b"AB"))  # fixext 2
    check(b"\xd6\x42ABCD", ExtType(0x42, b"ABCD"))  # fixext 4
    check(b"\xd7\x42ABCDEFGH", ExtType(0x42, b"ABCDEFGH"))  # fixext 8
    check(b"\xd8\x42" + b"A" * 16, ExtType(0x42, b"A" * 16))  # fixext 16
    check(b"\xc7\x03\x42ABC", ExtType(0x42, b"ABC"))  # ext 8
    check(b"\xc8\x01\x23\x42" + b"A" * 0x0123, ExtType(0x42, b"A" * 0x0123))  # ext 16
    check(
        b"\xc9\x00\x01\x23\x45\x42" + b"A" * 0x00012345,
        ExtType(0x42, b"A" * 0x00012345),
    )  # ext 32


def test_extension_type():
    def default(obj):
        print("default called", obj)
        if isinstance(obj, array.array):
            typecode = 123  # application specific typecode
            try:
                data = obj.tobytes()
            except AttributeError:
                data = obj.tostring()
            return ExtType(typecode, data)
        raise TypeError(f"Unknown type object {obj!r}")

    def ext_hook(code, data):
        print("ext_hook called", code, data)
        assert code == 123
        obj = array.array("d")
        obj.frombytes(data)
        return obj

    obj = [42, b"hello", array.array("d", [1.1, 2.2, 3.3])]
    s = msgpack.packb(obj, default=default)
    obj2 = msgpack.unpackb(s, ext_hook=ext_hook)
    assert obj == obj2


def test_overriding_hooks():
    def default(obj):
        if isinstance(obj, int):
            return {"__type__": "long", "__data__": str(obj)}
        else:
            return obj

    obj = {"testval": 1823746192837461928374619}
    refobj = {"testval": default(obj["testval"])}
    refout = msgpack.packb(refobj)
    assert isinstance(refout, (str, bytes))
    testout = msgpack.packb(obj, default=default)

    assert refout == testout


@pytest.mark.parametrize("autoreset", [False, True])
@pytest.mark.parametrize(
    "typecode, error",
    [
        (-129, ValueError),
        (-128, ValueError),
        (-1, ValueError),
        (128, ValueError),
        (256, ValueError),
        (2**100, ValueError),
        (1.5, TypeError),
        (None, TypeError),
        ("1", TypeError),
    ],
)
def test_pack_ext_type_invalid_code(typecode, error, autoreset):
    packer = msgpack.Packer(autoreset=autoreset)
    packer.pack(42)
    before = packer.bytes()
    with pytest.raises(error):
        packer.pack_ext_type(typecode, b"A")
    assert packer.bytes() == before

    packed = packer.pack_ext_type(0, b"A")
    if not autoreset:
        packed = packer.bytes()
        assert packed[:1] == msgpack.packb(42)
        packed = packed[1:]
    assert msgpack.unpackb(packed) == ExtType(0, b"A")


@pytest.mark.parametrize("typecode", [0, 127])
def test_pack_ext_type_code_boundary(typecode):
    packed = msgpack.Packer().pack_ext_type(typecode, b"A")
    assert msgpack.unpackb(packed) == ExtType(typecode, b"A")
