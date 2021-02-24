import pytest
from hypothesis import given
from hypothesis import strategies as st

try:
    from msgpack import _cmsgpack
except ImportError:
    _cmsgpack = None
from msgpack import fallback

# https://github.com/msgpack/msgpack/blob/master/spec.md#type-system
simple_types = (
    st.integers(min_value=-(2**63), max_value=(2**64)-1)
    | st.none()
    | st.booleans()
)


@pytest.mark.skipif(_cmsgpack is None, reason='C extension is not available')
@given(simple_types)
def test_extension_and_fallback_pack_identically(obj):
    extension_packer = _cmsgpack.Packer()
    fallback_packer = fallback.Packer()

    assert extension_packer.pack(obj) == fallback_packer.pack(obj)
