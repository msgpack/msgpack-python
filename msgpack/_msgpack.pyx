# coding: utf-8
#cython: embedsignature=True

from cpython cimport *
cdef extern from "Python.h":
    ctypedef char* const_char_ptr "const char*"
    ctypedef char* const_void_ptr "const void*"
    ctypedef struct PyObject
    cdef int PyObject_AsReadBuffer(object o, const_void_ptr* buff, Py_ssize_t* buf_len) except -1

from libc.stdlib cimport *
from libc.string cimport *
from libc.limits cimport *


cdef extern from "pack.h":
    struct msgpack_packer:
        char* buf
        size_t length
        size_t buf_size

    int msgpack_pack_int(msgpack_packer* pk, int d)
    int msgpack_pack_nil(msgpack_packer* pk)
    int msgpack_pack_true(msgpack_packer* pk)
    int msgpack_pack_false(msgpack_packer* pk)
    int msgpack_pack_long(msgpack_packer* pk, long d)
    int msgpack_pack_long_long(msgpack_packer* pk, long long d)
    int msgpack_pack_unsigned_long_long(msgpack_packer* pk, unsigned long long d)
    int msgpack_pack_float(msgpack_packer* pk, float d)
    int msgpack_pack_double(msgpack_packer* pk, double d)
    int msgpack_pack_array(msgpack_packer* pk, size_t l)
    int msgpack_pack_map(msgpack_packer* pk, size_t l)
    int msgpack_pack_raw(msgpack_packer* pk, size_t l)
    int msgpack_pack_raw_body(msgpack_packer* pk, char* body, size_t l)

cdef int DEFAULT_RECURSE_LIMIT=511


class BufferFull(Exception):
    pass


cdef class Packer(object):
    """MessagePack Packer

    usage:

        packer = Packer()
        astream.write(packer.pack(a))
        astream.write(packer.pack(b))
    """
    cdef msgpack_packer pk
    cdef object _default
    cdef object _bencoding
    cdef object _berrors
    cdef char *encoding
    cdef char *unicode_errors
    cdef bool use_float

    def __cinit__(self):
        cdef int buf_size = 1024*1024
        self.pk.buf = <char*> malloc(buf_size);
        if self.pk.buf == NULL:
            raise MemoryError("Unable to allocate internal buffer.")
        self.pk.buf_size = buf_size
        self.pk.length = 0

    def __init__(self, default=None, encoding='utf-8', unicode_errors='strict', use_single_float=False):
        self.use_float = use_single_float
        if default is not None:
            if not PyCallable_Check(default):
                raise TypeError("default must be a callable.")
        self._default = default
        if encoding is None:
            self.encoding = NULL
            self.unicode_errors = NULL
        else:
            if isinstance(encoding, unicode):
                self._bencoding = encoding.encode('ascii')
            else:
                self._bencoding = encoding
            self.encoding = PyBytes_AsString(self._bencoding)
            if isinstance(unicode_errors, unicode):
                self._berrors = unicode_errors.encode('ascii')
            else:
                self._berrors = unicode_errors
            self.unicode_errors = PyBytes_AsString(self._berrors)

    def __dealloc__(self):
        free(self.pk.buf);

    cdef int _pack(self, object o, int nest_limit=DEFAULT_RECURSE_LIMIT) except -1:
        cdef long long llval
        cdef unsigned long long ullval
        cdef long longval
        cdef float fval
        cdef double dval
        cdef char* rawval
        cdef int ret
        cdef dict d

        if nest_limit < 0:
            raise ValueError("Too deep.")

        if o is None:
            ret = msgpack_pack_nil(&self.pk)
        elif isinstance(o, bool):
            if o:
                ret = msgpack_pack_true(&self.pk)
            else:
                ret = msgpack_pack_false(&self.pk)
        elif PyLong_Check(o):
            if o > 0:
                ullval = o
                ret = msgpack_pack_unsigned_long_long(&self.pk, ullval)
            else:
                llval = o
                ret = msgpack_pack_long_long(&self.pk, llval)
        elif PyInt_Check(o):
            longval = o
            ret = msgpack_pack_long(&self.pk, longval)
        elif PyFloat_Check(o):
            if self.use_float:
               fval = o
               ret = msgpack_pack_float(&self.pk, fval)
            else:
               dval = o
               ret = msgpack_pack_double(&self.pk, dval)
        elif PyBytes_Check(o):
            rawval = o
            ret = msgpack_pack_raw(&self.pk, len(o))
            if ret == 0:
                ret = msgpack_pack_raw_body(&self.pk, rawval, len(o))
        elif PyUnicode_Check(o):
            if not self.encoding:
                raise TypeError("Can't encode unicode string: no encoding is specified")
            o = PyUnicode_AsEncodedString(o, self.encoding, self.unicode_errors)
            rawval = o
            ret = msgpack_pack_raw(&self.pk, len(o))
            if ret == 0:
                ret = msgpack_pack_raw_body(&self.pk, rawval, len(o))
        elif PyDict_CheckExact(o):
            d = <dict>o
            ret = msgpack_pack_map(&self.pk, len(d))
            if ret == 0:
                for k, v in d.iteritems():
                    ret = self._pack(k, nest_limit-1)
                    if ret != 0: break
                    ret = self._pack(v, nest_limit-1)
                    if ret != 0: break
        elif PyDict_Check(o):
            ret = msgpack_pack_map(&self.pk, len(o))
            if ret == 0:
                for k, v in o.items():
                    ret = self._pack(k, nest_limit-1)
                    if ret != 0: break
                    ret = self._pack(v, nest_limit-1)
                    if ret != 0: break
        elif PyTuple_Check(o) or PyList_Check(o):
            ret = msgpack_pack_array(&self.pk, len(o))
            if ret == 0:
                for v in o:
                    ret = self._pack(v, nest_limit-1)
                    if ret != 0: break
        elif self._default:
            o = self._default(o)
            ret = self._pack(o, nest_limit-1)
        else:
            raise TypeError("can't serialize %r" % (o,))
        return ret

    cpdef pack(self, object obj):
        cdef int ret
        ret = self._pack(obj, DEFAULT_RECURSE_LIMIT)
        if ret:
            raise TypeError
        buf = PyBytes_FromStringAndSize(self.pk.buf, self.pk.length)
        self.pk.length = 0
        return buf

    cpdef pack_array_header(self, size_t size):
        """returns the header for an array of the given size n, to be followed by its n packed elements"""
        msgpack_pack_array(&self.pk, size)
        buf = PyBytes_FromStringAndSize(self.pk.buf, self.pk.length)
        self.pk.length = 0
        return buf

    cpdef pack_map_header(self, size_t size):
        """returns the header for a map of the given size n, to be followed by its n packed key-value pairs"""
        msgpack_pack_map(&self.pk, size)
        buf = PyBytes_FromStringAndSize(self.pk.buf, self.pk.length)
        self.pk.length = 0
        return buf

