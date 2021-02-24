import pytest
from hypothesis import given
from hypothesis import strategies as st

try:
    from msgpack import _cmsgpack
except ImportError:
    _cmsgpack = None
from msgpack import fallback

# https://github.com/msgpack/msgpack/blob/master/spec.md#type-system
# TODO: test timestamps
# TODO: test the extension type
simple_types = (
    st.integers(min_value=-(2**63), max_value=2**64 - 1)
    | st.none()
    | st.booleans()
    | st.floats()
    # TODO: maximum byte size of a String object is (2^32)-1
    # the problem is that hypothesis only allows control over the max character count
    # TODO: String objects may contain invalid byte sequence
    | st.text()
    | st.binary(max_size=2**32 - 1)
)
def composite_types(any_type):
    return (
        st.lists(any_type, max_size=2**32 - 1)
        | st.dictionaries(simple_types, any_type, max_size=2**32 - 1)
    )
any_type = st.recursive(simple_types, composite_types)


@pytest.mark.skipif(_cmsgpack is None, reason='C extension is not available')
@given(any_type)
def test_extension_and_fallback_pack_identically(obj):
    extension_packer = _cmsgpack.Packer()
    fallback_packer = fallback.Packer()

    assert extension_packer.pack(obj) == fallback_packer.pack(obj)
