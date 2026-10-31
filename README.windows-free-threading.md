# Windows free-threaded CPython Bluetooth backend

## Windows

The Microsoft backend retains all 23 native entry points and actual Windows
Bluetooth/SDP SDK calls. It uses full-width SOCKET/HANDLE values, owned Unicode
and immutable I/O buffers, immediate native-error capture and checked resource
cleanup. A native lock initializes the process Winsock reference once; another
short native lock makes socket option transactions consistent. Neither encloses
Python API calls or blocking send/receive/accept operations.

BluetoothSocket protects owner/state transitions with a per-object RLock.
Each public I/O operation duplicates the native socket under that lock, releases
the lock before I/O, then closes only its own duplicate. Closing the owner is
idempotent and cannot recycle another call's descriptor. Reader and writer can
run concurrently. A pending call retains its endpoint until its lease ends;
applications should arrange peer completion or a finite timeout before closing
an owner with pending I/O. dup() shares endpoint options as Winsock specifies.
Advertisement registration/removal and its Python metadata form a serialized
transaction. Metadata is committed only after actual SDK success.

The stateless, multi-phase module declares no GIL use after these ownership and
synchronization changes. No PYTHON_GIL or -X gil override is required.
The annotated Windows wrapper and shared SDP codec have accurate native stubs;
other platform wrappers retain their existing typing status.

Software tests exercise actual native Winsock I/O on owned loopback sockets,
full duplex, concurrent close and descriptor reuse, mutable buffers, options,
timeouts, GC and threaded initialization. Local radio enumeration is read-only.
They do not perform a remote device inquiry, Bluetooth connection or service
registration. Physical RFCOMM, discovery and live SDP still need a separate
hardware acceptance run; software qualification does not claim that result.
The pre-existing Windows makefile/DeviceDiscoverer omissions remain documented.

## SDP codec

Encoded string lengths use UTF-8 byte counts. Boolean, signed/unsigned 128-bit
integers and URL elements have actual binary encoders; parser bounds errors
raise ValueError. Existing decoded string/short-UUID byte values are preserved.
