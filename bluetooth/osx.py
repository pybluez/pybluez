####################################
# MINIMAL IMPLEMENTATION OF osx.py:
####################################
import lightblue
from .btcommon import *

def lookup_name(address, timeout=10):
    print "TODO: implement"


def discover_devices(duration=8, flush_cache=True, lookup_names=False, lookup_class=False, device_id=-1):
    # This is order of discovered device attributes in C-code.
    btAddresIndex = 0
    namesIndex = 1
    classIndex = 2

    # Use lightblue to discover devices on OSX.
    devices = lightblue.finddevices(getnames=lookup_names, length=duration)

    ret = list()
    for device in devices:
        item = [device[btAddresIndex],]
        if lookup_names:
            item.append(device[namesIndex])
        if lookup_class:
            item.append(device[classIndex])

        if len(item) == 1: # in case of address-only we return string not tuple
            ret.append(item[0])
        else:
            ret.append(tuple(i for i in item))
    return ret

def find_service(name=None, uuid=None, address=None):
    if uuid:
        raise NotImplementedError("UUID argument is not supported on OS X.")
    return lightblue.findservices(addr=address, name=name)

################################################################################

# import lightblue
# from .btcommon import *

# class BluetoothSocket:
    
#     def __init__ (self, proto=RFCOMM, _sock=None):
#         if _sock is None:
#             _sock = lightblue.socket()
#         self._sock = _sock

#         if proto != RFCOMM:
#             raise NotImplementedError("Not supported protocol") ### name the protocol
#         self._proto = proto

#     def bind(self, addrport):
#         return self._sock.bind(addrport)

#     def listen(self, backlog):
#         return self._sock.listen(backlog)

#     def accept(self):
#         return self._sock.accept()

#     def connect(self, addrport):
#         return self._sock.connect(addrport)

#     def send(self, data):
#         return self._sock.send(data)

#     def recv(self, numbytes):
#         return self._sock.recv(numbytes)

#     def close(self):
#         return self._sock.close()

#     def getsockname(self):
#         return self._sock.getsockname()

#     def setblocking(self, blocking):
#         return self._sock.setblocking(blocking)

#     def settimeout(self, timeout):
#         return self._sock.settimeout(timeout)

#     def gettimeout(self):
#         return self._sock.gettimeout()

#     def fileno(self):
#         return self._sock.fileno()

#     def dup(self):
#         return BluetoothSocket(self._proto, self._sock)

#     def makefile(self, mode, bufsize):
#         return self.makefile(mode, bufsize)

# # THIS HEADER IS BAD -- SHOULD NOT INIT VAR. TO [] IN HEADER DEFINITION -- WILL GET WEIRD BUGS.....
# #def advertise_service(sock, name, service_id = "", service_class = [], profiles = [], provider = "", description = "", protocols = []):
def advertise_service(sock, name, service_id="", service_class=None, profiles=None, provider="", description="", protocols=None):
    if service_class is None:
        service_class = []
    if profiles is None:
        profiles = []
    if protocols is None:
        protocols = []

    lightblue.advertise(name, sock, protocols[0])

def stop_advertising(sock):
    lightblue.stop_advertising(sock)

# def discover_devices(duration=8, flush_cache=True, lookup_names=False, lookup_class=False, device_id=-1):
#     return lightblue.finddevices(getnames=lookup_names, length=duration)

def find_service(name=None, uuid=None, address=None):
    if uuid:
        raise NotImplementedError("UUID argument is not supported on OS X.")
    return lightblue.findservices(addr=address, name=name)

