#!/bin/bash
DOCKER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DOCKER_DIR/shared.env"

set -e -x

for V in "${PYTHON_VERSIONS[@]}"; do
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
