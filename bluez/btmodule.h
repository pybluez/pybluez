#ifndef __btmodule_h__
#define __btmodule_h__

#include "Python.h"
#include <bluetooth/bluetooth.h>
#include <bluetooth/sdp.h>
#include <bluetooth/sdp_lib.h>
#include <stdint.h>
#ifdef Py_GIL_DISABLED
#include <stdatomic.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* The object holding a socket.  It holds some extra information,
   like the address family, which is used to decode socket address
   arguments properly. */

typedef struct {
        PyObject_HEAD
#ifdef Py_GIL_DISABLED
        _Atomic int sock_fd;
#else
        int sock_fd;
#endif
        int sock_family;
        int sock_type;
        int sock_proto;
        PyObject *(*errorhandler)(void);
#ifdef Py_GIL_DISABLED
        _Atomic double sock_timeout;
        _Atomic int is_listening_socket;
        _Atomic uint32_t sdp_record_handle;
        _Atomic(sdp_session_t *) sdp_session;
#else
        double sock_timeout;
    int is_listening_socket;
    uint32_t sdp_record_handle;
    sdp_session_t *sdp_session;
#endif
} PySocketSockObject;


#ifdef __cplusplus
}
#endif

extern PyObject *bluetooth_error;

#endif // __btmodule_h__
