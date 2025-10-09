#cython: embedsignature=True, c_string_encoding=ascii, language_level=3
#cython: freethreading_compatible = True
import cython
from cpython cimport *
from cpython.datetime cimport import_datetime, datetime_new
import_datetime()

import datetime
cdef object utc = datetime.timezone.utc
cdef object epoch = datetime_new(1970, 1, 1, 0, 0, 0, 0, tz=utc)


### Packer

from cpython.bytearray cimport PyByteArray_Check, PyByteArray_CheckExact
from cpython.datetime cimport (
    PyDateTime_CheckExact, PyDelta_CheckExact,
    datetime_tzinfo, timedelta_days, timedelta_seconds, timedelta_microseconds,
)

cdef ExtType
cdef Timestamp

from .ext import ExtType, Timestamp


cdef extern from "Python.h":

    int PyMemoryView_Check(object obj)

cdef extern from "pack.h":
    struct msgpack_packer:
        char* buf
        size_t length
        size_t buf_size
        bint use_bin_type

    int msgpack_pack_nil(msgpack_packer* pk) except -1
    int msgpack_pack_true(msgpack_packer* pk) except -1
    int msgpack_pack_false(msgpack_packer* pk) except -1
    int msgpack_pack_long_long(msgpack_packer* pk, long long d) except -1
    int msgpack_pack_unsigned_long_long(msgpack_packer* pk, unsigned long long d) except -1
    int msgpack_pack_float(msgpack_packer* pk, float d) except -1
    int msgpack_pack_double(msgpack_packer* pk, double d) except -1
    int msgpack_pack_array(msgpack_packer* pk, size_t l) except -1
    int msgpack_pack_map(msgpack_packer* pk, size_t l) except -1
    int msgpack_pack_raw(msgpack_packer* pk, size_t l) except -1
    int msgpack_pack_bin(msgpack_packer* pk, size_t l) except -1
    int msgpack_pack_raw_body(msgpack_packer* pk, char* body, size_t l) except -1
    int msgpack_pack_ext(msgpack_packer* pk, char typecode, size_t l) except -1
    int msgpack_pack_timestamp(msgpack_packer* x, long long seconds, unsigned long nanoseconds) except -1


cdef int DEFAULT_RECURSE_LIMIT=511
cdef long long ITEM_LIMIT = (2**32)-1


cdef inline int PyBytesLike_Check(object o):
    return PyBytes_Check(o) or PyByteArray_Check(o)


cdef inline int PyBytesLike_CheckExact(object o):
    return PyBytes_CheckExact(o) or PyByteArray_CheckExact(o)


