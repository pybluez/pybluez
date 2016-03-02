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

"""
Provides a python interface to the Mac OSX IOBluetooth Framework classes,
through PyObjC.

For example:
    >>> from lightblue import _IOBluetooth
    >>> for d in _IOBluetooth.IOBluetoothDevice.recentDevices_(0):
    ...     print d.getName()
    ...
    Munkey
    Adam
    My Nokia 6600
    >>>

See http://developer.apple.com/documentation/DeviceDrivers/Reference/IOBluetooth/index.html
for Apple's IOBluetooth documentation.

See http://pyobjc.sourceforge.net for details on how to access Objective-C
classes through PyObjC.
"""

import objc


if hasattr(objc, 'ObjCLazyModule'):
    # `ObjCLazyModule` function is available for PyObjC version >= 2.4
    io_bluetooth = objc.ObjCLazyModule("IOBluetooth",
        frameworkIdentifier="com.apple.IOBluetooth",
        frameworkPath=objc.pathForFramework(
            "/System/Library/Frameworks/IOBluetooth.framework"
        ),
        metadict=globals())

    locals_ = locals()
    for variable_name in dir(io_bluetooth):
        locals_[variable_name] = getattr(io_bluetooth, variable_name)

else:
    try:
        # mac os 10.5 loads frameworks using bridgesupport metadata
        __bundle__ = objc.initFrameworkWrapper("IOBluetooth",
            frameworkIdentifier="com.apple.IOBluetooth",
            frameworkPath=objc.pathForFramework(
                "/System/Library/Frameworks/IOBluetooth.framework"),
            globals=globals())

    except (AttributeError, ValueError):
        # earlier versions use loadBundle() and setSignatureForSelector()

        objc.loadBundle("IOBluetooth", globals(),
            bundle_path=objc.pathForFramework('/System/Library/Frameworks/IOBluetooth.framework'))

        # Sets selector signatures in order to receive arguments correctly from
        # PyObjC methods. These MUST be set, otherwise the method calls won't work
        # at all, mostly because you can't pass by pointers in Python.

        # set to return int, and take an unsigned char output arg
        # i.e. in python: return (int, unsigned char) and accept no args
        objc.setSignatureForSelector("IOBluetoothSDPServiceRecord",
                "getRFCOMMChannelID:", "i12@0:o^C")

        # set to return int, and take an unsigned int output arg
        # i.e. in python: return (int, unsigned int) and accept no args
        objc.setSignatureForSelector("IOBluetoothSDPServiceRecord",
                "getL2CAPPSM:", "i12@0:o^S")

        # set to return int, and take (output object, unsigned char, object) args
        # i.e. in python: return (int, object) and accept (unsigned char, object)
        objc.setSignatureForSelector("IOBluetoothDevice",
                "openRFCOMMChannelSync:withChannelID:delegate:", "i16@0:o^@C@")

        # set to return int, and take (output object, unsigned int, object) args
        # i.e. in python: return (int, object) and accept (unsigned int, object)
        objc.setSignatureForSelector("IOBluetoothDevice",
                "openL2CAPChannelSync:withPSM:delegate:", "i20@0:o^@I@")

        # set to return int, take a const 6-char array arg
        # i.e. in python: return object and accept 6-char list
        # this seems to work even though the selector doesn't take a char aray,
        # it takes a struct 'BluetoothDeviceAddress' which contains a char array.
        objc.setSignatureForSelector("IOBluetoothDevice",
                "withAddress:", '@12@0:r^[6C]')

del objc
