import sys
import os
if sys.version < '3':
    from .btcommon import *
else:
    from bluetooth.btcommon import *

__version__ = 0.23

def _dbg(*args):
    return
    sys.stderr.write(*args)
    sys.stderr.write("\n")

if sys.platform == "win32":
    _dbg("trying widcomm")
    have_widcomm = False
    dll = "wbtapi.dll"
    sysroot = os.getenv ("SystemRoot")
    if os.path.exists (dll) or \
       os.path.exists (os.path.join (sysroot, "system32", dll)) or \
       os.path.exists (os.path.join (sysroot, dll)):
        try:
            from . import widcomm
            if widcomm.inquirer.is_device_ready ():
                # if the Widcomm stack is active and a Bluetooth device on that
                # stack is detected, then use the Widcomm stack
                from .widcomm import *
                have_widcomm = True
        except ImportError: 
            pass

    if not have_widcomm:
        # otherwise, fall back to the Microsoft stack
        _dbg("Widcomm not ready. falling back to MS stack")
        if sys.version < '3':
            from .msbt import *
        else:
            from bluetooth.msbt import *

elif sys.platform.startswith("linux"):
    if sys.version < '3':
        from .bluez import *
    else:
        from bluetooth.bluez import *
elif sys.platform == "darwin":
    from .macos import *
else:
    raise Exception("This platform (%s) is currently not supported by pybluez." % sys.platform)

discover_devices.__doc__ = \
    """Perform a Bluetooth device discovery.
   
    This function uses the first available Bluetooth resource to discover Bluetooth devices.

    Parameters
    ----------
    lookup_names : bool
        When set to True :func:`discover_devices` also attempts to look up the display name of each
        detected device. (the default is False).

    lookup_class : bool 
        When set to True :func:`discover_devices` attempts to look up the class of each detected device.
        (the default is False).

    Returns
    -------
    list
        Returns a list of device addresses as strings or a list of tuples. The content of the
        tuples depends on the values of lookup_names and lookup_class as detailed below.

        ============   ============   =====================================
        lookup_class   lookup_names   Return
        ============   ============   =====================================
        False          False          list of device addresses
        False          True           list of (address, name) tuples
        True           False          list of (address, class) tuples
        True           True           list of (address, name, class) tuples
        ============   ============   =====================================

    """

lookup_name.__doc__ = \
    """Look up the friendly name of a Bluetooth device.

    This function tries to determine the friendly name (human readable) of the device with
    the specified Bluetooth address.
  
    Parameters
    ----------
    address : str
        The Bluetooth address of the device.
    
    Returns
    -------
    str or None
        The friendly name of the device on success, and None on failure.

    Raises
    ------
    BluetoothError
        When the provided address is not a valid Bluetooth address.

    """

advertise_service.__doc__ = \
    """Advertise a service with the local SDP server.
  
    Parameters
    ----------
    sock : BluetoothSocket
        The :class:`BluetoothSocket` to use for advertising a service. The socket must be a bound,
        listening socket.
        
    name : str
        The name of the service and service_id (if specified). This should be a string
        of the form "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX", where each 'X' is a hexadecimal
        digit.

    service_classes : list 
        a list of service classes belonging to the advertised service.

        Each service class is represented by a 16-bit or 128-bit UUID.
        
        ============  ====================================
        UUID Type     Format
        ------------  ------------------------------------
        Short 16-bit  XXXX
        Full 128-bit  XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
        ============  ====================================

        where each 'X' is a hexadecimal digit.

        There are some constants for standard services, e.g. SERIAL_PORT_CLASS that equals to
        "1101". Some class constants provided by PyBluez are:

        ========================   ========================
        SERIAL_PORT_CLASS          LAN_ACCESS_CLASS           
        DIALUP_NET_CLASS           HEADSET_CLASS
        CORDLESS_TELEPHONY_CLASS   AUDIO_SOURCE_CLASS
        AUDIO_SINK_CLASS           PANU_CLASS                 
        NAP_CLASS                  GN_CLASS
        ========================   ========================

    profiles : list
        A list of service profiles that thie service fulfills. Each profile is a tuple with 
        (uuid, version). Most standard profiles use standard classes as UUIDs. 
        
        PyBluez offers a list of standard profiles, for example SERIAL_PORT_PROFILE. All standard profiles have
        the same name as the classes, except that _CLASS suffix is replaced by _PROFILE.

    provider : str
        A text string specifying the provider of the service

    description : str
        A text string describing the service

    protocols : list
        A list of protocols

    Note
    ----
    A note on working with Symbian smartphones: bt_discover in Python for Series 60 will only 
    detect service records with service class SERIAL_PORT_CLASS and profile SERIAL_PORT_PROFILE

    """

