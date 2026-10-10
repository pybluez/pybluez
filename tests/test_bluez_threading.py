import concurrent.futures
import socket
import sys
import threading
import unittest

import bluetooth._bluetooth as bt


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux BlueZ test")
class BluezThreadingTest(unittest.TestCase):
    def test_default_timeout_concurrency(self):
        workers = 8
        iterations = 200
        start = threading.Barrier(workers)

        def worker(index):
            start.wait()
            for step in range(iterations):
                value = None if (index + step) % 3 == 0 else ((index + step) % 5) / 1000.0
                bt.setdefaulttimeout(value)
                current = bt.getdefaulttimeout()
                self.assertTrue(current is None or isinstance(current, float))

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            list(pool.map(worker, range(workers)))

    def test_fromfd_close_timeout_io_overlap(self):
        cycles = 40
        for _ in range(cycles):
            left, right = socket.socketpair()
            sock = bt.fromfd(left.fileno(), socket.AF_UNIX, socket.SOCK_STREAM)
            start = threading.Barrier(3)

            def closer():
                start.wait()
                sock.close()
                sock.close()

            def timeout():
                start.wait()
                try:
                    sock.settimeout(0.0)
                    sock.gettimeout()
                except OSError:
                    pass

            def sender():
                start.wait()
                try:
                    sock.send(b"x")
                except OSError:
                    pass

            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
                    futures = [pool.submit(closer), pool.submit(timeout), pool.submit(sender)]
                    for future in futures:
                        future.result(timeout=5)
            finally:
                try:
                    sock.close()
                except OSError:
                    pass
                left.close()
                right.close()


if __name__ == "__main__":
    unittest.main()