cdef class Packer:
    """
    MessagePack Packer

    Usage::

        packer = Packer()
        astream.write(packer.pack(a))
        astream.write(packer.pack(b))

    Packer's constructor has some keyword arguments:

    :param default:
        When specified, it should be callable.
        Convert user type to builtin type that Packer supports.
        See also simplejson's document.

    :param bool use_single_float:
        Use single precision float type for float. (default: False)

    :param bool autoreset:
        Reset buffer after each pack and return its content as `bytes`. (default: True).
        If set this to false, use `bytes()` to get content and `.reset()` to clear buffer.

    :param bool use_bin_type:
        Use bin type introduced in msgpack spec 2.0 for bytes.
        It also enables str8 type for unicode. (default: True)

    :param bool strict_types:
        If set to true, types will be checked to be exact. Derived classes
        from serializeable types will not be serialized and will be
        treated as unsupported type and forwarded to default.
        Additionally tuples will not be serialized as lists.
        This is useful when trying to implement accurate serialization
        for python types.

    :param bool datetime:
        If set to true, datetime with tzinfo is packed into Timestamp type.
        Note that the tzinfo is stripped in the timestamp.
        You can get UTC datetime with `timestamp=3` option of the Unpacker.

    :param str unicode_errors:
        The error handler for encoding unicode. (default: 'strict')
        DO NOT USE THIS!!  This option is kept for very specific usage.

    :param int buf_size:
        The size of the internal buffer. (default: 256*1024)
        Useful if serialisation size can be correctly estimated,
        avoid unnecessary reallocations.
    """
    cdef msgpack_packer pk
    cdef object _default
    cdef object _berrors
    cdef const char *unicode_errors
    cdef size_t exports  # number of exported buffers
    cdef bint strict_types
    cdef bint use_float
    cdef bint autoreset
    cdef bint datetime

    def __cinit__(self, buf_size=256*1024, **_kwargs):
        self.pk.buf = <char*> PyMem_Malloc(buf_size)
        if self.pk.buf == NULL:
            raise MemoryError("Unable to allocate internal buffer.")
        self.pk.buf_size = buf_size
        self.pk.length = 0
        self.exports = 0

    def __dealloc__(self):
        PyMem_Free(self.pk.buf)
        self.pk.buf = NULL
        assert self.exports == 0

    cdef _check_exports(self):
        if self.exports > 0:
            raise BufferError("Existing exports of data: Packer cannot be changed")

    @cython.critical_section
    def __init__(self, *, default=None,
                 bint use_single_float=False, bint autoreset=True, bint use_bin_type=True,
                 bint strict_types=False, bint datetime=False, unicode_errors=None,
                 buf_size=256*1024):
        self.use_float = use_single_float
        self.strict_types = strict_types
        self.autoreset = autoreset
        self.datetime = datetime
        self.pk.use_bin_type = use_bin_type
        if default is not None:
            if not PyCallable_Check(default):
                raise TypeError("default must be a callable.")
        self._default = default

        self._berrors = unicode_errors
        if unicode_errors is None:
            self.unicode_errors = NULL
        else:
            self.unicode_errors = self._berrors

    # returns -2 when default should(o) be called
    cdef int _pack_inner(self, object o, bint will_default, int nest_limit) except -1:
        cdef long long llval
        cdef unsigned long long ullval
        cdef unsigned long ulval
        cdef const char* rawval
        cdef Py_ssize_t L
        cdef Py_buffer view
        cdef bint strict = self.strict_types

        if o is None:
            msgpack_pack_nil(&self.pk)
        elif o is True:
            msgpack_pack_true(&self.pk)
        elif o is False:
            msgpack_pack_false(&self.pk)
        elif PyLong_CheckExact(o) if strict else PyLong_Check(o):
            try:
                if o > 0:
                    ullval = o
                    msgpack_pack_unsigned_long_long(&self.pk, ullval)
                else:
                    llval = o
                    msgpack_pack_long_long(&self.pk, llval)
            except OverflowError as oe:
                if will_default:
                    return -2
                else:
                    raise OverflowError("Integer value out of range")
        elif PyFloat_CheckExact(o) if strict else PyFloat_Check(o):
            if self.use_float:
                msgpack_pack_float(&self.pk, <float>o)
            else:
                msgpack_pack_double(&self.pk, <double>o)
        elif PyBytesLike_CheckExact(o) if strict else PyBytesLike_Check(o):
            L = Py_SIZE(o)
            if L > ITEM_LIMIT:
                PyErr_Format(ValueError, b"%.200s object is too large", Py_TYPE(o).tp_name)
            rawval = o
            msgpack_pack_bin(&self.pk, L)
            msgpack_pack_raw_body(&self.pk, rawval, L)
        elif PyUnicode_CheckExact(o) if strict else PyUnicode_Check(o):
            if self.unicode_errors == NULL:
                rawval = PyUnicode_AsUTF8AndSize(o, &L)
                if L >ITEM_LIMIT:
                    raise ValueError("unicode string is too large")
            else:
                o = PyUnicode_AsEncodedString(o, NULL, self.unicode_errors)
                L = Py_SIZE(o)
                if L > ITEM_LIMIT:
                    raise ValueError("unicode string is too large")
                rawval = o
            msgpack_pack_raw(&self.pk, L)
            msgpack_pack_raw_body(&self.pk, rawval, L)
        elif PyDict_CheckExact(o) if strict else PyDict_Check(o):
            L = len(o)
            if L > ITEM_LIMIT:
                raise ValueError("dict is too large")
            msgpack_pack_map(&self.pk, L)
            for k, v in o.items():
                self._pack(k, nest_limit)
                self._pack(v, nest_limit)
        elif type(o) is ExtType if strict else isinstance(o, ExtType):
            # This should be before Tuple because ExtType is namedtuple.
            rawval = o.data
            L = len(o.data)
            if L > ITEM_LIMIT:
                raise ValueError("EXT data is too large")
            msgpack_pack_ext(&self.pk, <long>o.code, L)
            msgpack_pack_raw_body(&self.pk, rawval, L)
        elif type(o) is Timestamp:
            llval = o.seconds
            ulval = o.nanoseconds
            msgpack_pack_timestamp(&self.pk, llval, ulval)
        elif PyList_CheckExact(o) if strict else (PyTuple_Check(o) or PyList_Check(o)):
            L = Py_SIZE(o)
            if L > ITEM_LIMIT:
                raise ValueError("list is too large")
            msgpack_pack_array(&self.pk, L)
            for v in o:
                self._pack(v, nest_limit)
        elif PyMemoryView_Check(o):
            PyObject_GetBuffer(o, &view, PyBUF_SIMPLE)
            L = view.len
            if L > ITEM_LIMIT:
                PyBuffer_Release(&view);
                raise ValueError("memoryview is too large")
            try:
                msgpack_pack_bin(&self.pk, L)
                msgpack_pack_raw_body(&self.pk, <char*>view.buf, L)
            finally:
                PyBuffer_Release(&view);
        elif self.datetime and PyDateTime_CheckExact(o) and datetime_tzinfo(o) is not None:
            delta = o - epoch
            if not PyDelta_CheckExact(delta):
                raise ValueError("failed to calculate delta")
            llval = timedelta_days(delta) * <long long>(24*60*60) + timedelta_seconds(delta)
            ulval = timedelta_microseconds(delta) * 1000
            msgpack_pack_timestamp(&self.pk, llval, ulval)
        elif will_default:
            return -2
        elif self.datetime and PyDateTime_CheckExact(o):
            # this should be later than will_default
            PyErr_Format(ValueError, b"can not serialize '%.200s' object where tzinfo=None", Py_TYPE(o).tp_name)
        else:
            PyErr_Format(TypeError, b"can not serialize '%.200s' object", Py_TYPE(o).tp_name)

    cdef int _pack(self, object o, int nest_limit=DEFAULT_RECURSE_LIMIT) except -1:
        cdef int ret
        if nest_limit < 0:
            raise ValueError("recursion limit exceeded.")
        nest_limit -= 1
        if self._default is not None:
            ret = self._pack_inner(o, 1, nest_limit)
            if ret == -2:
                o = self._default(o)
            else:
                return ret
        return self._pack_inner(o, 0, nest_limit)

    @cython.critical_section
    def pack(self, object obj):
        cdef int ret
        self._check_exports()
        try:
            ret = self._pack(obj, DEFAULT_RECURSE_LIMIT)
        except:
            self.pk.length = 0
            raise
        if ret:  # should not happen.
            raise RuntimeError("internal error")
        if self.autoreset:
            buf = PyBytes_FromStringAndSize(self.pk.buf, self.pk.length)
            self.pk.length = 0
            return buf

    @cython.critical_section
    def pack_ext_type(self, typecode, data):
        self._check_exports()
        if len(data) > ITEM_LIMIT:
            raise ValueError("ext data too large")
        msgpack_pack_ext(&self.pk, typecode, len(data))
        msgpack_pack_raw_body(&self.pk, data, len(data))

    @cython.critical_section
    def pack_array_header(self, long long size):
        self._check_exports()
        if size > ITEM_LIMIT:
            raise ValueError("array too large")
        msgpack_pack_array(&self.pk, size)
        if self.autoreset:
            buf = PyBytes_FromStringAndSize(self.pk.buf, self.pk.length)
            self.pk.length = 0
            return buf

    @cython.critical_section
    def pack_map_header(self, long long size):
        self._check_exports()
        if size > ITEM_LIMIT:
            raise ValueError("map too learge")
        msgpack_pack_map(&self.pk, size)
        if self.autoreset:
            buf = PyBytes_FromStringAndSize(self.pk.buf, self.pk.length)
            self.pk.length = 0
            return buf

    @cython.critical_section
    def pack_map_pairs(self, object pairs):
        """
        Pack *pairs* as msgpack map type.

        *pairs* should be a sequence of pairs.
        (`len(pairs)` and `for k, v in pairs:` should be supported.)
        """
        self._check_exports()
        size = len(pairs)
        if size > ITEM_LIMIT:
            raise ValueError("map too large")
        msgpack_pack_map(&self.pk, size)
        for k, v in pairs:
            self._pack(k)
            self._pack(v)
        if self.autoreset:
            buf = PyBytes_FromStringAndSize(self.pk.buf, self.pk.length)
            self.pk.length = 0
            return buf

    @cython.critical_section
    def reset(self):
        """Reset internal buffer.

        This method is useful only when autoreset=False.
        """
        self._check_exports()
        self.pk.length = 0

    @cython.critical_section
    def bytes(self):
        """Return internal buffer contents as bytes object"""
        return PyBytes_FromStringAndSize(self.pk.buf, self.pk.length)

    def getbuffer(self):
        """Return memoryview of internal buffer.

        Note: Packer now supports buffer protocol. You can use memoryview(packer).
        """
        return memoryview(self)

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        PyBuffer_FillInfo(buffer, self, self.pk.buf, self.pk.length, 1, flags)
        self.exports += 1

    def __releasebuffer__(self, Py_buffer *buffer):
        self.exports -= 1


