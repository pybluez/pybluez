# Copyright (c) 2009 Bea Lam. All rights reserved.
#
# This file is part of LightBlue.
#
# LightBlue is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LightBlue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with LightBlue.  If not, see <http://www.gnu.org/licenses/>.

# Mac-specific utility functions and constants.

from Foundation import NSObject, NSDate, NSPoint, NSDefaultRunLoopMode, NSTimer
from AppKit import NSApplication, NSEvent, NSApplicationDefined, NSAnyEventMask
import objc

import time

from . import _IOBluetooth
from . import _lightbluecommon

# for mac os 10.5
try:
    from Foundation import NSUIntegerMax
    NSAnyEventMask = NSUIntegerMax
except:
    pass

# values of constants used in _IOBluetooth.framework
kIOReturnSuccess = 0       # defined in <IOKit/IOReturn.h>
kIOBluetoothUserNotificationChannelDirectionIncoming = 1
        # defined in <IOBluetooth/IOBluetoothUserLib.h>
kBluetoothHCIErrorPageTimeout = 0x04   # <IOBluetooth/Bluetooth.h>

# defined in <IOBluetooth/IOBluetoothUserLib.h>
kIOBluetoothServiceBrowserControllerOptionsNone = 0


LIGHTBLUE_NOTIFY_ID = 5444 # any old number
WAIT_MAX_TIMEOUT = 3


# IOBluetoothSDPUUID objects for RFCOMM and OBEX protocol UUIDs
PROTO_UUIDS = {
    _lightbluecommon.RFCOMM: _IOBluetooth.IOBluetoothSDPUUID.uuid16_(0x0003),
    _lightbluecommon.OBEX: _IOBluetooth.IOBluetoothSDPUUID.uuid16_(0x0008)
}


def formatdevaddr(addr):
    """
    Returns address of a device in usual form e.g. "00:00:00:00:00:00"

    - addr: address as returned by device.getAddressString() on an
      IOBluetoothDevice
    """
    # make uppercase cos PyS60 & Linux seem to always return uppercase
    # addresses
    # can safely encode to ascii cos BT addresses are only in hex (pyobjc
    # returns all strings in unicode)
    return addr.replace("-", ":").encode('ascii').upper()

def createbtdevaddr(addr):
    # in mac 10.5, can use BluetoothDeviceAddress directly
    chars = btaddrtochars(addr)
    try:
        btdevaddr = _IOBluetooth.BluetoothDeviceAddress(chars)
        return btdevaddr
    except:
        return chars

def btaddrtochars(addr):
    """
    Takes a bluetooth address and returns a tuple with the corresponding
    char values. This can then be used to construct a
    IOBluetoothDevice object, providing the signature of the withAddress:
    selector has been set (as in _setpyobjcsignatures() in this module).

    For example:
        >>> chars = btaddrtochars("00:0e:0a:00:a2:00")
        >>> chars
        (0, 14, 10, 0, 162, 0)
        >>> device = _IOBluetooth.IOBluetoothDevice.withAddress_(chars)
        >>> type(device)
        <objective-c class IOBluetoothDevice at 0xa4024988>
        >>> device.getAddressString()
        u'00-0e-0a-00-a2-00'
    """
    if not _lightbluecommon._isbtaddr(addr):
        raise TypeError("address %s not valid bluetooth address" % str(addr))
    if addr.find(":") == -1:
        addr = addr.replace("-", ":")   # consider alternative addr separator

    # unhexlify gives binary value like '\x0e', then ord to get the char value.
    # unhexlify throws TypeError if value is not a hex pair.
    import binascii
    chars = [ord(binascii.unhexlify(part)) for part in addr.split(":")]
    return tuple(chars)

def looponce():
    app = NSApplication.sharedApplication()

    # to push the run loops I seem to have to do this twice
    # use NSEventTrackingRunLoopMode or NSDefaultRunLoopMode?
    for i in range(2):
        event = app.nextEventMatchingMask_untilDate_inMode_dequeue_(
            NSAnyEventMask, NSDate.dateWithTimeIntervalSinceNow_(0.02),
            NSDefaultRunLoopMode, False)