def pack(object o, object stream, default=None, encoding='utf-8', unicode_errors='strict'):
    """
    pack an object `o` and write it to stream)."""
    packer = Packer(default=default, encoding=encoding, unicode_errors=unicode_errors)
    stream.write(packer.pack(o))

def packb(object o, default=None, encoding='utf-8', unicode_errors='strict', use_single_float=False):
    """
    pack o and return packed bytes."""
    packer = Packer(default=default, encoding=encoding, unicode_errors=unicode_errors,
                    use_single_float=use_single_float)
    return packer.pack(o)

cdef enum ExecMode:
    EXEC_SKIP,
    EXEC_CONSTRUCT,
    EXEC_ARRAY_SIZE,
    EXEC_MAP_SIZE

cdef extern from "unpack.h":
    ctypedef struct msgpack_user:
        int use_list
        PyObject* object_hook
        PyObject* list_hook
        char *encoding
        char *unicode_errors

    ctypedef struct template_context:
        msgpack_user user
        PyObject* obj
        size_t count
        unsigned int ct
        PyObject* key

    int template_execute(template_context* ctx, const_char_ptr data,
                         size_t len, size_t* off, ExecMode exec_mode)
    void template_init(template_context* ctx)
    object template_data(template_context* ctx)


def unpackb(object packed, object object_hook=None, object list_hook=None,
            bint use_list=0, encoding=None, unicode_errors="strict",
            ):
    """Unpack packed_bytes to object. Returns an unpacked object.

    Raises `ValueError` when `packed` contains extra bytes.
    """
    cdef template_context ctx
    cdef size_t off = 0
    cdef int ret

    cdef char* buf
    cdef Py_ssize_t buf_len
    PyObject_AsReadBuffer(packed, <const_void_ptr*>&buf, &buf_len)

    if encoding is None:
        enc = NULL
        err = NULL
    else:
        if isinstance(encoding, unicode):
            bencoding = encoding.encode('ascii')
        else:
            bencoding = encoding
        if isinstance(unicode_errors, unicode):
            berrors = unicode_errors.encode('ascii')
        else:
            berrors = unicode_errors
        enc = PyBytes_AsString(bencoding)
        err = PyBytes_AsString(berrors)

    template_init(&ctx)
    ctx.user.use_list = use_list
    ctx.user.object_hook = ctx.user.list_hook = NULL
    ctx.user.encoding = <const_char_ptr>enc
    ctx.user.unicode_errors = <const_char_ptr>err
    if object_hook is not None:
        if not PyCallable_Check(object_hook):
            raise TypeError("object_hook must be a callable.")
        ctx.user.object_hook = <PyObject*>object_hook
    if list_hook is not None:
        if not PyCallable_Check(list_hook):
            raise TypeError("list_hook must be a callable.")
        ctx.user.list_hook = <PyObject*>list_hook
    ret = template_execute(&ctx, buf, buf_len, &off, EXEC_CONSTRUCT)
    if ret == 1:
        obj = template_data(&ctx)
        if off < buf_len:
            raise ValueError("Extra data.")
        return obj
    else:
        return None


