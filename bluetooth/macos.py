"""macOS implementation of Bluetooth."""
import lightblue
from .btcommon import *

def discover_devices(duration=8, flush_cache=True, lookup_names=False,
        lookup_class=False, device_id=-1):
    # This is order of discovered device attributes in C-code.
    btAddresIndex = 0
    namesIndex = 1
    classIndex = 2

    # Use lightblue to discover devices on OSX.
    devices = lightblue.finddevices(getnames=lookup_names, length=duration)

    ret = list()
    for device in devices:
        item = [device[btAddresIndex], ]
        if lookup_names:
            item.append(device[namesIndex])
        if lookup_class:
            item.append(device[classIndex])

        # in case of address-only we return string not tuple
        if len(item) == 1:
            ret.append(item[0])
        else:
            ret.append(tuple(item))
    return ret


def lookup_name(address, timeout=10):
    print("TODO: implement")

# TODO: After a little looking around, it seems that we can go into some of the 
# lightblue internals and enhance the amount of SDP information that is returned 
# (e.g., CID/PSM, protocol, provider information).
#
# See: _searchservices() in _lightblue.py
def find_service(name=None, uuid=None, address=None):
    if address is not None:
        addresses = [address]
    else:
        addresses = discover_devices(lookup_names=False)

    results = []

    for address in addresses:
        # print "[DEBUG] Browsing services on %s..." % (addr)

        dresults = lightblue.findservices(addr=address, name=name)

        for tup in dresults:
            service = {}

            # LightBlue performs a service discovery and returns the found
            # services as a list of (device-address, service-port,
            # service-name) tuples.
            service["host"] = tup[0]
            service["port"] = tup[1]
            service["name"] = tup[2]

            # Add extra keys for compatibility with PyBluez API.
            service["description"] = None
            service["provider"] = None
            service["protocol"] = None
            service["service-classes"] = []
            service["profiles"] = []
            service["service-id"] = None

            results.append(service)

    return results


def read_local_bdaddr():
    return [lightblue.gethostaddr()]


def advertise_service(sock, name, service_id="", service_classes=None,
        profiles=None, provider="", description="", protocols=None):
    """
    Advertises a service with the local SDP server.
  
    Parameters
    ----------
    sock 
        must be a bound, listening socket.  
    name 
        should be the name of the service, and service_id (if specified) should be a string
        of the form "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX", where each 'X' is a hexadecimal
        digit.

    service_classes : list 
        a list of service classes whose this service belongs to.

        Each class service is a 16-bit UUID in the form "XXXX", where each 'X' is a
        hexadecimal digit, or a 128-bit UUID in the form "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX".
        There are some constants for standard services, e.g. SERIAL_PORT_CLASS that equals to
        "1101". Some class constants:

        =================   ========================   ==================
        SERIAL_PORT_CLASS   LAN_ACCESS_CLASS           DIALUP_NET_CLASS 
        HEADSET_CLASS       CORDLESS_TELEPHONY_CLASS   AUDIO_SOURCE_CLASS
        AUDIO_SINK_CLASS    PANU_CLASS                 NAP_CLASS
        GN_CLASS
        =================   ========================   ==================

    profiles : list
        a list of service profiles that thie service fulfills. Each profile is a tuple with 
        ( uuid, version). Most standard profiles use standard classes as UUIDs. PyBluez offers 
        a list of standard profiles, for example SERIAL_PORT_PROFILE. All standard profiles have
        the same name as the classes, except that _CLASS suffix is replaced by _PROFILE.

    provider : str
        A text string specifying the provider of the service

    description : str
        A text string describing the service

    protocols : list
        A list of protocols

    Notes
    -----
    A note on working with Symbian smartphones: bt_discover in Python for Series 60 will only 
    detect service records with service class SERIAL_PORT_CLASS and profile SERIAL_PORT_PROFILE

    """

    if protocols is None or protocols == RFCOMM:
        protocols = [lightblue.RFCOMM]

    lightblue.advertise(name, sock, protocols[0], service_id)


def stop_advertising(sock):
    lightblue.stop_advertising(sock)


# ============================= BluetoothSocket ============================== #
class BluetoothSocket:

    def __init__(self, proto=RFCOMM, _sock=None):
        if _sock is None:
            _sock = lightblue.socket()
        self._sock = _sock

        if proto != RFCOMM:
            # name the protocol
            raise NotImplementedError("Not supported protocol")
        self._proto = lightblue.RFCOMM
        self._addrport = None

    def _getport(self):
        return self._addrport[1]

    def bind(self, addrport):
        self._addrport = addrport
        return self._sock.bind(addrport)

    def listen(self, backlog):
        return self._sock.listen(backlog)

    def accept(self):
        return self._sock.accept()

    def connect(self, addrport):
        return self._sock.connect(addrport)

    def send(self, data):
        return self._sock.send(data)

    def recv(self, numbytes):
        return self._sock.recv(numbytes)

    def close(self):
        return self._sock.close()

    def getsockname(self):
        return self._sock.getsockname()

    def setblocking(self, blocking):
        return self._sock.setblocking(blocking)

    def settimeout(self, timeout):
        return self._sock.settimeout(timeout)

    def gettimeout(self):
        return self._sock.gettimeout()

    def fileno(self):
        return self._sock.fileno()

    def dup(self):
        return BluetoothSocket(self._proto, self._sock)

    def makefile(self, mode, bufsize):
        return self.makefile(mode, bufsize)

# ============================= DeviceDiscoverer ============================= #

class DeviceDiscoverer:
    def __init__ (self):
        raise NotImplementedError
