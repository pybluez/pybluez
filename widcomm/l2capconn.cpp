#include <windows.h>
#include <Python.h>

#include <BtIfDefinitions.h>
#include <BtIfClasses.h>
#include <com_error.h>
#include <port3.h>

#include "l2capconn.hpp"
#include "l2capif.hpp"

static inline void
dbg (const char *fmt, ...)
{
    return;
    va_list ap;
    va_start (ap, fmt);
    vfprintf (stderr, fmt, ap);
    va_end (ap);
}

WCL2CapConn::WCL2CapConn (PyObject *pyobj) 
    : CL2CapConn () 
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

WCL2CapConn::~WCL2CapConn () 
{
    closesocket (this->threadfd);
}

int
WCL2CapConn::AcceptClient () 
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

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
WCL2CapConn::OnDataReceived (void *p_data, UINT16 len)
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    data_received_t msg;
    msg.msg_type = DATA_RECEIVED;
    msg.len = len;

    send (this->threadfd, reinterpret_cast <char *> (&msg), sizeof (msg), 0);
    send (this->threadfd, reinterpret_cast <char *> (p_data), len, 0);
}

void 
WCL2CapConn::OnIncomingConnection () 
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    int msg = INCOMING_CONNECTION;
    send (this->threadfd, reinterpret_cast <char *> (&msg), sizeof (msg), 0);
}

void 
WCL2CapConn::OnConnectPendingReceived () 
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    // TODO
}
void 
WCL2CapConn::OnConnected () 
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    int msg = CONNECTED;
    send (this->threadfd, reinterpret_cast <char *> (&msg), sizeof (msg), 0);
}
void 
WCL2CapConn::OnCongestionStatus (BOOL is_congested) 
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    // TODO
}
void 
WCL2CapConn::OnRemoteDisconnected (UINT16 reason) 
{
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    int msg = REMOTE_DISCONNECTED;
    send (this->threadfd, reinterpret_cast <char *> (&msg), sizeof (msg), 0);
}

#pragma pack(pop)

// ===================

typedef struct _WCL2CapConnPyObject WCL2CapConnPyObject;

struct _WCL2CapConnPyObject {
    PyObject_HEAD

    WCL2CapConn *l2cap;
};
PyDoc_STRVAR(wcl2capconn_doc, "CL2CapConn wrapper");

extern PyTypeObject wcl2capconn_type;

static PyObject *
get_sockport (PyObject *s)
{
    WCL2CapConnPyObject *self = (WCL2CapConnPyObject*) s;
    return PyInt_FromLong (self->l2cap->GetSockPort ());
}

static PyObject *
accept_client (PyObject *s)
{
    WCL2CapConnPyObject *self = (WCL2CapConnPyObject*) s;
    return PyInt_FromLong (self->l2cap->AcceptClient ());
}

