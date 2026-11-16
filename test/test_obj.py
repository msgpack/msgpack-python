#!/usr/bin/env python

from io import BytesIO

from pytest import raises

from msgpack import Unpacker, packb, unpackb


def _decode_complex(obj):
    if b"__complex__" in obj:
        return complex(obj[b"real"], obj[b"imag"])
    return obj


def _encode_complex(obj):
    if isinstance(obj, complex):
        return {b"__complex__": True, b"real": 1, b"imag": 2}
    return obj


def test_encode_hook():
    packed = packb([3, 1 + 2j], default=_encode_complex)
    unpacked = unpackb(packed, use_list=1)
    assert unpacked[1] == {b"__complex__": True, b"real": 1, b"imag": 2}


def test_decode_hook():
    packed = packb([3, {b"__complex__": True, b"real": 1, b"imag": 2}])
    unpacked = unpackb(packed, object_hook=_decode_complex, use_list=1)
    assert unpacked[1] == 1 + 2j


def test_decode_pairs_hook():
    packed = packb([3, {1: 2, 3: 4}])
    prod_sum = 1 * 2 + 3 * 4
    unpacked = unpackb(
        packed,
        object_pairs_hook=lambda lst: sum(k * v for k, v in lst),
        use_list=1,
        strict_map_key=False,
    )
    assert unpacked[1] == prod_sum


def test_decode_pairs_hook_receives_list():
    def reject_duplicate_keys(pairs):
        keys = [k for k, _ in pairs]
        assert len(keys) == len(set(keys))
        return dict(pairs)

    packed = packb([{"a": 1, "b": 2}, 3])
    assert unpackb(packed, object_pairs_hook=reject_duplicate_keys) == [{"a": 1, "b": 2}, 3]
    assert unpackb(packed, object_pairs_hook=lambda pairs: pairs[0]) == [("a", 1), 3]
    assert unpackb(packed, object_pairs_hook=lambda pairs: None) == [None, 3]


def test_only_one_obj_hook():
    with raises(TypeError):
        unpackb(b"", object_hook=lambda x: x, object_pairs_hook=lambda x: x)


def test_bad_hook():
    with raises(TypeError):
        packed = packb([3, 1 + 2j], default=lambda o: o)
        unpackb(packed, use_list=1)


def _arr_to_str(arr):
    return "".join(str(c) for c in arr)


def test_array_hook():
    packed = packb([1, 2, 3])
    unpacked = unpackb(packed, list_hook=_arr_to_str, use_list=1)
    assert unpacked == "123"


def test_array_hook_with_use_list_false():
    seen = []

    def hook(items):
        seen.append(items)
        return {"items": items}

    packed = packb([1, 2])
    expected = {"items": (1, 2)}
    assert unpackb(packed, use_list=False, list_hook=hook) == expected

    stream = packed + packb(3)
    unpackers = [
        Unpacker(use_list=False, list_hook=hook),
        Unpacker(BytesIO(stream), use_list=False, list_hook=hook),
    ]
    unpackers[0].feed(stream)
    for unpacker in unpackers:
        assert unpacker.unpack() == expected
        assert unpacker.unpack() == 3
    assert seen == [(1, 2)] * 3


class DecodeError(Exception):
    pass


def bad_complex_decoder(o):
    raise DecodeError("Ooops!")


def test_an_exception_in_objecthook1():
    with raises(DecodeError):
        packed = packb({1: {"__complex__": True, "real": 1, "imag": 2}})
        unpackb(packed, object_hook=bad_complex_decoder, strict_map_key=False)


def test_an_exception_in_objecthook2():
    with raises(DecodeError):
        packed = packb({1: [{"__complex__": True, "real": 1, "imag": 2}]})
        unpackb(packed, list_hook=bad_complex_decoder, use_list=1, strict_map_key=False)
