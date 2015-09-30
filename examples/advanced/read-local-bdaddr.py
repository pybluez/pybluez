import os
import sys
import struct
import bluetooth


if __name__ == "__main__":
    bdaddr = bluetooth.read_local_bdaddr()
    print(bdaddr)
