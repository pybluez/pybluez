import sys
import fcntl
import struct
import array
import bluetooth
import bluetooth._bluetooth as bt   # low level bluetooth wrappers.


# Create the client socket
sock=bluetooth.BluetoothSocket(bluetooth.L2CAP)

if len(sys.argv) < 4:
    print("usage: l2capclient.py <addr> <timeout> <num_packets>")
    print("  address - device that l2-unreliable-server is running on")
    print("  timeout - wait timeout * 0.625ms before dropping unACK'd packets")
    print("  num_packets - number of 627-byte packets to send on connect")
    sys.exit(2)

bt_addr=sys.argv[1]
timeout = int(sys.argv[2])
num_packets = int(sys.argv[3])

print("trying to connect to %s:1001" % bt_addr)
port = 0x1001
sock.connect((bt_addr, port))

print("connected.  Adjusting link parameters.")
print("current flush timeout is %d ms" % bluetooth.read_flush_timeout( bt_addr ))
try:
    bluetooth.write_flush_timeout( bt_addr, timeout )
except bt.error as e:
    print("error setting flush timeout.  are you sure you're superuser?")
    print(e)
    sys.exit(1)
print("new flush timeout is %d ms" % bluetooth.read_flush_timeout( bt_addr ))

totalsent = 0 
for i in range(num_packets):
    pkt = "0" * 672
    totalsent += sock.send(pkt)
print("sent %d bytes total" % totalsent)

sock.close()
