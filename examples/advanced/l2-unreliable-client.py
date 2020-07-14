#!/usr/bin/env python3
"""PyBluez advanced example l2-unreliable-client.py"""

import sys

import bluetooth
import bluetooth._bluetooth as bluez  # low level bluetooth wrappers

# Create the client socket
sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)

if len(sys.argv) < 4:
    print("Usage: l2-unreliable-client.py <addr> <timeout> <num_packets>")
    print("  address - device that l2-unreliable-server is running on")
    print("  timeout - wait timeout * 0.625ms before dropping unACK'd packets")
    print("  num_packets - number of 627-byte packets to send on connect")
    sys.exit(2)

bt_addr = sys.argv[1]
timeout = int(sys.argv[2])
num_packets = int(sys.argv[3])

print("Trying to connect to {}:1001...".format(bt_addr))
port = 0x1001
sock.connect((bt_addr, port))

print("Connected. Adjusting link parameters.")
print("Current flush timeout is {} ms.".format(
    bluetooth.read_flush_timeout(bt_addr)))
try:
    bluetooth.write_flush_timeout(bt_addr, timeout)
except bluez.error as e:
    print("Error setting flush timeout. Are you sure you're superuser?")
    print(e)
    sys.exit(1)
print("New flush timeout is {} ms.".format(
    bluetooth.read_flush_timeout(bt_addr)))

totalsent = 0
for i in range(num_packets):
    pkt = "0" * 672
    totalsent += sock.send(pkt)

print("Sent {} bytes total.".format(totalsent))
sock.close()
