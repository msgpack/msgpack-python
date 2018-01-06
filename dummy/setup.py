from setuptools import setup, Extension

long_desc = """\
msgpack-python is renamed to just msgpack.

Install msgpack by ``pip install msgpack``.
"""


setup(name='msgpack-python',
      author='INADA Naoki',
      author_email='songofacandy@gmail.com',
      version="0.5.0",
      description="Transition package for msgpack",
      long_description=long_desc,
      install_requires=["msgpack>=0.5"],
      url='http://msgpack.org/',
      license='Apache 2.0',
      classifiers=[
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
      ],
)
