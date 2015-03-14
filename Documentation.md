## Requirements ##

### GNU/Linux: ###
  * bluez-libs 2.10 or greater
  * Python 2.3 or more recent version

### Windows XP: ###
  * Service Pack 2
  * Python 2.3 or more recent version
  * Microsoft Bluetooth stack or Widcomm/Broadcom Bluetooth stack

### Installation ###
As of version 0.20 [PyBluez](https://pypi.python.org/pypi/PyBluez) is also on [pypi](https://pypi.python.org/pypi/PyBluez) so [pip](http://www.pip-installer.org/en/latest/installing.html) can be used to instali it.

Just run in cammand line:
```
    $ pip install pybluez
```


Windows users can download and run the executable installer.

Debian/Ubuntu users can apt-get install python-bluetooth

Fedora users can yum install pybluez

Otherwise, check your OS distribution for packages, or download the latest release and untar it.

Then, in a shell, wherever you unpacked the tarball,
```
    $ python setup.py install 
```

## Examples ##
There are a few examples included with the source distribution. Most are simple and straightforward. One of them (bluezchat) requires that python gtk2 and glade2 bindings be installed. Here are a few of the simple examples.

  * [inquiry.py](https://code.google.com/p/pybluez/source/browse/examples/simple/inquiry.py) - Detecting nearby Bluetooth devices
  * [sdp-browse.py](https://code.google.com/p/pybluez/source/browse/examples/simple/sdp-browse.py) - Browsing SDP services on a Bluetooth device
  * [rfcomm-server.py](https://code.google.com/p/pybluez/source/browse/examples/simple/rfcomm-server.py) | [rfcomm-client.py](https://code.google.com/p/pybluez/source/browse/examples/simple/rfcomm-client.py) - establishing an RFCOMM connection.

## API Documentation ##

  * [API Reference for PyBluez 0.7](http://pybluez.googlecode.com/svn/www/docs-0.7/index.html)

## Programming with PyBluez ##
If you've done any sort of socket programming before at all, you should find it pretty easy to get started with PyBluez, as we tried to stick pretty close to the Python Socket module.

To communicate with another bluetooth device, you simply create a socket and open a connection. You specify the kind of connection you want (e.g. L2CAP, RFCOMM, SCO) as parameters when you create the socket.

There is also [Bluetooth Essentials for Programmers](http://www.cambridge.org/us/academic/subjects/computer-science/distributed-networked-and-mobile-computing/bluetooth-essentials-programmers)