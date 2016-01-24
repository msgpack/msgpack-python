# coding: utf-8

from collections import namedtuple
from msgpack import packb, unpackb


def test_namedtuple():
    T = namedtuple('T', "foo bar")
    def default(o):
        if isinstance(o, T):
            return dict(o._asdict())
        raise TypeError('Unsupported type %s' % (type(o),))
    packed = packb(T(1, 42), strict_types=True, use_bin_type=True, default=default)
    unpacked = unpackb(packed, encoding='utf-8')
    assert unpacked == {'foo': 1, 'bar': 42}
