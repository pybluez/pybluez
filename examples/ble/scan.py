from bluetooth.ble import DiscoveryService

service = DiscoveryService("hci0")
devices = service.discover(2)

for address, name in devices.items():
    print("name: {}, address: {}".format(name, address))