### Unpacker

cdef extern from "Python.h":
    #ctypedef struct PyObject
    object PyMemoryView_GetContiguous(object obj, int buffertype, char order)

from libc.stdlib cimport *
from libc.string cimport *
from libc.limits cimport *
from libc.stdint cimport uint64_t

from .exceptions import (
    BufferFull,
    OutOfData,
    ExtraData,
    FormatError,
    StackError,
)
from .ext import ExtType, Timestamp

cdef object giga = 1_000_000_000


cdef extern from "unpack.h":
    ctypedef struct msgpack_user:
        bint use_list
        bint raw
        bint has_pairs_hook # call object_hook with k-v pairs
        bint strict_map_key
        int timestamp
        PyObject* object_hook
        PyObject* list_hook
        PyObject* ext_hook
        PyObject* timestamp_t
        PyObject *giga;
        PyObject *utc;
        const char *unicode_errors
        Py_ssize_t max_str_len
        Py_ssize_t max_bin_len
        Py_ssize_t max_array_len
        Py_ssize_t max_map_len
        Py_ssize_t max_ext_len

    ctypedef struct unpack_context:
        msgpack_user user
        PyObject* obj
        Py_ssize_t count

    ctypedef int (*execute_fn)(unpack_context* ctx, const char* data,
                               Py_ssize_t len, Py_ssize_t* off) except? -1
    execute_fn unpack_construct
    execute_fn unpack_skip
    execute_fn read_array_header
    execute_fn read_map_header
    void unpack_init(unpack_context* ctx)
    object unpack_data(unpack_context* ctx)
    void unpack_clear(unpack_context* ctx)

