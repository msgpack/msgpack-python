import warnings
import pytest
import msgpack


def test_use_bin_type():
    with pytest.warns(FutureWarning):
        msgpack.packb(["foo", "bar"])
