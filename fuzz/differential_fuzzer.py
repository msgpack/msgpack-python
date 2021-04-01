import sys
import math

from msgpack import _cmsgpack, fallback


def replace_nan(data, sentinel):
    if type(data) == float and math.isnan(data):
        return sentinel
    if type(data) == list:
        return [replace_nan(x, sentinel) for x in data]
    if type(data) == dict:
        return {k: replace_nan(v, sentinel) for k, v in data.items()}
    return data


def TestOneInput(data):
    try:
        from_extension = _cmsgpack.unpackb(data)
    except:
        return
    try:
        from_fallback = fallback.unpackb(data)
    except:
        return
    sentinel = object()
    if replace_nan(from_extension, sentinel) != replace_nan(from_fallback, sentinel):
        raise RuntimeError(
            f"Decoding disagreement: input: {data}, from extension: {from_extension}, from fallback: {from_fallback}"
        )


def main():
    import atheris

    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
