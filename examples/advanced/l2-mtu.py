#!/usr/bin/env python3
"""PyBluez advanced example l2-mtu.py"""

import sys

import bluetooth

def usage():
    print("Usage: l2-mtu.py < server | client > [options]")
    print("  l2-mtu.py server - to start in server mode")
    print("  l2-mtu.py client <addr> - to start in client mode and connect to addr")
    sys.exit(2)

if len(sys.argv) < 2:
    usage()

mode = sys.argv[1]
if mode not in ["client", "server"]:
    usage()

if mode == "server":
    server_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    server_sock.bind(("", 0x1001))
    bluetooth.set_l2cap_mtu(server_sock, 65535)
    server_sock.listen(1)

    while True:
        print("Waiting for incoming connection...")
        client_sock, address = server_sock.accept()
        print("Accepted connection from", str(address))

        print("Waiting for data...")
        total = 0
        while True:
            try:
                data = client_sock.recv(65535)
            except bluetooth.BluetoothError as e:
                break
            if not data:
                break
            print("Received packet of size", len(data))
        client_sock.close()
        print("Connection closed.")

    server_sock.close()

else:
    sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    print("Connected. Adjusting link parameters.")
    bluetooth.set_l2cap_mtu(sock, 65535)

    bt_addr = sys.argv[2]
    print("Trying to connect to {}:1001...".format(bt_addr))
    port = 0x1001
    sock.connect((bt_addr, port))

    totalsent = 0
    for i in range(1, 65535, 100):
        pkt = "0" * i
        sent = sock.send(pkt)
        print("Sent packet of size {} (tried {}).".format(sent, len(pkt)))

    sock.close()
