PyBluez
=======

[![Build Status](https://github.com/pybluez/pybluez/workflows/Build/badge.svg)](https://github.com/pybluez/pybluez/actions?query=workflow%3ABuild)

The PyBluez module allows Python code to access the host machine's Bluetooth
resources.


Platform Support
----------------

| Linux  | Raspberry Pi | macOS | Windows |
|:------:|:------------:|:-----:|:-------:|
| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |


Python Version Support
----------------------

| Python 2 | Python 3 (min 3.5) |
|:--------:|:------------------:|
| Till Version 0.22 | Version 0.23 and newer |


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
print("Found {} devices.".format(len(nearby_devices)))

for addr, name in nearby_devices:
    print("  {} - {}".format(addr, name))
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

Please refer to the [installation instructions](/docs/install.rst).

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
