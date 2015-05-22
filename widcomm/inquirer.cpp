#include <windows.h>
#include <Python.h>

#include <BtIfDefinitions.h>
#include <BtIfClasses.h>
#include <com_error.h>
#include "util.h"
#include <port3.h>

#include "inquirer.hpp"

static inline void
dbg (const char *fmt, ...)
{
    return;
    va_list ap;
    va_start (ap, fmt);
    vfprintf (stderr, fmt, ap);
    va_end (ap);
}

static void 
dict_set_str_pyobj(PyObject *dict, const char *key, PyObject *valobj)
{
    PyObject *keyobj;
    keyobj = PyString_FromString (key);
    PyDict_SetItem (dict, keyobj, valobj);
    Py_DECREF (keyobj);
}

static void 
dict_set_strings(PyObject *dict, const char *key, const char *val)
{
    PyObject *keyobj, *valobj;
    keyobj = PyString_FromString (key);
    valobj = PyString_FromString (val);
    PyDict_SetItem (dict, keyobj, valobj);
    Py_DECREF (keyobj);
    Py_DECREF (valobj);
}

static void 
dict_set_str_long(PyObject *dict, const char *key, long val)
{
    PyObject *keyobj, *valobj;
    keyobj = PyString_FromString (key);
    valobj = PyInt_FromLong(val);
    PyDict_SetItem (dict, keyobj, valobj);
    Py_DECREF (keyobj);
    Py_DECREF (valobj);
}

WCInquirer::WCInquirer (PyObject *wcinq) 
{
    this->wcinq = wcinq;

    this->serverfd = socket (AF_INET, SOCK_STREAM, 0);
    this->threadfd = socket (AF_INET, SOCK_STREAM, 0);

    int status = SOCKET_ERROR;

    struct sockaddr_in saddr = { 0, };

    for (int i=0; i<10; i++) {
        this->sockport = 3000 + (unsigned short) (20000 *
                    (rand () / (RAND_MAX + 1.0)));

        saddr.sin_family = AF_INET;
        saddr.sin_port = htons (this->sockport);
        saddr.sin_addr.s_addr = inet_addr ("127.0.0.1");

        status = bind (this->serverfd, (struct sockaddr*) &saddr,
                sizeof (saddr));

        if (0 == status) break;
    }

    assert (0 == status);

    // instruct server socket to accept one connection
    status = listen (this->serverfd, 1);
    // TODO error checking

//    // connect the client socket to the server socket
//    status = connect (this->threadfd, (struct sockaddr*) &saddr, 
//            sizeof (saddr));
//    // TODO error checking

}

WCInquirer::~WCInquirer () 
{
    closesocket (this->threadfd);
}

int
WCInquirer::AcceptClient () 
{
    struct sockaddr_in useless;
    int useless_sz = sizeof (useless);
    this->threadfd = 
        accept (this->serverfd, (struct sockaddr*)&useless, &useless_sz);

    if (this->threadfd >= 0) {
        // put sockets into nonblocking mode
        unsigned long nonblocking = 1;
        ioctlsocket (this->threadfd, FIONBIO, &nonblocking);

        closesocket (this->serverfd);

        return 0;
    }

    return -1;
}

#pragma pack(push)
#pragma pack(1)

typedef struct {
    int msg_type;
    unsigned char bda[6];
    unsigned char devClass[3];
    unsigned char bdName[248];
    int bConnected;
} device_responded_msg_t;

void
WCInquirer::OnDeviceResponded (BD_ADDR bda, DEV_CLASS devClass, 
                BD_NAME bdName, BOOL bConnected)
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    device_responded_msg_t msg;
    memset (&msg, 0, sizeof (msg));

    msg.msg_type = DEVICE_RESPONDED;
    memcpy (msg.bda, bda, BD_ADDR_LEN);
    memcpy (msg.devClass, devClass, sizeof (devClass));
    memcpy (msg.bdName, bdName, strlen ((char*)bdName));
    msg.bConnected = bConnected;

    send (this->threadfd, reinterpret_cast <const char *> (&msg), 
            sizeof (msg), 0);
}

typedef struct {
    int msg_type;
    int success;
    short num_responses;
} inquiry_complete_msg_t;

void
WCInquirer::OnInquiryComplete (BOOL success, short num_responses)
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    inquiry_complete_msg_t msg;
    msg.msg_type = INQUIRY_COMPLETE;
    msg.success = success;
    msg.num_responses = num_responses;

    send (this->threadfd, reinterpret_cast <const char *> (&msg),
            sizeof (msg), 0);
}

