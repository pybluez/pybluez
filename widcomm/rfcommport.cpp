#include <windows.h>
#include <Python.h>

#include <BtIfDefinitions.h>
#include <BtIfClasses.h>
#include <com_error.h>
#include <port3.h>

#include "rfcommport.hpp"

static inline void
dbg (const char *fmt, ...)
{
    return;
    va_list ap;
    va_start (ap, fmt);
    vfprintf (stderr, fmt, ap);
    va_end (ap);
}

WCRfCommPort::WCRfCommPort (PyObject *pyobj) 
    : CRfCommPort () 
{
    this->pyobj = pyobj;
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
}

WCRfCommPort::~WCRfCommPort () 
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    closesocket (this->threadfd);
}

int
WCRfCommPort::AcceptClient () 
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
    int len;
} data_received_t;

void
WCRfCommPort::OnDataReceived (void *p_data, UINT16 len)
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    data_received_t msg;
    msg.msg_type = DATA_RECEIVED;
    msg.len = len;

    send (this->threadfd, reinterpret_cast <char *> (&msg), sizeof (msg), 0);
    send (this->threadfd, reinterpret_cast <char *> (p_data), len, 0);
}

typedef struct {
    int msg_type;
    unsigned int event_code;
} event_received_msg_t;

void
WCRfCommPort::OnEventReceived (UINT32 event_code)
{
    dbg ("%s:%d event %u received\n", __FILE__, __LINE__, event_code);

    event_received_msg_t msg;
    msg.msg_type = EVENT_RECEIVED;
    msg.event_code = event_code;

    send (this->threadfd, reinterpret_cast <char *> (&msg), sizeof (msg), 0);
}

#pragma pack(pop)

// ===================

typedef struct _WCRfCommPortPyObject WCRfCommPortPyObject;

struct _WCRfCommPortPyObject {
    PyObject_HEAD

    WCRfCommPort *rfcp;
};
PyDoc_STRVAR(wcrfcommport_doc, "CRfCommPort wrapper");

extern PyTypeObject wcrfcommport_type;

static PyObject *
get_sockport (PyObject *s)
{
    WCRfCommPortPyObject *self = (WCRfCommPortPyObject*) s;
    return PyInt_FromLong (self->rfcp->GetSockPort ());
}

static PyObject *
accept_client (PyObject *s)
{
    WCRfCommPortPyObject *self = (WCRfCommPortPyObject*) s;
    return PyInt_FromLong (self->rfcp->AcceptClient ());
}

static PyObject *
wc_open_server (PyObject *s, PyObject *args)
{
    WCRfCommPortPyObject *self = (WCRfCommPortPyObject*) s;

    UINT8 scn;
    UINT16 desired_mtu = RFCOMM_DEFAULT_MTU;
    if (!PyArg_ParseTuple (args, "B|H", &scn, &desired_mtu)) return NULL;

    CRfCommPort::PORT_RETURN_CODE result = 
        self->rfcp->OpenServer (scn, desired_mtu);

    return PyInt_FromLong (result);
}

static PyObject *
wc_open_client (PyObject *s, PyObject *args)
{
    UINT8 scn;
    char *bdaddr_in = NULL;
    int bdaddr_in_len;
    UINT16 desired_mtu = RFCOMM_DEFAULT_MTU;

    if(!PyArg_ParseTuple (args, "Bs#|H", &scn, &bdaddr_in, &bdaddr_in_len,
                &desired_mtu)) 
        return NULL;

    if (bdaddr_in_len != BD_ADDR_LEN) {
        PyErr_SetString (PyExc_ValueError, "invalid bdaddr");
        return NULL;
    }

    BD_ADDR bdaddr;
    memcpy (bdaddr, bdaddr_in, BD_ADDR_LEN);

    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;

    CRfCommPort::PORT_RETURN_CODE result;
    Py_BEGIN_ALLOW_THREADS;
    result = self->rfcp->OpenClient (scn, bdaddr, desired_mtu);
    Py_END_ALLOW_THREADS;

    return PyInt_FromLong (result);
}

static PyObject *
wc_is_connected (PyObject *s)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    BD_ADDR remote_addr;
    if (self->rfcp->IsConnected (&remote_addr)) {
        return Py_BuildValue ("s#", &remote_addr, BD_ADDR_LEN);
    } else {
        Py_RETURN_NONE;
    }
}

static PyObject *
wc_close (PyObject *s)
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    self->rfcp->Close ();
    Py_RETURN_NONE;
}

static PyObject *
wc_set_flow_enabled (PyObject *s, PyObject *arg)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    int enable = PyInt_AsLong (arg);
    CRfCommPort::PORT_RETURN_CODE result = self->rfcp->SetFlowEnabled (enable);
    return PyInt_FromLong (result);
}

static PyObject *
wc_set_modem_signal (PyObject *s, PyObject *arg)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    UINT8 signal = static_cast <UINT8> (PyInt_AsLong (arg));
    CRfCommPort::PORT_RETURN_CODE result = self->rfcp->SetModemSignal (signal);
    return PyInt_FromLong (result);
}

static PyObject *
wc_get_modem_status (PyObject *s)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    UINT8 signal;
    CRfCommPort::PORT_RETURN_CODE result = self->rfcp->GetModemStatus (&signal);
    return Py_BuildValue ("ii", result, signal);
}

static PyObject *
wc_send_error (PyObject *s, PyObject *arg)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    UINT8 errors = static_cast <UINT8> (PyInt_AsLong (arg));
    CRfCommPort::PORT_RETURN_CODE result = self->rfcp->SendError (errors);
    return PyInt_FromLong (result);
}

