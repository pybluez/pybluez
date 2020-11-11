import sys
import os
from bluetooth.btcommon import *
import bluetooth.docstrings as docstrings

__version__ = 0.40

def _dbg(*args):
    return
    sys.stderr.write(*args)
    sys.stderr.write("\n")

if sys.platform == "win32":
    _dbg("trying widcomm")
    have_widcomm = False
    dll = "wbtapi.dll"
    sysroot = os.getenv ("SystemRoot")
    if os.path.exists (dll) or \
       os.path.exists (os.path.join (sysroot, "system32", dll)) or \
       os.path.exists (os.path.join (sysroot, dll)):
        try:
            from . import widcomm
            if widcomm.inquirer.is_device_ready ():
                # if the Widcomm stack is active and a Bluetooth device on that
                # stack is detected, then use the Widcomm stack
                from .widcomm import *
                have_widcomm = True
        except ImportError: 
            pass

    if not have_widcomm:
        # otherwise, fall back to the Microsoft stack
        _dbg("Widcomm not ready. falling back to MS stack")
        from bluetooth.msbt import *

elif sys.platform.startswith("linux"):
    from bluetooth.bluez import *
elif sys.platform == "darwin":
    from bluetooth.macos import *
else:
    raise Exception("This platform (%s) is currently not supported by pybluez." % sys.platform)

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