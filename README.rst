======================
MessagePack for Python
======================

.. image:: https://travis-ci.org/msgpack/msgpack-python.svg?branch=master
   :target: https://travis-ci.org/msgpack/msgpack-python
   :alt: Build Status

.. image:: https://readthedocs.org/projects/msgpack-python/badge/?version=latest
   :target: https://msgpack-python.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


What's this
-----------

`MessagePack <https://msgpack.org/>`_ is an efficient binary serialization format.
It lets you exchange data among multiple languages like JSON.
But it's faster and smaller.
This package provides CPython bindings for reading and writing MessagePack data.


Very important notes for existing users
---------------------------------------

PyPI package name
^^^^^^^^^^^^^^^^^

TL;DR: When upgrading from msgpack-0.4 or earlier, don't do `pip install -U msgpack-python`.
Do `pip uninstall msgpack-python; pip install msgpack` instead.

Package name on PyPI was changed to msgpack from 0.5.
I upload transitional package (msgpack-python 0.5 which depending on msgpack)
for smooth transition from msgpack-python to msgpack.

Sadly, this doesn't work for upgrade install.  After `pip install -U msgpack-python`,
msgpack is removed and `import msgpack` fail.


Compatibility with old format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use ``use_bin_type=False`` option to pack ``bytes``
object into raw type in old msgpack spec, instead of bin type in new msgpack spec.

You can unpack old msgpack formatk using ``raw=True`` option.
It unpacks str (raw) type in msgpack into Python bytes.

See note in below for detail.


Install
-------

::

   $ pip install msgpack


Pure Python implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^

The extension module in msgpack (``msgpack._cmsgpack``) does not support
Python 2 and PyPy.

But msgpack provides a pure Python implementation (``msgpack.fallback``)
for PyPy and Python 2.