typedef struct {
    int msg_type;
} discovery_complete_msg_t;

void
WCInquirer::OnDiscoveryComplete ()
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    discovery_complete_msg_t msg;
    msg.msg_type = DISCOVERY_COMPLETE;

    send (this->threadfd, reinterpret_cast <const char *> (&msg), 
            sizeof (msg), 0);
}

typedef struct {
    int msg_type;
    CBtIf::STACK_STATUS new_status;
} stack_status_change_msg_t;

void
WCInquirer::OnStackStatusChange (STACK_STATUS new_status)
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    stack_status_change_msg_t msg;
    msg.msg_type = STACK_STATUS_CHAGE;
    msg.new_status = new_status;

    send (this->threadfd, reinterpret_cast <const char *> (&msg), 
            sizeof (msg), 0);
}

#pragma pack(pop)

// ===================

typedef struct _WCInquirerPyObject WCInquirerPyObject;

struct _WCInquirerPyObject {
    PyObject_HEAD

    WCInquirer *inq;

    int readfd;
    int writefd;
};
PyDoc_STRVAR(wcinquirer_doc, "CBtIf wrapper");

extern PyTypeObject wcinquirer_type;

static PyObject *
get_sockport (PyObject *s)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;
    return PyInt_FromLong (self->inq->GetSockPort ());
}

static PyObject *
accept_client (PyObject *s)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;
    return PyInt_FromLong (self->inq->AcceptClient ());
}

static PyObject * 
start_inquiry (PyObject *s)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;
    BOOL success = TRUE;
    Py_BEGIN_ALLOW_THREADS
    success = self->inq->StartInquiry ();
    Py_END_ALLOW_THREADS
    if (success) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
	
}

static PyObject *
start_discovery (PyObject *s, PyObject *args)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;

    dbg ("%s:%d start_discovery\n", __FILE__, __LINE__);

    char *bdaddr_in = NULL;
    int bdaddr_in_len = 0;
    char *uuid_str = NULL;
    int uuid_str_len = 0;
    BD_ADDR bdaddr;

    if (!PyArg_ParseTuple (args, "s#|s#", &bdaddr_in, &bdaddr_in_len, 
                &uuid_str, &uuid_str_len)) return 0;

    if (bdaddr_in_len != BD_ADDR_LEN) {
        PyErr_SetString (PyExc_ValueError, "invalid bdaddr");
        return NULL;
    }
    memcpy (bdaddr, bdaddr_in, BD_ADDR_LEN);

    GUID uuid = { 0 };
    GUID *puuid = NULL;
    if (uuid_str) {
        PyWidcomm::str2uuid (uuid_str, &uuid);
        puuid = &uuid;
    }

    BOOL result;
    Py_BEGIN_ALLOW_THREADS
    result = self->inq->StartDiscovery (bdaddr, puuid);
    Py_END_ALLOW_THREADS
   
    if (result) Py_RETURN_TRUE;
    else Py_RETURN_FALSE;
}

static PyObject *
is_device_ready (PyObject *s)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;
    dbg ("IsDeviceReady: %d\n", (self->inq->IsDeviceReady ()));
    if (self->inq->IsDeviceReady ()) Py_RETURN_TRUE;
    else Py_RETURN_FALSE;
}

static PyObject *
is_stack_server_up (PyObject *s)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;
    if (self->inq->IsStackServerUp ()) Py_RETURN_TRUE;
    else Py_RETURN_FALSE;
}

static PyObject * 
get_local_device_name (PyObject *s)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;
    BD_NAME name;
    if (self->inq->GetLocalDeviceName (&name)) {
        return PyString_FromString ( (const char *)name);
    } else {
        Py_RETURN_NONE;
    }
}

static PyObject *
get_local_device_version_info (PyObject *s)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;
    Py_RETURN_NONE;
//    DEV_VER_INFO info;
//    BOOL success = self->inq->GetLocalDeviceVersionInfo (&info);
//    if (success) {
//        return Py_BuildValue ("s#BHBHH", 
//                info.bd_addr, 6, 
//                info.hci_version,
//                info.hci_revision,
//                info.lmp_version,
//                info.manufacturer,
//                info.lmp_sub_version);
//    } else {
//        Py_RETURN_NONE;
//    }
}

#define MAX_SDP_DISCOVERY_RECORDS 2000

