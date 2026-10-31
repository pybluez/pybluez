#ifndef UNICODE
#define UNICODE
#endif

#define PY_SSIZE_T_CLEAN 1

#include <winsock2.h>
#include <ws2bth.h>
#include <BluetoothAPIs.h>

#include <Python.h>

#include <initguid.h>
#include <wchar.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>


static PyObject *
msbt_error(int error)
{
    return PyErr_SetExcFromWindowsErr(PyExc_OSError,
                                    error ? error : ERROR_GEN_FAILURE);
}

/* The one process-owned Winsock reference is shared by all interpreters.
 * The lock never encloses Python C API calls or thread-state attachment. */
static SRWLOCK winsock_init_lock = SRWLOCK_INIT;
static int winsock_started = 0;

static int
ensure_winsock(void)
{
    int status = 0;
    WSADATA data;
    Py_BEGIN_ALLOW_THREADS
    AcquireSRWLockExclusive(&winsock_init_lock);
    if (!winsock_started) {
        status = WSAStartup(MAKEWORD(2, 2), &data);
        if (status == 0) {
            winsock_started = 1;
        }
    }
    ReleaseSRWLockExclusive(&winsock_init_lock);
    Py_END_ALLOW_THREADS
    if (status != 0) {
        msbt_error(status);
        return 0;
    }
    return 1;
}

static int
socket_value(PyObject *value, SOCKET *socket_out)
{
    PyObject *index = PyNumber_Index(value);
    unsigned long long number;
    if (index == NULL) {
        return 0;
    }
    number = PyLong_AsUnsignedLongLong(index);
    Py_DECREF(index);
    if (PyErr_Occurred()) {
        return 0;
    }
    if (number > (unsigned long long)UINTPTR_MAX) {
        PyErr_SetString(PyExc_OverflowError, "socket handle does not fit this platform");
        return 0;
    }
    *socket_out = (SOCKET)(uintptr_t)number;
    if (*socket_out == INVALID_SOCKET) {
        msbt_error(WSAENOTSOCK);
        return 0;
    }
    return 1;
}

static PyObject *
socket_number(SOCKET value)
{
    return PyLong_FromUnsignedLongLong((unsigned long long)(uintptr_t)value);
}

/* Keep only immutable, owned storage while the thread state is detached.
 * Exporting a mutable buffer prevents resize; its owner lock protects the copy. */
static PyObject *
owned_buffer(Py_buffer *view)
{
    PyObject *result;
    PyObject *owner = view->obj;
    if (owner == NULL) {
        result = PyBytes_FromStringAndSize(view->buf, view->len);
        PyBuffer_Release(view);
        return result;
    }
    if (PyBytes_Check(owner)) {
        Py_INCREF(owner);
        result = owner;
        if (view->buf != PyBytes_AS_STRING(owner) ||
                view->len != PyBytes_GET_SIZE(owner)) {
            Py_DECREF(result);
            result = PyBytes_FromStringAndSize(view->buf, view->len);
        }
    } else {
        while (PyMemoryView_Check(owner) && PyMemoryView_GET_BASE(owner)) {
            owner = PyMemoryView_GET_BASE(owner);
        }
#ifdef Py_GIL_DISABLED
        Py_BEGIN_CRITICAL_SECTION(owner);
#endif
        result = PyBytes_FromStringAndSize(view->buf, view->len);
#ifdef Py_GIL_DISABLED
        Py_END_CRITICAL_SECTION();
#endif
    }
    PyBuffer_Release(view);
    return result;
}


static void
ba2str( BTH_ADDR ba, char *addr, size_t len )
{
    int i;
    unsigned char bytes[6];
    for( i=0; i<6; i++ ) {
        bytes[5-i] = (unsigned char) ((ba >> (i*8)) & 0xff);
    }
    sprintf_s( addr, len, "%02X:%02X:%02X:%02X:%02X:%02X",
            bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5] );
}

static void
ba2wstr( BTH_ADDR ba, wchar_t *addr, size_t len )
{
    int i;
    unsigned char bytes[6];
    for( i=0; i<6; i++ ) {
        bytes[5-i] = (unsigned char) ((ba >> (i*8)) & 0xff);
    }
    swprintf_s( addr, len, L"%02X:%02X:%02X:%02X:%02X:%02X",
            bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5] );
}

static PyObject *
msbt_initwinsock(PyObject *self, PyObject *unused)
{
    if (!ensure_winsock()) {
        return NULL;
    }
    Py_RETURN_NONE;
}
PyDoc_STRVAR(msbt_initwinsock_doc, "TODO");

static int
str2uuid(const char *text, GUID *uuid)
{
    unsigned char bytes[16];
    int i, count = 0, nibble = -1, value;
    if (strlen(text) != 36 || text[8] != '-' || text[13] != '-' ||
            text[18] != '-' || text[23] != '-') goto invalid;
    for (i = 0; i < 36; ++i) {
        unsigned char c = (unsigned char)text[i];
        if (i == 8 || i == 13 || i == 18 || i == 23) continue;
        if (c >= '0' && c <= '9') value = c - '0';
        else if (c >= 'a' && c <= 'f') value = c - 'a' + 10;
        else if (c >= 'A' && c <= 'F') value = c - 'A' + 10;
        else goto invalid;
        if (nibble < 0) nibble = value;
        else { bytes[count++] = (unsigned char)((nibble << 4) | value); nibble = -1; }
    }
    uuid->Data1 = ((DWORD)bytes[0] << 24) | ((DWORD)bytes[1] << 16) |
                  ((DWORD)bytes[2] << 8) | bytes[3];
    uuid->Data2 = (WORD)((bytes[4] << 8) | bytes[5]);
    uuid->Data3 = (WORD)((bytes[6] << 8) | bytes[7]);
    memcpy(uuid->Data4, bytes + 8, 8);
    return 1;
invalid:
    PyErr_SetString(PyExc_ValueError, "UUID must contain 32 hexadecimal digits in canonical 128-bit form");
    return 0;
}

