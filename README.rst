======
 PyBluez
======

Python extension module allowing access to system Bluetooth resources.

https://github.com/karulis/pybluez

**BUILD REQUIREMENTS:**

*GNU/Linux:*
 
- Python 2.3 or more recent version
- Python distutils (standard in most Python distros, separate package python-dev in Debian)
- BlueZ libraries and header files

*Windows:*

- Microsoft Windows XP SP1 or Windows Vista/7/8/8.1
- Visual C++ 2010 Express for build for Python 3.3 or newer 
- Visual C++ 2008 Express for build for Python 3.2 or older
- In order to build 64-bit debug and release executables, Visual Studio 2008/2010 Standard Edition is required
- Widcomm BTW development kit 5.0 or later (Optional)
- Python 2.3 or more recent version

**INSTALLATION:**

from a command shell:
>python setup.py install

**EXAMPLES:**

.. code-block:: python

    # simple inquiry example
    import bluetooth
    
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    print("found %d devices" % len(nearby_devices))
    
    for addr, name in nearby_devices:
        print("  %s - %s" % (addr, name))

*GNU/Linux and Windows XP examples:*

- `examples/simple/inquiry.py`_ - Detecting nearby Bluetooth devices
- `examples/simple/sdp-browse.py`_ - Browsing SDP services on a Bluetooth device.
- `examples/simple/rfcomm-server.py`_ - establishing an RFCOMM connection.
- `examples/simple/rfcomm-client.py`_ - establishing an RFCOMM connection.

*GNU/Linux only examples:*

- `examples/simple/l2capserver.py`_
- `examples/simple/l2capclient.py`_
- `examples/simple/asynchronous-inquiry.py`_

- `examples/bluezchat`_
- `examples/advanced/inquiry-with-rssi.py`_
- `examples/advanced/l2-unreliable-server.py`_
- `examples/advanced/l2-unreliable-client.py`_

*CONTACT:*

Please use the mailing list at
http://groups.google.com/group/pybluez/

*LICENSE:*

  PyBluez is free software; you can redistribute it and/or modify it under the
  terms of the GNU General Public License as published by the Free Software
  Foundation; either version 2 of the License, or (at your option) any later
  version.
  
  PyBluez is distributed in the hope that it will be useful, but WITHOUT ANY
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License along with
  PyBluez; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
  Fifth Floor, Boston, MA  02110-1301  USA
  
.. _examples/simple/inquiry.py: https://github.com/karulis/pybluez/blob/master/examples/simple/inquiry.py
.. _examples/simple/sdp-browse.py: https://github.com/karulis/pybluez/blob/master/examples/simple/sdp-browse.py
.. _examples/simple/rfcomm-server.py: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-server.py
.. _examples/simple/rfcomm-client.py: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-client.py

.. _examples/simple/l2capserver.py: https://github.com/karulis/pybluez/blob/master/examples/simple/l2capserver.py
.. _examples/simple/l2capclient.py: https://github.com/karulis/pybluez/blob/master/examples/simple/l2capclient.py
.. _examples/simple/asynchronous-inquiry.py: https://github.com/karulis/pybluez/blob/master/examples/simple/asynchronous-inquiry.py

.. _examples/bluezchat: https://github.com/karulis/pybluez/blob/master/examples/bluezchat
.. _examples/advanced/inquiry-with-rssi.py: https://github.com/karulis/pybluez/blob/master/examples/advanced/inquiry-with-rssi.py
.. _examples/advanced/l2-unreliable-server.py: https://github.com/karulis/pybluez/blob/master/examples/advanced/l2-unreliable-server.py
.. _examples/advanced/l2-unreliable-client.py: https://github.com/karulis/pybluez/blob/master/examples/advanced/l2-unreliable-client.py
