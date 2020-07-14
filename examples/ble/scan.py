#!/usr/bin/env python3
"""PyBluez ble example scan.py"""

from bluetooth.ble import DiscoveryService

service = DiscoveryService()
devices = service.discover(2)

for address, name in devices.items():
    print("Name: {}, address: {}".format(name, address))