Since the [pip](https://pip.pypa.io/) uses the pure Python implementation,
Python 2 support will not be dropped in foreseeable feature.


Windows
^^^^^^^

When you can't use a binary distribution, you need to install Visual Studio
or Windows SDK on Windows.
Without extension, using pure Python implementation on CPython runs slowly.


How to use
----------

.. note::

   In examples below, I use ``raw=False`` and ``use_bin_type=True`` for users
   using msgpack < 1.0.
   These options are default from msgpack 1.0 so you can omit them.


One-shot pack & unpack
^^^^^^^^^^^^^^^^^^^^^^

Use ``packb`` for packing and ``unpackb`` for unpacking.
msgpack provides ``dumps`` and ``loads`` as an alias for compatibility with
``json`` and ``pickle``.

``pack`` and ``dump`` packs to a file-like object.
``unpack`` and ``load`` unpacks from a file-like object.

.. code-block:: pycon

   >>> import msgpack
   >>> msgpack.packb([1, 2, 3], use_bin_type=True)
   '\x93\x01\x02\x03'
   >>> msgpack.unpackb(_, raw=False)
   [1, 2, 3]

``unpack`` unpacks msgpack's array to Python's list, but can also unpack to tuple:

.. code-block:: pycon

   >>> msgpack.unpackb(b'\x93\x01\x02\x03', use_list=False, raw=False)
   (1, 2, 3)

You should always specify the ``use_list`` keyword argument for backward compatibility.
See performance issues relating to `use_list option`_ below.

Read the docstring for other options.


Streaming unpacking
^^^^^^^^^^^^^^^^^^^

``Unpacker`` is a "streaming unpacker". It unpacks multiple objects from one
stream (or from bytes provided through its ``feed`` method).

.. code-block:: python

   import msgpack
   from io import BytesIO

   buf = BytesIO()
   for i in range(100):
      buf.write(msgpack.packb(i, use_bin_type=True))

   buf.seek(0)

   unpacker = msgpack.Unpacker(buf, raw=False)
   for unpacked in unpacker:
       print(unpacked)


Packing/unpacking of custom data type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is also possible to pack/unpack custom data types. Here is an example for
``datetime.datetime``.

.. code-block:: python

    import datetime
    import msgpack

    useful_dict = {
        "id": 1,
        "created": datetime.datetime.now(),
    }

    def decode_datetime(obj):
        if b'__datetime__' in obj:
            obj = datetime.datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
        return obj

    def encode_datetime(obj):
        if isinstance(obj, datetime.datetime):
            return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
        return obj


    packed_dict = msgpack.packb(useful_dict, default=encode_datetime, use_bin_type=True)
    this_dict_again = msgpack.unpackb(packed_dict, object_hook=decode_datetime, raw=False)

``Unpacker``'s ``object_hook`` callback receives a dict; the
``object_pairs_hook`` callback may instead be used to receive a list of
key-value pairs.


Extended types
^^^^^^^^^^^^^^

It is also possible to pack/unpack custom data types using the **ext** type.

.. code-block:: pycon

    >>> import msgpack
    >>> import array
    >>> def default(obj):
    ...     if isinstance(obj, array.array) and obj.typecode == 'd':
    ...         return msgpack.ExtType(42, obj.tostring())
    ...     raise TypeError("Unknown type: %r" % (obj,))
    ...
    >>> def ext_hook(code, data):
    ...     if code == 42:
    ...         a = array.array('d')
    ...         a.fromstring(data)
    ...         return a
    ...     return ExtType(code, data)
    ...
    >>> data = array.array('d', [1.2, 3.4])
    >>> packed = msgpack.packb(data, default=default, use_bin_type=True)
    >>> unpacked = msgpack.unpackb(packed, ext_hook=ext_hook, raw=False)
    >>> data == unpacked
    True


Advanced unpacking control
^^^^^^^^^^^^^^^^^^^^^^^^^^

As an alternative to iteration, ``Unpacker`` objects provide ``unpack``,
``skip``, ``read_array_header`` and ``read_map_header`` methods. The former two
read an entire message from the stream, respectively de-serialising and returning
the result, or ignoring it. The latter two methods return the number of elements
in the upcoming container, so that each element in an array, or key-value pair
in a map, can be unpacked or skipped individually.

Each of these methods may optionally write the packed data it reads to a
callback function:

.. code-block:: python

    from io import BytesIO

    def distribute(unpacker, get_worker):
        nelems = unpacker.read_map_header()
        for i in range(nelems):
            # Select a worker for the given key
            key = unpacker.unpack()
            worker = get_worker(key)

            # Send the value as a packed message to worker
            bytestream = BytesIO()
            unpacker.skip(bytestream.write)
            worker.send(bytestream.getvalue())


Notes
-----

string and binary type
^^^^^^^^^^^^^^^^^^^^^^

Early versions of msgpack didn't distinguish string and binary types.
The type for representing both string and binary types was named **raw**.

You can pack into and unpack from this old spec using ``use_bin_type=False``
and ``raw=True`` options.

.. code-block:: pycon

    >>> import msgpack
    >>> msgpack.unpackb(msgpack.packb([b'spam', u'eggs'], use_bin_type=False), raw=True)
    [b'spam', b'eggs']
    >>> msgpack.unpackb(msgpack.packb([b'spam', u'eggs'], use_bin_type=True), raw=False)
    [b'spam', 'eggs']


ext type
^^^^^^^^

To use the **ext** type, pass ``msgpack.ExtType`` object to packer.

.. code-block:: pycon

    >>> import msgpack
    >>> packed = msgpack.packb(msgpack.ExtType(42, b'xyzzy'))
    >>> msgpack.unpackb(packed)
    ExtType(code=42, data='xyzzy')

You can use it with ``default`` and ``ext_hook``. See below.


Note about performance
----------------------

GC
^^

CPython's GC starts when growing allocated object.
This means unpacking may cause useless GC.
You can use ``gc.disable()`` when unpacking large message.

use_list option
^^^^^^^^^^^^^^^

List is the default sequence type of Python.
But tuple is lighter than list.
You can use ``use_list=False`` while unpacking when performance is important.

Python's dict can't use list as key and MessagePack allows array for key of mapping.
``use_list=False`` allows unpacking such message.
Another way to unpacking such object is using ``object_pairs_hook``.


Development
-----------

Test
^^^^

MessagePack uses `pytest` for testing.
Run test with following command:

    $ make test


..
    vim: filetype=rst
