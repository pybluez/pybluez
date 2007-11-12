#pragma once

typedef struct _WCL2CapIfPyObject WCL2CapIfPyObject;

struct _WCL2CapIfPyObject {
    PyObject_HEAD

    CL2CapIf * l2capif;
};

extern PyTypeObject wcl2capif_type;

