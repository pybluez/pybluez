#!/usr/bin/env python3
"""PyBluez ble example beacon.py

Advertises a bluethooth low energy beacon for 15 seconds.
"""

import time

from bluetooth.ble import BeaconService

service = BeaconService()

service.start_advertising("11111111-2222-3333-4444-555555555555",
                          1, 1, 1, 200)
time.sleep(15)
service.stop_advertising()

print("Done.")
