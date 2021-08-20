import logging
import time
import socket

import objc
import Foundation

from bluetooth.btcommon import Protocols
from bluetooth.macos import util
from bluetooth.macos.btsocket.delegate import BluezBluetoothChannelDelegate

logger = logging.getLogger(__name__)

class _RFCOMMConnection:

    proto = Protocols.RFCOMM

    def __init__(self, channel=None):
        # self.channel is accessed by _BluetoothSocket parent
        self.channel = channel

    def connect(self, device, port, listener):
        # open RFCOMM channel (should timeout actually apply to opening of
        # channel as well? if so need to do timeout with async callbacks)
        logger.info(f"connecting RFCOMM: {device} {port} {listener}")
        result, self.channel = device.openRFCOMMChannelSync_withChannelID_delegate_(None, port, listener.delegate())
        logger.info(f"connecting result: {result}")
        time.sleep(1)
        if result == util.kIOReturnSuccess:
            self.channel.setDelegate_(listener.delegate())
            listener.registerclosenotif(self.channel)
        else:
            self.channel = None
        return result

    def write(self, data):
        if self.channel is None:
            raise socket.error("socket not connected")
        return BluezBluetoothChannelDelegate.synchronouslyWriteData_toRFCOMMChannel_(
                Foundation.NSData.alloc().initWithBytes_length_(data, len(data)),
                self.channel)

    def getwritemtu(self):
        return self.channel.getMTU()

    def getport(self):
        return self.channel.getChannelID()


class _L2CAPConnection:

    proto = Protocols.L2CAP

    def __init__(self, channel=None):
        # self.channel is accessed by _BluetoothSocket parent
        self.channel = channel

    def connect(self, device, port, listener):
        try:
            # pyobjc 2.0
            result, self.channel = device.openL2CAPChannelSync_withPSM_delegate_(None, port, listener.delegate())
        except TypeError:
            result, self.channel = device.openL2CAPChannelSync_withPSM_delegate_(port, listener.delegate())
        if result == util.kIOReturnSuccess:
            self.channel.setDelegate_(listener.delegate())
            listener.registerclosenotif(self.channel)
        else:
            self.channel = None
        return result

    def write(self, data):
        if self.channel is None:
            raise socket.error("socket not connected")
        return BluezBluetoothChannelDelegate.synchronouslyWriteData_toL2CAPChannel_(
                bytes(data), self.channel)

    def getwritemtu(self):
        return self.channel.getOutgoingMTU()

    def getport(self):
        return self.channel.getPSM()
