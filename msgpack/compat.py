import sys

if sys.version_info[0] == 2:
    PY2 = True
    int_types = (int, long)
    def dict_iteritems(d):
        return d.iteritems()
else:
    PY2 = False
    int_types = int
    unicode = str
    xrange = range
    def dict_iteritems(d):
        return d.items()

if hasattr(sys, 'pypy_version_info'):
    # cStringIO is slow on PyPy, StringIO is faster.  However: PyPy's own
    # StringBuilder is fastest.
    from __pypy__ import newlist_hint
    try:
        from __pypy__.builders import BytesBuilder as StringBuilder
    except ImportError:
        from __pypy__.builders import StringBuilder
    USING_STRINGBUILDER = True
    class StringIO(object):
        def __init__(self, s=b''):
            if s:
                self.builder = StringBuilder(len(s))
                self.builder.append(s)
            else:
                self.builder = StringBuilder()
        def write(self, s):
            if isinstance(s, memoryview):
                s = s.tobytes()
            elif isinstance(s, bytearray):
                s = bytes(s)
            self.builder.append(s)
        def getvalue(self):
            return self.builder.build()
else:
    USING_STRINGBUILDER = False
    from io import BytesIO as StringIO
    newlist_hint = lambda size: []
