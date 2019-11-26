import sys
import warnings

import msgpack
from msgpack import TimestampType

def test_timestamp_type():
    if sys.version_info[0] < 3:
        warnings.warn("msgpack-python does not support TimestampType in Python2.")
        return
    # timestamp32
    ts = TimestampType(2**32 - 1)
    assert ts.to_bytes() == b"\xff\xff\xff\xff"
    packed = msgpack.packb(ts)
    assert packed == b"\xd6\xff" + ts.to_bytes()
    unpacked = msgpack.unpackb(packed)
    assert ts == unpacked
    assert ts.seconds == 2**32 - 1 and ts.nanoseconds == 0


    # timestamp64
    ts = TimestampType(2**34 - 1, 999999999)
    assert ts.to_bytes() == b"\xee\x6b\x27\xff\xff\xff\xff\xff"
    packed = msgpack.packb(ts)
    assert packed == b"\xd7\xff" + ts.to_bytes()
    unpacked = msgpack.unpackb(packed)
    assert ts == unpacked
    assert ts.seconds == 2**34 - 1 and ts.nanoseconds == 999999999

    # timestamp96
    ts = TimestampType(2**63 - 1, 999999999)
    assert ts.to_bytes() == b"\x3b\x9a\xc9\xff\x7f\xff\xff\xff\xff\xff\xff\xff"
    packed = msgpack.packb(ts)
    assert packed == b"\xc7\x0c\xff" + ts.to_bytes()
    unpacked = msgpack.unpackb(packed)
    assert ts == unpacked
    assert ts.seconds == 2**63 - 1 and ts.nanoseconds == 999999999

    # negative fractional
    ts = TimestampType(-2.3)  #s: -3, ns: 700000000
    assert ts.to_bytes() == b"\x29\xb9\x27\x00\xff\xff\xff\xff\xff\xff\xff\xfd"
    packed = msgpack.packb(ts)
    assert packed == b"\xc7\x0c\xff" + ts.to_bytes()
    unpacked = msgpack.unpackb(packed)
    assert ts == unpacked
    assert ts.seconds == -3 and ts.nanoseconds == 700000000