cdef inline init_ctx(unpack_context *ctx,
                     object object_hook, object object_pairs_hook,
                     object list_hook, object ext_hook,
                     bint use_list, bint raw, int timestamp,
                     bint strict_map_key,
                     const char* unicode_errors,
                     Py_ssize_t max_str_len, Py_ssize_t max_bin_len,
                     Py_ssize_t max_array_len, Py_ssize_t max_map_len,
                     Py_ssize_t max_ext_len):
    unpack_init(ctx)
    ctx.user.use_list = use_list
    ctx.user.raw = raw
    ctx.user.strict_map_key = strict_map_key
    ctx.user.object_hook = ctx.user.list_hook = <PyObject*>NULL
    ctx.user.max_str_len = max_str_len
    ctx.user.max_bin_len = max_bin_len
    ctx.user.max_array_len = max_array_len
    ctx.user.max_map_len = max_map_len
    ctx.user.max_ext_len = max_ext_len

    if object_hook is not None and object_pairs_hook is not None:
        raise TypeError("object_pairs_hook and object_hook are mutually exclusive.")

    if object_hook is not None:
        if not PyCallable_Check(object_hook):
            raise TypeError("object_hook must be a callable.")
        ctx.user.object_hook = <PyObject*>object_hook

    if object_pairs_hook is None:
        ctx.user.has_pairs_hook = False
    else:
        if not PyCallable_Check(object_pairs_hook):
            raise TypeError("object_pairs_hook must be a callable.")
        ctx.user.object_hook = <PyObject*>object_pairs_hook
        ctx.user.has_pairs_hook = True

    if list_hook is not None:
        if not PyCallable_Check(list_hook):
            raise TypeError("list_hook must be a callable.")
        ctx.user.list_hook = <PyObject*>list_hook

    if ext_hook is not None:
        if not PyCallable_Check(ext_hook):
            raise TypeError("ext_hook must be a callable.")
        ctx.user.ext_hook = <PyObject*>ext_hook

    if timestamp < 0 or 3 < timestamp:
        raise ValueError("timestamp must be 0..3")

    # Add Timestamp type to the user object so it may be used in unpack.h
    ctx.user.timestamp = timestamp
    ctx.user.timestamp_t = <PyObject*>Timestamp
    ctx.user.giga = <PyObject*>giga
    ctx.user.utc = <PyObject*>utc
    ctx.user.unicode_errors = unicode_errors

