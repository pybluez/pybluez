#include <windows.h>

#ifndef _BTWLIB
#error "_BTWLIB is not defined"
#endif

#include <Python.h>

#include <BtIfDefinitions.h>
#include <BtIfClasses.h>
#include <com_error.h>

#include "inquirer.hpp"
#include "rfcommport.hpp"
#include "l2capconn.hpp"

extern PyTypeObject wcinquirer_type;
extern PyTypeObject wcrfcommport_type;
extern PyTypeObject wcrfcommif_type;
extern PyTypeObject wcl2capif_type;
extern PyTypeObject wcl2capconn_type;
extern PyTypeObject wcsdpservice_type;

static PyMethodDef widcomm_methods[] = {
    { NULL, NULL }
};

extern "C" {

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC
init_widcomm(void)
{
    PyObject *m;

    wcinquirer_type.ob_type   = &PyType_Type;
    wcrfcommport_type.ob_type = &PyType_Type;
    wcrfcommif_type.ob_type   = &PyType_Type;
    wcl2capif_type.ob_type    = &PyType_Type;
    wcl2capconn_type.ob_type    = &PyType_Type;
    wcsdpservice_type.ob_type = &PyType_Type;

    m = Py_InitModule("_widcomm", widcomm_methods);

    // inquirer
    Py_INCREF((PyObject *)&wcinquirer_type);
    if (PyModule_AddObject(m, "_WCInquirer", 
                (PyObject *)&wcinquirer_type) != 0) {
        return;
    }

    // rfcomm port
    Py_INCREF((PyObject *)&wcrfcommport_type);
    if (PyModule_AddObject(m, "_WCRfCommPort", 
                (PyObject *)&wcrfcommport_type) != 0) {
        return;
    }

    // rfcomm if
    Py_INCREF((PyObject *)&wcrfcommif_type);
    if (PyModule_AddObject(m, "_WCRfCommIf", 
                (PyObject *)&wcrfcommif_type) != 0) {
        return;
    }

    // l2cap if
    Py_INCREF((PyObject *)&wcl2capif_type);
    if (PyModule_AddObject(m, "_WCL2CapIf", 
                (PyObject *)&wcl2capif_type) != 0) {
        return;
    }

    // l2cap conn
    Py_INCREF((PyObject *)&wcl2capconn_type);
    if (PyModule_AddObject(m, "_WCL2CapConn", 
                (PyObject *)&wcl2capconn_type) != 0) {
        return;
    }

    // sdp service advertisement
    Py_INCREF((PyObject *)&wcsdpservice_type);
    if (PyModule_AddObject(m, "_WCSdpService", 
                (PyObject *)&wcsdpservice_type) != 0) {
        return;
    }
#else
    PyMODINIT_FUNC
    PyInit__widcomm(void)
    {
        PyObject *m;

        Py_TYPE(&wcinquirer_type)   = &PyType_Type;
        Py_TYPE(&wcrfcommport_type) = &PyType_Type;
        Py_TYPE(&wcrfcommif_type)   = &PyType_Type;
        Py_TYPE(&wcl2capif_type)    = &PyType_Type;
        Py_TYPE(&wcl2capconn_type)  = &PyType_Type;
        Py_TYPE(&wcsdpservice_type) = &PyType_Type;

        //m = Py_InitModule("_widcomm", widcomm_methods);
        static struct PyModuleDef moduledef = {
            PyModuleDef_HEAD_INIT,
            "_widcomm",
            NULL,
            -1,
            widcomm_methods,
            NULL,
            NULL,
            NULL,
            NULL
        };
        m = PyModule_Create(&moduledef);

        // inquirer
        Py_INCREF((PyObject *)&wcinquirer_type);
        if (PyModule_AddObject(m, "_WCInquirer",
                    (PyObject *)&wcinquirer_type) != 0) {
            return NULL;
        }

        // rfcomm port
        Py_INCREF((PyObject *)&wcrfcommport_type);
        if (PyModule_AddObject(m, "_WCRfCommPort",
                    (PyObject *)&wcrfcommport_type) != 0) {
            return NULL;
        }

        // rfcomm if
        Py_INCREF((PyObject *)&wcrfcommif_type);
        if (PyModule_AddObject(m, "_WCRfCommIf",
                    (PyObject *)&wcrfcommif_type) != 0) {
            return NULL;
        }

        // l2cap if
        Py_INCREF((PyObject *)&wcl2capif_type);
        if (PyModule_AddObject(m, "_WCL2CapIf",
                    (PyObject *)&wcl2capif_type) != 0) {
            return NULL;
        }

        // l2cap conn
        Py_INCREF((PyObject *)&wcl2capconn_type);
        if (PyModule_AddObject(m, "_WCL2CapConn",
                    (PyObject *)&wcl2capconn_type) != 0) {
            return NULL;
        }

        // sdp service advertisement
        Py_INCREF((PyObject *)&wcsdpservice_type);
        if (PyModule_AddObject(m, "_WCSdpService",
                    (PyObject *)&wcsdpservice_type) != 0) {
            return NULL;
        }

#endif

#define ADD_INT_CONST(m, a) PyModule_AddIntConstant(m, #a, a)
    ADD_INT_CONST(m, RFCOMM_DEFAULT_MTU);

    // CRfCommPort::PORT_RETURN_CODE enum
    PyModule_AddIntConstant(m, "RFCOMM_SUCCESS", CRfCommPort::SUCCESS);
    PyModule_AddIntConstant(m, "RFCOMM_ALREADY_OPENED", CRfCommPort::ALREADY_OPENED);
    PyModule_AddIntConstant(m, "RFCOMM_NOT_OPENED", CRfCommPort::NOT_OPENED);
    PyModule_AddIntConstant(m, "RFCOMM_HANDLE_ERROR", CRfCommPort::HANDLE_ERROR);
    PyModule_AddIntConstant(m, "RFCOMM_LINE_ERR", CRfCommPort::LINE_ERR);
    PyModule_AddIntConstant(m, "RFCOMM_START_FAILED", CRfCommPort::START_FAILED);
    PyModule_AddIntConstant(m, "RFCOMM_PAR_NEG_FAILED", CRfCommPort::PAR_NEG_FAILED);
    PyModule_AddIntConstant(m, "RFCOMM_PORT_NEG_FAILED", CRfCommPort::PORT_NEG_FAILED);
    PyModule_AddIntConstant(m, "RFCOMM_PEER_CONNECTION_FAILED", CRfCommPort::PEER_CONNECTION_FAILED);
    PyModule_AddIntConstant(m, "RFCOMM_PEER_TIMEOUT", CRfCommPort::PEER_TIMEOUT);
    PyModule_AddIntConstant(m, "RFCOMM_INVALID_PARAMETER", CRfCommPort::INVALID_PARAMETER);
    PyModule_AddIntConstant(m, "RFCOMM_UNKNOWN_ERROR", CRfCommPort::UNKNOWN_ERROR);

    ADD_INT_CONST (m, PORT_EV_RXFLAG);
    ADD_INT_CONST (m, PORT_EV_TXEMPTY);
    ADD_INT_CONST (m, PORT_EV_CTS);
    ADD_INT_CONST (m, PORT_EV_DSR);
    ADD_INT_CONST (m, PORT_EV_RLSD);
    ADD_INT_CONST (m, PORT_EV_BREAK);
    ADD_INT_CONST (m, PORT_EV_ERR);
    ADD_INT_CONST (m, PORT_EV_RING);
    ADD_INT_CONST (m, PORT_EV_CTSS);
    ADD_INT_CONST (m, PORT_EV_DSRS);
    ADD_INT_CONST (m, PORT_EV_RLSDS);
    ADD_INT_CONST (m, PORT_EV_OVERRUN);
    ADD_INT_CONST (m, PORT_EV_TXCHAR);
    ADD_INT_CONST (m, PORT_EV_CONNECTED);
    ADD_INT_CONST (m, PORT_EV_CONNECT_ERR);
    ADD_INT_CONST (m, PORT_EV_FC);
    ADD_INT_CONST (m, PORT_EV_FCS);

    ADD_INT_CONST (m, BTM_SEC_NONE);
    ADD_INT_CONST (m, BTM_SEC_IN_AUTHORIZE);
    ADD_INT_CONST (m, BTM_SEC_IN_AUTHENTICATE);
    ADD_INT_CONST (m, BTM_SEC_IN_ENCRYPT);
    ADD_INT_CONST (m, BTM_SEC_OUT_AUTHORIZE);
    ADD_INT_CONST (m, BTM_SEC_OUT_AUTHENTICATE);
    ADD_INT_CONST (m, BTM_SEC_OUT_ENCRYPT);
    ADD_INT_CONST (m, BTM_SEC_BOND);

    PyModule_AddIntConstant(m, "INQ_DEVICE_RESPONDED", 
            WCInquirer::DEVICE_RESPONDED);
    PyModule_AddIntConstant(m, "INQ_INQUIRY_COMPLETE", 
            WCInquirer::INQUIRY_COMPLETE);
    PyModule_AddIntConstant(m, "INQ_DISCOVERY_COMPLETE", 
            WCInquirer::DISCOVERY_COMPLETE);
    PyModule_AddIntConstant(m, "INQ_STACK_STATUS_CHANGE", 
            WCInquirer::STACK_STATUS_CHAGE);


    PyModule_AddIntConstant(m, "RFCOMM_DATA_RECEIVED", 
            WCRfCommPort::DATA_RECEIVED);
    PyModule_AddIntConstant(m, "RFCOMM_EVENT_RECEIVED", 
            WCRfCommPort::EVENT_RECEIVED);

    PyModule_AddIntConstant(m, "L2CAP_DATA_RECEIVED", 
            WCL2CapConn::DATA_RECEIVED);
    PyModule_AddIntConstant(m, "L2CAP_INCOMING_CONNECTION", 
            WCL2CapConn::INCOMING_CONNECTION);
    PyModule_AddIntConstant(m, "L2CAP_REMOTE_DISCONNECTED", 
            WCL2CapConn::REMOTE_DISCONNECTED);
    PyModule_AddIntConstant(m, "L2CAP_CONNECTED", 
            WCL2CapConn::CONNECTED);

    ADD_INT_CONST (m, SDP_OK);
    ADD_INT_CONST (m, SDP_COULD_NOT_ADD_RECORD);
    ADD_INT_CONST (m, SDP_INVALID_RECORD);
    ADD_INT_CONST (m, SDP_INVALID_PARAMETERS);
#if PY_MAJOR_VERSION >= 3
    return m;
#endif
}

} // extern "C"