stop_advertising.__doc__ = \
    """Try to stop advertising a bluetooth service.

    This function instructs the local SDP server to stop advertising the service associated
    with socket.  You should typically call this right before you close socket.
    
    Parameters
    ----------
    sock : BluetoothSocket
        The :class:`BluetoothSocket` to stop advertising the service on.
    
    Raises
    ------
    BluetoothError
        When SDP fails to stop advertising for some reason.

    """"""
    

    """

find_service.__doc__ = \
    """Use to find available Bluetooth services.

    This function uses the service discovery protocol (SDP) to search for Bluetooth
    services matching the specified criteria and returns the search results.

    The search criteria are defined by passing one or more parameters to the function.

    If no criteria are specified then a list of all nearby services detected is 
    returned. If more than one criteria is specified, then the search results will 
    match all the criteria specified.
    
    Parameters
    ----------
    name: str or None
        The friendly name of a Bluetooth device. 

    uuid : str or None
        A valid 16-bit or 128-bit UUID.

        ============  ====================================
        UUID Type     Format
        ------------  ------------------------------------
        Short 16-bit  XXXX
        Full 128-bit  XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
        ============  ====================================

        where each 'X' is a hexadecimal digit. 

    address : str or None
        The Bluetooth address of a device or "localhost". 
        If "localhost" is provided the function will search for Bluetooth services on the
        local machine.
    
    Returns
    -------
    list
        The search results will be a list of dictionaries.  Each dictionary represents a 
        search match having the following key/value pairs.

        =============== ===========================================================
        Key             Value
        =============== ===========================================================
        host            the bluetooth address of the device advertising the
                        service.
        name            the name of the service being advertised.
        description     a description of the service being advertised.
        provider        the name of the person/organization providing the service.
        protocol        either 'RFCOMM', 'L2CAP', None if the protocol was not specified, 

                        or 'UNKNOWN' if the protocol was specified but unrecognized.
        port            the L2CAP PSM number if the protocol is 'L2CAP', 

                        the RFCOMM channel number if the protocol is 'RFCOMM', 

                        or None if the protocol wasn't specified.
        service-classes a list of service class IDs (UUID strings). Possibly
                        empty
        profiles        a list of profiles the service claims to support.
        
                        a profile takes the form of (UUID, version) pairs. 

                        Possibly empty.
        service-id      the Service ID of the service.  None if it wasn't set

                        See the Bluetooth spec for the difference between

                        Service ID and Service Class ID List
        =============== ===========================================================

        """
BluetoothSocket.__doc__ = \
    """ A Bluetooth Socket representing one endpoint of a Bluetooth connection.

    Parameters
    ----------

    proto : int
        The protocol the socket will use. The options are HCI, L2CAP, RFCOMM, or SCO. 
        The default is RFCOMM.
        
        .. note:: RFCOMM is the only protocol available for Windows and macOS systems.

    """

BluetoothSocket.dup.__doc__ =\
    """Duplicate the socket

    Returns
    -------
    BluetoothSocket
        A new :class:`BluetoothSocket` connected to the same system resource.
        
    """
BluetoothSocket.accept.__doc__ = \
    """Accept a connection.

    Returns
    -------
    tuple
        A tuple containing a :class:`BluetoothSocket` and a Bluetooth address.

    Raises
    ------
    BluetoothError
        When an attempt to accept a connection fails.
    """
BluetoothSocket.bind.__doc__ = \
    """Bind the socket to a local address and port.

    Parameters
    ----------
    addrport : tuple
        A tuple of the form (address str, port int)

    Raises
    ------
    BluetoothError
        When an attempt to bind the socket fails.

        """

#BluetoothSocket.get_l2cap_options.__doc__ =\
#    """Get the L2CAP options for the specified L2CAP socket.

#    Options are: omtu, imtu, flush_to, mode, fcs, max_tx, txwin_size.
        
#    Returns
#    -------
#    list
#        A list of L2CAP options available for the socket.

#    """
BluetoothError.__doc__ = \
    """Raised when a bluetooth function or method fails for a Bluetooth I/O
    related reason.

    """
