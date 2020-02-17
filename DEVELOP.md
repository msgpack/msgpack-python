# Developer's note

## Wheels

Wheels for macOS and Linux are built on Travis and AppVeyr, in
[methane/msgpack-wheels](https://github.com/methane/msgpack-wheels) repository.

Wheels for Windows are built on Github Actions in this repository.


### Build

```
$ make cython
```


### Test

MessagePack uses `pytest` for testing.
Run test with following command:

```
$ make test
```
