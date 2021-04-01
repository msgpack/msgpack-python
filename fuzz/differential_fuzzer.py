import sys
import math

from msgpack import _cmsgpack, fallback


def TestOneInput(data):
    try:
        from_extension = _cmsgpack.unpackb(data)
    except:
        return
    try:
        from_fallback = fallback.unpackb(data)
    except:
        return
    good = from_extension == from_fallback or (
        math.isnan(from_extension) and math.isnan(from_fallback)
    )
    if not good:
        raise RuntimeError(
            f"Decoding disagreement: input: {data}, from extension: {from_extension}, from fallback: {from_fallback}"
        )


def main():
    import atheris

    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