def waituntil(conditionfunc, timeout=None):
    """
    Waits until conditionfunc() returns true, or <timeout> seconds have passed.
    (If timeout=None, this waits indefinitely until conditionfunc() returns
    true.) Returns false if the process timed out, otherwise returns true.

    Note!! You must call interruptwait() when you know that conditionfunc()
    should be checked (e.g. if you are waiting for data and you know some data
    has arrived) so that this can check conditionfunc(); otherwise it will just
    continue to wait. (This allows the function to wait for an event that is
    sent by interruptwait() instead of polling conditionfunc().)

    This allows the caller to wait while the main event loop processes its
    events. This must be done for certain situations, e.g. to receive socket
    data or to accept client connections on a server socket, since IOBluetooth
    requires the presence of an event loop to run these operations.

    This function doesn't need to be called if there is something else that is
    already processing the main event loop, e.g. if called from within a Cocoa
    application.
    """
    app = NSApplication.sharedApplication()
    starttime = time.time()
    if timeout is None:
        timeout = NSDate.distantFuture().timeIntervalSinceNow()
    if not isinstance(timeout, (int, float)):
        raise TypeError("timeout must be int or float, was %s" % \
                type(timeout))
    endtime = starttime + timeout
    while True:
        currtime = time.time()
        if currtime >= endtime:
            return False
        # use WAIT_MAX_TIMEOUT, don't wait forever in case of KeyboardInterrupt
        e = app.nextEventMatchingMask_untilDate_inMode_dequeue_(NSAnyEventMask, NSDate.dateWithTimeIntervalSinceNow_(min(endtime - currtime, WAIT_MAX_TIMEOUT)), NSDefaultRunLoopMode, True)
        if e is not None:
            if (e.type() == NSApplicationDefined and e.subtype() == LIGHTBLUE_NOTIFY_ID):
                if conditionfunc():
                    return True
            else:
                app.postEvent_atStart_(e, True)

def interruptwait():
    """
    If waituntil() has been called, this will interrupt the waiting process so
    it can check whether it should stop waiting.
    """
    evt = NSEvent.otherEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(NSApplicationDefined, NSPoint(), NSApplicationDefined, 0, 1, None, LIGHTBLUE_NOTIFY_ID, 0, 0)
    NSApplication.sharedApplication().postEvent_atStart_(evt, True)


class BBCocoaSleeper(NSObject):
    def init(self):
        self = super().init()
        self.timedout = False
        return self

    @objc.python_method
    def sleep(self, timeout):
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                timeout, self, "timedOut:", None, False)
        self.timedout = False
        waituntil(lambda: self.timedout)

    def timedOut_(self, timer):
        self.timedout = True
        interruptwait()
    timedOut_ = objc.selector(timedOut_, signature=b"v@:@")

def waitfor(timeout):
    sleeper = BBCocoaSleeper.alloc().init()
    sleeper.sleep(timeout)


class BBFileLikeObjectReader(NSObject):
    """
    Provides a suitable delegate class for the BBDelegatingInputStream class in
    LightAquaBlue.framework.

    This basically provides a wrapper for a python file-like object so that it
    can be read through a NSInputStream.
    """

    def initWithFileLikeObject_(self, fileobj):
        self = super().init()
        self.__fileobj = fileobj
        return self
    initWithFileLikeObject_ = objc.selector(initWithFileLikeObject_,
        signature=b"@@:@")

    def readDataWithMaxLength_(self, maxlength):
        try:
            data = self.__fileobj.read(maxlength)
        except Exception:
            return None
        return memoryview(data.encode())
    readDataWithMaxLength_ = objc.selector(readDataWithMaxLength_,
            signature=b"@@:I")    #"@12@0:4I8"    #"@:I"


class BBFileLikeObjectWriter(NSObject):
    """
    Provides a suitable delegate class for the BBDelegatingOutputStream class in
    LightAquaBlue.framework.

    This basically provides a wrapper for a python file-like object so that it
    can be written to through a NSOutputStream.
    """

    def initWithFileLikeObject_(self, fileobj):
        self = super().init()
        self.__fileobj = fileobj
        return self
    initWithFileLikeObject_ = objc.selector(initWithFileLikeObject_,
        signature=b"@@:@")

    def write_(self, data):
        try:
            self.__fileobj.write(data)
        except Exception:
            return -1
        return data.length()
    write_ = objc.selector(write_, signature=b"i12@0:4@8")    #i12@0:4@8  #i@:@

