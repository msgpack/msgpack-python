===========================
MessagePack Python Binding
===========================

:author: INADA Naoki
:version: 0.2.0
:date: 2012-06-27

.. image:: https://secure.travis-ci.org/msgpack/msgpack-python.png
   :target: https://travis-ci.org/#!/msgpack/msgpack-python

WHAT IT IS
----------

`MessagePack <http://msgpack.org/>`_ is a fast, compact binary serialization format, suitable for
similar data to JSON. This package provides CPython bindings for reading and
writing MessagePack data.

HOW TO USE
-----------

one-shot pack & unpack
^^^^^^^^^^^^^^^^^^^^^^

Use ``packb`` for packing and ``unpackb`` for unpacking.
msgpack provides ``dumps`` and ``loads`` as alias for compatibility with
``json`` and ``pickle``.

``pack`` and ``dump`` packs to file-like object.
``unpack`` and ``load`` unpacks from file-like object.

::

   >>> import msgpack
   >>> msgpack.packb([1, 2, 3])
   '\x93\x01\x02\x03'
   >>> msgpack.unpackb(_)
   [1, 2, 3]

``unpack`` unpacks msgpack's array to Python's list, but can unpack to tuple::

   >>> msgpack.unpackb(b'\x93\x01\x02\x03', use_list=False)
   (1, 2, 3)

You should always pass the ``use_list`` keyword argument. See performance issues relating to use_list_ below.

Read the docstring for other options.


streaming unpacking
^^^^^^^^^^^^^^^^^^^

``Unpacker`` is a "streaming unpacker". It unpacks multiple objects from one
stream (or from bytes provided through its ``feed`` method).

::

   import msgpack
   from io import BytesIO

   buf = BytesIO()
   for i in range(100):
      buf.write(msgpack.packb(range(i)))

   buf.seek(0)

   unpacker = msgpack.Unpacker(buf)
   for unpacked in unpacker:
       print unpacked


packing/unpacking of custom data type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is also possible to pack/unpack custom data types. Here is an example for
``datetime.datetime``.

::

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


advanced unpacking control
^^^^^^^^^^^^^^^^^^^^^^^^^^

As an alternative to iteration, ``Unpacker`` objects provide ``unpack``,
``skip``, ``read_array_header`` and ``read_map_header`` methods. The former two
read an entire message from the stream, respectively deserialising and returning
the result, or ignoring it. The latter two methods return the number of elements
in the upcoming container, so that each element in an array, or key-value pair
in a map, can be unpacked or skipped individually.

Each of these methods may optionally write the packed data it reads to a
callback function:

::

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

INSTALL
---------
You can use ``pip`` or ``easy_install`` to install msgpack::

   $ easy_install msgpack-python
     or
   $ pip install msgpack-python


Windows
^^^^^^^
msgpack provides some binary distribution for Windows.
You can install msgpack without compiler with them.

When you can't use binary distribution, you need to install Visual Studio
or Windows SDK on Windows. (NOTE: Visual C++ Express 2010 doesn't support
amd64. Windows SDK is recommanded way to build amd64 msgpack without any fee.)


PERFORMANCE NOTE
-----------------

GC
^^

CPython's GC starts when growing allocated object.
This means unpacking may cause useless GC.
You can use ``gc.disable()`` when unpacking large message.

use_list
^^^^^^^^^
List is the default sequence type of Python.
But tuple is lighter than list.
You can use ``use_list=False`` while unpacking when performance is important.

Python's dict can't use list as key and MessagePack allows array for key of mapping.
``use_list=False`` allows unpacking such message.
Another way to unpacking such object is using ``object_pairs_hook``.


TEST
----
MessagePack uses `nosetest` for testing.
Run test with following command:

    $ nosetests test


..
    vim: filetype=rst
