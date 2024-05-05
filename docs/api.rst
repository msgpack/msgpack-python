API reference
=============

.. module:: msgpack

.. autofunction:: pack

``dump()`` is an alias for :func:`pack`

.. autofunction:: packb

``dumps()`` is an alias for :func:`packb`

.. autofunction:: unpack

``load()`` is an alias for :func:`unpack`

.. autofunction:: unpackb

``loads()`` is an alias for :func:`unpackb`

.. autoclass:: Packer
    :members:

.. autoclass:: Unpacker
    :members:

.. autoclass:: ExtType

.. autoclass:: Timestamp
    :members:
    :special-members: __init__

exceptions
----------

These exceptions are accessible via `msgpack` package.
(For example, `msgpack.OutOfData` is shortcut for `msgpack.exceptions.OutOfData`)

.. automodule:: msgpack.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
