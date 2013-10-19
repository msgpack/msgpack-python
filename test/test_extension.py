import array
import struct
import msgpack

def test_pack_extended_type():
    def p(s):
        packer = msgpack.Packer()
        packer.pack_extended_type(0x42, s)
        return packer.bytes()
    assert p('A')        == '\xd4\x42A'          # fixext 1
    assert p('AB')       == '\xd5\x42AB'         # fixext 2
    assert p('ABCD')     == '\xd6\x42ABCD'       # fixext 4
    assert p('ABCDEFGH') == '\xd7\x42ABCDEFGH'   # fixext 8
    assert p('A'*16)     == '\xd8\x42' + 'A'*16  # fixext 16
    assert p('ABC')      == '\xc7\x03\x42ABC'        # ext 8
    assert p('A'*0x0123)        == '\xc8\x01\x23\x42' + 'A'*0x0123 # ext 16
    assert p('A'*0x00012345)    == '\xc9\x00\x01\x23\x45\x42' + 'A'*0x00012345 # ext 32

def test_unpack_extended_type():
    class MyUnpacker(msgpack.Unpacker):
        def read_extended_type(self, typecode, data):
            return (typecode, data)

    def u(s):
        unpacker = MyUnpacker()
        unpacker.feed(s)
        return unpacker.unpack_one()

    assert u('\xd4\x42A')         == (0x42, 'A')        # fixext 1
    assert u('\xd5\x42AB')        == (0x42, 'AB')       # fixext 2
    assert u('\xd6\x42ABCD')      == (0x42, 'ABCD')     # fixext 4
    assert u('\xd7\x42ABCDEFGH')  == (0x42, 'ABCDEFGH') # fixext 8
    assert u('\xd8\x42' + 'A'*16) == (0x42, 'A'*16)     # fixext 16
    assert u('\xc7\x03\x42ABC')   == (0x42, 'ABC')      # ext 8
    assert (u('\xc8\x01\x23\x42' + 'A'*0x0123) ==
            (0x42, 'A'*0x0123))                         # ext 16
    assert (u('\xc9\x00\x01\x23\x45\x42' + 'A'*0x00012345) ==
            (0x42, 'A'*0x00012345))                     # ext 32


def test_extension_type():
    class MyPacker(msgpack.Packer):
        def handle_unknown_type(self, obj):
            if isinstance(obj, array.array):
                typecode = 123 # application specific typecode
                data = obj.tostring()
                self.pack_extended_type(typecode, data)
                return True

    class MyUnpacker(msgpack.Unpacker):
        def read_extended_type(self, typecode, data):
            assert typecode == 123
            obj = array.array('d')
            obj.fromstring(data)
            return obj

    obj = [42, 'hello', array.array('d', [1.1, 2.2, 3.3])]
    packer = MyPacker()
    unpacker = MyUnpacker(None)
    s = packer.pack(obj)
    unpacker.feed(s)
    obj2 = unpacker.unpack_one()
    assert obj == obj2
