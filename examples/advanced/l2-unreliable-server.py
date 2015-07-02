import sys
import bluetooth

server_sock=bluetooth.BluetoothSocket( bluetooth.L2CAP )
server_sock.bind(("",0x1001))
server_sock.listen(1)
while True:
    print("waiting for incoming connection")
    client_sock,address = server_sock.accept()
    print("Accepted connection from %s" % str(address))

    print("waiting for data")
    total = 0
    while True:
        try:
            data = client_sock.recv(1024)
        except bluetooth.BluetoothError as e:
            break
        if len(data) == 0: break
        total += len(data)
        print("total byte read: %d" % total)

    client_sock.close()

    print("connection closed")

server_sock.close()
