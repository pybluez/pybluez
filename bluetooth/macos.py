from __future__ import annotations

from typing import TYPE_CHECKING

import lightblue

from .btcommon import RFCOMM

if TYPE_CHECKING:
    from socket import socket


# TODO: Remove or implement unused arguments
def discover_devices(duration: int = 8, flush_cache: bool = True,
                     lookup_names: bool = False, lookup_class: bool = False,
                     device_id: int = -1) -> list:
    # This is order of discovered device attributes in C-code.
    btAddresIndex = 0
    namesIndex = 1
    classIndex = 2

    # Use lightblue to discover devices on OSX.
    devices = lightblue.finddevices(getnames=lookup_names,
                                    length=duration)

    ret = list()
    for device in devices:
        item = [device[btAddresIndex], ]
        if lookup_names:
            item.append(device[namesIndex])
        if lookup_class:
            item.append(device[classIndex])

        # in case of address-only we return string not tuple
        ret.append(item[0] if len(item) == 1 else tuple(item))
    return ret


# TODO: Implement
def lookup_name(address: str, timeout: int = 10):
    print("TODO: implement")


# TODO: After a little looking around, it seems that we can go into some
# of the lightblue internals and enhance the amount of SDP information
# that is returned (e.g., CID/PSM, protocol, provider information).
#
# See: _searchservices() in _lightblue.py
def find_service(name: str = None, uuid: str = None,
                 address: str = None) -> list:
    if address is not None:
        addresses = [address]
    else:
        addresses = discover_devices(lookup_names=False)

    results = []

    for address in addresses:
        # print "[DEBUG] Browsing services on %s..." % (addr)
        dresults: list[tuple] = lightblue.findservices(addr=address, name=name)

        for host, port, name in dresults:
            service = dict(
                # LightBlue performs a service discovery and returns the found
                # services as a list of (device-address, service-port,
                # service-name) tuples.
                host=host,
                port=port,
                name=name,
                # Add extra keys for compatibility with PyBluez API.
                description=None,
                provider=None,
                protocol=None,
                profiles=[],)
            service["service-classes"] = []
            service["service-id"] = None
            results.append(service)

    return results


def read_local_bdaddr():
    return [lightblue.gethostaddr()]


def advertise_service(sock: socket, name, service_id: str = "",
                      service_classes=None, profiles=None,
                      provider: str = "", description: str = "",
                      protocols=None) -> None:
    if protocols is None or protocols == RFCOMM:
        protocols = [lightblue.RFCOMM]
    lightblue.advertise(name, sock, protocols[0], service_id)


def stop_advertising(sock: socket):
    lightblue.stop_advertising(sock)


# ============================= BluetoothSocket ==============================
class BluetoothSocket:

    def __init__(self, proto: int = RFCOMM, _sock: socket = None):
        if _sock is None:
            _sock = lightblue.socket()
        self._sock: socket = _sock

        if proto != RFCOMM:
            # name the protocol
            raise NotImplementedError("Not supported protocol")
        self._proto: int = proto
        self._addrport: tuple[str, int] = None

    def _getport(self):
        return self._addrport[1]

    def bind(self, addrport: tuple[str, int]):
        self._addrport = addrport
        return self._sock.bind(addrport)

    def listen(self, backlog):
        return self._sock.listen(backlog)

    def accept(self):
        return self._sock.accept()

    def connect(self, addrport: tuple[str, int]):
        return self._sock.connect(addrport)

    def send(self, data):
        return self._sock.send(data)

    def recv(self, numbytes: int):
        return self._sock.recv(numbytes)

    def close(self):
        return self._sock.close()

    def getsockname(self):
        return self._sock.getsockname()

    def setblocking(self, blocking: bool):
        return self._sock.setblocking(blocking)

    def settimeout(self, timeout: float):
        return self._sock.settimeout(timeout)

    def gettimeout(self):
        return self._sock.gettimeout()

    def fileno(self):
        return self._sock.fileno()

    def dup(self):
        return BluetoothSocket(self._proto, self._sock)

    def makefile(self, mode, bufsize):
        return self.makefile(mode, bufsize)


# ============================= DeviceDiscoverer =============================
class DeviceDiscoverer:
    def __init__(self):
        raise NotImplementedError