// ====================== SOCKET FUNCTIONS ========================

/* Each descriptor is caller-owned. Public BluetoothSocket methods hold a
 * separate native descriptor lease for the entire operation. */
#define MSBT_SOCKET_CALL(result, expression, saved_error) do { \
    Py_BEGIN_ALLOW_THREADS \
    (result) = (expression); \
    (saved_error) = WSAGetLastError(); \
    Py_END_ALLOW_THREADS \
} while (0)

static int
address_value(PyObject *value, SOCKADDR_BTH *address, int allow_any)
{
    wchar_t *text;
    Py_ssize_t length;
    int size = sizeof(*address);
    int result, error;
    ZeroMemory(address, sizeof(*address));
    address->addressFamily = AF_BTH;
    if (value == Py_None && allow_any) {
        return 1;
    }
    text = PyUnicode_AsWideCharString(value, &length);
    if (text == NULL) {
        return 0;
    }
    if (allow_any && length == 0) {
        PyMem_Free(text);
        return 1;
    }
    if ((Py_ssize_t)wcslen(text) != length) {
        PyMem_Free(text);
        PyErr_SetString(PyExc_ValueError, "embedded null in Bluetooth address");
        return 0;
    }
    result = WSAStringToAddressW(text, AF_BTH, NULL,
                               (LPSOCKADDR)address, &size);
    error = result == SOCKET_ERROR ? WSAGetLastError() : 0;
    PyMem_Free(text);
    if (result == SOCKET_ERROR) {
        msbt_error(error);
        return 0;
    }
    return 1;
}

static PyObject *
msbt_socket(PyObject *self, PyObject *args)
{
    int type, protocol, error;
    SOCKET descriptor;
    PyObject *result;
    if (!PyArg_ParseTuple(args, "ii:socket", &type, &protocol)) return NULL;
    if (!ensure_winsock()) return NULL;
    MSBT_SOCKET_CALL(descriptor, socket(AF_BTH, type, protocol), error);
    if (descriptor == INVALID_SOCKET) return msbt_error(error);
    result = socket_number(descriptor);
    if (result == NULL) closesocket(descriptor);
    return result;
}
PyDoc_STRVAR(msbt_socket_doc, "Create a native Windows Bluetooth socket.");

