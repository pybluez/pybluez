import bluetooth.macos.discovery as discovery
#from bluetooth.macos.btsocket import BluetoothSocket

from bluetooth.btcommon import *
from bluetooth.macos.btsocket import BluetoothSocket

def discover_devices(duration=8, flush_cache=True, lookup_names=False,
        lookup_class=False, device_id=-1):
    
    inquiry = discovery.DeviceDiscoverer(duration)

    return inquiry.get_devices_sync()


def lookup_name(address, timeout=10):
    raise Exception("not implemented")

def read_local_bdaddr():
    import lightblue
    return [lightblue.gethostaddr()]


def advertise_service(sock, name, service_id="", service_classes=None,
        profiles=None, provider="", description="", protocols=None):

    if protocols is None or protocols == RFCOMM:
        protocols = [Protocols.RFCOMM]

    import lightblue
    lightblue.advertise(name, sock, protocols[0], service_id)


def stop_advertising(sock):
    import lightblue
    lightblue.stop_advertising(sock)

