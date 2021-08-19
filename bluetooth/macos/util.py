# values of constants used in _IOBluetooth.framework
kIOReturnSuccess = 0       # defined in <IOKit/IOReturn.h>
kIOBluetoothUserNotificationChannelDirectionIncoming = 1
        # defined in <IOBluetooth/IOBluetoothUserLib.h>
kBluetoothHCIErrorPageTimeout = 0x04   # <IOBluetooth/Bluetooth.h>

# defined in <IOBluetooth/IOBluetoothUserLib.h>
kIOBluetoothServiceBrowserControllerOptionsNone = 0


def formatdevaddr(addr):
    """
    Returns address of a device in usual form e.g. "00:00:00:00:00:00"

    - addr: address as returned by device.getAddressString() on an
      IOBluetoothDevice
    """
    # make uppercase cos PyS60 & Linux seem to always return uppercase
    # addresses
    # can safely encode to ascii cos BT addresses are only in hex (pyobjc
    # returns all strings in unicode)
    return addr.replace("-", ":").upper()