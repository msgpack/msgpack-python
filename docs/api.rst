API reference
=============

.. module:: msgpack_sorted

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

.. autoclass:: Timestamp
    :members:
    :special-members: __init__

exceptions
----------

These exceptions are accessible via `msgpack_sorted` package.
(For example, `msgpack_sorted.OutOfData` is shortcut
for `msgpack_sorted.exceptions.OutOfData`)

.. automodule:: msgpack_sorted.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
