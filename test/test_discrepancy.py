import io
from pytest import raises, mark

try:
    from msgpack import _cmsgpack
except ImportError:
    _cmsgpack = None


@mark.skipif(_cmsgpack is None, reason="C extension not awailable")
@mark.parametrize("use_unpack", [True, False])
def test_exceed_max_buffer_size(use_unpack):
    """The C extension used to have a bug: when reading objects that require
    a buffer bigger than max_buffer_size it would behave as if there is not
    enough data

    See https://github.com/msgpack/msgpack-python/pull/464#issuecomment-786457374
    """
    buffer_size = 11
    max_buffer_size = 10
    f = io.BytesIO(b"\xc6" + buffer_size.to_bytes(4, "big") + b"z" * buffer_size)
    u = _cmsgpack.Unpacker(f, max_buffer_size=max_buffer_size)

    with raises(ValueError):
        if use_unpack:
            u.unpack()
        else:
            next(u)
