import pytest
from hypothesis import given
from hypothesis import strategies as st

try:
    from msgpack import _cmsgpack
except ImportError:
    _cmsgpack = None
from msgpack import fallback

HYPOTHESIS_MAX = 2**10

# https://github.com/msgpack/msgpack/blob/master/spec.md#type-system
# TODO: test timestamps
# TODO: test the extension type
simple_types = (
    st.integers(min_value=-(2**63), max_value=2**64 - 1)
    | st.none()
    | st.booleans()
    | st.floats()
    # TODO: String objects may contain invalid byte sequence
    | st.text(max_size=HYPOTHESIS_MAX)
    | st.binary(max_size=HYPOTHESIS_MAX)
)
def composite_types(any_type):
    return (
        st.lists(any_type, max_size=HYPOTHESIS_MAX)
        | st.dictionaries(simple_types, any_type, max_size=HYPOTHESIS_MAX)
    )
any_type = st.recursive(simple_types, composite_types)


@pytest.mark.skipif(_cmsgpack is None, reason='C extension is not available')
@given(any_type)
def test_extension_and_fallback_pack_identically(obj):
    extension_packer = _cmsgpack.Packer()
    fallback_packer = fallback.Packer()

    assert extension_packer.pack(obj) == fallback_packer.pack(obj)


@pytest.mark.parametrize('impl', [fallback, _cmsgpack])
@given(obj=any_type)
def test_roudtrip(obj, impl):
    if impl is None:
        pytest.skip('C extension is not available')
    packer = impl.Packer()
    unpacker = impl.Unpacker(strict_map_key=False)
    unpacker.feed(packer.pack(obj))
    got = list(unpacker)
    # using [obj] == got fails because NaN != NaN
    assert repr([obj]) == repr(got)
