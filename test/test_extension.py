import array
import msgpack

def test_extension_type():
    class MyPacker(msgpack.Packer):
        def handle_extended_type(self, obj):
            if isinstance(obj, array.array):
                fmt = "ext 32"
                typecode = 123 # application specific typecode
                data = obj.tostring()
                return fmt, typecode, data

    class MyUnpacker(msgpack.Unpacker):
        def handle_extended_type(self, typecode, data):
            assert typecode == 123
            obj = array.array('d')
            obj.fromstring(data)
            return obj

    obj = [42, 'hello', array.array('d', [1.1, 2.2, 3.3])]
    s = msgpack.packb(obj, MyPacker)
    obj2 = msgpack.unpackb(s, MyUnpacker)
    assert obj == obj2
    
