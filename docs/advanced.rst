Advanced usage
===============

Packer
------

autoreset
~~~~~~~~~

When you used ``autoreset=False`` option of :class:`~msgpack.Packer`, 
``pack()`` method doesn't return packed ``bytes``.

You can use :meth:`~msgpack.Packer.bytes` or :meth:`~msgpack.Packer.getbuffer` to
get packed data.

``bytes()`` returns ``bytes`` object.  ``getbuffer()`` returns some bytes-like
object.  It's concrete type is implement detail and it will be changed in future
versions.

You can reduce temporary bytes object by using ``Unpacker.getbuffer()``.

.. code-block:: python

    packer = Packer(use_bin_type=True, autoreset=False)

    packer.pack([1, 2])
    packer.pack([3, 4])

    with open('data.bin', 'wb') as f:
        f.write(packer.getbuffer())

    packer.reset()  # reset internal buffer
