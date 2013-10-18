import array
import msgpack

def test_extension_type():
    class MyPacker(msgpack.Packer):
        def handle_unknown_type(self, obj):
            if isinstance(obj, array.array):
                fmt = "ext 32"
                typecode = 123 # application specific typecode
                data = obj.tostring()
                self.pack_extended_type(fmt, typecode, data)
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
