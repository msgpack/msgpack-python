#!/bin/bash
set -ex
${PYTHON} -VV
${PYTHON} -m pip install setuptools wheel pytest build
${PYTHON} setup.py build_ext -if
${PYTHON} -c "from msgpack import _cmsgpack"
${PYTHON} -m pytest -v test
${PYTHON} -m build
