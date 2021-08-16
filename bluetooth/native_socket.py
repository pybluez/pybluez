import socket

from bluetooth.btcommon import *

class BluetoothSocket(socket.socket):
    def __init__ (self, proto=RFCOMM):
        _proto = {
            L2CAP: socket.BTPROTO_L2CAP,
            RFCOMM: socket.BTPROTO_RFCOMM
        }[proto]

        super().__init__ (socket.AF_BLUETOOTH, socket.SOCK_STREAM, _proto)
