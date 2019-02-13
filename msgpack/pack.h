/*
 * MessagePack for Python packing routine
 *
 * Copyright (C) 2009 Naoki INADA
 *
 *    Licensed under the Apache License, Version 2.0 (the "License");
 *    you may not use this file except in compliance with the License.
 *    You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing, software
 *    distributed under the License is distributed on an "AS IS" BASIS,
 *    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *    See the License for the specific language governing permissions and
 *    limitations under the License.
 */

#include <stddef.h>
#include <stdlib.h>
#include "sysdep.h"
#include <limits.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _MSC_VER
#define inline __inline
#endif

typedef struct msgpack_packer {
    char *buf;
    size_t length;
    size_t buf_size;
    bool use_bin_type;
    PyObject *write;
} msgpack_packer;

typedef struct Packer Packer;

static inline void msgpack_packer_init(msgpack_packer* pk, PyObject* write)
{
    Py_INCREF(write);
    pk->write = write;
    pk->length = 0;
    pk->buf_size = 1024*1024;
    pk->buf = (char*) PyMem_Malloc(pk->buf_size);
    if (pk->buf == NULL) {
        PyErr_SetString(PyExc_MemoryError, "Unable to allocate internal buffer.");
    }
}

static inline void msgpack_packer_free(msgpack_packer* pk)
{
    PyMem_Free(pk->buf);
    Py_XDECREF(pk->write);
    pk->buf = NULL;
    pk->write = NULL;
}

static inline int msgpack_pack_flush(msgpack_packer* pk)
{
    PyObject_CallFunctionObjArgs(pk->write, PyBytes_FromStringAndSize(pk->buf, pk->length), NULL);
    pk->length = 0;
    return 0;
}

static inline int msgpack_pack_write(msgpack_packer* pk, const char *data, size_t l)
{
    char* buf = pk->buf;
    size_t bs = pk->buf_size;
    size_t len = pk->length;

    if (len + l > bs) {
        // fill remainder of buffer
        size_t rem = bs - len;
        memcpy(buf + len, data, bs - len);
        data += rem;
        l -= rem;

        // flush buffer
        PyObject_CallFunctionObjArgs(pk->write, PyBytes_FromStringAndSize(pk->buf, bs), NULL);
        len = 0;

        // for large writes, bypass buffer entirely
        if (l >= bs) {
            PyObject_CallFunctionObjArgs(pk->write, PyBytes_FromStringAndSize(data, l), NULL);
            pk->length = 0;
            return 0;
        }
    }
    memcpy(buf + len, data, l);
    pk->length = len + l;
    return 0;
}

#define msgpack_pack_append_buffer(user, buf, len) \
        return msgpack_pack_write(user, (const char*)buf, len)

#include "pack_template.h"

// return -2 when o is too long
static inline int
msgpack_pack_unicode(msgpack_packer *pk, PyObject *o, long long limit)
{
#if PY_MAJOR_VERSION >= 3
    assert(PyUnicode_Check(o));

    Py_ssize_t len;
    const char* buf = PyUnicode_AsUTF8AndSize(o, &len);
    if (buf == NULL)
        return -1;

    if (len > limit) {
        return -2;
    }

    int ret = msgpack_pack_raw(pk, len);
    if (ret) return ret;

    return msgpack_pack_raw_body(pk, buf, len);
#else
    PyObject *bytes;
    Py_ssize_t len;
    int ret;

    // py2
    bytes = PyUnicode_AsUTF8String(o);
    if (bytes == NULL)
        return -1;

    len = PyString_GET_SIZE(bytes);
    if (len > limit) {
        Py_DECREF(bytes);
        return -2;
    }

    ret = msgpack_pack_raw(pk, len);
    if (ret) {
        Py_DECREF(bytes);
        return -1;
    }
    ret = msgpack_pack_raw_body(pk, PyString_AS_STRING(bytes), len);
    Py_DECREF(bytes);
    return ret;
#endif
}

#ifdef __cplusplus
}
#endif
