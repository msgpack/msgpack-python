API reference
=============

.. module:: msgpack

.. autofunction:: pack

:func:`dump` is alias for :func:`pack`

.. autofunction:: packb

:func:`dumps` is alias for :func:`packb`

.. autofunction:: unpack

:func:`load` is alias for :func:`unpack`

.. autofunction:: unpackb

:func:`loads` is alias for :func:`unpackb`

.. autoclass:: Packer
    :members:

.. autoclass:: Unpacker
    :members:

.. autoclass:: ExtType

exceptions
-----------

These exceptions are accessible via `msgpack` package.
(For example, `msgpack.OutOfData` is shortcut for `msgpack.exceptions.OutOfData`)

.. automodule:: msgpack.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
