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
Provides a python interface to the Mac OSX IOBluetoothUI Framework classes,
through PyObjC.

For example:
    >>> from lightblue import _IOBluetoothUI
    >>> selector = _IOBluetoothUI.IOBluetoothDeviceSelectorController.deviceSelector()
    >>> selector.runModal()    # ask user to select a device
    -1000
    >>> for device in selector.getResults():
    ...     print device.getName()    # show name of selected device
    ...
    Nokia 6600
    >>>

See http://developer.apple.com/documentation/DeviceDrivers/Reference/IOBluetoothUI/index.html
for Apple's IOBluetoothUI documentation.

See http://pyobjc.sourceforge.net for details on how to access Objective-C
classes through PyObjC.
"""

import objc

try:
    # mac os 10.5 loads frameworks using bridgesupport metadata
    __bundle__ = objc.initFrameworkWrapper("IOBluetoothUI",
            frameworkIdentifier="com.apple.IOBluetoothUI",
            frameworkPath=objc.pathForFramework(
                "/System/Library/Frameworks/IOBluetoothUI.framework"),
            globals=globals())

except (AttributeError, ValueError):
    # earlier versions use loadBundle() and setSignatureForSelector()

    objc.loadBundle("IOBluetoothUI", globals(),
       bundle_path=objc.pathForFramework('/System/Library/Frameworks/IOBluetoothUI.framework'))

del objc