def default_read_extended_type(typecode, data):
    raise NotImplementedError("Cannot decode extended type with typecode=%d" % typecode)

cdef inline int get_data_from_buffer(object obj,
                                     Py_buffer *view,
                                     char **buf,
                                     Py_ssize_t *buffer_len) except 0:
    cdef object contiguous
    cdef Py_buffer tmp
    if PyObject_GetBuffer(obj, view, PyBUF_FULL_RO) == -1:
        raise
    if view.itemsize != 1:
        PyBuffer_Release(view)
        raise BufferError("cannot unpack from multi-byte object")
    if PyBuffer_IsContiguous(view, b'A') == 0:
        PyBuffer_Release(view)
        # create a contiguous copy and get buffer
        contiguous = PyMemoryView_GetContiguous(obj, PyBUF_READ, b'C')
        PyObject_GetBuffer(contiguous, view, PyBUF_SIMPLE)
        # view must hold the only reference to contiguous,
        # so memory is freed when view is released
        Py_DECREF(contiguous)
    buffer_len[0] = view.len
    buf[0] = <char*> view.buf
    return 1


def unpackb(object packed, *, object object_hook=None, object list_hook=None,
            bint use_list=True, bint raw=False, int timestamp=0, bint strict_map_key=True,
            unicode_errors=None,
            object_pairs_hook=None, ext_hook=ExtType,
            Py_ssize_t max_str_len=-1,
            Py_ssize_t max_bin_len=-1,
            Py_ssize_t max_array_len=-1,
            Py_ssize_t max_map_len=-1,
            Py_ssize_t max_ext_len=-1):
    """
    Unpack packed_bytes to object. Returns an unpacked object.

    Raises ``ExtraData`` when *packed* contains extra bytes.
    Raises ``ValueError`` when *packed* is incomplete.
    Raises ``FormatError`` when *packed* is not valid msgpack.
    Raises ``StackError`` when *packed* contains too nested.
    Other exceptions can be raised during unpacking.

    See :class:`Unpacker` for options.

    *max_xxx_len* options are configured automatically from ``len(packed)``.
    """
    cdef unpack_context ctx
    cdef Py_ssize_t off = 0
    cdef int ret

    cdef Py_buffer view
    cdef char* buf = NULL
    cdef Py_ssize_t buf_len
    cdef const char* cerr = NULL

    if unicode_errors is not None:
        cerr = unicode_errors

    get_data_from_buffer(packed, &view, &buf, &buf_len)

    if max_str_len == -1:
        max_str_len = buf_len
    if max_bin_len == -1:
        max_bin_len = buf_len
    if max_array_len == -1:
        max_array_len = buf_len
    if max_map_len == -1:
        max_map_len = buf_len//2
    if max_ext_len == -1:
        max_ext_len = buf_len

    try:
        init_ctx(&ctx, object_hook, object_pairs_hook, list_hook, ext_hook,
                 use_list, raw, timestamp, strict_map_key, cerr,
                 max_str_len, max_bin_len, max_array_len, max_map_len, max_ext_len)
        ret = unpack_construct(&ctx, buf, buf_len, &off)
    finally:
        PyBuffer_Release(&view);

    if ret == 1:
        obj = unpack_data(&ctx)
        if off < buf_len:
            raise ExtraData(obj, PyBytes_FromStringAndSize(buf+off, buf_len-off))
        return obj
    unpack_clear(&ctx)
    if ret == 0:
        raise ValueError("Unpack failed: incomplete input")
    elif ret == -2:
        raise FormatError
    elif ret == -3:
        raise StackError
    raise ValueError("Unpack failed: error = %d" % (ret,))