static PyObject *
wc_listen (PyObject *s, PyObject *a)
{
    WCL2CapConnPyObject *self = (WCL2CapConnPyObject*) s;
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    if (! PyObject_IsInstance (a, (PyObject*)&wcl2capif_type)) {
        return NULL;
    }
    WCL2CapIfPyObject *l2cap_if = (WCL2CapIfPyObject*) a;
    BOOL result;
    Py_BEGIN_ALLOW_THREADS;
    result = self->l2cap->Listen (l2cap_if->l2capif);
    Py_END_ALLOW_THREADS;
    dbg ("    listen: %d\n", result);
    if (result) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *
wc_accept (PyObject *s, PyObject *args)
{
    WCL2CapConnPyObject *self = (WCL2CapConnPyObject*) s;
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    UINT16 desired_mtu = L2CAP_DEFAULT_MTU;
    if (!PyArg_ParseTuple (args, "|H", &desired_mtu)) return NULL;
    BOOL result;
    Py_BEGIN_ALLOW_THREADS;
    dbg ("   calling accept (%p)\n", self->l2cap);
    result = self->l2cap->Accept ();
    dbg ("   accept: %d\n", result);
    Py_END_ALLOW_THREADS;
    if (result) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *
wc_connect (PyObject *s, PyObject *args)
{
    WCL2CapConnPyObject *self = (WCL2CapConnPyObject*) s;
    WCL2CapIfPyObject *l2cap_if = NULL;

    char *bdaddr_in = NULL;
    int bdaddr_in_len;
    UINT16 desired_mtu = L2CAP_DEFAULT_MTU;;

    if(!PyArg_ParseTuple (args, "O!s#|H", 
                &wcl2capif_type, &l2cap_if,
                &bdaddr_in, &bdaddr_in_len,
                &desired_mtu)) 
        return NULL;

    if (bdaddr_in_len != BD_ADDR_LEN) {
        PyErr_SetString (PyExc_ValueError, "invalid bdaddr");
        return NULL;
    }

    BD_ADDR bdaddr;
    memcpy (bdaddr, bdaddr_in, BD_ADDR_LEN);

    BOOL result;
    Py_BEGIN_ALLOW_THREADS;
    result = self->l2cap->Connect (l2cap_if->l2capif, bdaddr, desired_mtu);
    Py_END_ALLOW_THREADS;

    return PyInt_FromLong (result);
}

static PyObject *
wc_disconnect (PyObject *s)
{
    WCL2CapConnPyObject *self = (WCL2CapConnPyObject*) s;
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);
    Py_BEGIN_ALLOW_THREADS;
    self->l2cap->Disconnect ();
    Py_END_ALLOW_THREADS;
    Py_RETURN_NONE;
}

static PyObject *
wc_remote_bd_addr (PyObject *s)
{
    WCL2CapConnPyObject *self = (WCL2CapConnPyObject*) s;
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    tBT_CONN_STATS connstats;
    if (!self->l2cap->GetConnectionStats (&connstats)) {
        Py_RETURN_NONE;
    }
    if (!connstats.bIsConnected) Py_RETURN_NONE;
    return Py_BuildValue ("s#", &self->l2cap->m_RemoteBdAddr, BD_ADDR_LEN);
}

static PyObject *
wc_write (PyObject *s, PyObject *args)
{
    _WCL2CapConnPyObject *self = (_WCL2CapConnPyObject*) s;
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    char *data = NULL;
    int datalen;
    if (!PyArg_ParseTuple (args, "s#", &data, &datalen)) return NULL;

    UINT16 written = 0;
    BOOL result;

    Py_BEGIN_ALLOW_THREADS;
    result = self->l2cap->Write (data, datalen, &written);
    Py_END_ALLOW_THREADS;

    return Py_BuildValue ("II", result, written);
}

static PyObject *
wc_get_connection_stats (PyObject *s)
{
    _WCL2CapConnPyObject *self = (_WCL2CapConnPyObject*) s;
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    tBT_CONN_STATS stats;
    memset (&stats, 0, sizeof (stats));
    BOOL result;
    Py_BEGIN_ALLOW_THREADS;
    result = self->l2cap->GetConnectionStats (&stats);
    Py_END_ALLOW_THREADS;
    return Py_BuildValue ("iIiIII", result, 
            stats.bIsConnected, stats.Rssi, stats.BytesSent,
            stats.BytesRcvd, stats.Duration);
}

static PyObject *
wc_switch_role (PyObject *s, PyObject *arg)
{
    _WCL2CapConnPyObject *self = (_WCL2CapConnPyObject*) s;
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    MASTER_SLAVE_ROLE new_role = 
        static_cast <MASTER_SLAVE_ROLE> (PyInt_AsLong (arg));
    BOOL result = self->l2cap->SwitchRole (new_role);
    return PyInt_FromLong (result);
}

static PyObject *
wc_set_link_supervision_timeout (PyObject *s, PyObject *arg)
{
    _WCL2CapConnPyObject *self = (_WCL2CapConnPyObject*) s;
    dbg ("%s:%d:%s\n", __FILE__, __LINE__, __FUNCTION__);

    UINT16 timeoutSlot = static_cast <UINT16> (PyInt_AsLong (arg));
    BOOL result = self->l2cap->SetLinkSupervisionTimeOut (timeoutSlot);
    return PyInt_FromLong (result);
}

static PyMethodDef wcl2capconn_methods[] = {
    { "get_sockport", (PyCFunction) get_sockport, METH_NOARGS, "" },
    { "accept_client", (PyCFunction) accept_client, METH_NOARGS, "" },
    { "listen", (PyCFunction) wc_listen, METH_O, "" },
    { "accept", (PyCFunction) wc_accept, METH_VARARGS, "" },
    { "connect", (PyCFunction) wc_connect, METH_VARARGS, "" },
    { "disconnect", (PyCFunction) wc_disconnect, METH_NOARGS, "" },
    { "remote_bd_addr", (PyCFunction) wc_remote_bd_addr, METH_NOARGS, "" },
    { "write", (PyCFunction)wc_write, METH_VARARGS, "" },
    { "get_connection_stats", (PyCFunction)wc_get_connection_stats, 
        METH_NOARGS, "" },
    { "switch_role", (PyCFunction)wc_switch_role, METH_O, "" },
    { "set_link_supervision_timeout", 
        (PyCFunction)wc_set_link_supervision_timeout, METH_O, "" },
    { NULL, NULL }
};

static PyObject *
wcl2capconn_repr(WCL2CapConnPyObject *s)
{
    return PyString_FromString("_WCL2CapConn object");
}

static PyObject *
wcl2capconn_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyObject *newobj;

    newobj = type->tp_alloc(type, 0);
    if (newobj != NULL) {
        WCL2CapConnPyObject *self = (WCL2CapConnPyObject *)newobj;
        self->l2cap = NULL;
    }
    return newobj;
}

