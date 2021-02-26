import io
import struct
from pytest import raises, mark, skip

from msgpack.exceptions import OutOfData
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


@mark.parametrize(
    "type",
    [
        b"\xc6",  # bin 32
        b"\xdb",  # str 32
    ],
)
@mark.parametrize("impl", [fallback, _cmsgpack])
@mark.parametrize("use_unpack", [True, False])
def test_exceed_max_bin_len(type, impl, use_unpack):
    """msgpack attempts to prevent denial of service attacks that cause the
    parser to allocate too much memory. When the input is supplied via feed()
    this protection is implemented the same in both the extension and
    the fallback: feed() raises BufferFull. When the input is supplied via a
    file the extension and the fallback implement the protection differently:
    Extension:
        1. If there is enough data in the buffer to parse an object go to 5
        2. If the buffer is max_buffer_size and is full raise an error
        3. Read some data and append it to the buffer
        4. Go to 1
        5. Return the object
    Fallback:
        1. Check that the length of a bin/str/ext is in the sane range
        2. Read exactly that many bytes
    At the time of writing the fallback applies the length sanity check even
    when the data is supplied via feed() leading to a discrepancy: when you
    feed() a header of a bin, str or ext that is too large and call unpack()
    the extension asks for more data but the fallback raises a ValueError

    See https://github.com/msgpack/msgpack-python/pull/464#issuecomment-786506188
    """
    if impl is None:
        skip("C extension not awailable")

    bin_len = 11
    max_buffer_size = 10
    u = impl.Unpacker(max_buffer_size=max_buffer_size)
    u.feed(type + struct.pack(">I", bin_len))
    if use_unpack:
        with raises(OutOfData):
            u.unpack()
    else:
        with raises(StopIteration):
            next(u)