cdef class Unpacker:
    """Streaming unpacker.

    Arguments:

    :param file_like:
        File-like object having `.read(n)` method.
        If specified, unpacker reads serialized data from it and `.feed()` is not usable.

    :param int read_size:
        Used as `file_like.read(read_size)`. (default: `min(16*1024, max_buffer_size)`)

    :param bool use_list:
        If true, unpack msgpack array to Python list.
        Otherwise, unpack to Python tuple. (default: True)

    :param bool raw:
        If true, unpack msgpack raw to Python bytes.
        Otherwise, unpack to Python str by decoding with UTF-8 encoding (default).

    :param int timestamp:
        Control how timestamp type is unpacked:

            0 - Timestamp
            1 - float  (Seconds from the EPOCH)
            2 - int  (Nanoseconds from the EPOCH)
            3 - datetime.datetime  (UTC).

    :param bool strict_map_key:
        If true (default), only str or bytes are accepted for map (dict) keys.

    :param object_hook:
        When specified, it should be callable.
        Unpacker calls it with a dict argument after unpacking msgpack map.
        (See also simplejson)

    :param object_pairs_hook:
        When specified, it should be callable.
        Unpacker calls it with a list of key-value pairs after unpacking msgpack map.
        (See also simplejson)

    :param str unicode_errors:
        The error handler for decoding unicode. (default: 'strict')
        This option should be used only when you have msgpack data which
        contains invalid UTF-8 string.

    :param int max_buffer_size:
        Limits size of data waiting unpacked.  0 means 2**32-1.
        The default value is 100*1024*1024 (100MiB).
        Raises `BufferFull` exception when it is insufficient.
        You should set this parameter when unpacking data from untrusted source.

    :param int max_str_len:
        Deprecated, use *max_buffer_size* instead.
        Limits max length of str. (default: max_buffer_size)

    :param int max_bin_len:
        Deprecated, use *max_buffer_size* instead.
        Limits max length of bin. (default: max_buffer_size)

    :param int max_array_len:
        Limits max length of array.
        (default: max_buffer_size)

    :param int max_map_len:
        Limits max length of map.
        (default: max_buffer_size//2)

    :param int max_ext_len:
        Deprecated, use *max_buffer_size* instead.
        Limits max size of ext type.  (default: max_buffer_size)

    Example of streaming deserialize from file-like object::

        unpacker = Unpacker(file_like)
        for o in unpacker:
            process(o)

    Example of streaming deserialize from socket::

        unpacker = Unpacker()
        while True:
            buf = sock.recv(1024**2)
            if not buf:
                break
            unpacker.feed(buf)
            for o in unpacker:
                process(o)

    Raises ``ExtraData`` when *packed* contains extra bytes.
    Raises ``OutOfData`` when *packed* is incomplete.
    Raises ``FormatError`` when *packed* is not valid msgpack.
    Raises ``StackError`` when *packed* contains too nested.
    Other exceptions can be raised during unpacking.
    """
    cdef unpack_context ctx
    cdef char* buf
    cdef Py_ssize_t buf_size, buf_head, buf_tail
    cdef object file_like
    cdef object file_like_read
    cdef Py_ssize_t read_size
    # To maintain refcnt.
    cdef object object_hook, object_pairs_hook, list_hook, ext_hook
    cdef object unicode_errors
    cdef Py_ssize_t max_buffer_size
    cdef uint64_t stream_offset

    def __cinit__(self):
        self.buf = NULL

    def __dealloc__(self):
        PyMem_Free(self.buf)
        self.buf = NULL

    @cython.critical_section
    def __init__(self, file_like=None, *, Py_ssize_t read_size=0,
                 bint use_list=True, bint raw=False, int timestamp=0, bint strict_map_key=True,
                 object object_hook=None, object object_pairs_hook=None, object list_hook=None,
                 unicode_errors=None, Py_ssize_t max_buffer_size=100*1024*1024,
                 object ext_hook=ExtType,
                 Py_ssize_t max_str_len=-1,
                 Py_ssize_t max_bin_len=-1,
                 Py_ssize_t max_array_len=-1,
                 Py_ssize_t max_map_len=-1,
                 Py_ssize_t max_ext_len=-1):
        cdef const char *cerr=NULL

        self.object_hook = object_hook
        self.object_pairs_hook = object_pairs_hook
        self.list_hook = list_hook
        self.ext_hook = ext_hook

        self.file_like = file_like
        if file_like:
            self.file_like_read = file_like.read
            if not PyCallable_Check(self.file_like_read):
                raise TypeError("`file_like.read` must be a callable.")

        if not max_buffer_size:
            max_buffer_size = INT_MAX
        if max_str_len == -1:
            max_str_len = max_buffer_size
        if max_bin_len == -1:
            max_bin_len = max_buffer_size
        if max_array_len == -1:
            max_array_len = max_buffer_size
        if max_map_len == -1:
            max_map_len = max_buffer_size//2
        if max_ext_len == -1:
            max_ext_len = max_buffer_size

        if read_size > max_buffer_size:
            raise ValueError("read_size should be less or equal to max_buffer_size")
        if not read_size:
            read_size = min(max_buffer_size, 1024**2)

        self.max_buffer_size = max_buffer_size
        self.read_size = read_size
        self.buf = <char*>PyMem_Malloc(read_size)
        if self.buf == NULL:
            raise MemoryError("Unable to allocate internal buffer.")
        self.buf_size = read_size
        self.buf_head = 0
        self.buf_tail = 0
        self.stream_offset = 0

        if unicode_errors is not None:
            self.unicode_errors = unicode_errors
            cerr = unicode_errors

        init_ctx(&self.ctx, object_hook, object_pairs_hook, list_hook,
                 ext_hook, use_list, raw, timestamp, strict_map_key, cerr,
                 max_str_len, max_bin_len, max_array_len,
                 max_map_len, max_ext_len)

    @cython.critical_section
    def feed(self, object next_bytes):
        """Append `next_bytes` to internal buffer."""
        cdef Py_buffer pybuff
        cdef char* buf
        cdef Py_ssize_t buf_len

        if self.file_like is not None:
            raise AssertionError(
                    "unpacker.feed() is not be able to use with `file_like`.")

        get_data_from_buffer(next_bytes, &pybuff, &buf, &buf_len)
        try:
            self.append_buffer(buf, buf_len)
        finally:
            PyBuffer_Release(&pybuff)

    cdef append_buffer(self, void* _buf, Py_ssize_t _buf_len):
        cdef:
            char* buf = self.buf
            char* new_buf
            Py_ssize_t head = self.buf_head
            Py_ssize_t tail = self.buf_tail
            Py_ssize_t buf_size = self.buf_size
            Py_ssize_t new_size

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
                new_buf = <char*>PyMem_Malloc(new_size)
                if new_buf == NULL:
                    # self.buf still holds old buffer and will be freed during
                    # obj destruction
                    raise MemoryError("Unable to enlarge internal buffer.")
                memcpy(new_buf, buf + head, tail - head)
                PyMem_Free(buf)

                buf = new_buf
                buf_size = new_size
                tail -= head
                head = 0

        memcpy(buf + tail, <char*>(_buf), _buf_len)
        self.buf = buf
        self.buf_head = head
        self.buf_size = buf_size
        self.buf_tail = tail + _buf_len

    cdef int read_from_file(self) except -1:
        cdef Py_ssize_t remains = self.max_buffer_size - (self.buf_tail - self.buf_head)
        if remains <= 0:
            raise BufferFull

        next_bytes = self.file_like_read(min(self.read_size, remains))
        if next_bytes:
            self.append_buffer(PyBytes_AsString(next_bytes), PyBytes_Size(next_bytes))
        else:
            self.file_like = None
        return 0

    cdef object _unpack(self, execute_fn execute, bint iter=0):
        cdef int ret
        cdef object obj
        cdef Py_ssize_t prev_head

        while 1:
            prev_head = self.buf_head
            if prev_head < self.buf_tail:
                ret = execute(&self.ctx, self.buf, self.buf_tail, &self.buf_head)
                self.stream_offset += self.buf_head - prev_head
            else:
                ret = 0

            if ret == 1:
                obj = unpack_data(&self.ctx)
                unpack_init(&self.ctx)
                return obj
            elif ret == 0:
                if self.file_like is not None:
                    self.read_from_file()
                    continue
                if iter:
                    raise StopIteration("No more data to unpack.")
                else:
                    raise OutOfData("No more data to unpack.")
            elif ret == -2:
                raise FormatError
            elif ret == -3:
                raise StackError
            else:
                raise ValueError("Unpack failed: error = %d" % (ret,))

    @cython.critical_section
    def read_bytes(self, Py_ssize_t nbytes):
        """Read a specified number of raw bytes from the stream"""
        cdef Py_ssize_t nread
        nread = min(self.buf_tail - self.buf_head, nbytes)
        ret = PyBytes_FromStringAndSize(self.buf + self.buf_head, nread)
        self.buf_head += nread
        if nread < nbytes and self.file_like is not None:
            ret += self.file_like.read(nbytes - nread)
            nread = len(ret)
        self.stream_offset += nread
        return ret

    @cython.critical_section
    def unpack(self):
        """Unpack one object

        Raises `OutOfData` when there are no more bytes to unpack.
        """
        return self._unpack(unpack_construct)

    @cython.critical_section
    def skip(self):
        """Read and ignore one object, returning None

        Raises `OutOfData` when there are no more bytes to unpack.
        """
        return self._unpack(unpack_skip)

    @cython.critical_section
    def read_array_header(self):
        """assuming the next object is an array, return its size n, such that
        the next n unpack() calls will iterate over its contents.

        Raises `OutOfData` when there are no more bytes to unpack.
        """
        return self._unpack(read_array_header)

    @cython.critical_section
    def read_map_header(self):
        """assuming the next object is a map, return its size n, such that the
        next n * 2 unpack() calls will iterate over its key-value pairs.

        Raises `OutOfData` when there are no more bytes to unpack.
        """
        return self._unpack(read_map_header)

    @cython.critical_section
    def tell(self):
        """Returns the current position of the Unpacker in bytes, i.e., the
        number of bytes that were read from the input, also the starting
        position of the next object.
        """
        return self.stream_offset

    def __iter__(self):
        return self

    @cython.critical_section
    def __next__(self):
        return self._unpack(unpack_construct, 1)

    # for debug.
    #def _buf(self):
    #    return PyString_FromStringAndSize(self.buf, self.buf_tail)

    #def _off(self):
    #    return self.buf_head
