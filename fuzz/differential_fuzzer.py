import sys

from msgpack import _cmsgpack, fallback


def TestOneInput(data):
    try:
        from_extension = _cmsgpack.unpackb(buf)
    except:
        return
    try:
        from_fallback = fallback.unpackb(buf)
    except:
        return
    if from_extension != from_fallback:
        raise RuntimeError(
            f"Decoding disagreement: input: {data}, from extension: {from_extension}, from fallback: {from_fallback}"
        )


def main():
    import atheris

    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
