#include <windows.h>
#include <Python.h>

#include <BtIfDefinitions.h>
#include <BtIfClasses.h>
#include <com_error.h>

#include "util.h"

// ===================

typedef struct _WCSdpServicePyObject WCSdpServicePyObject;

struct _WCSdpServicePyObject {
    PyObject_HEAD

    CSdpService * sdpservice;
};
PyDoc_STRVAR(wcsdpservice_doc, "CSdpService wrapper");

extern PyTypeObject wcsdpservice_type;

static PyObject *
add_service_class_id_list (WCSdpServicePyObject *self, PyObject *arg)
{
    int nuids = PySequence_Size (arg);
    if (nuids < 0) {
        return NULL;
    }

    GUID *uuids = (GUID*) malloc (nuids * sizeof (GUID));

    for (int i=0; i<nuids; i++) {
        PyObject *uuid_obj = PySequence_GetItem (arg, i);
        char *uuid_str = PyBytes_AsString (uuid_obj);
        if (uuid_str){
            Py_DECREF (uuid_obj);
            goto fail;
        }

        if (uuid_str) {
            PyWidcomm::str2uuid (uuid_str, &uuids[i]);
        }

        Py_DECREF (uuid_obj);
    }

    SDP_RETURN_CODE result = 
        self->sdpservice->AddServiceClassIdList (nuids, uuids);

    free (uuids);
    return PyLong_FromLong (result);
fail:
    free (uuids);
    return NULL;
}

static PyObject *
add_profile_descriptor_list (WCSdpServicePyObject *self, PyObject *args)
{
    char *uuid_str = NULL;
    int uuid_str_len = 0;
    UINT16 version = 0;
    GUID uuid;
    if (!PyArg_ParseTuple (args, "s#H", &uuid_str, &uuid_str_len, &version)) 
        return NULL;
    PyWidcomm::str2uuid (uuid_str, &uuid);
    SDP_RETURN_CODE result = 
        self->sdpservice->AddProfileDescriptorList (&uuid, version);
    return PyLong_FromLong (result);
}

static PyObject *
add_service_name (WCSdpServicePyObject *self, PyObject *arg)
{
    char *name = PyBytes_AsString (arg);
    if (!name) return NULL;
    SDP_RETURN_CODE result = self->sdpservice->AddServiceName (name);
    return PyLong_FromLong (result);
}

static PyObject *
add_rfcomm_protocol_descriptor (WCSdpServicePyObject *self, PyObject *arg)
{
    int port = PyLong_AsLong (arg);
    if (PyErr_Occurred ()) return NULL;
    UINT8 scn = static_cast <UINT8> (port);
    SDP_RETURN_CODE result = 
        self->sdpservice->AddRFCommProtocolDescriptor (scn);
    return PyLong_FromLong (result);
}

static PyObject *
add_l2cap_protocol_descriptor (WCSdpServicePyObject *self, PyObject *arg)
{
    int port = PyLong_AsLong (arg);
    if (PyErr_Occurred ()) return NULL;
    UINT16 psm = static_cast <UINT16> (port);
    SDP_RETURN_CODE result = self->sdpservice->AddL2CapProtocolDescriptor (psm);
    return PyLong_FromLong (result);
}

static PyObject *
make_public_browseable (WCSdpServicePyObject *self)
{
    SDP_RETURN_CODE result = self->sdpservice->MakePublicBrowseable ();
    return PyLong_FromLong (result);
}

static PyObject *
set_availability (WCSdpServicePyObject *self, PyObject *arg)
{
    UINT8 available = static_cast <UINT8> (PyLong_AsLong (arg));
    if (PyErr_Occurred ()) return NULL;
    SDP_RETURN_CODE result = self->sdpservice->SetAvailability (available);
    return PyLong_FromLong (result);
}

static PyMethodDef wcsdpservice_methods[] = {
    { "add_service_class_id_list", 
        (PyCFunction)add_service_class_id_list, METH_O, "" },
    { "add_profile_descriptor_list",
        (PyCFunction)add_profile_descriptor_list, METH_VARARGS, "" },
    { "add_service_name", 
        (PyCFunction)add_service_name, METH_O, "" },
    { "add_rfcomm_protocol_descriptor", 
        (PyCFunction)add_rfcomm_protocol_descriptor, METH_O, "" },
    { "add_l2cap_protocol_descriptor", 
        (PyCFunction)add_l2cap_protocol_descriptor, METH_O, "" },
    { "make_public_browseable",
        (PyCFunction)make_public_browseable, METH_NOARGS, "" },
    { "set_availability",
        (PyCFunction)set_availability, METH_O, "" },
    { NULL, NULL }
};

static PyObject *
wcsdpservice_repr(WCSdpServicePyObject *s)
{
    return PyUnicode_FromString("_WCSdpService object");
}

static PyObject *
wcsdpservice_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *newobj;

    newobj = type->tp_alloc(type, 0);
    if (newobj != NULL) {
        WCSdpServicePyObject *self = (WCSdpServicePyObject *)newobj;
        self->sdpservice = NULL;
    }
    return newobj;
}

static void
wcsdpservice_dealloc(WCSdpServicePyObject *self)
{
    if (self->sdpservice) {
        delete self->sdpservice;
        self->sdpservice = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

int
wcsdpservice_initobj(PyObject *s, PyObject *args, PyObject *kwds)
{
    WCSdpServicePyObject *self = (WCSdpServicePyObject *)s;
    self->sdpservice = new CSdpService ();
    return 0;
}

/* Type object for socket objects. */
PyTypeObject wcsdpservice_type = {
    PyVarObject_HEAD_INIT(NULL, 0)   /* Must fill in type value later */
    "_widcomm._WCSdpService",            /* tp_name */
    sizeof(WCSdpServicePyObject),     /* tp_basicsize */
    0,                  /* tp_itemsize */
    (destructor)wcsdpservice_dealloc,     /* tp_dealloc */
    0,                  /* tp_print */
    0,                  /* tp_getattr */
    0,                  /* tp_setattr */
    0,                  /* tp_compare */
    (reprfunc)wcsdpservice_repr,          /* tp_repr */
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
    wcsdpservice_doc,               /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    wcsdpservice_methods,               /* tp_methods */
    0,                  /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    wcsdpservice_initobj,             /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    wcsdpservice_new,             /* tp_new */
    PyObject_Del,               /* tp_free */
};



