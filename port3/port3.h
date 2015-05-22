
#if PY_MAJOR_VERSION >= 3
    #define PyInt_FromLong PyLong_FromLong
    #define PyString_FromString PyUnicode_FromString
    #define PyString_FromStringAndSize PyBytes_FromStringAndSize
    #define _PyString_Resize _PyBytes_Resize
    #define PyString_AS_STRING PyBytes_AS_STRING
    #define PyInt_AsLong PyLong_AsLong
    #define PyString_AsString PyBytes_AsString
    #define PyInt_Check PyLong_Check
    #define PyInt_AS_LONG PyLong_AS_LONG
    #define BYTES_FORMAT_CHR "y#"
#else
    #ifndef Py_TYPE
        #define Py_TYPE(ob) (((PyObject*)(ob))->ob_type)
    #endif
    #define BYTES_FORMAT_CHR "s#"
#endif
