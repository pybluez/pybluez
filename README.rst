PyBluez
=======

|versions| |wheel| |build status| |license|


+-------+--------------+-------+---------+
| Linux | Raspberry Pi | macOS | Windows |
+-------+--------------+-------+---------+

Python extension module allowing access to system Bluetooth resources.

For installation please refer to :ref:`installing`.

About
-----

PyBluez is a Bluetooth extension module for Python, allowing Python developers to use 
system Bluetooth resources. PyBluez works with GNU/Linux, macOS, and Windows.

Quickly find available Bluetooth devices to use in your applications.

.. code-block:: python

    # simple inquiry example
    import bluetooth

    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    print("found %d devices" % len(nearby_devices))

    for addr, name in nearby_devices:
        print("  %s - %s" % (addr, name))

GNU/Linux users can now experiment with Bluetooth Low Energy devices.

.. code-block:: python


    # bluetooth low energy scan
    from bluetooth.ble import DiscoveryService

    service = DiscoveryService()
    devices = service.discover(2)

    for address, name in devices.items():
        print("name: {}, address: {}".format(name, address))


GNU/Linux and Windows examples:
"""""""""""""""""""""""""""""""

-   `examples/simple/inquiry.py <https://github.com/pybluez/pybluez/blob/master/examples/simple/inquiry.py>`_ -
    Detecting nearby Bluetooth devices
-   `examples/simple/sdp-browse.py <https://github.com/pybluez/pybluez/blob/master/examples/simple/sdp-browse.py>`_ -
    Browsing SDP services on a Bluetooth device.
-   `examples/simple/rfcomm-server.py <https://github.com/pybluez/pybluez/blob/master/examples/simple/rfcomm-server.py>`_ -
    establishing an RFCOMM connection.
-   `examples/simple/rfcomm-client.py <https://github.com/pybluez/pybluez/blob/master/examples/simple/rfcomm-client.py>`_ -
    establishing an RFCOMM connection.
-   `examples/advanced/read-local-bdaddr.py <https://github.com/pybluez/pybluez/blob/master/examples/advanced/read-local-bdaddr.py>`_ -
    provides the local Bluetooth device address.

GNU/Linux only examples:
""""""""""""""""""""""""

-   `examples/simple/l2capserver.py <https://github.com/pybluez/pybluez/blob/master/examples/simple/l2capserver.py>`_
-   `examples/simple/l2capclient.py <https://github.com/pybluez/pybluez/blob/master/examples/simple/l2capclient.py>`_
-   `examples/simple/asynchronous-inquiry.py <https://github.com/pybluez/pybluez/blob/master/examples/simple/asynchronous-inquiry.py>`_
-   `examples/bluezchat <https://github.com/pybluez/pybluez/blob/master/examples/bluezchat>`_
-   `examples/advanced/inquiry-with-rssi.py <https://github.com/pybluez/pybluez/blob/master/examples/advanced/inquiry-with-rssi.py>`_
-   `examples/advanced/l2-unreliable-server.py <https://github.com/pybluez/pybluez/blob/master/examples/advanced/l2-unreliable-server.py>`_
-   `examples/advanced/l2-unreliable-client.py <https://github.com/pybluez/pybluez/blob/master/examples/advanced/l2-unreliable-client.py>`_

GNU/Linux experimental BLE support:
"""""""""""""""""""""""""""""""""""

-   `examples/ble/scan.py <https://github.com/pybluez/pybluez/blob/master/examples/ble/scan.py>`_
-   `examples/ble/beacon.py <https://github.com/pybluez/pybluez/blob/master/examples/ble/beacon.py>`_
-   `examples/ble/beacon\_scan.py <https://github.com/pybluez/pybluez/blob/master/examples/ble/beacon_scan.py>`_
-   `examples/ble/read\_name.py <https://github.com/pybluez/pybluez/blob/master/examples/ble/read_name.py>`_


Contact
-------

Please file bugs to the `issue tracker <bugs_>`_. Questions can be asked on the
`mailing list <ml_>`_ hosted on Google Groups, but unfortunately it is not very
active.




.. we should place license in a seperate file.



.. _bugs: https://github.com/pybluez/pybluez/issues
.. _ml: http://groups.google.com/group/pybluez/>

.. |build status| image:: https://travis-ci.org/pybluez/pybluez.svg?branch=master
    :target: https://travis-ci.org/pybluez/pybluez

.. |license| image:: https://img.shields.io/pypi/l/pybluez.svg
    :target: https://pypi.org/project/pybluez/

.. |wheel| image:: https://img.shields.io/pypi/wheel/pybluez.svg
    :target: https://pypi.org/project/pybluez/

.. |versions| image:: https://img.shields.io/pypi/pyversions/pybluez.svg
    :target: https://pypi.org/project/pybluez/
