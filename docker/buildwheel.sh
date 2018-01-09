#!/bin/bash
set -e -x

ARCH=`uname -p`
echo "arch=$ARCH"

for V in cp36-cp36m cp35-cp35m cp27-cp27m cp27-cp27mu; do
    PYBIN=/opt/python/$V/bin
    rm -rf build/       # Avoid lib build by narrow Python is used by wide python
    $PYBIN/python setup.py bdist_wheel -p manylinux1_${ARCH}
done