def unpack(object stream, object object_hook=None, object list_hook=None,
           bint use_list=0, encoding=None, unicode_errors="strict",
           ):
    """Unpack an object from `stream`.

    Raises `ValueError` when `stream` has extra bytes.
    """
    return unpackb(stream.read(), use_list=use_list,
                   object_hook=object_hook, list_hook=list_hook,
                   encoding=encoding, unicode_errors=unicode_errors,
                   )

class UnpackException(ValueError):
    def __init__(self, code, *args, **kwargs):
        self.code = code
        super(UnpackException, self).__init__(*args, **kwargs)

class UnexpectedTypeException(UnpackException):
    def __init__(self, *args, **kwargs):
        super(UnexpectedTypeException, self).__init__(-2, *args, **kwargs)

cdef class Unpacker(object):
    """
    Streaming unpacker.

    `file_like` is a file-like object having `.read(n)` method.
    When `Unpacker` initialized with `file_like`, unpacker reads serialized data
    from it and `.feed()` method is not usable.

    `read_size` is used as `file_like.read(read_size)`.
    (default: min(1024**2, max_buffer_size))

    If `use_list` is true, msgpack list is deserialized to Python list.
    Otherwise, it is deserialized to Python tuple. (default: False)

    `object_hook` is same to simplejson. If it is not None, it should be callable
    and Unpacker calls it when deserializing key-value.

    `encoding` is encoding used for decoding msgpack bytes. If it is None (default),
    msgpack bytes is deserialized to Python bytes.

    `unicode_errors` is used for decoding bytes.

    `max_buffer_size` limits size of data waiting unpacked.
    0 means system's INT_MAX (default).
    Raises `BufferFull` exception when it is insufficient.
    You shoud set this parameter when unpacking data from untrasted source.

    example of streaming deserialize from file-like object::

        unpacker = Unpacker(file_like)
        for o in unpacker:
            do_something(o)

    example of streaming deserialize from socket::

        unpacker = Unpacker()
        while 1:
            buf = sock.recv(1024**2)
            if not buf:
                break
            unpacker.feed(buf)
            for o in unpacker:
                do_something(o)
    """
    cdef template_context ctx
    cdef char* buf
    cdef size_t buf_size, buf_head, buf_tail
    cdef object file_like
    cdef object file_like_read
    cdef Py_ssize_t read_size
    cdef bint use_list
    cdef object object_hook
    cdef object _bencoding
    cdef object _berrors
    cdef char *encoding
    cdef char *unicode_errors
    cdef size_t max_buffer_size

    def __cinit__(self):
        self.buf = NULL

    def __dealloc__(self):
        free(self.buf)
        self.buf = NULL

    def __init__(self, file_like=None, Py_ssize_t read_size=0, bint use_list=0,
                 object object_hook=None, object list_hook=None,
                 encoding=None, unicode_errors='strict', int max_buffer_size=0,
                 object object_pairs_hook=None,
                 ):
        self.use_list = use_list
        self.file_like = file_like
        if file_like:
            self.file_like_read = file_like.read
            if not PyCallable_Check(self.file_like_read):
                raise ValueError("`file_like.read` must be a callable.")
        if not max_buffer_size:
            max_buffer_size = INT_MAX
        if read_size > max_buffer_size:
            raise ValueError("read_size should be less or equal to max_buffer_size")
        if not read_size:
            read_size = min(max_buffer_size, 1024**2)
        self.max_buffer_size = max_buffer_size
        self.read_size = read_size
        self.buf = <char*>malloc(read_size)
        if self.buf == NULL:
            raise MemoryError("Unable to allocate internal buffer.")
        self.buf_size = read_size
        self.buf_head = 0
        self.buf_tail = 0
        template_init(&self.ctx)
        self.ctx.user.use_list = use_list
        self.ctx.user.object_hook = self.ctx.user.list_hook = <PyObject*>NULL
        if object_hook is not None:
            if not PyCallable_Check(object_hook):
                raise TypeError("object_hook must be a callable.")
            self.ctx.user.object_hook = <PyObject*>object_hook
        if list_hook is not None:
            if not PyCallable_Check(list_hook):
                raise TypeError("list_hook must be a callable.")
            self.ctx.user.list_hook = <PyObject*>list_hook
        if encoding is None:
            self.ctx.user.encoding = NULL
            self.ctx.user.unicode_errors = NULL
        else:
            if isinstance(encoding, unicode):
                self._bencoding = encoding.encode('ascii')
            else:
                self._bencoding = encoding
            self.ctx.user.encoding = PyBytes_AsString(self._bencoding)
            if isinstance(unicode_errors, unicode):
                self._berrors = unicode_errors.encode('ascii')
            else:
                self._berrors = unicode_errors
            self.ctx.user.unicode_errors = PyBytes_AsString(self._berrors)

    def feed(self, object next_bytes):
        cdef char* buf
        cdef Py_ssize_t buf_len
        if self.file_like is not None:
            raise AssertionError(
                    "unpacker.feed() is not be able to use with`file_like`.")
        PyObject_AsReadBuffer(next_bytes, <const_void_ptr*>&buf, &buf_len)
        self.append_buffer(buf, buf_len)

    cdef append_buffer(self, void* _buf, Py_ssize_t _buf_len):
        cdef:
            char* buf = self.buf
            char* new_buf
            size_t head = self.buf_head
            size_t tail = self.buf_tail
            size_t buf_size = self.buf_size
            size_t new_size

        if tail + _buf_len > buf_size:
            if ((tail - head) + _buf_len) <= buf_size:
                # move to front.
                memmove(buf, buf + head, tail - head)
                tail -= head
                head = 0
            else:
                # expand buffer.
                new_size = (tail-head) + _buf_len
                if new_size > self.max_buffer_size:
                    raise BufferFull
                new_size = min(new_size*2, self.max_buffer_size)
                new_buf = <char*>malloc(new_size)
                if new_buf == NULL:
                    # self.buf still holds old buffer and will be freed during
                    # obj destruction
                    raise MemoryError("Unable to enlarge internal buffer.")
                memcpy(new_buf, buf + head, tail - head)
                free(buf)

                buf = new_buf
                buf_size = new_size
                tail -= head
                head = 0

        memcpy(buf + tail, <char*>(_buf), _buf_len)
        self.buf = buf
        self.buf_head = head
        self.buf_size = buf_size
        self.buf_tail = tail + _buf_len

    cdef read_from_file(self):
        next_bytes = self.file_like_read(
                min(self.read_size,
                    self.max_buffer_size - (self.buf_tail - self.buf_head)
                    ))
        if next_bytes:
            self.append_buffer(PyBytes_AsString(next_bytes), PyBytes_Size(next_bytes))
        else:
            self.file_like = None

    cdef object _unpack(self, ExecMode exec_mode):
        cdef int ret
        cdef object obj
        while 1:
            ret = template_execute(&self.ctx, self.buf, self.buf_tail, &self.buf_head, exec_mode)
            if ret == 1:
                if exec_mode:
                    obj = template_data(&self.ctx)
                else:
                    obj = None
                template_init(&self.ctx)
                return obj
            elif ret == 0:
                if self.file_like is not None:
                    self.read_from_file()
                    continue
                raise StopIteration("No more data to unpack.")
            else:
                raise UnpackException(ret, "Unpack failed: error = %d" % (ret,))

    def unpack(self):
        """unpack one object"""
        return self._unpack(EXEC_CONSTRUCT)

    def skip(self):
        """read and ignore one object, returning None"""
        return self._unpack(EXEC_SKIP)

    def read_array_header(self):
        """assuming the next object is an array, return its size n, such that the next n unpack() calls will iterate over its contents."""
        try:
            return self._unpack(EXEC_ARRAY_SIZE)
        except UnpackException as exc:
            if exc.code == -2:
                raise UnexpectedTypeException('Did not find an array header')
            raise

    def read_map_header(self):
        """assuming the next object is a map, return its size n, such that the next n * 2 unpack() calls will iterate over its key-value pairs."""
        try:
            return self._unpack(EXEC_MAP_SIZE)
        except UnpackException as exc:
            if exc.code == -2:
                raise UnexpectedTypeException('Did not find a map header')
            raise

    def __iter__(self):
        return self

    def __next__(self):
        return self._unpack(EXEC_CONSTRUCT)

    # for debug.
    #def _buf(self):
    #    return PyString_FromStringAndSize(self.buf, self.buf_tail)

    #def _off(self):
    #    return self.buf_head

