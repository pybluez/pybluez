from bluetooth.btcommon import Protocols
from bluetooth.macos.btsocket import btsocket

class BluetoothSocket:

    def __init__(self, proto=Protocols.RFCOMM, _sock=None):
        if _sock is None:
            _sock = btsocket._BluetoothSocket(btsocket._RFCOMMConnection())

        self._sock = _sock

        if proto != Protocols.RFCOMM:
            raise NotImplementedError(f"unsupported protocol: {proto}")
            
        self._proto = Protocols.RFCOMM
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

    def has_data(self):
        if self._sock._isclosed():
            raise Exception(f"polling a closed connection")
        return not self._sock.__incomingdata.empty()