static PyObject *
msbt_bind(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object, *text;
    SOCKET descriptor;
    SOCKADDR_BTH address;
    int port, status, error;
    if (!PyArg_ParseTuple(args, "OOi:bind", &descriptor_object, &text, &port)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    if (!address_value(text, &address, 1)) return NULL;
    address.port = (ULONG)port;
    MSBT_SOCKET_CALL(status, bind(descriptor, (SOCKADDR *)&address, sizeof(address)), error);
    if (status == SOCKET_ERROR) return msbt_error(error);
    Py_RETURN_NONE;
}
PyDoc_STRVAR(msbt_bind_doc, "Bind a native Bluetooth socket to an address and port.");

static PyObject *
msbt_listen(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object;
    SOCKET descriptor;
    int backlog, status, error;
    if (!PyArg_ParseTuple(args, "Oi:listen", &descriptor_object, &backlog)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    MSBT_SOCKET_CALL(status, listen(descriptor, backlog), error);
    if (status == SOCKET_ERROR) return msbt_error(error);
    Py_RETURN_NONE;
}
PyDoc_STRVAR(msbt_listen_doc, "Listen on a bound Bluetooth socket.");

static PyObject *
msbt_accept(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object, *number, *result;
    SOCKET descriptor, client;
    SOCKADDR_BTH address = {0};
    int size = sizeof(address), error;
    char text[18];
    if (!PyArg_ParseTuple(args, "O:accept", &descriptor_object)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    MSBT_SOCKET_CALL(client, accept(descriptor, (SOCKADDR *)&address, &size), error);
    if (client == INVALID_SOCKET) return msbt_error(error);
    if (address.addressFamily != AF_BTH || size < sizeof(address)) {
        closesocket(client);
        return msbt_error(WSAEAFNOSUPPORT);
    }
    ba2str(address.btAddr, text, sizeof(text));
    number = socket_number(client);
    if (number == NULL) {
        closesocket(client);
        return NULL;
    }
    result = Py_BuildValue("Nsk", number, text, address.port);
    if (result == NULL) closesocket(client);
    return result;
}
PyDoc_STRVAR(msbt_accept_doc, "Accept a Bluetooth socket, returning its full-width handle and peer.");

static PyObject *
msbt_connect(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object, *text;
    SOCKET descriptor;
    SOCKADDR_BTH address;
    int port, status, error;
    if (!PyArg_ParseTuple(args, "OOi:connect", &descriptor_object, &text, &port)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    if (!address_value(text, &address, 0)) return NULL;
    address.port = (ULONG)port;
    MSBT_SOCKET_CALL(status, connect(descriptor, (SOCKADDR *)&address, sizeof(address)), error);
    if (status == SOCKET_ERROR) return msbt_error(error);
    Py_RETURN_NONE;
}
PyDoc_STRVAR(msbt_connect_doc, "Connect a Bluetooth socket to an address and port.");

static PyObject *
msbt_send(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object, *owned;
    SOCKET descriptor;
    Py_buffer view;
    const char *data;
    int flags = 0, length, sent, error;
    if (!PyArg_ParseTuple(args, "Os*|i:send", &descriptor_object, &view, &flags)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) {
        PyBuffer_Release(&view);
        return NULL;
    }
    if (view.len > INT_MAX) {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_OverflowError, "send buffer exceeds Winsock length range");
        return NULL;
    }
    length = (int)view.len;
    owned = owned_buffer(&view);
    if (owned == NULL) return NULL;
    data = PyBytes_AS_STRING(owned);
    MSBT_SOCKET_CALL(sent, send(descriptor, data, length, flags), error);
    Py_DECREF(owned);
    if (sent == SOCKET_ERROR) return msbt_error(error);
    return PyLong_FromLong(sent);
}
PyDoc_STRVAR(msbt_send_doc, "Send immutable or snapshotted buffer data through Winsock.");

static PyObject *
msbt_recv(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object, *result;
    SOCKET descriptor;
    Py_ssize_t requested;
    char *data;
    int flags = 0, received, error;
    if (!PyArg_ParseTuple(args, "On|i:recv", &descriptor_object, &requested, &flags)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    if (requested < 0 || requested > INT_MAX) {
        PyErr_SetString(PyExc_ValueError, "receive size must be between zero and INT_MAX");
        return NULL;
    }
    result = PyBytes_FromStringAndSize(NULL, requested);
    if (result == NULL || requested == 0) return result;
    data = PyBytes_AS_STRING(result);
    MSBT_SOCKET_CALL(received, recv(descriptor, data, (int)requested, flags), error);
    if (received == SOCKET_ERROR) {
        Py_DECREF(result);
        return msbt_error(error);
    }
    if (received != requested && _PyBytes_Resize(&result, received) < 0) return NULL;
    return result;
}
PyDoc_STRVAR(msbt_recv_doc, "Receive into owned, unpublished bytes storage.");

static PyObject *
msbt_close(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object;
    SOCKET descriptor;
    int status, error;
    if (!PyArg_ParseTuple(args, "O:close", &descriptor_object)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    MSBT_SOCKET_CALL(status, closesocket(descriptor), error);
    if (status == SOCKET_ERROR) return msbt_error(error);
    Py_RETURN_NONE;
}
PyDoc_STRVAR(msbt_close_doc, "Close one caller-owned native socket descriptor.");

static PyObject *
socket_address(PyObject *args, int peer)
{
    PyObject *descriptor_object;
    SOCKET descriptor;
    SOCKADDR_BTH address = {0};
    int size = sizeof(address), status, error;
    char text[18];
    if (!PyArg_ParseTuple(args, "O", &descriptor_object)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    Py_BEGIN_ALLOW_THREADS
    status = peer ? getpeername(descriptor, (SOCKADDR *)&address, &size)
                  : getsockname(descriptor, (SOCKADDR *)&address, &size);
    error = WSAGetLastError();
    Py_END_ALLOW_THREADS
    if (status == SOCKET_ERROR) return msbt_error(error);
    if (address.addressFamily != AF_BTH || size < sizeof(address)) {
        PyErr_SetString(PyExc_OSError, "the socket address is not a Bluetooth address");
        return NULL;
    }
    ba2str(address.btAddr, text, sizeof(text));
    return Py_BuildValue("sk", text, address.port);
}

static PyObject *msbt_getpeername(PyObject *self, PyObject *args) { return socket_address(args, 1); }
static PyObject *msbt_getsockname(PyObject *self, PyObject *args) { return socket_address(args, 0); }
PyDoc_STRVAR(msbt_getpeername_doc, "Return the connected Bluetooth peer address and port.");
PyDoc_STRVAR(msbt_getsockname_doc, "Return the local Bluetooth address and port.");

static PyObject *
msbt_dup(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object, *result;
    SOCKET descriptor, duplicate = INVALID_SOCKET;
    WSAPROTOCOL_INFOW protocol;
    int status, error = 0;
    if (!PyArg_ParseTuple(args, "O:dup", &descriptor_object)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    ZeroMemory(&protocol, sizeof(protocol));
    Py_BEGIN_ALLOW_THREADS
    status = WSADuplicateSocketW(descriptor, GetCurrentProcessId(), &protocol);
    if (status == SOCKET_ERROR) {
        error = WSAGetLastError();
    } else {
        duplicate = WSASocketW(FROM_PROTOCOL_INFO, FROM_PROTOCOL_INFO,
                               FROM_PROTOCOL_INFO, &protocol, 0, WSA_FLAG_OVERLAPPED);
        if (duplicate == INVALID_SOCKET) error = WSAGetLastError();
    }
    Py_END_ALLOW_THREADS
    if (duplicate == INVALID_SOCKET) return msbt_error(error);
    result = socket_number(duplicate);
    if (result == NULL) closesocket(duplicate);
    return result;
}
PyDoc_STRVAR(msbt_dup_doc, "Duplicate a socket descriptor while preserving shared Winsock state.");

/* Device operations keep all Windows handles and result buffers local to the
 * call. The automated software gate does not issue radio inquiries. */
static PyObject *
msbt_discover_devices(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *keywords[] = {"duration", "flush_cache", NULL};
    BLUETOOTH_DEVICE_INFO info = {0};
    BLUETOOTH_DEVICE_SEARCH_PARAMS criteria = {0};
    HBLUETOOTH_DEVICE_FIND find = NULL;
    PyObject *result, *name, *item;
    int duration = 8, flush_cache = 1;
    BOOL more;
    DWORD error = 0;
    char address[18];
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|ip:discover_devices", keywords,
                                    &duration, &flush_cache)) return NULL;
    if (duration < (flush_cache ? 1 : 0) || duration > 48) {
        PyErr_SetString(PyExc_ValueError, "inquiry duration must fit the Windows 1..48 multiplier range");
        return NULL;
    }
    result = PyList_New(0);
    if (result == NULL) return NULL;
    info.dwSize = sizeof(info);
    criteria.dwSize = sizeof(criteria);
    criteria.fReturnAuthenticated = TRUE;
    criteria.fReturnRemembered = !flush_cache;
    criteria.fReturnConnected = TRUE;
    criteria.fReturnUnknown = TRUE;
    criteria.fIssueInquiry = flush_cache;
    criteria.cTimeoutMultiplier = (UCHAR)duration;
    Py_BEGIN_ALLOW_THREADS
    find = BluetoothFindFirstDevice(&criteria, &info);
    if (find == NULL) error = GetLastError();
    Py_END_ALLOW_THREADS
    if (find == NULL) {
        if (error == ERROR_NO_MORE_ITEMS) return result;
        Py_DECREF(result);
        return msbt_error((int)error);
    }
    for (;;) {
        ba2str(info.Address.ullLong, address, sizeof(address));
        name = PyUnicode_FromWideChar(info.szName,
                    (Py_ssize_t)wcsnlen_s(info.szName, _countof(info.szName)));
        if (name == NULL) goto fail;
        item = Py_BuildValue("sOk", address, name, info.ulClassofDevice);
        Py_DECREF(name);
        if (item == NULL) goto fail;
        if (PyList_Append(result, item) < 0) {
            Py_DECREF(item);
            goto fail;
        }
        Py_DECREF(item);
        Py_BEGIN_ALLOW_THREADS
        more = BluetoothFindNextDevice(find, &info);
        error = more ? ERROR_SUCCESS : GetLastError();
        Py_END_ALLOW_THREADS
        if (!more) {
            if (error != ERROR_NO_MORE_ITEMS) {
                msbt_error((int)error);
                goto fail;
            }
            break;
        }
    }
    BluetoothFindDeviceClose(find);
    return result;
fail:
    BluetoothFindDeviceClose(find);
    Py_DECREF(result);
    return NULL;
}
PyDoc_STRVAR(msbt_discover_devices_doc,
             "Discover devices, or return cached devices when flush_cache is false.");

static PyObject *
msbt_list_local(PyObject *self, PyObject *unused)
{
    BLUETOOTH_FIND_RADIO_PARAMS parameters = {sizeof(parameters)};
    HBLUETOOTH_RADIO_FIND find;
    HANDLE radio = NULL;
    BLUETOOTH_RADIO_INFO info;
    PyObject *result = PyList_New(0), *item;
    DWORD error = 0;
    BOOL more;
    char address[18];
    if (result == NULL) return NULL;
    Py_BEGIN_ALLOW_THREADS
    find = BluetoothFindFirstRadio(&parameters, &radio);
    if (find == NULL) error = GetLastError();
    Py_END_ALLOW_THREADS
    if (find == NULL) {
        if (error == ERROR_NO_MORE_ITEMS) return result;
        Py_DECREF(result);
        return msbt_error((int)error);
    }
    for (;;) {
        ZeroMemory(&info, sizeof(info));
        info.dwSize = sizeof(info);
        Py_BEGIN_ALLOW_THREADS
        error = BluetoothGetRadioInfo(radio, &info);
        CloseHandle(radio);
        radio = NULL;
        Py_END_ALLOW_THREADS
        if (error != ERROR_SUCCESS) {
            msbt_error((int)error);
            goto fail;
        }
        ba2str(info.address.ullLong, address, sizeof(address));
        item = PyUnicode_FromString(address);
        if (item == NULL) goto fail;
        if (PyList_Append(result, item) < 0) {
            Py_DECREF(item);
            goto fail;
        }
        Py_DECREF(item);
        Py_BEGIN_ALLOW_THREADS
        more = BluetoothFindNextRadio(find, &radio);
        error = more ? ERROR_SUCCESS : GetLastError();
        Py_END_ALLOW_THREADS
        if (!more) {
            if (error != ERROR_NO_MORE_ITEMS) {
                msbt_error((int)error);
                goto fail;
            }
            break;
        }
    }
    BluetoothFindRadioClose(find);
    return result;
fail:
    if (radio != NULL) CloseHandle(radio);
    BluetoothFindRadioClose(find);
    Py_DECREF(result);
    return NULL;
}
PyDoc_STRVAR(msbt_list_local_doc, "Return local Bluetooth adapter addresses.");

static PyObject *
msbt_lookup_name(PyObject *self, PyObject *args)
{
    PyObject *text;
    SOCKADDR_BTH address;
    BLUETOOTH_FIND_RADIO_PARAMS parameters = {sizeof(parameters)};
    BLUETOOTH_DEVICE_INFO info = {0};
    HBLUETOOTH_RADIO_FIND find;
    HANDLE radio = NULL;
    DWORD error = 0;
    if (!PyArg_ParseTuple(args, "O:lookup_name", &text)) return NULL;
    if (!address_value(text, &address, 0)) return NULL;
    info.dwSize = sizeof(info);
    info.Address.ullLong = address.btAddr;
    Py_BEGIN_ALLOW_THREADS
    find = BluetoothFindFirstRadio(&parameters, &radio);
    if (find == NULL) {
        error = GetLastError();
    } else {
        error = BluetoothGetDeviceInfo(radio, &info);
        CloseHandle(radio);
        BluetoothFindRadioClose(find);
    }
    Py_END_ALLOW_THREADS
    if (error != ERROR_SUCCESS) return msbt_error((int)error);
    return PyUnicode_FromWideChar(info.szName,
                  (Py_ssize_t)wcsnlen_s(info.szName, _countof(info.szName)));
}
PyDoc_STRVAR(msbt_lookup_name_doc, "Return the cached Windows device name for a Bluetooth address.");

static int
record_object(PyObject *record, const char *key, PyObject *value)
{
    return PyDict_SetItemString(record, key, value);
}

static int
record_wtext(PyObject *record, const char *key, const wchar_t *text)
{
    PyObject *value;
    int status;
    if (text == NULL) return record_object(record, key, Py_None);
    value = PyUnicode_FromWideChar(text, -1);
    if (value == NULL) return -1;
    status = record_object(record, key, value);
    Py_DECREF(value);
    return status;
}

static int
record_text(PyObject *record, const char *key, const char *text)
{
    PyObject *value = PyUnicode_FromString(text);
    int status;
    if (value == NULL) return -1;
    status = record_object(record, key, value);
    Py_DECREF(value);
    return status;
}

static int
local_address(wchar_t *text, size_t length)
{
    SOCKET descriptor;
    SOCKADDR_BTH address = {0};
    int size = sizeof(address), status, error = 0;
    Py_BEGIN_ALLOW_THREADS
    descriptor = socket(AF_BTH, SOCK_STREAM, BTHPROTO_RFCOMM);
    if (descriptor == INVALID_SOCKET) {
        error = WSAGetLastError();
    } else {
        address.addressFamily = AF_BTH;
        address.port = BT_PORT_ANY;
        status = bind(descriptor, (SOCKADDR *)&address, sizeof(address));
        if (status == SOCKET_ERROR) {
            error = WSAGetLastError();
        } else if (getsockname(descriptor, (SOCKADDR *)&address, &size) == SOCKET_ERROR) {
            error = WSAGetLastError();
        }
        closesocket(descriptor);
    }
    Py_END_ALLOW_THREADS
    if (error) {
        msbt_error(error);
        return 0;
    }
    ba2wstr(address.btAddr, text, length);
    return 1;
}

static PyObject *
service_record(WSAQUERYSETW *query, const wchar_t *host)
{
    PyObject *record = PyDict_New(), *value;
    CSADDR_INFO *address;
    const char *protocol = "UNKNOWN";
    if (record == NULL) return NULL;
    if (record_wtext(record, "host", host) < 0 ||
            record_wtext(record, "name", query->lpszServiceInstanceName) < 0 ||
            record_wtext(record, "description", query->lpszComment) < 0) goto fail;
    if (record_object(record, "port", Py_None) < 0) goto fail;
    address = query->dwNumberOfCsAddrs ? query->lpcsaBuffer : NULL;
    if (address && address->RemoteAddr.lpSockaddr &&
            address->RemoteAddr.iSockaddrLength >= sizeof(SOCKADDR_BTH) &&
            address->RemoteAddr.lpSockaddr->sa_family == AF_BTH) {
        if (address->iProtocol == BTHPROTO_RFCOMM) protocol = "RFCOMM";
        else if (address->iProtocol == BTHPROTO_L2CAP) protocol = "L2CAP";
        if (address->iProtocol == BTHPROTO_RFCOMM || address->iProtocol == BTHPROTO_L2CAP) {
            value = PyLong_FromUnsignedLong(((SOCKADDR_BTH *)address->RemoteAddr.lpSockaddr)->port);
            if (value == NULL) goto fail;
            if (record_object(record, "port", value) < 0) {
                Py_DECREF(value);
                goto fail;
            }
            Py_DECREF(value);
        }
    }
    if (record_text(record, "protocol", protocol) < 0) goto fail;
    if (query->lpBlob == NULL ||
            (query->lpBlob->cbSize && query->lpBlob->pBlobData == NULL)) {
        msbt_error(ERROR_INVALID_DATA);
        goto fail;
    }
    value = PyBytes_FromStringAndSize((const char *)query->lpBlob->pBlobData,
                                    query->lpBlob->cbSize);
    if (value == NULL) goto fail;
    if (record_object(record, "rawrecord", value) < 0) {
        Py_DECREF(value);
        goto fail;
    }
    Py_DECREF(value);
    return record;
fail:
    Py_DECREF(record);
    return NULL;
}

static PyObject *
msbt_find_service(PyObject *self, PyObject *args)
{
    PyObject *address_object, *result = NULL, *record;
    const char *uuid_text;
    GUID uuid;
    wchar_t *wide = NULL, host[20];
    SOCKADDR_BTH parsed_address;
    WSAQUERYSETW initial = {0}, *query = NULL, *replacement;
    DWORD capacity = sizeof(WSAQUERYSETW), required, flags = LUP_FLUSHCACHE | LUP_RETURN_ALL;
    HANDLE lookup = NULL;
    int status, error;
    if (!PyArg_ParseTuple(args, "Us:find_service", &address_object, &uuid_text)) return NULL;
    if (!str2uuid(uuid_text, &uuid)) return NULL;
    wide = PyUnicode_AsWideCharString(address_object, NULL);
    if (wide == NULL) return NULL;
    if (wcscmp(wide, L"localhost") == 0) {
        PyMem_Free(wide);
        wide = NULL;
        if (!local_address(host, _countof(host))) return NULL;
        flags |= LUP_RES_SERVICE;
    } else {
        if (!address_value(address_object, &parsed_address, 0)) {
            PyMem_Free(wide);
            return NULL;
        }
        ba2wstr(parsed_address.btAddr, host, _countof(host));
        PyMem_Free(wide);
        wide = NULL;
    }
    initial.dwSize = sizeof(initial);
    initial.dwNameSpace = NS_BTH;
    initial.lpServiceClassId = &uuid;
    initial.lpszContext = host;
    MSBT_SOCKET_CALL(status, WSALookupServiceBeginW(&initial, flags, &lookup), error);
    if (status == SOCKET_ERROR) {
        if (error == WSASERVICE_NOT_FOUND) return PyList_New(0);
        return msbt_error(error);
    }
    result = PyList_New(0);
    if (result == NULL) goto fail;
    query = (WSAQUERYSETW *)malloc(capacity);
    if (query == NULL) {
        PyErr_NoMemory();
        goto fail;
    }
    for (;;) {
        ZeroMemory(query, capacity);
        query->dwSize = sizeof(*query);
        required = capacity;
        MSBT_SOCKET_CALL(status, WSALookupServiceNextW(lookup, flags, &required, query), error);
        if (status == SOCKET_ERROR) {
            if (error == WSA_E_NO_MORE || error == WSAENOMORE) break;
            if (error != WSAEFAULT || required <= capacity) {
                msbt_error(error);
                goto fail;
            }
            replacement = (WSAQUERYSETW *)realloc(query, required);
            if (replacement == NULL) {
                PyErr_NoMemory();
                goto fail;
            }
            query = replacement;
            capacity = required;
            continue;
        }
        record = service_record(query, host);
        if (record == NULL) goto fail;
        if (PyList_Append(result, record) < 0) {
            Py_DECREF(record);
            goto fail;
        }
        Py_DECREF(record);
    }
    free(query);
    MSBT_SOCKET_CALL(status, WSALookupServiceEnd(lookup), error);
    if (status == SOCKET_ERROR) {
        Py_DECREF(result);
        return msbt_error(error);
    }
    return result;
fail:
    free(query);
    WSALookupServiceEnd(lookup);
    Py_XDECREF(result);
    return NULL;
}
PyDoc_STRVAR(msbt_find_service_doc, "Query real Windows SDP service records for a Bluetooth address.");

static PyObject *
msbt_set_service_raw(PyObject *self, PyObject *args)
{
    Py_buffer view;
    PyObject *handle_object = Py_None, *record;
    HANDLE handle = NULL;
    BTH_SET_SERVICE *service;
    ULONG version = BTH_SDP_VERSION;
    WSAQUERYSETW query = {0};
    BLOB blob = {0};
    size_t size;
    int advertise, status, error;
    if (!PyArg_ParseTuple(args, "s*i|O:set_service_raw", &view, &advertise, &handle_object)) return NULL;
    if (view.len <= 0 || (size_t)view.len > ULONG_MAX - (sizeof(BTH_SET_SERVICE) - 1)) {
        PyBuffer_Release(&view);
        PyErr_SetString(PyExc_ValueError, "SDP record size does not fit the Windows API");
        return NULL;
    }
    if (handle_object != Py_None) {
        handle = PyLong_AsVoidPtr(handle_object);
        if (handle == NULL && PyErr_Occurred()) {
            PyBuffer_Release(&view);
            return NULL;
        }
    }
    size = sizeof(BTH_SET_SERVICE) + (size_t)view.len - 1;
    record = owned_buffer(&view);
    if (record == NULL) return NULL;
    service = (BTH_SET_SERVICE *)calloc(1, size);
    if (service == NULL) {
        Py_DECREF(record);
        return PyErr_NoMemory();
    }
    service->pSdpVersion = &version;
    service->pRecordHandle = &handle;
    service->ulRecordLength = (ULONG)PyBytes_GET_SIZE(record);
    memcpy(service->pRecord, PyBytes_AS_STRING(record), PyBytes_GET_SIZE(record));
    Py_DECREF(record);
    blob.cbSize = (ULONG)size;
    blob.pBlobData = (BYTE *)service;
    query.dwSize = sizeof(query);
    query.dwNameSpace = NS_BTH;
    query.lpBlob = &blob;
    MSBT_SOCKET_CALL(status, WSASetServiceW(&query,
                     advertise ? RNRSERVICE_REGISTER : RNRSERVICE_DELETE, 0), error);
    free(service);
    if (status == SOCKET_ERROR) return msbt_error(error);
    return PyLong_FromVoidPtr(handle);
}
PyDoc_STRVAR(msbt_set_service_raw_doc, "Register or remove an actual Windows SDP record.");

static PyObject *
msbt_set_service(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object, *name_object, *description_object;
    const char *uuid_text;
    SOCKET descriptor;
    wchar_t *name, *description;
    int advertise, length, status, error;
    SOCKADDR_BTH address = {0};
    CSADDR_INFO socket_info = {0};
    WSAQUERYSETW query = {0};
    GUID uuid;
    if (!PyArg_ParseTuple(args, "OiUUs:set_service", &descriptor_object, &advertise,
                         &name_object, &description_object, &uuid_text)) return NULL;
    if (!str2uuid(uuid_text, &uuid) || !socket_value(descriptor_object, &descriptor)) return NULL;
    name = PyUnicode_AsWideCharString(name_object, NULL);
    if (name == NULL) return NULL;
    description = PyUnicode_AsWideCharString(description_object, NULL);
    if (description == NULL) {
        PyMem_Free(name);
        return NULL;
    }
    length = sizeof(address);
    MSBT_SOCKET_CALL(status, getsockname(descriptor, (SOCKADDR *)&address, &length), error);
    if (status != SOCKET_ERROR && address.addressFamily != AF_BTH) {
        status = SOCKET_ERROR;
        error = WSAEAFNOSUPPORT;
    }
    if (status != SOCKET_ERROR) {
        socket_info.iProtocol = BTHPROTO_RFCOMM;
        socket_info.iSocketType = SOCK_STREAM;
        socket_info.LocalAddr.lpSockaddr = (SOCKADDR *)&address;
        socket_info.LocalAddr.iSockaddrLength = sizeof(address);
        socket_info.RemoteAddr = socket_info.LocalAddr;
        query.dwSize = sizeof(query);
        query.dwNameSpace = NS_BTH;
        query.dwNumberOfCsAddrs = 1;
        query.lpcsaBuffer = &socket_info;
        query.lpServiceClassId = &uuid;
        query.lpszServiceInstanceName = name;
        query.lpszComment = description;
        MSBT_SOCKET_CALL(status, WSASetServiceW(&query,
                         advertise ? RNRSERVICE_REGISTER : RNRSERVICE_DELETE, 0), error);
    }
    PyMem_Free(name);
    PyMem_Free(description);
    if (status == SOCKET_ERROR) return msbt_error(error);
    Py_RETURN_NONE;
}
PyDoc_STRVAR(msbt_set_service_doc, "Register or remove a named RFCOMM service using the Windows SDK.");

/* A timeout updates two native options. Keep these short configuration
 * transactions consistent without serializing blocking send/recv operations. */
static SRWLOCK socket_config_lock = SRWLOCK_INIT;

static PyObject *
msbt_setblocking(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object;
    SOCKET descriptor;
    int block, status, error;
    u_long nonblocking;
    if (!PyArg_ParseTuple(args, "Oi:setblocking", &descriptor_object, &block)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    nonblocking = block ? 0 : 1;
    Py_BEGIN_ALLOW_THREADS
    AcquireSRWLockExclusive(&socket_config_lock);
    status = ioctlsocket(descriptor, FIONBIO, &nonblocking);
    error = WSAGetLastError();
    ReleaseSRWLockExclusive(&socket_config_lock);
    Py_END_ALLOW_THREADS
    if (status == SOCKET_ERROR) return msbt_error(error);
    Py_RETURN_NONE;
}
PyDoc_STRVAR(msbt_setblocking_doc, "Set the shared native socket blocking mode.");

static PyObject *
msbt_settimeout(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object;
    SOCKET descriptor;
    double seconds, milliseconds;
    DWORD timeout;
    int status, error = 0;
    if (!PyArg_ParseTuple(args, "Od:settimeout", &descriptor_object, &seconds)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    if (!Py_IS_FINITE(seconds) || seconds < 0) {
        PyErr_SetString(PyExc_ValueError, "timeout must be finite and non-negative");
        return NULL;
    }
    milliseconds = ceil(seconds * 1000.0);
    if (milliseconds > UINT32_MAX) {
        PyErr_SetString(PyExc_OverflowError, "timeout exceeds the Winsock millisecond range");
        return NULL;
    }
    timeout = (DWORD)milliseconds;
    Py_BEGIN_ALLOW_THREADS
    AcquireSRWLockExclusive(&socket_config_lock);
    status = setsockopt(descriptor, SOL_SOCKET, SO_RCVTIMEO,
                        (const char *)&timeout, sizeof(timeout));
    if (status == SOCKET_ERROR) {
        error = WSAGetLastError();
    } else {
        status = setsockopt(descriptor, SOL_SOCKET, SO_SNDTIMEO,
                            (const char *)&timeout, sizeof(timeout));
        if (status == SOCKET_ERROR) error = WSAGetLastError();
    }
    ReleaseSRWLockExclusive(&socket_config_lock);
    Py_END_ALLOW_THREADS
    if (status == SOCKET_ERROR) return msbt_error(error);
    Py_RETURN_NONE;
}
PyDoc_STRVAR(msbt_settimeout_doc, "Set native receive/send timeouts; zero means no OS timeout.");

static PyObject *
msbt_gettimeout(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object;
    SOCKET descriptor;
    DWORD timeout = 0;
    int length = sizeof(timeout), status, error;
    if (!PyArg_ParseTuple(args, "O:gettimeout", &descriptor_object)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    Py_BEGIN_ALLOW_THREADS
    AcquireSRWLockShared(&socket_config_lock);
    status = getsockopt(descriptor, SOL_SOCKET, SO_RCVTIMEO,
                        (char *)&timeout, &length);
    error = WSAGetLastError();
    ReleaseSRWLockShared(&socket_config_lock);
    Py_END_ALLOW_THREADS
    if (status == SOCKET_ERROR) return msbt_error(error);
    return PyFloat_FromDouble((double)timeout / 1000.0);
}
PyDoc_STRVAR(msbt_gettimeout_doc, "Return the native receive timeout in seconds.");

static PyObject *
msbt_setsockopt(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object, *value, *index, *owned = NULL;
    SOCKET descriptor;
    unsigned int option;
    long converted;
    int level, integer, length, status, error;
    const char *data;
    Py_buffer view;
    if (!PyArg_ParseTuple(args, "OiIO:setsockopt", &descriptor_object, &level, &option, &value)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    if (PyIndex_Check(value)) {
        index = PyNumber_Index(value);
        if (index == NULL) return NULL;
        converted = PyLong_AsLong(index);
        Py_DECREF(index);
        if (converted == -1 && PyErr_Occurred()) return NULL;
        integer = (int)converted;
        data = (const char *)&integer;
        length = sizeof(integer);
    } else {
        if (PyObject_GetBuffer(value, &view, PyBUF_SIMPLE) < 0) return NULL;
        if (view.len > INT_MAX) {
            PyBuffer_Release(&view);
            PyErr_SetString(PyExc_OverflowError, "option buffer exceeds Winsock length range");
            return NULL;
        }
        length = (int)view.len;
        owned = owned_buffer(&view);
        if (owned == NULL) return NULL;
        data = PyBytes_AS_STRING(owned);
    }
    Py_BEGIN_ALLOW_THREADS
    AcquireSRWLockExclusive(&socket_config_lock);
    status = setsockopt(descriptor, level, (int)option, data, length);
    error = WSAGetLastError();
    ReleaseSRWLockExclusive(&socket_config_lock);
    Py_END_ALLOW_THREADS
    Py_XDECREF(owned);
    if (status == SOCKET_ERROR) return msbt_error(error);
    Py_RETURN_NONE;
}
PyDoc_STRVAR(msbt_setsockopt_doc, "Set an integer or buffer-valued native socket option.");

static PyObject *
msbt_getsockopt(PyObject *self, PyObject *args)
{
    PyObject *descriptor_object, *result = NULL;
    SOCKET descriptor;
    unsigned int option;
    int level, value = 0, length, status, error;
    Py_ssize_t requested = 0;
    char *data;
    if (!PyArg_ParseTuple(args, "OiI|n:getsockopt", &descriptor_object, &level, &option, &requested)) return NULL;
    if (!socket_value(descriptor_object, &descriptor)) return NULL;
    if (requested < 0 || requested > INT_MAX) {
        PyErr_SetString(PyExc_ValueError, "option buffer size must be between zero and INT_MAX");
        return NULL;
    }
    if (requested) {
        result = PyBytes_FromStringAndSize(NULL, requested);
        if (result == NULL) return NULL;
        data = PyBytes_AS_STRING(result);
        length = (int)requested;
    } else {
        data = (char *)&value;
        length = sizeof(value);
    }
    Py_BEGIN_ALLOW_THREADS
    AcquireSRWLockShared(&socket_config_lock);
    status = getsockopt(descriptor, level, (int)option, data, &length);
    error = WSAGetLastError();
    ReleaseSRWLockShared(&socket_config_lock);
    Py_END_ALLOW_THREADS
    if (status == SOCKET_ERROR) {
        Py_XDECREF(result);
        return msbt_error(error);
    }
    if (!requested) return PyLong_FromLong(value);
    if (length < 0 || length > requested) {
        Py_DECREF(result);
        return msbt_error(WSAEFAULT);
    }
    if (length != requested && _PyBytes_Resize(&result, length) < 0) return NULL;
    return result;
}
PyDoc_STRVAR(msbt_getsockopt_doc, "Get an integer option or owned option bytes.");

// =======================  ADMINISTRATIVE =========================

static PyMethodDef msbt_methods[] = {
    { "initwinsock", (PyCFunction)msbt_initwinsock, METH_NOARGS, 
        msbt_initwinsock_doc },
    { "socket", (PyCFunction)msbt_socket, METH_VARARGS, msbt_socket_doc },
    { "bind", (PyCFunction)msbt_bind, METH_VARARGS, msbt_bind_doc },
    { "listen", (PyCFunction)msbt_listen, METH_VARARGS, msbt_listen_doc },
    { "accept", (PyCFunction)msbt_accept, METH_VARARGS, msbt_accept_doc },
    { "connect", (PyCFunction)msbt_connect, METH_VARARGS, msbt_connect_doc },
    { "send", (PyCFunction)msbt_send, METH_VARARGS, msbt_send_doc },
    { "recv", (PyCFunction)msbt_recv, METH_VARARGS, msbt_recv_doc },
    { "close", (PyCFunction)msbt_close, METH_VARARGS, msbt_close_doc },
    { "getsockname", (PyCFunction)msbt_getsockname, METH_VARARGS, 
        msbt_getsockname_doc },
    { "getpeername", (PyCFunction)msbt_getpeername, METH_VARARGS,
        msbt_getpeername_doc },
    { "dup", (PyCFunction)msbt_dup, METH_VARARGS, msbt_dup_doc },
    { "discover_devices", (PyCFunction)msbt_discover_devices,
            METH_VARARGS | METH_KEYWORDS, msbt_discover_devices_doc },
    { "list_local", (PyCFunction)msbt_list_local,
            METH_NOARGS, msbt_list_local_doc },
    { "lookup_name", (PyCFunction)msbt_lookup_name, METH_VARARGS, msbt_lookup_name_doc },
    { "find_service", (PyCFunction)msbt_find_service, METH_VARARGS, msbt_find_service_doc },
    { "set_service", (PyCFunction)msbt_set_service, METH_VARARGS, msbt_set_service_doc },
    { "set_service_raw", (PyCFunction)msbt_set_service_raw, METH_VARARGS, msbt_set_service_raw_doc },
    { "setblocking", (PyCFunction)msbt_setblocking, METH_VARARGS, msbt_setblocking_doc },
    { "settimeout", (PyCFunction)msbt_settimeout, METH_VARARGS, msbt_settimeout_doc },
    { "gettimeout", (PyCFunction)msbt_gettimeout, METH_VARARGS, msbt_gettimeout_doc },
    { "setsockopt", (PyCFunction)msbt_setsockopt, METH_VARARGS, msbt_setsockopt_doc },
    { "getsockopt", (PyCFunction)msbt_getsockopt, METH_VARARGS, msbt_getsockopt_doc },
    { NULL, NULL }
};

PyDoc_STRVAR(msbt_doc, "Microsoft Bluetooth APIs with owned per-call resources.");

#define ADD_INT_CONSTANT(m, a) do { \
    if (PyModule_AddIntConstant(m, #a, a) < 0) return -1; \
} while (0)

static int
msbt_exec(PyObject *m)
{
    if (!ensure_winsock()) return -1;

    ADD_INT_CONSTANT(m, AF_BTH);
    ADD_INT_CONSTANT(m, SOCK_STREAM);
    ADD_INT_CONSTANT(m, BTHPROTO_RFCOMM);
    ADD_INT_CONSTANT(m, BT_PORT_ANY);

    ADD_INT_CONSTANT(m, SOL_RFCOMM);
    ADD_INT_CONSTANT(m, SO_BTH_AUTHENTICATE);
    ADD_INT_CONSTANT(m, SO_BTH_ENCRYPT);
    ADD_INT_CONSTANT(m, SO_BTH_MTU);
    ADD_INT_CONSTANT(m, SO_BTH_MTU_MAX);
    ADD_INT_CONSTANT(m, SO_BTH_MTU_MIN);

    return 0;
}

/* No process-global Python objects: all Python results belong to the calling
 * interpreter. Shared Winsock startup/configuration state has native locks;
 * detached operations retain their own buffers and caller-owned descriptors. */
static PyModuleDef_Slot msbt_slots[] = {
    {Py_mod_exec, msbt_exec},
#if PY_VERSION_HEX >= 0x030C0000
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
#endif
#if PY_VERSION_HEX >= 0x030D0000
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

static struct PyModuleDef msbt_module = {
    PyModuleDef_HEAD_INIT,
    "_msbt", msbt_doc, 0, msbt_methods, msbt_slots, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__msbt(void)
{
    return PyModuleDef_Init(&msbt_module);
}
