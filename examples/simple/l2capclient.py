#!/usr/bin/env python3
"""PyBluez simple example l2capclient.py

Demo L2CAP client for bluetooth module.

$Id: l2capclient.py 524 2007-08-15 04:04:52Z albert $
"""

import sys

import bluetooth


sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)

if len(sys.argv) < 2:
    print("Usage: l2capclient.py <addr>")
    sys.exit(2)

bt_addr = sys.argv[1]
port = 0x1001

print("Trying to connect to {} on PSM 0x{}...".format(bt_addr, port))

sock.connect((bt_addr, port))

print("Connected. Type something...")
while True:
    data = input()
    if not data:
        break
    sock.send(data)
    data = sock.recv(1024)
    print("Data received:", str(data))

sock.close()
