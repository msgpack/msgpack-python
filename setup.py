#!/usr/bin/env python
# coding: utf-8
import os
import sys
import shutil
from glob import glob
from distutils.command.sdist import sdist
from setuptools import setup, Extension

from distutils.command.build_ext import build_ext

try:
    import Cython.Compiler.Main as cython_compiler
    have_cython = True
except ImportError:
    have_cython = False


def cythonize(src):
    sys.stderr.write("cythonize: %r\n" % (src,))
    cython_compiler.compile([src])

def ensure_source(src):
    pyx = os.path.splitext(src)[0] + '.pyx'

    if not os.path.exists(src):
        if not have_cython:
            raise Exception("""\
Cython is required for building extension from checkout.
Install Cython >= 0.16 or install msgpack from PyPI.
""")
        cythonize(pyx)
    elif (os.path.exists(pyx) and
          os.stat(src).st_mtime < os.stat(pyx).st_mtime and
          have_cython):
        cythonize(pyx)

    # Use C++ compiler on win32.
    # MSVC9 doesn't provide stdint.h when using C Compiler.
    if sys.platform == 'win32':
        cpp = src + 'pp'
        shutil.copy(src, cpp)
        return cpp
    else:
        return src


class BuildExt(build_ext):
    def build_extension(self, ext):
        ext.sources = list(map(ensure_source, ext.sources))
        return build_ext.build_extension(self, ext)


exec(open('msgpack/_version.py').read())

version_str = '.'.join(str(x) for x in version[:3])
if len(version) > 3 and version[3] != 'final':
    version_str += version[3]

# take care of extension modules.
if have_cython:
    class Sdist(sdist):
        def __init__(self, *args, **kwargs):
            for src in glob('msgpack/*.pyx'):
                cythonize(src)
            sdist.__init__(self, *args, **kwargs)
else:
    Sdist = sdist

sources = ['msgpack/_msgpack.c']
libraries = []
if sys.platform == 'win32':
    libraries.append('ws2_32')

if sys.byteorder == 'big':
    macros = [('__BIG_ENDIAN__', '1')]
else:
    macros = [('__LITTLE_ENDIAN__', '1')]

msgpack_mod = Extension('msgpack._msgpack',
                        sources=sources,
                        libraries=libraries,
                        include_dirs=['.'],
                        define_macros=macros,
                        )
del sources, libraries, macros


desc = 'MessagePack (de)serializer.'
f = open('README.rst')
long_desc = f.read()
f.close()
del f

setup(name='msgpack-python',
      author='INADA Naoki',
      author_email='songofacandy@gmail.com',
      version=version_str,
      cmdclass={'build_ext': BuildExt, 'sdist': Sdist},
      ext_modules=[msgpack_mod],
      packages=['msgpack'],
      description=desc,
      long_description=long_desc,
      url='http://msgpack.org/',
      download_url='http://pypi.python.org/pypi/msgpack/',
      classifiers=[
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          ]
      )
