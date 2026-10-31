"""Windows native software tests; only sockets on this process's loopback.

These exercise the actual Winsock I/O, ownership and configuration paths used
by RFCOMM. They do not qualify a physical radio, run device inquiries, connect
to Bluetooth peers, or register services with the local SDP server.
"""
import concurrent.futures
import gc
import os
import socket
import sys
import sysconfig
import threading
import unittest
from contextlib import contextmanager

if sys.platform != "win32":
    raise unittest.SkipTest("Microsoft Bluetooth backend is Windows-only")

import bluetooth
from bluetooth import _msbt as bt


@contextmanager
def endpoints():
    left, right = socket.socketpair()
    try:
        descriptor = bt.dup(left.fileno())
    finally:
        left.close()
    wrapped = bluetooth.BluetoothSocket(sockfd=descriptor)
    right.settimeout(5)
    wrapped.settimeout(2)
    try:
        yield wrapped, right
    finally:
        wrapped.close()
        right.close()


def receive_exact(peer, size):
    chunks = bytearray()
    while len(chunks) < size:
        chunk = peer.recv(size - len(chunks))
        if not chunk:
            raise AssertionError("unexpected end of loopback stream")
        chunks.extend(chunk)
    return bytes(chunks)


class MicrosoftFreeThreadingTest(unittest.TestCase):
    def setUp(self):
        self.assertEqual(sysconfig.get_config_var("Py_GIL_DISABLED"), 1)
        self.assertFalse(sys._is_gil_enabled())
        self.assertIsNone(sys.flags.gil)
        self.assertNotIn("gil", sys._xoptions)
        self.assertNotIn("PYTHON_GIL", os.environ)

    def tearDown(self):
        self.assertFalse(sys._is_gil_enabled())

    def test_api_surface_and_threaded_winsock_initialization(self):
        names = ("initwinsock socket bind listen accept connect send recv close "
                 "getsockname getpeername dup discover_devices list_local lookup_name "
                 "find_service set_service set_service_raw setblocking settimeout "
                 "gettimeout setsockopt getsockopt").split()
        for name in names:
            self.assertTrue(callable(getattr(bt, name)), name)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(list(pool.map(lambda _: bt.initwinsock(), range(128))), [None] * 128)
        self.assertTrue(bt.__file__.endswith(".pyd"))

    def test_real_native_buffer_and_text_roundtrips(self):
        with endpoints() as (wrapped, peer):
            for payload in (bytes(range(256)), bytearray(b"mutable"), memoryview(b"slice")[1:4], "Крыло"):
                expected = payload.encode() if isinstance(payload, str) else bytes(payload)
                self.assertEqual(wrapped.send(payload), len(expected))
                self.assertEqual(receive_exact(peer, len(expected)), expected)
                peer.sendall(expected)
                self.assertEqual(receive_exact(wrapped, len(expected)), expected)
            self.assertEqual(wrapped.recv(0), b"")

    def test_native_dup_retains_endpoint_after_original_close(self):
        with endpoints() as (wrapped, peer):
            duplicate = wrapped.dup()
            try:
                self.assertNotEqual(duplicate.fileno(), wrapped.fileno())
                wrapped.close()
                self.assertEqual(duplicate.send(b"owned"), 5)
                self.assertEqual(peer.recv(5), b"owned")
                peer.sendall(b"reply")
                self.assertEqual(duplicate.recv(5), b"reply")
            finally:
                duplicate.close()

    def test_real_integer_buffer_and_index_socket_options(self):
        class Index:
            def __index__(self):
                return 1
        with endpoints() as (wrapped, _):
            fd = wrapped.fileno()
            for value, expected in ((1, 1), (bytearray((0).to_bytes(4, "little")), 0),
                                    (memoryview((1).to_bytes(4, "little")), 1), (Index(), 1)):
                bt.setsockopt(fd, socket.SOL_SOCKET, socket.SO_KEEPALIVE, value)
                self.assertEqual(bt.getsockopt(fd, socket.SOL_SOCKET, socket.SO_KEEPALIVE), expected)
                self.assertEqual(int.from_bytes(bt.getsockopt(fd, socket.SOL_SOCKET, socket.SO_KEEPALIVE, 4), "little"), expected)

    def test_timeout_nonblocking_and_blocking_transitions(self):
        with endpoints() as (wrapped, peer):
            wrapped.settimeout(None)
            self.assertIsNone(wrapped.gettimeout())
            wrapped.settimeout(0)
            self.assertEqual(wrapped.gettimeout(), 0)
            with self.assertRaises(OSError) as raised:
                wrapped.recv(1)
            self.assertEqual(raised.exception.winerror, 10035)
            wrapped.settimeout(0.0001)
            self.assertGreaterEqual(wrapped.gettimeout(), 0.001)
            with self.assertRaises(OSError) as raised:
                wrapped.recv(1)
            self.assertIn(raised.exception.winerror, (10060, 10035))
            wrapped.setblocking(True)
            self.assertIsNone(wrapped.gettimeout())
            peer.sendall(b"ok")
            self.assertEqual(wrapped.recv(2), b"ok")
            for value in (-1, float("inf"), float("nan")):
                with self.assertRaises(ValueError):
                    wrapped.settimeout(value)

    def test_full_duplex_does_not_hold_owner_lock_during_receive(self):
        with endpoints() as (wrapped, peer):
            ready = threading.Event()
            def reader():
                ready.set()
                return wrapped.recv(5)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(reader)
                self.assertTrue(ready.wait(1))
                # A blocked read must not prevent the request being sent.
                self.assertEqual(wrapped.send(b"request"), 7)
                self.assertEqual(peer.recv(7), b"request")
                peer.sendall(b"reply")
                self.assertEqual(future.result(timeout=3), b"reply")

    def test_concurrent_close_is_idempotent_and_keeps_new_sockets_alive(self):
        for _ in range(40):
            with endpoints() as (wrapped, _):
                barrier = threading.Barrier(8)
                def close_then_open(_, barrier=barrier, wrapped=wrapped):
                    barrier.wait()
                    wrapped.close()
                    return socket.socketpair()
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                    sentinels = list(pool.map(close_then_open, range(8)))
                try:
                    self.assertEqual(wrapped.fileno(), -1)
                    for left, right in sentinels:
                        right.sendall(b"live")
                        self.assertEqual(left.recv(4), b"live")
                finally:
                    for pair in sentinels:
                        for sock in pair:
                            sock.close()
                with self.assertRaises(OSError):
                    wrapped.send(b"closed")

    def test_in_flight_lease_survives_owner_close_and_descriptor_churn(self):
        # Acquire a real native lease deterministically before close; exercise
        # exactly the same lifetime primitive used by all public I/O methods.
        with endpoints() as (wrapped, peer):
            acquired, proceed = threading.Event(), threading.Event()
            def receive_on_lease():
                with wrapped._lease() as descriptor:
                    acquired.set()
                    if not proceed.wait(3):
                        raise AssertionError("lease test coordination timed out")
                    return bt.recv(descriptor, 5)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(receive_on_lease)
                self.assertTrue(acquired.wait(1))
                wrapped.close()
                sentinels = [socket.socketpair() for _ in range(64)]
                try:
                    proceed.set()
                    peer.sendall(b"lease")
                    self.assertEqual(future.result(timeout=3), b"lease")
                    for left, right in sentinels:
                        left.sendall(b"sentinel")
                        self.assertEqual(right.recv(8), b"sentinel")
                finally:
                    for pair in sentinels:
                        for sock in pair:
                            sock.close()

    def test_parallel_native_roundtrips_and_gc(self):
        def worker(index):
            with endpoints() as (wrapped, peer):
                for iteration in range(64):
                    payload = ("%d:%d:" % (index, iteration)).encode() + bytes(range(256))
                    self.assertEqual(wrapped.send(payload), len(payload))
                    self.assertEqual(receive_exact(peer, len(payload)), payload)
                    peer.sendall(payload)
                    self.assertEqual(receive_exact(wrapped, len(payload)), payload)
                    if iteration % 8 == 0:
                        gc.collect()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(worker, range(8)))

    def test_mutable_buffer_snapshot_is_consistent_during_other_thread_updates(self):
        with endpoints() as (wrapped, peer):
            mutable = bytearray(b"a" * 32768)
            stop = threading.Event()
            def mutate():
                while not stop.is_set():
                    mutable[:] = b"a" * len(mutable)
                    mutable[:] = b"b" * len(mutable)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(mutate)
                try:
                    for _ in range(64):
                        count = wrapped.send(memoryview(mutable))
                        actual = receive_exact(peer, count)
                        self.assertIn(actual, (b"a" * count, b"b" * count))
                finally:
                    stop.set()
                    future.result(timeout=3)

    def test_argument_validation_precedes_any_radio_operation(self):
        with endpoints() as (wrapped, _):
            fd = wrapped.fileno()
            for size in (-1, 1 << 33):
                with self.assertRaises(ValueError):
                    bt.recv(fd, size)
            with self.assertRaises(OverflowError):
                bt.dup(1 << 100)
            with self.assertRaises(TypeError):
                bt.dup(object())
            with self.assertRaises(ValueError):
                bt.bind(fd, "\0", 1)
            with self.assertRaises(ValueError):
                bt.find_service("localhost", "invalid")
            with self.assertRaises(ValueError):
                bt.set_service(fd, True, "name", "description", "invalid")
            with self.assertRaises(ValueError):
                bt.set_service_raw(b"", True)
            with self.assertRaises(ValueError):
                bt.discover_devices(duration=49)
            with self.assertRaises(ValueError):
                bluetooth.advertise_service(wrapped, "name", service_id="invalid")
            # A TCP endpoint cannot be treated as a Bluetooth address/SDP
            # socket: reject it before any WSASetService registration.
            with self.assertRaises(OSError):
                wrapped.getsockname()
            with self.assertRaises(OSError):
                wrapped.getpeername()
            with self.assertRaises(OSError):
                wrapped.advertise_service("valid name")
            with self.assertRaises(OSError):
                wrapped.stop_advertising()

    def test_real_local_adapter_enumeration_is_read_only(self):
        # BluetoothFindFirst/NextRadio + BluetoothGetRadioInfo do not inquire
        # for remote devices, pair, connect, advertise, or change radio state.
        addresses = bluetooth.read_local_bdaddr()
        self.assertTrue(all(bluetooth.is_valid_address(value) for value in addresses))

    def test_stateless_native_module_in_independent_interpreters(self):
        from concurrent import interpreters
        code = """
import socket, sys
import bluetooth
from bluetooth import _msbt
assert not sys._is_gil_enabled()
for _ in range(32):
    left, right = socket.socketpair()
    duplicate = _msbt.dup(left.fileno())
    left.close()
    try:
        assert _msbt.send(duplicate, b'interpreter') == 11
        assert right.recv(11) == b'interpreter'
        right.sendall(b'owned')
        assert _msbt.recv(duplicate, 5) == b'owned'
    finally:
        _msbt.close(duplicate)
        right.close()
assert not sys._is_gil_enabled()
"""
        def worker(_):
            interpreter = interpreters.create()
            try:
                interpreter.exec(code)
            finally:
                interpreter.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(worker, range(8)))


if __name__ == "__main__":
    unittest.main()
