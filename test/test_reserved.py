import msgpack

reserved_bytes = b"\xc1\xc4\xc5\xc6\xc7\xc8\xc9\xd4\xd5\xd6\xd7\xd8\xd9"

def test_skip_reserved():
    packed_list = msgpack.packb([])
    for b in reserved_bytes:
        assert msgpack.unpackb(b+packed_list, use_list=1) == []
