PyBluez
=======

[![Build Status](https://travis-ci.org/pybluez/pybluez.svg?branch=master)](https://travis-ci.org/pybluez/pybluez)

The PyBluez module allows Python code to access the host machine's Bluetooth
resources.

| Linux  | Raspberry Pi | macOS | Windows |
| ------ | ------------ | ----- | ------- |
|        |              |       |         |




Contributors Wanted
-------------------

**This project is not under active development.** Contributions are strongly
desired to resolve compatibility problems on newer systems, address bugs, and
improve platform support for various features.


Examples
--------

```python
# simple inquiry example
import bluetooth

nearby_devices = bluetooth.discover_devices(lookup_names=True)
print("found %d devices" % len(nearby_devices))

for addr, name in nearby_devices:
    print("  %s - %s" % (addr, name))
```

```python
# bluetooth low energy scan
from bluetooth.ble import DiscoveryService

service = DiscoveryService()
devices = service.discover(2)

for address, name in devices.items():
    print("name: {}, address: {}".format(name, address))
```

### GNU/Linux and Windows XP examples:

-   [examples/simple/inquiry.py](https://github.com/pybluez/pybluez/blob/master/examples/simple/inquiry.py) -
    Detecting nearby Bluetooth devices
-   [examples/simple/sdp-browse.py](https://github.com/pybluez/pybluez/blob/master/examples/simple/sdp-browse.py) -
    Browsing SDP services on a Bluetooth device.
-   [examples/simple/rfcomm-server.py](https://github.com/pybluez/pybluez/blob/master/examples/simple/rfcomm-server.py) -
    establishing an RFCOMM connection.
-   [examples/simple/rfcomm-client.py](https://github.com/pybluez/pybluez/blob/master/examples/simple/rfcomm-client.py) -
    establishing an RFCOMM connection.
-   [examples/advanced/read-local-bdaddr.py](https://github.com/pybluez/pybluez/blob/master/examples/advanced/read-local-bdaddr.py) -
    provides the local Bluetooth device address.

### GNU/Linux only examples:

-   [examples/simple/l2capserver.py](https://github.com/pybluez/pybluez/blob/master/examples/simple/l2capserver.py)
-   [examples/simple/l2capclient.py](https://github.com/pybluez/pybluez/blob/master/examples/simple/l2capclient.py)
-   [examples/simple/asynchronous-inquiry.py](https://github.com/pybluez/pybluez/blob/master/examples/simple/asynchronous-inquiry.py)
-   [examples/bluezchat](https://github.com/pybluez/pybluez/blob/master/examples/bluezchat)
-   [examples/advanced/inquiry-with-rssi.py](https://github.com/pybluez/pybluez/blob/master/examples/advanced/inquiry-with-rssi.py)
-   [examples/advanced/l2-unreliable-server.py](https://github.com/pybluez/pybluez/blob/master/examples/advanced/l2-unreliable-server.py)
-   [examples/advanced/l2-unreliable-client.py](https://github.com/pybluez/pybluez/blob/master/examples/advanced/l2-unreliable-client.py)

### GNU/Linux experimental BLE support:

-   [examples/ble/scan.py](https://github.com/pybluez/pybluez/blob/master/examples/ble/scan.py)
-   [examples/ble/beacon.py](https://github.com/pybluez/pybluez/blob/master/examples/ble/beacon.py)
-   [examples/ble/beacon\_scan.py](https://github.com/pybluez/pybluez/blob/master/examples/ble/beacon_scan.py)
-   [examples/ble/read\_name.py](https://github.com/pybluez/pybluez/blob/master/examples/ble/read_name.py)


Contact
-------

Please file bugs to the [issue tracker][bugs]. Questions can be asked on the
[mailing list][ml] hosted on Google Groups, but unfortunately it is not very
active.

[bugs]: https://github.com/pybluez/pybluez/issues
[ml]: http://groups.google.com/group/pybluez/


Installation
------------

Use pip (there are also binaries for Windows platform on PyPI or here - [Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pybluez)):

    pip install pybluez

For experimental Bluetooth Low Energy support(only for Linux platform -
for additional dependencies please take look at:
[ble-dependencies](https://bitbucket.org/OscarAcena/pygattlib/src/45e04060881a20189412681f52d55ff5add9f388/DEPENDS?at=default)):

    pip install pybluez\[ble\]

For source installation:

    python setup.py install

for Bluetooth Low Energy support:

    pip install -e .\[ble\]

### Build Requirements

#### GNU/Linux

-   Python 2.3 or more recent version
-   Python distutils (standard in most Python distros, separate package
    python-dev in Debian)
-   BlueZ libraries and header files

#### Windows

-   Microsoft Windows XP SP1 or Windows Vista/7/8/8.1
-   Visual C++ 2010 Express for build for Python 3.3 or newer
-   Visual C++ 2008 Express for build for Python 3.2 or older
-   In order to build 64-bit debug and release executables, Visual
    Studio 2008/2010 Standard Edition is required
-   Widcomm BTW development kit 5.0 or later (Optional)
-   Python 2.3 or more recent version

#### macOS

-   Python 2.3 or later
-   Xcode
-   PyObjc 3.1b or later
    (<https://pythonhosted.org/pyobjc/install.html#manual-installation>)


License
-------

> PyBluez is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

> PyBluez is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

> You should have received a copy of the GNU General Public License along with
PyBluez; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
Fifth Floor, Boston, MA 02110-1301 USA

