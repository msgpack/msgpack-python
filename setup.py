#!/usr/bin/env python
# coding: utf-8
import io
import os
import sys
from glob import glob
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist


PYPY = hasattr(sys, "pypy_version_info")
PY2 = sys.version_info[0] == 2


class NoCython(Exception):
    pass


try:
    import Cython.Compiler.Main as cython_compiler

    have_cython = True
except ImportError:
    have_cython = False


def cythonize(src):
    sys.stderr.write("cythonize: %r\n" % (src,))
    cython_compiler.compile([src], cplus=True)


def ensure_source(src):
    pyx = os.path.splitext(src)[0] + ".pyx"

    if not os.path.exists(src):
        if not have_cython:
            raise NoCython
        cythonize(pyx)
    elif (
        os.path.exists(pyx)
        and os.stat(src).st_mtime < os.stat(pyx).st_mtime
        and have_cython
    ):
        cythonize(pyx)
    return src


class BuildExt(build_ext):
    def build_extension(self, ext):
        try:
            ext.sources = list(map(ensure_source, ext.sources))
        except NoCython:
            print("WARNING")
            print("Cython is required for building extension from checkout.")
            print("Install Cython >= 0.16 or install msgpack from PyPI.")
            print("Falling back to pure Python implementation.")
            return
        try:
            return build_ext.build_extension(self, ext)
        except Exception as e:
            print("WARNING: Failed to compile extension modules.")
            print("msgpack uses fallback pure python implementation.")
            print(e)


# Cython is required for sdist
class Sdist(sdist):
    def __init__(self, *args, **kwargs):
        cythonize("msgpack/_cmsgpack.pyx")
        sdist.__init__(self, *args, **kwargs)


libraries = []
macros = []

if sys.platform == "win32":
    libraries.append("ws2_32")
    macros = [("__LITTLE_ENDIAN__", "1")]

ext_modules = []
if not PYPY and not PY2 and not os.environ.get("MSGPACK_PUREPYTHON"):
    ext_modules.append(
        Extension(
            "msgpack._cmsgpack",
            sources=["msgpack/_cmsgpack.cpp"],
            libraries=libraries,
            include_dirs=["."],
            define_macros=macros,
        )
    )
del libraries, macros


setup(
    cmdclass={"build_ext": BuildExt, "sdist": Sdist},
    ext_modules=ext_modules,
    packages=["msgpack"],
)
