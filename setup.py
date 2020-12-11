#!/usr/bin/env python
# coding: utf-8
import io
import os
import sys
from glob import glob
from distutils.command.sdist import sdist
from setuptools import setup, Extension

from distutils.command.build_ext import build_ext


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


exec(open("msgpack/_version.py").read())

version_str = ".".join(str(x) for x in version[:3])
if len(version) > 3 and version[3] != "final":
    version_str += version[3]

# Cython is required for sdist
class Sdist(sdist):
    def __init__(self, *args, **kwargs):
        cythonize("msgpack/_cmsgpack.pyx")
        sdist.__init__(self, *args, **kwargs)


libraries = []
if sys.platform == "win32":
    libraries.append("ws2_32")

if sys.byteorder == "big":
    macros = [("__BIG_ENDIAN__", "1")]
else:
    macros = [("__LITTLE_ENDIAN__", "1")]

ext_modules = []
if not PYPY and not PY2:
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


desc = "MessagePack (de)serializer."
with io.open("README.md", encoding="utf-8") as f:
    long_desc = f.read()
del f

setup(
    name="msgpack",
    author="Inada Naoki",
    author_email="songofacandy@gmail.com",
    version=version_str,
    cmdclass={"build_ext": BuildExt, "sdist": Sdist},
    ext_modules=ext_modules,
    packages=["msgpack"],
    description=desc,
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://msgpack.org/",
    project_urls={
        "Documentation": "https://msgpack-python.readthedocs.io/",
        "Source": "https://github.com/msgpack/msgpack-python",
        "Tracker": "https://github.com/msgpack/msgpack-python/issues",
    },
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
    ],
)