static PyObject *
wc_purge (PyObject *s, PyObject *arg)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    UINT8 purge_flags = static_cast <UINT8> (PyInt_AsLong (arg));
    CRfCommPort::PORT_RETURN_CODE result = self->rfcp->Purge (purge_flags);
    return PyInt_FromLong (result);
}

static PyObject *
wc_write (PyObject *s, PyObject *args)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;

    char *data = NULL;
    int datalen;
    if (!PyArg_ParseTuple (args, "s#", &data, &datalen)) return NULL;

    UINT16 written = 0;
    CRfCommPort::PORT_RETURN_CODE status;

    Py_BEGIN_ALLOW_THREADS;
    status = self->rfcp->Write (data, datalen, &written);
    Py_END_ALLOW_THREADS;

    return Py_BuildValue ("II", status, written);
}

static PyObject *
wc_get_connection_stats (PyObject *s)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    tBT_CONN_STATS stats;
    memset (&stats, 0, sizeof (stats));
    CRfCommPort::PORT_RETURN_CODE result = 
        self->rfcp->GetConnectionStats (&stats);

    return Py_BuildValue ("iIiIII", result, 
            stats.bIsConnected,
            stats.Rssi,
            stats.BytesSent,
            stats.BytesRcvd,
            stats.Duration);
}

static PyObject *
wc_switch_role (PyObject *s, PyObject *arg)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    MASTER_SLAVE_ROLE new_role = 
        static_cast <MASTER_SLAVE_ROLE> (PyInt_AsLong (arg));
    BOOL result = self->rfcp->SwitchRole (new_role);
    return PyInt_FromLong (result);
}

static PyObject *
wc_set_link_supervision_timeout (PyObject *s, PyObject *arg)
{
    _WCRfCommPortPyObject *self = (_WCRfCommPortPyObject*) s;
    UINT16 timeoutSlot = static_cast <UINT16> (PyInt_AsLong (arg));
    CRfCommPort::PORT_RETURN_CODE result = 
        self->rfcp->SetLinkSupervisionTimeOut (timeoutSlot);
    return PyInt_FromLong (result);
}

static PyMethodDef wcrfcommport_methods[] = {
    { "get_sockport", (PyCFunction) get_sockport, METH_NOARGS, "" },
    { "accept_client", (PyCFunction) accept_client, METH_NOARGS, "" },
    { "open_server", (PyCFunction)wc_open_server, METH_VARARGS, "" },
    { "open_client", (PyCFunction)wc_open_client, METH_VARARGS, "" },
    { "close", (PyCFunction)wc_close, METH_NOARGS, "" },
    { "is_connected", (PyCFunction)wc_is_connected, METH_NOARGS, "" },
    { "set_flow_enabled", (PyCFunction)wc_set_flow_enabled, METH_O, "" },
    { "set_modem_signal", (PyCFunction)wc_set_modem_signal, METH_O, "" },
    { "get_modem_status", (PyCFunction)wc_get_modem_status, METH_NOARGS, "" },
    { "send_error", (PyCFunction)wc_send_error, METH_O, "" },
    { "purge", (PyCFunction)wc_purge, METH_O, "" },
    { "write", (PyCFunction)wc_write, METH_VARARGS, "" },
    { "get_connection_stats", (PyCFunction)wc_get_connection_stats, 
        METH_NOARGS, "" },
    { "switch_role", (PyCFunction)wc_switch_role, METH_O, "" },
    { "set_link_supervision_timeout", 
        (PyCFunction)wc_set_link_supervision_timeout, METH_O, "" },
    { NULL, NULL }
};

static PyObject *
wcrfcommport_repr(WCRfCommPortPyObject *s)
{
    return PyString_FromString("_WCRfCommPort object");
}

static PyObject *
wcrfcommport_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *newobj;

    newobj = type->tp_alloc(type, 0);
    if (newobj != NULL) {
        WCRfCommPortPyObject *self = (WCRfCommPortPyObject *)newobj;
        self->rfcp = NULL;
    }
    return newobj;
}

static void
wcrfcommport_dealloc(WCRfCommPortPyObject *self)
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    if (self->rfcp) {
        delete self->rfcp;
        self->rfcp = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

int
wcrfcommport_initobj(PyObject *s, PyObject *args, PyObject *kwds)
{
    WCRfCommPortPyObject *self = (WCRfCommPortPyObject *)s;
    self->rfcp = new WCRfCommPort (s);
    return 0;
}

/* Type object for socket objects. */
PyTypeObject wcrfcommport_type = {
#if PY_MAJOR_VERSION < 3
    PyObject_HEAD_INIT(0)   /* Must fill in type value later */
    0,                  /* ob_size */
#else
    PyVarObject_HEAD_INIT(NULL, 0)   /* Must fill in type value later */
#endif
    "_widcomm._WCRfCommPort",            /* tp_name */
    sizeof(WCRfCommPortPyObject),     /* tp_basicsize */
    0,                  /* tp_itemsize */
    (destructor)wcrfcommport_dealloc,     /* tp_dealloc */
    0,                  /* tp_print */
    0,                  /* tp_getattr */
    0,                  /* tp_setattr */
    0,                  /* tp_compare */
    (reprfunc)wcrfcommport_repr,          /* tp_repr */
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
    wcrfcommport_doc,               /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    wcrfcommport_methods,               /* tp_methods */
    0,                  /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    wcrfcommport_initobj,             /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    wcrfcommport_new,             /* tp_new */
    PyObject_Del,               /* tp_free */
};

