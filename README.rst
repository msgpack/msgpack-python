===========================
MessagePack Python Binding
===========================

:author: INADA Naoki
:version: 0.2.0
:date: 2012-06-27

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
       data = buf.read(4)
       if not data:
           break
       unpacker.seed(buf.read(16))
       for unpacked in unpacker:
           print unpacked


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
