from msgpack import Bypass, packb, unpackb


def test_roundtrip_bypassed_bytes():
    binary = b"\x00\x01\x02\x03\x04\x05"

    binary_packed = packb(binary)
    binary_bypassed_packed = packb(Bypass(binary_packed))

    assert binary_bypassed_packed == binary_packed
    assert unpackb(binary_packed) == binary


def test_roundtrip_bypassed_object():
    obj = {"key0": {"key1": {"key2": {"key3": [1, 2, 3]}}}}

    obj_packed = packb(obj)
    obj_bypassed_packed = packb(Bypass(obj_packed))

    assert obj_bypassed_packed == obj_packed
    assert unpackb(obj_bypassed_packed) == obj


def test_roundtrip_deep_bypassed_object():
    obj = {"key0": {"key1": {"key2": {"key3": [1, 2, 3]}}}}
    obj_bypassed = {"key0": {"key1": {"key2": {"key3": [1, 2, Bypass(packb(3))]}}}}

    assert packb(obj) == packb(obj_bypassed)
    assert unpackb(packb(obj)) == obj


def test_roundtrip_bypassed_object_with_cache():
    class SimpleCache:
        def __init__(self, obj):
            self.obj = obj
            self.packed = None

        def get_packed(self):
            if self.packed is None:
                self.packed = packb(self.obj)

            return Bypass(self.packed)

    def default(obj):
        if isinstance(obj, SimpleCache):
            return obj.get_packed()
        return obj

    obj = {"key0": {"key1": {"key2": {"key3": [1, 2, 3]}}}}
    cache = SimpleCache(obj)

    obj_packed = packb(cache.obj, default=default)
    cache.packed = obj_packed
    obj_bypassed_packed = packb(Bypass(cache.packed))

    assert obj_bypassed_packed == obj_packed
    assert unpackb(obj_bypassed_packed) == cache.obj
