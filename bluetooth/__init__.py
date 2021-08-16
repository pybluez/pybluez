import sys
import os
from bluetooth.btcommon import *
import bluetooth.docstrings as docstrings

__version__ = 0.41

def _dbg(*args):
    return
    sys.stderr.write(*args)
    sys.stderr.write("\n")

if sys.platform == "darwin":
    from bluetooth.macos import *
else:
    if sys.platform == "win32":    
        from bluetooth.msbt import *
    elif sys.platform.startswith("linux"):
        from bluetooth.bluez import *
    else:
        raise Exception("This platform (%s) is currently not supported by pybluez." % sys.platform)

    from bluetooth.native_socket import BluetoothSocket

discover_devices.__doc__ = docstrings.discover_devices_doc
lookup_name.__doc__ = docstrings.lookup_name_doc
advertise_service.__doc__ = docstrings.advertise_service_doc
stop_advertising.__doc__ = docstrings.stop_advertising_doc
find_service.__doc__ = docstrings.find_service_doc
BluetoothSocket.__doc__ = docstrings.BluetoothSocket_doc
BluetoothSocket.dup.__doc__ = docstrings.BluetoothSocket_dup_doc
BluetoothSocket.accept.__doc__ = docstrings.BluetoothSocket_accept_doc
BluetoothSocket.bind.__doc__ =  docstrings.BluetoothSocket_bind_doc
BluetoothError.__doc__ =  docstrings.BluetoothError_doc