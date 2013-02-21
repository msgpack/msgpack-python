import msgpack

reserved_bytes = [
        b"\xc1",
        b"\xc4",
        b"\xc5",
        b"\xc6",
        b"\xc7",
        b"\xc8",
        b"\xc9",
        b"\xd4",
        b"\xd5",
        b"\xd6",
        b"\xd7",
        b"\xd8",
        b"\xd9",
        ]

def test_skip_reserved():
    packed_list = msgpack.packb([])
    for b in reserved_bytes:
        assert msgpack.unpackb(b+packed_list, use_list=1) == []
