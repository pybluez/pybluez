import bluetooth

socket = bluetooth.BluetoothSocket()
socket.connect(("00:13:43:a2:d1:5a", 0x0005))

socket.send(b'\xc0U\x02\x03\x00\xea')
socket.send(b'\xc0U\x02\x03\x00\xea')
socket.send(b'\xc0U\x02\x03\x00\xea')
socket.send(b'\xc0U\x02\x03\x00\xea')
socket.send(b'\xc0U\x02\x03\x00\xea')

result = socket.recv(1024)

print(result)


