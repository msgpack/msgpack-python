from msgpack import fallback

try:
    from msgpack import _cmsgpack

    has_ext = True
except ImportError:
    has_ext = False
import timeit


def profile(name, func):
    times = timeit.repeat(func, number=1000, repeat=4)
    times = ", ".join(["%8f" % t for t in times])
    print("%-30s %40s" % (name, times))


def simple(name, data):
    if has_ext:
        packer = _cmsgpack.Packer()
        profile("packing %s (ext)" % name, lambda: packer.pack(data))
    packer = fallback.Packer()
    profile("packing %s (fallback)" % name, lambda: packer.pack(data))

    data = packer.pack(data)
    if has_ext:
        profile("unpacking %s (ext)" % name, lambda: _cmsgpack.unpackb(data))
    profile("unpacking %s (fallback)" % name, lambda: fallback.unpackb(data))


def main():
    simple("integers", [7] * 10000)
    simple("bytes", [b"x" * n for n in range(100)] * 10)
    simple("lists", [[]] * 10000)
    simple("dicts", [{}] * 10000)


main()
