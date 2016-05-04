#!/bin/bash
set -e -x

for V in cp35-cp35m cp34-cp34m cp27-cp27m cp27-cp27mu; do
    PYBIN=/opt/python/$V/bin
    $PYBIN/python setup.py install
    $PYBIN/pip install pytest
    pushd test
    $PYBIN/python -c 'import sys; print(hex(sys.maxsize))'
    $PYBIN/python -c 'from msgpack import _packer, _unpacker'
    $PYBIN/py.test -v
    popd
done
