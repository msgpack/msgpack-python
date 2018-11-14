#!/bin/bash
set -e -x

for V in cp36-cp36m cp35-cp35m cp27-cp27m cp27-cp27mu; do
    PYBIN=/opt/python/$V/bin
    $PYBIN/python setup.py install
    rm -rf build/       # Avoid lib build by narrow Python is used by wide python
    $PYBIN/pip install pytest
    pushd test          # prevent importing msgpack package in current directory.
    $PYBIN/python -c 'import sys; print(hex(sys.maxsize))'
    $PYBIN/python -c 'from msgpack import _cmsgpack'  # Ensure extension is available
    $PYBIN/pytest -v .
    popd
done
