
from nose.tools import *

from msgpack import packb


def test_canonical():
    # This test serialises a dictionary 3 times.
    # Without canonicalisation each serialisation would be different
    # (on Python 2.6 anyway)
    d = {'year': 1, 'month': 2, 'day': 3}
    s1 = packb(d, canonical=True)

    for i in range(30):
        d[i] = i
    for i in range(30):
        del d[i]
    s2 = packb(d, canonical=True)

    d = dict(d)
    s3 = packb(d, canonical=True)

    eq_(s1, s2, s3)

if __name__ == '__main__':
    from nose import main
    main()
