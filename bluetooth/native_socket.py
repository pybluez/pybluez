import socket

from bluetooth.btcommon import *

protocols =  {
    RFCOMM: socket.BTPROTO_RFCOMM
}

if not sys.platform.startswith("win"):
    protocols[L2CAP] = socket.BTPROTO_L2CAP,


class BluetoothSocket(socket.socket):
    def __init__ (self, proto=RFCOMM):
        _proto = protocols[proto]

        super().__init__ (socket.AF_BLUETOOTH, socket.SOCK_STREAM, _proto)
