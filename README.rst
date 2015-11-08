=======================
MessagePack for Python
=======================

:author: INADA Naoki
:version: 0.4.6
:date: 2015-03-13

.. image:: https://secure.travis-ci.org/msgpack/msgpack-python.png
   :target: https://travis-ci.org/#!/msgpack/msgpack-python
   

What's this
------------

`MessagePack <http://msgpack.org/>`_ is a fast, compact binary serialization format, suitable for
similar data to JSON. This package provides CPython bindings for reading and
writing MessagePack data.

Install
---------

::

   $ pip install msgpack-python

PyPy
^^^^^

msgpack-python provides pure python implementation.  PyPy can use this.

Windows
^^^^^^^

When you can't use binary distribution, you need to install Visual Studio
or Windows SDK on Windows. (NOTE: Visual C++ Express 2010 doesn't support
amd64. Windows SDK is recommended way to build amd64 msgpack without any fee.)

Without extension, using pure python implementation on CPython runs slowly.

Notes
-----

Note for msgpack 2.0 support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

msgpack 2.0 adds two types: *bin* and *ext*.

*raw* was bytes or string type like Python 2's ``str``.
To distinguish string and bytes, msgpack 2.0 adds *bin*.
It is non-string binary like Python 3's ``bytes``.

To use *bin* type for packing ``bytes``, pass ``use_bin_type=True`` to
packer argument.

.. code-block:: pycon

    >>> import msgpack
    >>> packed = msgpack.packb([b'spam', u'egg'], use_bin_type=True)
    >>> msgpack.unpackb(packed, encoding='utf-8')
    ['spam', u'egg']

You shoud use it carefully. When you use ``use_bin_type=True``, packed
binary can be unpacked by unpackers supporting msgpack-2.0.

To use *ext* type, pass ``msgpack.ExtType`` object to packer.

.. code-block:: pycon

    >>> import msgpack
    >>> packed = msgpack.packb(msgpack.ExtType(42, b'xyzzy'))
    >>> msgpack.unpackb(packed)
    ExtType(code=42, data='xyzzy')

You can use it with ``default`` and ``ext_hook``. See below.

Note for msgpack 0.2.x users
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The msgpack 0.3 have some incompatible changes.

The default value of ``use_list`` keyword argument is ``True`` from 0.3.
You should pass the argument explicitly for backward compatibility.

`Unpacker.unpack()` and some unpack methods now raises `OutOfData`
instead of `StopIteration`.
`StopIteration` is used for iterator protocol only.


How to use
-----------

One-shot pack & unpack
^^^^^^^^^^^^^^^^^^^^^^

Use ``packb`` for packing and ``unpackb`` for unpacking.
msgpack provides ``dumps`` and ``loads`` as alias for compatibility with
``json`` and ``pickle``.

``pack`` and ``dump`` packs to file-like object.
``unpack`` and ``load`` unpacks from file-like object.

.. code-block:: pycon

   >>> import msgpack
   >>> msgpack.packb([1, 2, 3])
   '\x93\x01\x02\x03'
   >>> msgpack.unpackb(_)
   [1, 2, 3]

``unpack`` unpacks msgpack's array to Python's list, but can unpack to tuple:

.. code-block:: pycon

   >>> msgpack.unpackb(b'\x93\x01\x02\x03', use_list=False)
   (1, 2, 3)

You should always pass the ``use_list`` keyword argument. See performance issues relating to `use_list option`_ below.

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
      buf.write(msgpack.packb(range(i)))

   buf.seek(0)

   unpacker = msgpack.Unpacker(buf)
   for unpacked in unpacker:
       print unpacked


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


    packed_dict = msgpack.packb(useful_dict, default=encode_datetime)
    this_dict_again = msgpack.unpackb(packed_dict, object_hook=decode_datetime)

``Unpacker``'s ``object_hook`` callback receives a dict; the
``object_pairs_hook`` callback may instead be used to receive a list of
key-value pairs.

Extended types
^^^^^^^^^^^^^^^

It is also possible to pack/unpack custom data types using the msgpack 2.0 feature.

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
    >>> packed = msgpack.packb(data, default=default)
    >>> unpacked = msgpack.unpackb(packed, ext_hook=ext_hook)
    >>> data == unpacked
    True


Advanced unpacking control
^^^^^^^^^^^^^^^^^^^^^^^^^^

As an alternative to iteration, ``Unpacker`` objects provide ``unpack``,
``skip``, ``read_array_header`` and ``read_map_header`` methods. The former two
read an entire message from the stream, respectively deserialising and returning
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

Note about performance
------------------------

GC
^^

CPython's GC starts when growing allocated object.
This means unpacking may cause useless GC.
You can use ``gc.disable()`` when unpacking large message.

use_list option
^^^^^^^^^^^^^^^^
List is the default sequence type of Python.
But tuple is lighter than list.
You can use ``use_list=False`` while unpacking when performance is important.

Python's dict can't use list as key and MessagePack allows array for key of mapping.
``use_list=False`` allows unpacking such message.
Another way to unpacking such object is using ``object_pairs_hook``.


Test
----
MessagePack uses `pytest` for testing.
Run test with following command:

    $ py.test

..
    vim: filetype=rst
