#include <windows.h>
#include <Python.h>
#include <tchar.h>

#include <BtIfDefinitions.h>
#include <BtIfClasses.h>
#include <com_error.h>
#include <port3.h>

#include "util.h"
#include "l2capif.hpp"

// ===================

static inline void
dbg (const char *fmt, ...)
{
    return;
    va_list ap;
    va_start (ap, fmt);
    vfprintf (stderr, fmt, ap);
    va_end (ap);
}

PyDoc_STRVAR(wcl2capif_doc, "CL2CapIf wrapper");

static PyObject *
assign_psm_value (PyObject *s, PyObject *args)
{
//    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    WCL2CapIfPyObject *self = (WCL2CapIfPyObject*) s;

    char *uuid_str = NULL;
    int uuid_str_len = 0;
    UINT16 psm = 0;
    char *service_name = _T("");

    if(!PyArg_ParseTuple (args, "s#|H", &uuid_str, &uuid_str_len, &psm))
        return NULL;

    GUID uuid = { 0 };
    PyWidcomm::str2uuid (uuid_str, &uuid);

    BOOL result = self->l2capif->AssignPsmValue (&uuid, psm);
    dbg ("%s:%d:%s (%d)\n", __FILE__, __LINE__, __FUNCTION__, 
            self->l2capif->GetPsm());

    if (result) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *
wc_register (PyObject *s)
{
    WCL2CapIfPyObject *self = (WCL2CapIfPyObject*) s;
    return PyInt_FromLong (self->l2capif->Register ());
}

static PyObject *
wc_deregister (PyObject *s)
{
    WCL2CapIfPyObject *self = (WCL2CapIfPyObject*) s;
    self->l2capif->Deregister ();
    Py_RETURN_NONE;
}

static PyObject *
get_psm (PyObject *s)
{
    WCL2CapIfPyObject *self = (WCL2CapIfPyObject*) s;

    return PyInt_FromLong (self->l2capif->GetPsm ());
}

static PyObject *
set_security_level (PyObject *s, PyObject *args)
{
    char *service_name = NULL;
    UINT8 security_level = BTM_SEC_NONE;
    int is_server;

    if(!PyArg_ParseTuple (args, "sBi", &service_name, &security_level,
                &is_server))
        return NULL;

    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    WCL2CapIfPyObject *self = (WCL2CapIfPyObject*) s;
    BOOL result = self->l2capif->SetSecurityLevel (service_name, 
            security_level, (BOOL) is_server);

//    dbg ("%s:%d:%s %d\n", __FILE__, __LINE__, __FUNCTION__, result);

    if (result) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyMethodDef wcl2capif_methods[] = {
    { "assign_psm_value", (PyCFunction)assign_psm_value, METH_VARARGS, "" },
    { "register", (PyCFunction)wc_register, METH_NOARGS, "" },
    { "deregister", (PyCFunction)wc_deregister, METH_NOARGS, "" },
    { "get_psm", (PyCFunction)get_psm, METH_NOARGS, "" },
    { "set_security_level", (PyCFunction)set_security_level, METH_VARARGS, "" },
    { NULL, NULL }
};

static PyObject *
wcl2capif_repr(WCL2CapIfPyObject *s)
{
    return PyString_FromString("_WCL2CapIf object");
}

static PyObject *
wcl2capif_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *newobj;

    newobj = type->tp_alloc(type, 0);
    if (newobj != NULL) {
        WCL2CapIfPyObject *self = (WCL2CapIfPyObject *)newobj;
        self->l2capif = NULL;
    }
    return newobj;
}

static void
wcl2capif_dealloc(WCL2CapIfPyObject *self)
{
    if (self->l2capif) {
        delete self->l2capif;
        self->l2capif = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

int
wcl2capif_initobj(PyObject *s, PyObject *args, PyObject *kwds)
{
    WCL2CapIfPyObject *self = (WCL2CapIfPyObject *)s;
    self->l2capif = new CL2CapIf ();
    return 0;
}

/* Type object for socket objects. */
PyTypeObject wcl2capif_type = {
#if PY_MAJOR_VERSION < 3
    PyObject_HEAD_INIT(0)   /* Must fill in type value later */
    0,                  /* ob_size */
#else
    PyVarObject_HEAD_INIT(NULL, 0)   /* Must fill in type value later */
#endif
    "_widcomm._WCL2CapIf",            /* tp_name */
    sizeof(WCL2CapIfPyObject),     /* tp_basicsize */
    0,                  /* tp_itemsize */
    (destructor)wcl2capif_dealloc,     /* tp_dealloc */
    0,                  /* tp_print */
    0,                  /* tp_getattr */
    0,                  /* tp_setattr */
    0,                  /* tp_compare */
    (reprfunc)wcl2capif_repr,          /* tp_repr */
    0,                  /* tp_as_number */
    0,                  /* tp_as_sequence */
    0,                  /* tp_as_mapping */
    0,                  /* tp_hash */
    0,                  /* tp_call */
    0,                  /* tp_str */
    PyObject_GenericGetAttr,        /* tp_getattro */
    0,                  /* tp_setattro */
    0,                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    wcl2capif_doc,               /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    wcl2capif_methods,               /* tp_methods */
    0,                  /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    wcl2capif_initobj,             /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    wcl2capif_new,             /* tp_new */
    PyObject_Del,               /* tp_free */
};


