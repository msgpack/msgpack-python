#!/bin/bash
set -ex
${PYTHON} -VV
${PYTHON} -m pip install setuptools wheel pytest
${PYTHON} setup.py build_ext -if
${PYTHON} -c "from msgpack import _cmsgpack"
${PYTHON} setup.py bdist_wheel
${PYTHON} -m pytest -v test
