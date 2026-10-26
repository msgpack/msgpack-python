#!/usr/bin/env python
import sysconfig
import tracemalloc

import pytest

from msgpack import (
    ExtType,
    OutOfData,
    Packer,
    PackOverflowError,
    PackValueError,
    Unpacker,
    UnpackValueError,
    packb,
    unpackb,
)


def test_integer():
    x = -(2**63)
    assert unpackb(packb(x)) == x
    with pytest.raises(PackOverflowError):
        packb(x - 1)

    x = 2**64 - 1
    assert unpackb(packb(x)) == x
    with pytest.raises(PackOverflowError):
        packb(x + 1)


def test_single_float():
    x = 3.4028234663852886e38  # FLT_MAX
    assert unpackb(packb(x, use_single_float=True)) == x
    with pytest.raises(PackOverflowError):
        packb(x * 2, use_single_float=True)

    # Infinities are representable in single precision, so they must not raise.
    for x in (float("inf"), float("-inf")):
        assert unpackb(packb(x, use_single_float=True)) == x


def test_array_header():
    packer = Packer()
    packer.pack_array_header(2**32 - 1)
    with pytest.raises(PackValueError):
        packer.pack_array_header(2**32)


def test_map_header():
    packer = Packer()
    packer.pack_map_header(2**32 - 1)
    with pytest.raises(PackValueError):
        packer.pack_array_header(2**32)


@pytest.mark.parametrize("method", ["pack_array_header", "pack_map_header"])
@pytest.mark.parametrize("size", [-1, -(2**32)])
def test_negative_header_size(method, size):
    packer = Packer(autoreset=False)
    packer.pack("existing")
    with pytest.raises(PackValueError, match="size must be non-negative"):
        getattr(packer, method)(size)
    assert packer.bytes() == packb("existing")


def test_max_str_len():
    d = "x" * 3
    packed = packb(d)

    unpacker = Unpacker(max_str_len=3, raw=False)
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_str_len=2, raw=False)
    with pytest.raises(UnpackValueError):
        unpacker.feed(packed)
        unpacker.unpack()


def test_max_bin_len():
    d = b"x" * 3
    packed = packb(d, use_bin_type=True)

    unpacker = Unpacker(max_bin_len=3)
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_bin_len=2)
    with pytest.raises(UnpackValueError):
        unpacker.feed(packed)
        unpacker.unpack()


def test_max_array_len():
    d = [1, 2, 3]
    packed = packb(d)

    unpacker = Unpacker(max_array_len=3)
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_array_len=2)
    with pytest.raises(UnpackValueError):
        unpacker.feed(packed)
        unpacker.unpack()


def test_max_map_len():
    d = {1: 2, 3: 4, 5: 6}
    packed = packb(d)

    unpacker = Unpacker(max_map_len=3, strict_map_key=False)
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_map_len=2, strict_map_key=False)
    with pytest.raises(UnpackValueError):
        unpacker.feed(packed)
        unpacker.unpack()


@pytest.mark.parametrize("size", [9999, 10000, 10001, 20001])
@pytest.mark.parametrize("use_list", [False, True])
def test_array_preallocation_boundary(size, use_list):
    value = list(range(size))
    expected = value if use_list else tuple(value)
    packed = packb(value)
    assert unpackb(packed, use_list=use_list, list_hook=lambda obj: obj) == expected

    unpacker = Unpacker(use_list=use_list)
    # Suspend after crossing the preallocation boundary.
    unpacker.feed(packed[:-1])
    with pytest.raises(OutOfData):
        unpacker.unpack()
    unpacker.feed(packed[-1:])
    assert unpacker.unpack() == expected


@pytest.mark.parametrize("size", [9999, 10000, 10001, 20001])
def test_pairs_preallocation_boundary(size):
    value = {str(i): i for i in range(size)}
    expected = list(value.items())
    packed = packb(value)
    assert unpackb(packed, object_pairs_hook=list) == expected

    unpacker = Unpacker(object_pairs_hook=list)
    unpacker.feed(packed[:-1])
    with pytest.raises(OutOfData):
        unpacker.unpack()
    unpacker.feed(packed[-1:])
    assert unpacker.unpack() == expected


