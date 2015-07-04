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

"LightBlue - a simple bluetooth library."

# Docstrings for attributes in this module.
_docstrings = {

"finddevices":
    """
    Performs a device discovery and returns the found devices as a list of 
    (address, name, class-of-device) tuples. Raises BluetoothError if an error
    occurs.
    
    Arguments:
        - getnames=True: True if device names should be retrieved during 
          discovery. If false, None will be returned instead of the device
          name.
        - length=10: the number of seconds to spend discovering devices 
          (this argument has no effect on Python for Series 60)
            
    Do not invoke a new discovery before a previous discovery has finished.
    Also, to minimise interference with other wireless and bluetooth traffic, 
    and to conserve battery power on the local device, discoveries should not 
    be invoked too frequently (an interval of at least 20 seconds is 
    recommended).
    """,
"findservices":
    """
    Performs a service discovery and returns the found services as a list of 
    (device-address, service-port, service-name) tuples. Raises BluetoothError 
    if an error occurs.
    
    Arguments:
        - addr=None: a device address, to search only for services on a 
          specific device
        - name=None: a service name string, to search only for a service with a
          specific name
        - servicetype=None: can be RFCOMM or OBEX to search only for RFCOMM or
          OBEX-type services. (OBEX services are not returned from an RFCOMM
          search)
          
    If more than one criteria is specified, this returns services that match 
    all criteria.
    
    Currently the Python for Series 60 implementation will only find RFCOMM and 
    OBEX services.
    """,
"finddevicename":
    """
    Returns the name of the device with the given bluetooth address.
    finddevicename(gethostaddr()) returns the local device name.
    
    Arguments:
        - address: the address of the device to look up
        - usecache=True: if True, the device name will be fetched from a local
          cache if possible. If False, or if the device name is not in the 
          cache, the remote device will be contacted to request its name.
    
    Raise BluetoothError if the name cannot be retrieved.
    """,
"gethostaddr":
    """
    Returns the address of the local bluetooth device. 

    Raise BluetoothError if the local device is not available.
    """,
"gethostclass":
    """
    Returns the class of device of the local bluetooth device. 
    
    These values indicate the device's major services and the type of the 
    device (e.g. mobile phone, laptop, etc.). If you google for 
    "assigned numbers bluetooth baseband" you might find some documents
    that discuss how to extract this information from the class of device.

    Raise BluetoothError if the local device is not available.
    """,
"socket":
    """
    socket(proto=RFCOMM) -> socket object
    
    Returns a new socket object.
    
    Arguments:
        - proto=RFCOMM: the type of socket to be created - either L2CAP or
          RFCOMM. 
          
    Note that L2CAP sockets are not available on Python For Series 60, and
    only L2CAP client sockets are supported on Mac OS X and Linux (i.e. you can
    connect() the socket but not bind(), accept(), etc.).
    """,
"advertise":
    """
    Starts advertising a service with the given name, using the given server
    socket. Raises BluetoothError if the service cannot be advertised.
    
    Arguments:
        - name: name of the service to be advertised
        - sock: the socket object that will serve this service. The socket must 
          be already bound to a channel. If a RFCOMM service is being 
          advertised, the socket should also be listening.
        - servicetype: the type of service to advertise - either RFCOMM or 
          OBEX. (L2CAP services are not currently supported.)
          
    (If the servicetype is RFCOMM, the service will be advertised with the
    Serial Port Profile; if the servicetype is OBEX, the service will be
    advertised with the OBEX Object Push Profile.)
    """,
"stopadvertise":
    """
    Stops advertising the service on the given socket. Raises BluetoothError if 
    no service is advertised on the socket.
    
    This will error if the given socket is already closed.
    """,
"selectdevice":
    """
    Displays a GUI which allows the end user to select a device from a list of 
    discovered devices. 
    
    Returns the selected device as an (address, name, class-of-device) tuple. 
    Returns None if the selection was cancelled.
    
    (On Python For Series 60, the device selection will fail if there are any 
    open bluetooth connections.)
    """,
"selectservice":
    """
    Displays a GUI which allows the end user to select a service from a list of 
    discovered devices and their services.
    
    Returns the selected service as a (device-address, service-port, service-
    name) tuple. Returns None if the selection was cancelled.
    
    (On Python For Series 60, the device selection will fail if there are any 
    open bluetooth connections.)
    
    Currently the Python for Series 60 implementation will only find RFCOMM and 
    OBEX services.
    """
}


# import implementation modules
from _lightblue import *
from _lightbluecommon import *
import obex     # plus submodule

# set docstrings
import _lightblue
localattrs = locals()
for attr in _lightblue.__all__:
    try:
        localattrs[attr].__doc__ = _docstrings[attr]
    except KeyError:
        pass
del attr, localattrs
