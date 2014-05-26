0.4.3
=====
:release date: TBD

Inconpatible Changes
--------------------

Changes
-------

Bugs fixed
----------

* Unpacker may unpack wrong uint32 value on 32bit or LLP64 environment. (#101)

0.4.2
=====
:release date: 2014-03-26

Inconpatible Changes
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

Inconpatible Changes
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

Inconpatible Changes
--------------------

* Raises TypeError instead of ValueError when packer receives unsupported type.

Changes
-------

* Support New msgpack spec.


0.3.0
=====

Inconpatible Changes
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
=======
:release date: 2012-12-22

Bugs fixed
----------

* Fix SEGV when object_hook or object_pairs_hook raise Exception. (#39)

0.2.3
=======
:release date: 2012-12-11

Changes
-------
* Warn when use_list is not specified. It's default value will be changed in 0.3.

Bugs fixed
-----------
* Can't pack subclass of dict.

0.2.2
=======
:release date: 2012-09-21

Changes
-------
* Add ``use_single_float`` option to ``Packer``. When it is true, packs float
  object in single precision format.

Bugs fixed
-----------
* ``unpack()`` didn't restores gc state when it called with gc disabled.
  ``unpack()`` doesn't control gc now instead of restoring gc state collectly.
  User can control gc state when gc cause performance issue.

* ``Unpacker``'s ``read_size`` option didn't used.

0.2.1
=======
:release date: 2012-08-20

Changes
-------
* Add ``max_buffer_size`` parameter to Unpacker. It limits internal buffer size
  and allows unpack data from untrusted source safely.

* Unpacker's buffer reallocation algorithm is less greedy now. It cause perforamce
  derease in rare case but memory efficient and don't allocate than ``max_buffer_size``.

Bugs fixed
----------
* Fix msgpack didn't work on SPARC Solaris. It was because choosing wrong byteorder
  on compilation time. Use ``sys.byteorder`` to get correct byte order.
  Very thanks to Chris Casey for giving test environment to me.


0.2.0
=======
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
=======
:release date: 2012-04-21

New
----
* Don't accept subtype of list and tuple as msgpack list. (Steeve Morin)
  It allows customize how it serialized with ``default`` argument.

Bugs fixed
-----------
* Fix wrong error message. (David Wolever)
* Fix memory leak while unpacking when ``object_hook`` or ``list_hook`` is used.
  (Steeve Morin)

Other changes
-------------
* setup.py works on Python 2.5 (Steffen Siering)
* Optimization for serializing dict.


0.1.12
=======
:release date: 2011-12-27

Bugs fixed
-------------

* Re-enable packs/unpacks removed at 0.1.11. It will be removed when 0.2 is released.


0.1.11
=======
:release date: 2011-12-26

Bugs fixed
-------------

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
======
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
======
:release date: 2011-01-10

New feature
------------
* Support ``loads`` and ``dumps`` aliases for API compatibility with
  simplejson and pickle.

* Add *object_hook* and *list_hook* option to unpacker. It allows you to
  hook unpacing mapping type and array type.

* Add *default* option to packer. It allows you to pack unsupported types.

* unpacker accepts (old) buffer types.

Bugs fixed
----------
* Fix segv around ``Unpacker.feed`` or ``Unpacker(file)``.


0.1.7
======
:release date: 2010-11-02

New feature
------------
* Add *object_hook* and *list_hook* option to unpacker. It allows you to
  hook unpacing mapping type and array type.

* Add *default* option to packer. It allows you to pack unsupported types.

* unpacker accepts (old) buffer types.

Bugs fixed
----------
* Compilation error on win32.