static PyObject *
read_discovery_records (PyObject *s, PyObject *args)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;

    UINT8 *bdaddr_in = NULL;
    int bdaddr_in_len = 0;
    char *uuid_str = NULL;
    int uuid_str_len = 0;
    BD_ADDR bdaddr;

    if (!PyArg_ParseTuple (args, "s#|s#", &bdaddr_in, &bdaddr_in_len, 
                &uuid_str, &uuid_str_len)) return 0;

    if (bdaddr_in_len != BD_ADDR_LEN) {
        PyErr_SetString (PyExc_ValueError, "invalid bdaddr");
        return NULL;
    }
    memcpy (bdaddr, bdaddr_in, BD_ADDR_LEN);

    int nrecords = 0;

    CSdpDiscoveryRec *records = new CSdpDiscoveryRec[MAX_SDP_DISCOVERY_RECORDS];

    if (uuid_str) {
        dbg ("filtering by uuid %s\n", uuid_str);
        GUID uuid = { 0 };
        PyWidcomm::str2uuid (uuid_str, &uuid);

        nrecords = self->inq->ReadDiscoveryRecords (bdaddr, 
                MAX_SDP_DISCOVERY_RECORDS,
                records,
                &uuid);
    } else {
        dbg ("no uuid specified.\n");
        nrecords = self->inq->ReadDiscoveryRecords (bdaddr, 
                MAX_SDP_DISCOVERY_RECORDS,
                records);
        dbg ("nrecords: %d\n", nrecords);
    }

    char bdaddr_str[18];
    sprintf_s (bdaddr_str, sizeof(bdaddr_str), "%02X:%02X:%02X:%02X:%02X:%02X",
            bdaddr_in[0], bdaddr_in[1], bdaddr_in[2], 
            bdaddr_in[3], bdaddr_in[4], bdaddr_in[5]);

    PyObject *result = PyList_New (nrecords);
    for (int i=0; i<nrecords; i++) {
        PyObject *dict = PyDict_New ();

        // host name offering the service
        dict_set_strings (dict, "host", bdaddr_str);

        // service name
        dict_set_strings (dict, "name", records[i].m_service_name);

        // protocol and port number
        UINT8 scn;
        UINT16 psm;
        if (records[i].FindRFCommScn (&scn)) {
            dict_set_strings (dict, "protocol", "RFCOMM");
            dict_set_str_long (dict, "port", scn);
        } else if (records[i].FindL2CapPsm (&psm)) {
            dict_set_strings (dict, "protocol", "L2CAP");
            dict_set_str_long (dict, "port", psm);
        } else {
            dict_set_strings (dict, "protocol", "UNKNOWN");
            dict_set_str_pyobj (dict, "port", Py_None);
        }

        // service description
        SDP_DISC_ATTTR_VAL desc;
        if (records[i].FindAttribute (0x0101, &desc) &&
            desc.num_elem > 0 && 
            desc.elem[0].type == ATTR_TYPE_ARRAY) {
            dict_set_strings (dict, "description", 
                    (char*)desc.elem[0].val.array);
        } else {
            dict_set_strings (dict, "description", "");
        }

        dict_set_strings (dict, "provider", "");

        PyObject *profiles_list = PyList_New (0);
        dict_set_str_pyobj (dict, "profiles", profiles_list);
        Py_DECREF (profiles_list);

        dict_set_strings (dict, "service-id", "");

        // service class list
        PyObject *uuid_list = PyList_New (0);
//        SDP_DISC_ATTTR_VAL service_classes;
//        if (records[i].FindAttribute (0x0001, &service_classes)) {
//
//            printf ("service-classes: %d\n", desc.num_elem);
//            for (int j=0; j<desc.num_elem; j++) {
//                if (desc.elem[j].type == ATTR_TYPE_UUID ||
//                    desc.elem[j].type == ATTR_TYPE_ARRAY) {
//                    printf ("   array len: %d\n", desc.elem[j].len);
//                    unsigned char *u = desc.elem[j].val.array;
//                    char buf[255];
//                    memset (buf, 0, sizeof (buf));
//                    memcpy (buf, desc.elem[j].val.array, desc.elem[j].len);
//                    sprintf (buf, 
//        "%02X%02X%02X%02X-%02X%02X-%02X%02X-%02X%02X-%02X%02X%02X%02X%02X%02X",
//                            u[0], u[1], u[2], u[3],
//                            u[4], u[5], u[6], u[7],
//                            u[8], u[9], u[10], u[11],
//                            u[12], u[13], u[14], u[15]);
//                    printf ("%s\n", buf);
//                    PyObject *uuid_pyobj = PyString_FromString (buf);
//                    PyList_Append (uuid_list, uuid_pyobj);
//                    Py_DECREF (uuid_pyobj);
//                } else {
//                    printf ("     elem type: %d\n", desc.elem[j].type);
//                }
//            }
//        }
        dict_set_str_pyobj (dict, "service-classes", uuid_list);
        Py_DECREF (uuid_list);
        
        PyList_SetItem (result, i, dict);
    }

    delete [] records;

    return result;
}

