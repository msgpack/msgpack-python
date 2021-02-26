import io
import struct
from pytest import raises, mark, skip

from msgpack import fallback

try:
    from msgpack import _cmsgpack
except ImportError:
    _cmsgpack = None


@mark.parametrize("impl", [fallback, _cmsgpack])
@mark.parametrize("use_unpack", [True, False])
def test_exceed_max_buffer_size(impl, use_unpack):
    """The C extension used to have a bug: when reading objects that require
    a buffer bigger than max_buffer_size it would behave as if there is not
    enough data

    See https://github.com/msgpack/msgpack-python/pull/464#issuecomment-786457374
    """
    if impl is None:
        skip("C extension not awailable")

    buffer_size = 11
    max_buffer_size = 10
    f = io.BytesIO(b"\xc6" + struct.pack(">I", buffer_size) + b"z" * buffer_size)
    u = impl.Unpacker(f, max_buffer_size=max_buffer_size)

    with raises(ValueError):
        if use_unpack:
            u.unpack()
        else:
            next(u)
