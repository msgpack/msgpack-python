#!/bin/bash
DOCKER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DOCKER_DIR/shared.env"

set -e -x

ARCH=`uname -p`
echo "arch=$ARCH"

for V in "${PYTHON_VERSIONS[@]}"; do
    PYBIN=/opt/python/$V/bin
    rm -rf build/       # Avoid lib build by narrow Python is used by wide python
    $PYBIN/python setup.py bdist_wheel -p manylinux1_${ARCH}
done
