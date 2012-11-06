===========================
MessagePack Python Binding
===========================

:author: INADA Naoki
:version: 0.2.0
:date: 2012-06-27

.. image:: https://secure.travis-ci.org/msgpack/msgpack-python.png
   :target: https://travis-ci.org/#!/msgpack/msgpack-python

HOW TO USE
-----------

one-shot pack & unpack
^^^^^^^^^^^^^^^^^^^^^^

Use ``packb`` for packing and ``unpackb`` for unpacking.
msgpack provides ``dumps`` and ``loads`` as alias for compatibility with
``json`` and ``pickle``.

``pack`` and ``dump`` packs to file-like object.
``unpack`` and ``load`` unpacks from file-like object.

   >>> import msgpack
   >>> msgpack.packb([1, 2, 3])
   '\x93\x01\x02\x03'
   >>> msgpack.unpackb(_)
   (1, 2, 3)


``unpack`` unpacks msgpack's array to Python's tuple.
To unpack it to list, Use ``use_list`` option.

   >>> msgpack.unpackb(b'\x93\x01\x02\x03', use_list=True)
   [1, 2, 3]

Read docstring for other options.


streaming unpacking
^^^^^^^^^^^^^^^^^^^

``Unpacker`` is "streaming unpacker". It unpacks multiple objects from one
stream.

::

   import msgpack
   from io import BytesIO

   buf = BytesIO()
   for i in range(100):
      buf.write(msgpack.packb(range(i)))

   buf.seek(0)

   unpacker = msgpack.Unpacker()
   while True:
       data = buf.read(16)
       if not data:
           break
       unpacker.feed(data)

       for unpacked in unpacker:
           print unpacked

packing/unpacking of custom data type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Also possible to pack/unpack user's data types. Here is an example for
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


TEST
----
MessagePack uses `nosetest` for testing.
Run test with following command:

    $ nosetests test


..
    vim: filetype=rst