static PyObject *
get_remote_device_info (PyObject *s, PyObject *args)
{
    // TODO
    Py_RETURN_NONE;
}

static PyObject *
get_next_remote_device_info (PyObject *s, PyObject *args)
{
    // TODO
    Py_RETURN_NONE;
}

static PyObject *
get_local_device_address (PyObject *s)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;
    BOOL result = self->inq->GetLocalDeviceInfo ();
    if (result) {
        return Py_BuildValue ("s", self->inq->m_BdName);
    } else {
        Py_RETURN_NONE;
    }
}

static PyObject *
get_btw_version_info (PyObject *s)
{
    WCInquirerPyObject *self = (WCInquirerPyObject*) s;
    char buf[MAX_PATH];
    BOOL result = self->inq->GetBTWVersionInfo (buf, MAX_PATH);
    if (result) {
        return PyString_FromString (buf);
    } else {
        Py_RETURN_NONE;
    }
}

static PyMethodDef wcinquirer_methods[] = {
    { "get_sockport", (PyCFunction) get_sockport, METH_NOARGS, "" },
    { "accept_client", (PyCFunction) accept_client, METH_NOARGS, "" },
    { "start_inquiry", (PyCFunction)start_inquiry, METH_NOARGS, "" },
    { "start_discovery", (PyCFunction)start_discovery, METH_VARARGS, "" },
    { "is_device_ready", (PyCFunction)is_device_ready, METH_NOARGS, "" },
    { "is_stack_server_up", (PyCFunction)is_stack_server_up, METH_NOARGS, "" },
    { "get_local_device_name", 
        (PyCFunction)get_local_device_name, METH_NOARGS, "" },
    { "get_local_device_version_info", 
        (PyCFunction)get_local_device_version_info, METH_NOARGS, ""},
    { "read_discovery_records",
        (PyCFunction)read_discovery_records, METH_VARARGS, "" },
    { "get_remote_device_info",
        (PyCFunction)get_remote_device_info, METH_VARARGS, "" },
    { "get_next_remote_device_info",
        (PyCFunction)get_next_remote_device_info, METH_VARARGS, "" },
    { "get_local_device_address",
        (PyCFunction)get_local_device_address, METH_NOARGS, "" },
    { "get_btw_version_info",
        (PyCFunction)get_btw_version_info, METH_NOARGS, "" },
    { NULL, NULL }
};

static PyObject *
wcinquirer_repr(WCInquirerPyObject *s)
{
    return PyString_FromString("_WCInquirer object");
}

static PyObject *
wcinquirer_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *newobj;

    newobj = type->tp_alloc(type, 0);
    if (newobj != NULL) {
        WCInquirerPyObject *self = (WCInquirerPyObject *)newobj;
        self->inq = NULL;
    }
    return newobj;
}

static void
wcinquirer_dealloc(WCInquirerPyObject *self)
{
    if (self->inq) {
        delete self->inq;
        self->inq = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

int
wcinquirer_initobj(PyObject *s, PyObject *args, PyObject *kwds)
{
    WCInquirerPyObject *self = (WCInquirerPyObject *)s;

    self->inq = new WCInquirer (s);

    return 0;
}

/* Type object for socket objects. */
PyTypeObject wcinquirer_type = {
#if PY_MAJOR_VERSION < 3
    PyObject_HEAD_INIT(0)   /* Must fill in type value later */
    0,                  /* ob_size */
#else
    PyVarObject_HEAD_INIT(NULL, 0)   /* Must fill in type value later */
#endif
    "_widcomm._WCInquirer",            /* tp_name */
    sizeof(WCInquirerPyObject),     /* tp_basicsize */
    0,                  /* tp_itemsize */
    (destructor)wcinquirer_dealloc,     /* tp_dealloc */
    0,                  /* tp_print */
    0,                  /* tp_getattr */
    0,                  /* tp_setattr */
    0,                  /* tp_compare */
    (reprfunc)wcinquirer_repr,          /* tp_repr */
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
    wcinquirer_doc,               /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    wcinquirer_methods,               /* tp_methods */
    0,                  /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    wcinquirer_initobj,             /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    wcinquirer_new,             /* tp_new */
    PyObject_Del,               /* tp_free */
};
