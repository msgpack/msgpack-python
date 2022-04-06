// SPDX-FileCopyrightText: 2008-2022 INADA Naoki <songofacandy@gmail.com> and other contributors
//
// SPDX-License-Identifier: Apache-2.0

#include "Python.h"

/* cython does not support this preprocessor check => write it in raw C */
static PyObject *
buff_to_buff(char *buff, Py_ssize_t size)
{
    return PyMemoryView_FromMemory(buff, size, PyBUF_READ);
}
