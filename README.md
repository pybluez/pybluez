PyBluez2
=======

[![Build Status](https://github.com/hiaselhans/pybluez2/workflows/Build/badge.svg)](https://github.com/pybluez/pybluez/actions?query=workflow%3ABuild)

The PyBluez module allows Python code to access the host machine's Bluetooth
resources.
It supports scanning for devices and opening bluetooth sockets (via native sockets on win/linux)


Platform Support
----------------

| Linux  | macOS | Windows |
|:------:|:-----:|:-------:|
| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |


Python Version Support
----------------------

- Windows: >= 3.9
- Mac: >= 3.5
- Linux: >= 3.5


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

Installation
------------

Install using pip:

```
pip install pybluez2
```

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
