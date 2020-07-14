#!/usr/bin/env python3
"""PyBluez advanced example read-local-bdaddr.py

Read the local Bluetooth device address
"""

import bluetooth

if __name__ == "__main__":
    print(bluetooth.read_local_bdaddr())
