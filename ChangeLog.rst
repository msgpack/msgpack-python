1.1.2
=====

Release Date: 2025-10-08

* Update Cython to v3.1.4
* Update cibuildwheel to v3.2.0
* Drop Python 3.8
* Add Python 3.14

1.1.1
=====

Release Date: 2025-06-13

* No change from 1.1.1rc1.

1.1.1rc1
========

Release Date: 2025-06-06

* Update Cython to 3.1.1 and cibuildwheel to 2.23.3.

1.1.0
=====

Release Date: 2024-09-10

* use ``PyLong_*`` instead of ``PyInt_*`` for compatibility with
  future Cython. (#620)

1.1.0rc2
========

Release Date: 2024-08-19

* Update Cython to 3.0.11 for better Python 3.13 support.
* Update cibuildwheel to 2.20.0 to build Python 3.13 wheels.

1.1.0rc1
========

Release Date: 2024-05-07

* Update Cython to 3.0.10 to reduce C warnings and future support for Python 3.13.
* Stop using C++ mode in Cython to reduce compile error on some compilers.
* ``Packer()`` has ``buf_size`` option to specify initial size of
  internal buffer to reduce reallocation.
* The default internal buffer size of ``Packer()`` is reduced from
  1MiB to 256KiB to optimize for common use cases. Use ``buf_size``
  if you are packing large data.
* ``Timestamp.to_datetime()`` and ``Timestamp.from_datetime()`` become
  more accurate by avoiding floating point calculations. (#591)
* The Cython code for ``Unpacker`` has been slightly rewritten for maintainability.
* The fallback implementation of ``Packer()`` and ``Unpacker()`` now uses keyword-only
  arguments to improve compatibility with the Cython implementation.

1.0.8
=====

Release Date: 2024-03-01

* Update Cython to 3.0.8. This fixes memory leak when iterating
  ``Unpacker`` object on Python 3.12.
* Do not include C/Cython files in binary wheels.


1.0.7
=====

Release Date: 2023-09-28

* Fix build error of extension module on Windows. (#567)
* ``setup.py`` doesn't skip build error of extension module. (#568)


1.0.6
=====

Release Date: 2023-09-21

.. note::
   v1.0.6 Wheels for Windows don't contain extension module.
   Please upgrade to v1.0.7 or newer.

* Add Python 3.12 wheels (#517)
* Remove Python 2.7, 3.6, and 3.7 support


1.0.5
=====

Release Date: 2023-03-08

* Use ``__BYTE_ORDER__`` instead of ``__BYTE_ORDER`` for portability. (#513, #514)
* Add Python 3.11 wheels (#517)
* fallback: Fix packing multidimensional memoryview (#527)

1.0.4
=====

Release Date: 2022-06-03

* Support Python 3.11 (beta).
* Don't define `__*_ENDIAN__` macro on Unix. by @methane in https://github.com/msgpack/msgpack-python/pull/495
* Use PyFloat_Pack8() on Python 3.11a7 by @vstinner in https://github.com/msgpack/msgpack-python/pull/499
* Fix Unpacker max_buffer_length handling by @methane in https://github.com/msgpack/msgpack-python/pull/506

1.0.3
=====

Release Date: 2021-11-24 JST

* Fix Docstring (#459)
* Fix error formatting (#463)
* Improve error message about strict_map_key (#485)

1.0.2
=====

* Fix year 2038 problem regression in 1.0.1. (#451)

1.0.1
=====

* Add Python 3.9 and linux/arm64 wheels. (#439)
* Fixed Unpacker.tell() after read_bytes() (#426)
* Fixed unpacking datetime before epoch on Windows (#433)
* Fixed fallback Packer didn't check DateTime.tzinfo (#434)

1.0.0
=====

Release Date: 2020-02-17

* Remove Python 2 support from the ``msgpack/_cmsgpack``.
  ``msgpack/fallback`` still supports Python 2.
* Remove ``encoding`` option from the Packer and Unpacker.
* Unpacker: The default value of ``max_buffer_size`` is changed to 100MiB.
* Unpacker: ``strict_map_key`` is True by default now.
* Unpacker: String map keys are interned.
* Drop old buffer protocol support.
* Support Timestamp type.
* Support serializing and decerializing ``datetime`` object
  with tzinfo.
* Unpacker: ``Fix Unpacker.read_bytes()`` in fallback implementation. (#352)


0.6.2
=====

Release Date: 2019-09-20

* Support Python 3.8.
* Update Cython to 0.29.13 for support Python 3.8.
* Some small optimizations.


0.6.1
======

Release Date: 2019-01-25

This release is for mitigating pain caused by v0.6.0 reduced max input limits
for security reason.

* ``unpackb(data)`` configures ``max_*_len`` options from ``len(data)``,
  instead of static default sizes.

* ``Unpacker(max_buffer_len=N)`` configures ``max_*_len`` options from ``N``,
  instead of static default sizes.

* ``max_bin_len``, ``max_str_len``, and ``max_ext_len`` are deprecated.
  Since this is minor release, it's document only deprecation.


0.6.0
======

Release Date: 2018-11-30

This release contains some backward incompatible changes for security reason (DoS).

Important changes
-----------------

* unpacker: Default value of input limits are smaller than before to avoid DoS attack.
  If you need to handle large data, you need to specify limits manually. (#319)

* Unpacker doesn't wrap underlying ``ValueError`` (including ``UnicodeError``) into
  ``UnpackValueError``.  If you want to catch all exception during unpack, you need
  to use ``try ... except Exception`` with minimum try code block. (#323, #233)

* ``PackValueError`` and ``PackOverflowError`` are also removed.  You need to catch
  normal ``ValueError`` and ``OverflowError``. (#323, #233)

* Unpacker has ``strict_map_key`` option now.  When it is true, only bytes and str
  (unicode in Python 2) are allowed for map keys.  It is recommended to avoid
  hashdos.  Default value of this option is False for backward compatibility reason.
  But it will be changed True in 1.0. (#296, #334)

Other changes
-------------

* Extension modules are merged.  There is ``msgpack._cmsgpack`` instead of
  ``msgpack._packer`` and ``msgpack._unpacker``. (#314, #328)

* Add ``Unpacker.getbuffer()`` method. (#320)

* unpacker: ``msgpack.StackError`` is raised when input data contains too
  nested data. (#331)

* unpacker: ``msgpack.FormatError`` is raised when input data is not valid
  msgpack format. (#331)


0.5.6
======

* Fix fallback.Unpacker.feed() dropped unused data from buffer (#287)
* Resurrect fallback.unpack() and _unpacker.unpack().
  They were removed at 0.5.5 but it breaks backward compatibility. (#288, #290)

0.5.5
======

* Fix memory leak in pure Python Unpacker.feed() (#283)
* Fix unpack() didn't support `raw` option (#285)

0.5.4
======

* Undeprecate ``unicode_errors`` option. (#278)

0.5.3
======

* Fixed regression when passing ``unicode_errors`` to Packer but not ``encoding``. (#277)

0.5.2
======

* Add ``raw`` option to Unpacker.  It is preferred way than ``encoding`` option.

* Packer.pack() reset buffer on exception (#274)


0.5.1
======

* Remove FutureWarning about use_bin_type option (#271)

0.5.0
======

There are some deprecations.  Please read changes carefully.

Changes
-------

* Drop Python 2.6 and ~3.4 support.  Python 2.7 and 3.5+ are supported.

* Deprecate useless custom exceptions.  Use ValueError instead of PackValueError,
  Exception instead of PackException and UnpackException, etc...
  See msgpack/exceptions.py

* Add *strict_types* option to packer.  It can be used to serialize subclass of
  builtin types.  For example, when packing object which type is subclass of dict,
  ``default()`` is called.  ``default()`` is called for tuple too.

* Pure Python implementation supports packing memoryview object.

* Support packing bytearray.

* Add ``Unpacker.tell()``.  And ``write_bytes`` option is deprecated.


Bugs fixed
----------

* Fixed zero length raw can't be decoded when encoding is specified. (#236)


0.4.8
=====
:release date: 2016-07-29

Bugs fixed
----------

* Calling ext_hook with wrong length. (Only on Windows, maybe. #203)


0.4.7
=====
:release date: 2016-01-25

Bugs fixed
----------

* Memory leak when unpack is failed

Changes
-------

* Reduce compiler warnings while building extension module
* unpack() now accepts ext_hook argument like Unpacker and unpackb()
* Update Cython version to 0.23.4
* default function is called when integer overflow


0.4.6
=====
:release date: 2015-03-13

Bugs fixed
----------

* fallback.Unpacker: Fix Data corruption when OutOfData.
  This bug only affects "Streaming unpacking."


0.4.5
=====
:release date: 2015-01-25

Incompatible Changes
--------------------

Changes
-------

Bugs fixed
----------

* Fix test failure on pytest 2.3.  (by @ktdreyer)
* Fix typos in ChangeLog.  (Thanks to @dmick)
* Improve README.rst  (by @msabramo)


0.4.4
=====
:release date: 2015-01-09

Incompatible Changes
--------------------

Changes
-------

Bugs fixed
----------

* Fix compile error.

0.4.3
=====
:release date: 2015-01-07

Incompatible Changes
--------------------

Changes
-------

Bugs fixed
----------

* Unpacker may unpack wrong uint32 value on 32bit or LLP64 environment. (#101)
* Build failed on Windows Python 2.7.

0.4.2
=====
:release date: 2014-03-26

Incompatible Changes
--------------------

Changes
-------

Bugs fixed
----------

* Unpacker doesn't increment refcount of ExtType hook.
* Packer raises no exception for inputs doesn't fit to msgpack format.

0.4.1
=====
:release date: 2014-02-17

Incompatible Changes
--------------------

Changes
-------

* fallback.Unpacker.feed() supports bytearray.

Bugs fixed
----------

* Unpacker doesn't increment refcount of hooks. Hooks may be GCed while unpacking.
* Unpacker may read unfilled internal buffer.

0.4.0
=====
:release date: 2013-10-21

Incompatible Changes
--------------------

* Raises TypeError instead of ValueError when packer receives unsupported type.

Changes
-------

* Support New msgpack spec.


0.3.0
=====

Incompatible Changes
--------------------

* Default value of ``use_list`` is ``True`` for now. (It was ``False`` for 0.2.x)
  You should pass it explicitly for compatibility to 0.2.x.
* `Unpacker.unpack()` and some unpack methods now raise `OutOfData` instead of
  `StopIteration`. `StopIteration` is used for iterator protocol only.

Changes
-------
* Pure Python fallback module is added. (thanks to bwesterb)
* Add ``.skip()`` method to ``Unpacker`` (thanks to jnothman)
* Add capturing feature. You can pass the writable object to
  ``Unpacker.unpack()`` as a second parameter.
* Add ``Packer.pack_array_header`` and ``Packer.pack_map_header``.
  These methods only pack header of each type.
* Add ``autoreset`` option to ``Packer`` (default: True).
  Packer doesn't return packed bytes and clear internal buffer.
* Add ``Packer.pack_map_pairs``. It packs sequence of pair to map type.



0.2.4
=====
:release date: 2012-12-22

Bugs fixed
----------

* Fix SEGV when object_hook or object_pairs_hook raise Exception. (#39)

0.2.3
=====
:release date: 2012-12-11

Changes
-------
* Warn when use_list is not specified. It's default value will be changed in 0.3.

Bugs fixed
----------
* Can't pack subclass of dict.

0.2.2
=====
:release date: 2012-09-21

Changes
-------
* Add ``use_single_float`` option to ``Packer``. When it is true, packs float
  object in single precision format.

Bugs fixed
----------
* ``unpack()`` didn't restores gc state when it called with gc disabled.
  ``unpack()`` doesn't control gc now instead of restoring gc state collectly.
  User can control gc state when gc cause performance issue.

* ``Unpacker``'s ``read_size`` option didn't used.

0.2.1
=====
:release date: 2012-08-20

Changes
-------
* Add ``max_buffer_size`` parameter to Unpacker. It limits internal buffer size
  and allows unpack data from untrusted source safely.

* Unpacker's buffer reallocation algorithm is less greedy now. It cause performance
  decrease in rare case but memory efficient and don't allocate than ``max_buffer_size``.

Bugs fixed
----------
* Fix msgpack didn't work on SPARC Solaris. It was because choosing wrong byteorder
  on compilation time. Use ``sys.byteorder`` to get correct byte order.
  Very thanks to Chris Casey for giving test environment to me.


0.2.0
=====
:release date: 2012-06-27

Changes
-------
* Drop supporting Python 2.5 and unify tests for Py2 and Py3.
* Use new version of msgpack-c. It packs correctly on big endian platforms.
* Remove deprecated packs and unpacks API.

Bugs fixed
----------
* #8 Packing subclass of dict raises TypeError. (Thanks to Steeve Morin.)


0.1.13
======
:release date: 2012-04-21

New
---
* Don't accept subtype of list and tuple as msgpack list. (Steeve Morin)
  It allows customize how it serialized with ``default`` argument.

Bugs fixed
----------
* Fix wrong error message. (David Wolever)
* Fix memory leak while unpacking when ``object_hook`` or ``list_hook`` is used.
  (Steeve Morin)

Other changes
-------------
* setup.py works on Python 2.5 (Steffen Siering)
* Optimization for serializing dict.


0.1.12
======
:release date: 2011-12-27

Bugs fixed
----------

* Re-enable packs/unpacks removed at 0.1.11. It will be removed when 0.2 is released.


0.1.11
======
:release date: 2011-12-26

Bugs fixed
----------

* Include test code for Python3 to sdist. (Johan Bergström)
* Fix compilation error on MSVC. (davidgaleano)


0.1.10
======
:release date: 2011-08-22

New feature
-----------
* Add ``encoding`` and ``unicode_errors`` option to packer and unpacker.
  When this option is specified, (un)packs unicode object instead of bytes.
  This enables using msgpack as a replacement of json. (tailhook)


0.1.9
=====
:release date: 2011-01-29

New feature
-----------
* ``use_list`` option is added to unpack(b) like Unpacker.
  (Use keyword argument because order of parameters are different)

Bugs fixed
----------
* Fix typo.
* Add MemoryError check.

0.1.8
=====
:release date: 2011-01-10

New feature
-----------
* Support ``loads`` and ``dumps`` aliases for API compatibility with
  simplejson and pickle.

* Add *object_hook* and *list_hook* option to unpacker. It allows you to
  hook unpacking mapping type and array type.

* Add *default* option to packer. It allows you to pack unsupported types.

* unpacker accepts (old) buffer types.

Bugs fixed
----------
* Fix segv around ``Unpacker.feed`` or ``Unpacker(file)``.


0.1.7
=====
:release date: 2010-11-02

New feature
-----------
* Add *object_hook* and *list_hook* option to unpacker. It allows you to
  hook unpacking mapping type and array type.

* Add *default* option to packer. It allows you to pack unsupported types.

* unpacker accepts (old) buffer types.

Bugs fixed
----------
* Compilation error on win32.