@pytest.mark.parametrize("kind", ["list", "tuple", "pairs"])
@pytest.mark.thread_unsafe(reason="tracemalloc changes process-wide state and measures all threads")
def test_nested_headers_preallocation(kind):
    packer = Packer()
    header = (
        packer.pack_map_header(100_000) if kind == "pairs" else packer.pack_array_header(100_000)
    )
    unpacker = Unpacker(
        use_list=kind != "tuple", object_pairs_hook=list if kind == "pairs" else None
    )
    # Map headers nest in key position, so no completed pairs are needed.
    unpacker.feed(header * 16)
    already_tracing = tracemalloc.is_tracing()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        with pytest.raises(OutOfData):
            unpacker.unpack()
        # Full preallocation would retain over 12 MB in the C unpacker.
        assert tracemalloc.get_traced_memory()[0] - before < 4 * 1024 * 1024
    finally:
        if not already_tracing:
            tracemalloc.stop()


def test_max_ext_len():
    d = ExtType(42, b"abc")
    packed = packb(d)

    unpacker = Unpacker(max_ext_len=3)
    unpacker.feed(packed)
    assert unpacker.unpack() == d

    unpacker = Unpacker(max_ext_len=2)
    with pytest.raises(UnpackValueError):
        unpacker.feed(packed)
        unpacker.unpack()


# PyPy fails following tests because of constant folding?
# https://bugs.pypy.org/issue1721
# @pytest.mark.skipif(True, reason="Requires very large memory.")
# def test_binary():
#    x = b'x' * (2**32 - 1)
#    assert unpackb(packb(x)) == x
#    del x
#    x = b'x' * (2**32)
#    with pytest.raises(ValueError):
#        packb(x)
#
#
# @pytest.mark.skipif(True, reason="Requires very large memory.")
# def test_string():
#    x = 'x' * (2**32 - 1)
#    assert unpackb(packb(x)) == x
#    x += 'y'
#    with pytest.raises(ValueError):
#        packb(x)
#
#
# @pytest.mark.skipif(True, reason="Requires very large memory.")
# def test_array():
#    x = [0] * (2**32 - 1)
#    assert unpackb(packb(x)) == x
#    x.append(0)
#    with pytest.raises(ValueError):
#        packb(x)


# auto max len


def test_auto_max_array_len():
    packed = b"\xde\x00\x06zz"
    with pytest.raises(UnpackValueError):
        unpackb(packed, raw=False)

    unpacker = Unpacker(max_buffer_size=5, raw=False)
    unpacker.feed(packed)
    with pytest.raises(UnpackValueError):
        unpacker.unpack()


# Skip on free-threaded CPython builds because this test depends on recursion behavior.
IS_FREE_THREADED_BUILD = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


@pytest.mark.skipif(IS_FREE_THREADED_BUILD, reason="Skipped on free-threaded build")
@pytest.mark.thread_unsafe
def test_nest_limit_1024():
    import sys

    # Build a list nested 1024 levels deep
    d = None
    for _ in range(1024):
        d = [d]

    # Temporarily raise Python's recursion limit so packing 1024 levels succeeds
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, 30000))
    try:
        packed = packb(d)
        result = unpackb(packed)
    finally:
        sys.setrecursionlimit(old_limit)

    # Verify structure iteratively to avoid hitting C-level recursion limit in ==
    for _ in range(1024):
        assert isinstance(result, list) and len(result) == 1
        result = result[0]
    assert result is None


def test_auto_max_map_len():
    # len(packed) == 6 -> max_map_len == 3
    packed = b"\xde\x00\x04zzz"
    with pytest.raises(UnpackValueError):
        unpackb(packed, raw=False)

    unpacker = Unpacker(max_buffer_size=6, raw=False)
    unpacker.feed(packed)
    with pytest.raises(UnpackValueError):
        unpacker.unpack()
