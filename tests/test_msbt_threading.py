import concurrent.futures
import threading
import time
import unittest
from unittest import mock

from bluetooth import msbt

class BluetoothSocketThreadingTest(unittest.TestCase):
    def make_socket(self, fd=101):
        with mock.patch.object(msbt.bt, "socket", return_value=fd):
            return msbt.BluetoothSocket()

    def test_concurrent_close_has_single_native_owner(self):
        sock = self.make_socket()
        calls = []
        entered = threading.Event()
        release = threading.Event()

        def fake_close(fd):
            calls.append(fd)
            entered.set()
            release.wait(2)
            return None

        with mock.patch.object(msbt.bt, "close", side_effect=fake_close):
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                first = pool.submit(sock.close)
                self.assertTrue(entered.wait(2))
                second = pool.submit(sock.close)
                self.assertIsNone(second.result(timeout=2))
                release.set()
                self.assertIsNone(first.result(timeout=2))

        self.assertEqual(calls, [101])
        self.assertEqual(sock.fileno(), -1)
        with mock.patch.object(msbt.bt, "send") as send:
            with self.assertRaises(OSError):
                sock.send(b"x")
            send.assert_not_called()

    def test_settimeout_updates_native_and_python_state_atomically(self):
        sock = self.make_socket()
        events = []
        events_lock = threading.Lock()
        start = threading.Barrier(8)

        def fake_setblocking(fd, value):
            with events_lock:
                events.append((threading.get_ident(), "blocking", value))
            time.sleep(0.002)

        def fake_settimeout(fd, value):
            with events_lock:
                events.append((threading.get_ident(), "timeout", value))

        def worker(index):
            start.wait()
            sock.settimeout(0.0 if index % 2 == 0 else float(index + 1))

        with (
            mock.patch.object(msbt.bt, "setblocking", side_effect=fake_setblocking),
            mock.patch.object(msbt.bt, "settimeout", side_effect=fake_settimeout),
        ):
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(worker, range(8)))

        self.assertEqual(len(events), 16)
        for index in range(0, len(events), 2):
            first, second = events[index:index + 2]
            self.assertEqual(first[0], second[0])
            self.assertEqual(first[1], "blocking")
            self.assertEqual(second[1], "timeout")

        with sock._state_lock:
            self.assertEqual(sock._blocking, sock._timeout != 0)

    def test_advertise_and_stop_bookkeeping_is_serialized(self):
        sock = self.make_socket()
        service_calls = []
        calls_lock = threading.Lock()

        def fake_set_service_raw(record, advertise, handle=None):
            with calls_lock:
                service_calls.append((record, advertise, handle))
            time.sleep(0.002)
            if advertise:
                return 77
            return None

        def run_pair(callable_):
            start = threading.Barrier(2)

            def worker():
                start.wait()
                try:
                    callable_()
                    return "ok"
                except OSError:
                    return "error"

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                return list(pool.map(lambda _: worker(), range(2)))

        with (
            mock.patch.object(msbt.bt, "getsockname", return_value=("00:00:00:00:00:00", 7)),
            mock.patch.object(msbt.bt, "set_service_raw", side_effect=fake_set_service_raw),
            mock.patch.object(msbt, "sdp_make_data_element", return_value=b"record"),
        ):
            advertised = run_pair(lambda: msbt.advertise_service(sock, "svc"))
            self.assertCountEqual(advertised, ["ok", "error"])
            self.assertEqual(
                [call for call in service_calls if call[1] is True],
                [(b"record", True, None)],
            )
            with sock._state_lock:
                self.assertEqual(sock._raw_sdp_record, b"record")
                self.assertEqual(sock._sdp_handle, 77)

            stopped = run_pair(lambda: msbt.stop_advertising(sock))
            self.assertCountEqual(stopped, ["ok", "error"])
            self.assertEqual(
                [call for call in service_calls if call[1] is False],
                [(b"record", False, 77)],
            )
            with sock._state_lock:
                self.assertIsNone(sock._raw_sdp_record)
                self.assertIsNone(sock._sdp_handle)

if __name__ == "__main__":
    unittest.main()
