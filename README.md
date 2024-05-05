# MessagePack for Python

[![Build Status](https://github.com/msgpack/msgpack-python/actions/workflows/wheel.yml/badge.svg)](https://github.com/msgpack/msgpack-python/actions/workflows/wheel.yml)
[![Documentation Status](https://readthedocs.org/projects/msgpack-python/badge/?version=latest)](https://msgpack-python.readthedocs.io/en/latest/?badge=latest)

## What's this

[MessagePack](https://msgpack.org/) is an efficient binary serialization format.
It lets you exchange data among multiple languages like JSON.
But it's faster and smaller.
This package provides CPython bindings for reading and writing MessagePack data.

## Install

```
$ pip install msgpack
```

### Pure Python implementation

The extension module in msgpack (`msgpack._cmsgpack`) does not support PyPy.

But msgpack provides a pure Python implementation (`msgpack.fallback`) for PyPy.


### Windows

When you can't use a binary distribution, you need to install Visual Studio
or Windows SDK on Windows.
Without extension, using pure Python implementation on CPython runs slowly.


## How to use

### One-shot pack & unpack

Use `packb` for packing and `unpackb` for unpacking.
msgpack provides `dumps` and `loads` as an alias for compatibility with
`json` and `pickle`.

`pack` and `dump` packs to a file-like object.
`unpack` and `load` unpacks from a file-like object.

```pycon
>>> import msgpack
>>> msgpack.packb([1, 2, 3])
'\x93\x01\x02\x03'
>>> msgpack.unpackb(_)
[1, 2, 3]
```

Read the docstring for options.


### Streaming unpacking

`Unpacker` is a "streaming unpacker". It unpacks multiple objects from one
stream (or from bytes provided through its `feed` method).

```py
import msgpack
from io import BytesIO

buf = BytesIO()
for i in range(100):
   buf.write(msgpack.packb(i))

buf.seek(0)

unpacker = msgpack.Unpacker(buf)
for unpacked in unpacker:
    print(unpacked)
```


### Packing/unpacking of custom data type

It is also possible to pack/unpack custom data types. Here is an example for
`datetime.datetime`.

```py
import datetime
import msgpack

useful_dict = {
    "id": 1,
    "created": datetime.datetime.now(),
}

def decode_datetime(obj):
    if '__datetime__' in obj:
        obj = datetime.datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
    return obj

def encode_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
    return obj


packed_dict = msgpack.packb(useful_dict, default=encode_datetime)
this_dict_again = msgpack.unpackb(packed_dict, object_hook=decode_datetime)
```

`Unpacker`'s `object_hook` callback receives a dict; the
`object_pairs_hook` callback may instead be used to receive a list of
key-value pairs.

NOTE: msgpack can encode datetime with tzinfo into standard ext type for now.
See `datetime` option in `Packer` docstring.


### Extended types

It is also possible to pack/unpack custom data types using the **ext** type.

```pycon
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
```


### Advanced unpacking control

As an alternative to iteration, `Unpacker` objects provide `unpack`,
`skip`, `read_array_header` and `read_map_header` methods. The former two
read an entire message from the stream, respectively de-serialising and returning
the result, or ignoring it. The latter two methods return the number of elements
in the upcoming container, so that each element in an array, or key-value pair
in a map, can be unpacked or skipped individually.


## Notes

### string and binary type in old msgpack spec

Early versions of msgpack didn't distinguish string and binary types.
The type for representing both string and binary types was named **raw**.

You can pack into and unpack from this old spec using `use_bin_type=False`
and `raw=True` options.

```pycon
>>> import msgpack
>>> msgpack.unpackb(msgpack.packb([b'spam', 'eggs'], use_bin_type=False), raw=True)
[b'spam', b'eggs']
>>> msgpack.unpackb(msgpack.packb([b'spam', 'eggs'], use_bin_type=True), raw=False)
[b'spam', 'eggs']
```

### ext type

To use the **ext** type, pass `msgpack.ExtType` object to packer.

```pycon
>>> import msgpack
>>> packed = msgpack.packb(msgpack.ExtType(42, b'xyzzy'))
>>> msgpack.unpackb(packed)
ExtType(code=42, data='xyzzy')
```

You can use it with `default` and `ext_hook`. See below.


### Security

To unpacking data received from unreliable source, msgpack provides
two security options.

`max_buffer_size` (default: `100*1024*1024`) limits the internal buffer size.
It is used to limit the preallocated list size too.

`strict_map_key` (default: `True`) limits the type of map keys to bytes and str.
While msgpack spec doesn't limit the types of the map keys,
there is a risk of the hashdos.
If you need to support other types for map keys, use `strict_map_key=False`.


### Performance tips

CPython's GC starts when growing allocated object.
This means unpacking may cause useless GC.
You can use `gc.disable()` when unpacking large message.

List is the default sequence type of Python.
But tuple is lighter than list.
You can use `use_list=False` while unpacking when performance is important.


## Major breaking changes in the history

### msgpack 0.5

Package name on PyPI was changed from `msgpack-python` to `msgpack` from 0.5.

When upgrading from msgpack-0.4 or earlier, do `pip uninstall msgpack-python` before
`pip install -U msgpack`.


### msgpack 1.0

* Python 2 support

  * The extension module does not support Python 2 anymore.
    The pure Python implementation (`msgpack.fallback`) is used for Python 2.
  
  * msgpack 1.0.6 drops official support of Python 2.7, as pip and
    GitHub Action (setup-python) no longer support Python 2.7.

* Packer

  * Packer uses `use_bin_type=True` by default.
    Bytes are encoded in bin type in msgpack.
  * The `encoding` option is removed.  UTF-8 is used always.

* Unpacker

  * Unpacker uses `raw=False` by default.  It assumes str types are valid UTF-8 string
    and decode them to Python str (unicode) object.
  * `encoding` option is removed.  You can use `raw=True` to support old format (e.g. unpack into bytes, not str).
  * Default value of `max_buffer_size` is changed from 0 to 100 MiB to avoid DoS attack.
    You need to pass `max_buffer_size=0` if you have large but safe data.
  * Default value of `strict_map_key` is changed to True to avoid hashdos.
    You need to pass `strict_map_key=False` if you have data which contain map keys
    which type is not bytes or str.
