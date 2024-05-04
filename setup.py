#!/usr/bin/env python
import os
import sys


libraries = []
macros = []

if sys.platform == "win32":
    libraries.append("ws2_32")
    macros = [("__LITTLE_ENDIAN__", "1")]
    cflags = os.environ.get("CFLAGS")
    cxx20flag = "/std:c++20"
    if cflags is None:
        cflags = cxx20flag
    elif cxx20flag not in cflags:
        cflags += " " + cxx20flag
    os.environ["CFLAGS"] = cflags


from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist


PYPY = hasattr(sys, "pypy_version_info")


class NoCython(Exception):
    pass


try:
    import Cython.Compiler.Main as cython_compiler

    have_cython = True
except ImportError:
    have_cython = False


def cythonize(src):
    if not have_cython:
        raise Exception("Cython is required for building from checkout")
    sys.stderr.write(f"cythonize: {src!r}\n")
    cython_compiler.compile([src], cplus=True)


def ensure_source(src):
    pyx = os.path.splitext(src)[0] + ".pyx"

    if not os.path.exists(src) or have_cython and os.stat(src).st_mtime < os.stat(pyx).st_mtime:
        cythonize(pyx)


class BuildExt(build_ext):
    def build_extension(self, ext):
        for src in ext.sources:
            ensure_source(src)
        return build_ext.build_extension(self, ext)


# Cython is required for sdist
class Sdist(sdist):
    def __init__(self, *args, **kwargs):
        cythonize("msgpack/_cmsgpack.pyx")
        sdist.__init__(self, *args, **kwargs)


ext_modules = []
if not PYPY and not os.environ.get("MSGPACK_PUREPYTHON"):
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
