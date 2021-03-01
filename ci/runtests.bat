%PYTHON%\python.exe -m pip install -U pip wheel pytest hypothesis
%PYTHON%\python.exe setup.py build_ext -i
%PYTHON%\python.exe setup.py install
%PYTHON%\python.exe -c "import sys; print(hex(sys.maxsize))"
%PYTHON%\python.exe -c "from msgpack import _cmsgpack"
%PYTHON%\python.exe setup.py bdist_wheel
%PYTHON%\python.exe -m pytest -v test
SET EL=%ERRORLEVEL%
exit /b %EL%
