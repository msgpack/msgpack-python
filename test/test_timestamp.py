import msgpack
from msgpack import Timestamp


def test_timestamp():
    # timestamp32
    ts = Timestamp(2**32 - 1)
    assert ts.to_bytes() == b"\xff\xff\xff\xff"
    packed = msgpack.packb(ts)
    assert packed == b"\xd6\xff" + ts.to_bytes()
    unpacked = msgpack.unpackb(packed)
    assert ts == unpacked
    assert ts.seconds == 2**32 - 1 and ts.nanoseconds == 0

    # timestamp64
    ts = Timestamp(2**34 - 1, 999999999)
    assert ts.to_bytes() == b"\xee\x6b\x27\xff\xff\xff\xff\xff"
    packed = msgpack.packb(ts)
    assert packed == b"\xd7\xff" + ts.to_bytes()
    unpacked = msgpack.unpackb(packed)
    assert ts == unpacked
    assert ts.seconds == 2**34 - 1 and ts.nanoseconds == 999999999

    # timestamp96
    ts = Timestamp(2**63 - 1, 999999999)
    assert ts.to_bytes() == b"\x3b\x9a\xc9\xff\x7f\xff\xff\xff\xff\xff\xff\xff"
    packed = msgpack.packb(ts)
    assert packed == b"\xc7\x0c\xff" + ts.to_bytes()
    unpacked = msgpack.unpackb(packed)
    assert ts == unpacked
    assert ts.seconds == 2**63 - 1 and ts.nanoseconds == 999999999

    # negative fractional
    ts = Timestamp(-2.3)  #s: -3, ns: 700000000
    assert ts.to_bytes() == b"\x29\xb9\x27\x00\xff\xff\xff\xff\xff\xff\xff\xfd"
    packed = msgpack.packb(ts)
    assert packed == b"\xc7\x0c\xff" + ts.to_bytes()
    unpacked = msgpack.unpackb(packed)
    assert ts == unpacked
    assert ts.seconds == -3 and ts.nanoseconds == 700000000


def test_timestamp_to():
    t = Timestamp(42, 14)
    assert t.to_float_s() == 42.000000014
    assert t.to_unix_ns() == 42000000014
