import logging
from array import array
from typing import Any

import msgpack


def dfa(o: array):
    logging.info("Default called for %s", o)
    return dict(data=o.tobytes(), tcode=o.typecode)


def decode_array(obj):
    if isinstance(obj, dict) and "tcode" in obj:
        return memoryview(obj["data"]).cast(obj["tcode"])
    return obj


def encode_array(obj: Any, posn: int) -> Any | dict[str, Any]:
    if isinstance(obj, array):
        tcode = obj.typecode
        itemsize = obj.itemsize
        length = len(obj)
        bytesize = itemsize * length
        offset = posn + 1 + 5 + 1  # fixmap, fixstr + 4, binX
        if bytesize < 256:
            offset += 1
        elif bytesize < 65536:
            offset += 2
        elif bytesize < 2**32:
            offset += 4
        else:
            raise ValueError("Array too large (>= 4GiB)")

        print(f"{offset=}, {itemsize=}")
        if offset % itemsize == 0:
            pad = 0
        else:
            offset += 4  # prefix with pad so fixstr + 3 + ?
            pad = itemsize - (offset % itemsize)
            # use fixstr for padding so deduct one
            if pad < 2:
                pad += itemsize  # prewrap as pad cannot be less than one
            pad -= 1

        if pad:
            obj = dict(
                pad="." * pad,
                data=obj.tobytes(),
                tcode=tcode,
            )
        else:
            obj = dict(
                data=obj.tobytes(),
                tcode=tcode,
            )
    return obj


def check_align(pa, itemsize):
    """
    check of start of data, 0xc4 + 1/0xc5 + 2, 0xc6 + 4
    has aligned offset
    """
    offset = pa.index(b"\xa4data") + 5
    print(f"After data={offset}")
    if pa.startswith(b"\xc4", offset):
        offset += 2
    elif pa.startswith(b"\xc5", offset):
        offset += 3
    elif pa.startswith(b"\xc6", offset):
        offset += 5
    print(f"{offset=}, align={offset % itemsize}")
    assert offset % itemsize == 0


def test_default_top():
    eo = array("f", [0.1])
    pa = msgpack.packb(eo, default=dfa)
    print(pa)
    ao = msgpack.unpackb(pa, object_hook=decode_array)
    assert eo == ao

    pa = msgpack.packb(eo, default=encode_array)
    print(pa)
    check_align(pa, eo.itemsize)
    ad = msgpack.unpackb(pa)
    assert eo == memoryview(ad["data"]).cast(ad["tcode"])
    ao = msgpack.unpackb(pa, object_hook=decode_array)
    assert eo == ao
    print("Unpacked as", ao.tolist())


def test_default_second():
    eo = dict(config="ladybug", ndata=array("d", [0.1]))
    pa = msgpack.packb(eo, default=dfa)
    print(pa)
    ao = msgpack.unpackb(pa, object_hook=decode_array)
    assert eo == ao

    pa = msgpack.packb(eo, default=encode_array)
    print(pa)
    check_align(pa, eo["ndata"].itemsize)
    print(eo)
    ao = msgpack.unpackb(pa)
    ad = ao["ndata"]
    assert eo["ndata"] == memoryview(ad["data"]).cast(ad["tcode"])
    ao = msgpack.unpackb(pa, object_hook=decode_array)
    assert eo == ao
    print("Unpacked as", ao, ao["ndata"].tolist())


if __name__ == "__main__":
    print(msgpack.__file__)
    test_default_top()
    test_default_second()
