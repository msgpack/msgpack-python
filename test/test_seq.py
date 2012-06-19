#!/usr/bin/env python
# coding: utf-8

import six
from nose import main
from nose.tools import *

import io
import msgpack

binarydata = [chr(i) for i in range(256)]
binarydata = six.b("".join(binarydata))

def gen_binary_data(idx):
    data = binarydata[:idx % 300]
    return data

def test_exceeding_unpacker_read_size():
    dumpf = io.BytesIO()

    packer = msgpack.Packer()

    NUMBER_OF_STRINGS = 6
    read_size = 16
                                # 5 ok for read_size=16, while 6 glibc detected *** python: double free or corruption (fasttop):
                                # 20 ok for read_size=256, while 25 segfaults / glibc detected *** python: double free or corruption (!prev)
                                # 40 ok for read_size=1024, while 50 introduces errors
                                # 7000 ok for read_size=1024*1024, while 8000 leads to  glibc detected *** python: double free or corruption (!prev):

    for idx in range(NUMBER_OF_STRINGS):
        data = gen_binary_data(idx)
        dumpf.write(packer.pack(data))

    f = io.BytesIO(dumpf.getvalue())
    dumpf.close()

    unpacker = msgpack.Unpacker(f, read_size=read_size)

    read_count = 0
    for idx, o in enumerate(unpacker):
        assert_equal(type(o), bytes)
        assert_equal(o, gen_binary_data(idx))
        read_count += 1

    assert_equal(read_count, NUMBER_OF_STRINGS)


if __name__ == '__main__':
    main()
    #test_exceeding_unpacker_read_size()
