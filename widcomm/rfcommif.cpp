#include <windows.h>
#include <Python.h>
#include <tchar.h>

#include <BtIfDefinitions.h>
#include <BtIfClasses.h>
#include <com_error.h>

#include "util.h"

// ===================

typedef struct _WCRfCommIfPyObject WCRfCommIfPyObject;

struct _WCRfCommIfPyObject {
    PyObject_HEAD

    CRfCommIf * rfcommif;
};
PyDoc_STRVAR(wcrfcommif_doc, "CRfCommIf wrapper");

extern PyTypeObject wcrfcommif_type;

static PyObject *
assign_scn_value (PyObject *s, PyObject *args)
{
    WCRfCommIfPyObject *self = (WCRfCommIfPyObject*) s;

    char *uuid_str = NULL;
    int uuid_str_len = 0;
    UINT8 scn = 0;
    char *service_name = _T("");

    if(!PyArg_ParseTuple (args, "s#|Bs", &uuid_str, &uuid_str_len, 
                &scn, &service_name))
        return NULL;

    GUID uuid = { 0 };
    PyWidcomm::str2uuid (uuid_str, &uuid);

//    printf ("AssignScnValue\n");
    BOOL result = self->rfcommif->AssignScnValue (&uuid, scn, service_name);

    if (result) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *
get_scn (PyObject *s)
{
    WCRfCommIfPyObject *self = (WCRfCommIfPyObject*) s;

    return PyLong_FromLong (self->rfcommif->GetScn ());
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

    WCRfCommIfPyObject *self = (WCRfCommIfPyObject*) s;
    BOOL result = self->rfcommif->SetSecurityLevel (service_name, 
            security_level, (BOOL) is_server);

    if (result) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyMethodDef wcrfcommif_methods[] = {
    { "assign_scn_value", (PyCFunction)assign_scn_value, METH_VARARGS, "" },
    { "get_scn", (PyCFunction)get_scn, METH_NOARGS, "" },
    { "set_security_level", (PyCFunction)set_security_level, METH_VARARGS, "" },
    { NULL, NULL }
};

static PyObject *
wcrfcommif_repr(WCRfCommIfPyObject *s)
{
    return PyUnicode_FromString("_WCRfCommIf object");
}

static PyObject *
wcrfcommif_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *newobj;

    newobj = type->tp_alloc(type, 0);
    if (newobj != NULL) {
        WCRfCommIfPyObject *self = (WCRfCommIfPyObject *)newobj;
        self->rfcommif = NULL;
    }
    return newobj;
}

static void
wcrfcommif_dealloc(WCRfCommIfPyObject *self)
{
    if (self->rfcommif) {
        delete self->rfcommif;
        self->rfcommif = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

int
wcrfcommif_initobj(PyObject *s, PyObject *args, PyObject *kwds)
{
    WCRfCommIfPyObject *self = (WCRfCommIfPyObject *)s;
    self->rfcommif = new CRfCommIf ();
    return 0;
}

/* Type object for socket objects. */
PyTypeObject wcrfcommif_type = {
    PyVarObject_HEAD_INIT(NULL, 0)   /* Must fill in type value later */
    "_widcomm._WCRfCommIf",            /* tp_name */
    sizeof(WCRfCommIfPyObject),     /* tp_basicsize */
    0,                  /* tp_itemsize */
    (destructor)wcrfcommif_dealloc,     /* tp_dealloc */
    0,                  /* tp_print */
    0,                  /* tp_getattr */
    0,                  /* tp_setattr */
    0,                  /* tp_compare */
    (reprfunc)wcrfcommif_repr,          /* tp_repr */
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
    wcrfcommif_doc,               /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    wcrfcommif_methods,               /* tp_methods */
    0,                  /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    wcrfcommif_initobj,             /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    wcrfcommif_new,             /* tp_new */
    PyObject_Del,               /* tp_free */
};


