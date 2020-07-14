#!/usr/bin/env python3
"""PyBluez advanced example l2-unreliable-server.py"""

import bluetooth

server_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
server_sock.bind(("", 0x1001))
server_sock.listen(1)

while True:
    print("Waiting for incoming connection...")
    client_sock, address = server_sock.accept()
    print("Accepted connection from", str(address))

    print("Waiting for data...")
    total = 0
    while True:
        try:
            data = client_sock.recv(1024)
        except bluetooth.BluetoothError as e:
            break
        if not data:
            break
        total += len(data)
        print("Total byte read:", total)

    client_sock.close()
    print("Connection closed")

server_sock.close()
