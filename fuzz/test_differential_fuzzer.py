import sys
import math
import os
import pytest

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


SCRIPT_DIR = os.path.dirname(__file__)
CORPUS_DIR = os.path.join(SCRIPT_DIR, "test_differential_fuzzer_seed_corpus")
if os.path.exists(CORPUS_DIR):
    CORPUS = [
        open(os.path.join(CORPUS_DIR, f), "rb").read() for f in os.listdir(CORPUS_DIR)
    ]
else:
    # When this file is executed as a fuzz target the dirrectory
    # test_differential_fuzzer_seed_corpus does not exist
    CORPUS = []


@pytest.mark.parametrize("data", CORPUS)
def test_try_the_seed_corpus(data):
    TestOneInput(data)


def main():
    import atheris

    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
