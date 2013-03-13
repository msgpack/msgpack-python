set MSSdk=1
set DISTUTILS_USE_SDK=1

rem Python27 x86
rem call "C:\Program Files\Microsoft SDKs\Windows\v6.1\Bin\SetEnv.cmd" /Release /x86 /xp
call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars32.bat"
c:\Python27\python setup.py build_ext -f build install
pause

rem Python27 amd64
rem call "C:\Program Files\Microsoft SDKs\Windows\v6.1\Bin\SetEnv.cmd" /Release /x64 /xp
call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars64.bat"
c:\Python27_amd64\python setup.py build_ext -f build install
pause

rem Python33 x86
call "C:\Program Files\Microsoft SDKs\Windows\v7.1\bin\SetEnv.cmd" /Release /x86 /xp
c:\Python33\python setup.py build_ext -f build install
pause

rem Python33 amd64
call "C:\Program Files\Microsoft SDKs\Windows\v7.1\bin\SetEnv.cmd" /Release /x64 /xp
c:\Python33_amd64\python setup.py build_ext -f build install
pause