static void
wcl2capconn_dealloc(WCL2CapConnPyObject *self)
{
    if (self->l2cap) {
        delete self->l2cap;
        self->l2cap = NULL;
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

int
wcl2capconn_initobj(PyObject *s, PyObject *args, PyObject *kwds)
{
    WCL2CapConnPyObject *self = (WCL2CapConnPyObject *)s;
    self->l2cap = new WCL2CapConn (s);
    return 0;
}

/* Type object for socket objects. */
PyTypeObject wcl2capconn_type = {
#if PY_MAJOR_VERSION < 3
    PyObject_HEAD_INIT(0)   /* Must fill in type value later */
    0,                  /* ob_size */
#else
    PyVarObject_HEAD_INIT(NULL, 0)   /* Must fill in type value later */
#endif
    "_widcomm._WCL2CapConn",            /* tp_name */
    sizeof(WCL2CapConnPyObject),     /* tp_basicsize */
    0,                  /* tp_itemsize */
    (destructor)wcl2capconn_dealloc,     /* tp_dealloc */
    0,                  /* tp_print */
    0,                  /* tp_getattr */
    0,                  /* tp_setattr */
    0,                  /* tp_compare */
    (reprfunc)wcl2capconn_repr,          /* tp_repr */
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
    wcl2capconn_doc,               /* tp_doc */
    0,                  /* tp_traverse */
    0,                  /* tp_clear */
    0,                  /* tp_richcompare */
    0,                  /* tp_weaklistoffset */
    0,                  /* tp_iter */
    0,                  /* tp_iternext */
    wcl2capconn_methods,               /* tp_methods */
    0,                  /* tp_members */
    0,                  /* tp_getset */
    0,                  /* tp_base */
    0,                  /* tp_dict */
    0,                  /* tp_descr_get */
    0,                  /* tp_descr_set */
    0,                  /* tp_dictoffset */
    wcl2capconn_initobj,             /* tp_init */
    PyType_GenericAlloc,            /* tp_alloc */
    wcl2capconn_new,             /* tp_new */
    PyObject_Del,               /* tp_free */
};

