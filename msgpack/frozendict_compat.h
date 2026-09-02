#ifndef MSGPACK_FROZENDICT_COMPAT_H
#define MSGPACK_FROZENDICT_COMPAT_H

#include <Python.h>

/* frozendict (PEP 814) is a builtin type added in CPython 3.15. */
#if PY_VERSION_HEX >= 0x030f0000
/* PyFrozenDict_Check / PyFrozenDict_CheckExact come from
 * Include/cpython/dictobject.h, pulled in transitively by Python.h. */
#else
#define PyFrozenDict_Check(op) 0
#define PyFrozenDict_CheckExact(op) 0
#endif

#endif
