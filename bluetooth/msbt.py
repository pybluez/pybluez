"""Windows implementation of Bluetooth."""
from bluetooth import *
import bluetooth._msbt as bt

bt.initwinsock ()

# ============== SDP service registration and unregistration ============

def discover_devices (duration=8, flush_cache=True, lookup_names=False,
                      lookup_class=False, device_id=-1):
    """Perform a bluetooth device discovery.
   
    uses the first available bluetooth resource to discover bluetooth devices.

    Parameters
    ----------
    lookup_names : bool, optional
        When set to True discover_devices also attempts to look up the display name of each
        detected device. (the default is False)

    lookup_class : bool, optional 
        When set to True discover devices attempts to look up the class of each detected device.
        (the default is False)

    Returns
    -------
    list
        Returns a list of device addresses as strings or a list of tuples. The content of the
        tuples depends on the values of lookup_names and lookup_class. 

        ============   ============   =====================================
        lookup_class   lookup_names   Return
        ============   ============   =====================================
        False          False          list of device addresses
        False          True           list of (address, name) tuples
        True           False          list of (address, class) tuples
        True           True           list of (address, name, class) tuples
        ============   ============   =====================================

    """

    #this is order of items in C-code
    btAddresIndex = 0
    namesIndex = 1
    classIndex = 2

    try:
        devices = bt.discover_devices(duration=duration, flush_cache=flush_cache)
    except OSError:
        return []
    ret = list()
    for device in devices:
        item = [device[btAddresIndex],]
        if lookup_names:
            item.append(device[namesIndex])
        if lookup_class:
            item.append(device[classIndex])

        if len(item) == 1: # in case of address-only we return string not tuple
            ret.append(item[0])
        else:
            ret.append(tuple(i for i in item))
    return ret


def read_local_bdaddr():
    return bt.list_local()


def lookup_name (address, timeout=10):
    if not is_valid_address (address): 
        raise ValueError ("Invalid Bluetooth address")
    try:
        return bt.lookup_name(address)
    except OSError:
        return None


class BluetoothSocket:
    def __init__ (self, proto = RFCOMM, sockfd = None):
        if proto not in [ RFCOMM ]:
            raise ValueError ("invalid protocol")

        if sockfd:
            self._sockfd = sockfd
        else:
            self._sockfd = bt.socket (bt.SOCK_STREAM, bt.BTHPROTO_RFCOMM)
        self._proto = proto

        # used by advertise_service and stop_advertising
        self._sdp_handle = None
        self._raw_sdp_record = None

        # used to track if in blocking or non-blocking mode (FIONBIO appears
        # write only)
        self._blocking = True
        self._timeout = False

    def bind (self, addrport):
        if self._proto == RFCOMM:
            addr, port = addrport

            if port == 0: port = bt.BT_PORT_ANY
            bt.bind (self._sockfd, addr, port)

    def listen (self, backlog):
        bt.listen (self._sockfd, backlog)

    def accept (self):
        clientfd, addr, port = bt.accept (self._sockfd)
        client = BluetoothSocket (self._proto, sockfd=clientfd)
        return client, (addr, port)

    def connect (self, addrport):
        addr, port = addrport
        bt.connect (self._sockfd, addr, port)

    def send (self, data):
        return bt.send (self._sockfd, data)

    def recv (self, numbytes):
        return bt.recv (self._sockfd, numbytes)

    def close (self):
        return bt.close (self._sockfd)

    def getsockname (self):
        return bt.getsockname (self._sockfd)

    def getpeername (self):
        return bt.getpeername (self._sockfd)

    getpeername.__doc__ = bt.getpeername.__doc__

    def setblocking (self, blocking):
        bt.setblocking (self._sockfd, blocking)
        self._blocking = blocking

    def settimeout (self, timeout):
        if timeout < 0: raise ValueError ("invalid timeout")

        if timeout == 0:
            self.setblocking (False)
        else:
            self.setblocking (True)

        bt.settimeout (self._sockfd, timeout)
        self._timeout = timeout

    def gettimeout (self):    
        if self._blocking and not self._timeout: return None
        return bt.gettimeout (self._sockfd)

    def fileno (self):
        return self._sockfd

    def dup (self):
        return BluetoothSocket (self._proto, sockfd=bt.dup (self._sockfd))

    def makefile (self):
        # TODO
        raise Exception("Not yet implemented")


def advertise_service (sock, name, service_id = "", service_classes = [], \
        profiles = [], provider = "", description = "", protocols = []):
    """
    Advertises a service with the local SDP server.
  
    Parameters
    ----------
    sock 
        must be a bound, listening socket.  
    name 
        should be the name of the service, and service_id (if specified) should be a string
        of the form "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX", where each 'X' is a hexadecimal
        digit.

    service_classes : list 
        a list of service classes whose this service belongs to.

        Each class service is a 16-bit UUID in the form "XXXX", where each 'X' is a
        hexadecimal digit, or a 128-bit UUID in the form "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX".
        There are some constants for standard services, e.g. SERIAL_PORT_CLASS that equals to
        "1101". Some class constants:

        =================   ========================   ==================
        SERIAL_PORT_CLASS   LAN_ACCESS_CLASS           DIALUP_NET_CLASS 
        HEADSET_CLASS       CORDLESS_TELEPHONY_CLASS   AUDIO_SOURCE_CLASS
        AUDIO_SINK_CLASS    PANU_CLASS                 NAP_CLASS
        GN_CLASS
        =================   ========================   ==================

    profiles : list
        A list of service profiles that thie service fulfills. Each profile is a tuple with 
        ( uuid, version). Most standard profiles use standard classes as UUIDs. PyBluez offers 
        a list of standard profiles, for example SERIAL_PORT_PROFILE. All standard profiles have
        the same name as the classes, except that _CLASS suffix is replaced by _PROFILE.

    provider : str
        A text string specifying the provider of the service

    description : str
        A text string describing the service

    protocols : list
        A list of protocols

    Notes
    -----
    A note on working with Symbian smartphones: bt_discover in Python for Series 60 will only 
    detect service records with service class SERIAL_PORT_CLASS and profile SERIAL_PORT_PROFILE

    """
    if service_id != "" and not is_valid_uuid (service_id):
        raise ValueError ("invalid UUID specified for service_id")
    for uuid in service_classes:
        if not is_valid_uuid (uuid):
            raise ValueError ("invalid UUID specified in service_classes")
    for uuid, version in profiles:
        if not is_valid_uuid (uuid) or  version < 0 or  version > 0xFFFF:
            raise ValueError ("Invalid Profile Descriptor")
    for uuid in protocols:
        if not is_valid_uuid (uuid):
            raise ValueError ("invalid UUID specified in protocols")        

    if sock._raw_sdp_record is not None:
        raise IOError ("service already advertised")

    avpairs = []

    # service UUID
    if len (service_id) > 0:
        avpairs.append (("UInt16", SERVICE_ID_ATTRID))
        avpairs.append (("UUID", service_id))

    # service class list
    if len (service_classes) > 0:
        seq = [ ("UUID", svc_class) for svc_class in service_classes ]
        avpairs.append (("UInt16", SERVICE_CLASS_ID_LIST_ATTRID))
        avpairs.append (("ElemSeq", seq))

    # set protocol and port information
    assert sock._proto == RFCOMM
    addr, port = sock.getsockname ()
    avpairs.append (("UInt16", PROTOCOL_DESCRIPTOR_LIST_ATTRID))
    l2cap_pd = ("ElemSeq", (("UUID", L2CAP_UUID),))
    rfcomm_pd = ("ElemSeq", (("UUID", RFCOMM_UUID), ("UInt8", port)))
    proto_list = [ l2cap_pd, rfcomm_pd ]
    for proto_uuid in protocols:
        proto_list.append (("ElemSeq", (("UUID", proto_uuid),)))
    avpairs.append (("ElemSeq", proto_list))

    # make the service publicly browseable
    avpairs.append (("UInt16", BROWSE_GROUP_LIST_ATTRID))
    avpairs.append (("ElemSeq", (("UUID", PUBLIC_BROWSE_GROUP),)))

    # profile descriptor list
    if len (profiles) > 0:
        seq = [ ("ElemSeq", (("UUID",uuid), ("UInt16",version))) \
                for uuid, version in profiles ]
        avpairs.append (("UInt16", 
            BLUETOOTH_PROFILE_DESCRIPTOR_LIST_ATTRID))
        avpairs.append (("ElemSeq", seq))

    # service name
    avpairs.append (("UInt16", SERVICE_NAME_ATTRID))
    avpairs.append (("String", name))

    # service description
    if len (description) > 0:
        avpairs.append (("UInt16", SERVICE_DESCRIPTION_ATTRID))
        avpairs.append (("String", description))
    
    # service provider
    if len (provider) > 0:
        avpairs.append (("UInt16", PROVIDER_NAME_ATTRID))
        avpairs.append (("String", provider))

    sock._raw_sdp_record = sdp_make_data_element ("ElemSeq", avpairs)
#    pr = sdp_parse_raw_record (sock._raw_sdp_record)
#    for attrid, val in pr.items ():
#        print "%5s: %s" % (attrid, val)
#    print binascii.hexlify (sock._raw_sdp_record)
#    print repr (sock._raw_sdp_record)

    sock._sdp_handle = bt.set_service_raw (sock._raw_sdp_record, True)

def stop_advertising (sock):
    if sock._raw_sdp_record is None:
        raise IOError ("service isn't advertised, " \
                        "but trying to un-advertise")
    bt.set_service_raw (sock._raw_sdp_record, False, sock._sdp_handle)
    sock._raw_sdp_record = None
    sock._sdp_handle = None

def find_service (name = None, uuid = None, address = None):
    if address is not None:
        addresses = [ address ]
    else:
        addresses = discover_devices (lookup_names = False)

    results = []

    for addr in addresses:
        uuidstr = uuid or PUBLIC_BROWSE_GROUP
        if not is_valid_uuid (uuidstr): raise ValueError ("invalid UUID")

        uuidstr = to_full_uuid (uuidstr)

        dresults = bt.find_service (addr, uuidstr)

        for dict in dresults:
            raw = dict["rawrecord"]

            record = sdp_parse_raw_record (raw)

            if SERVICE_CLASS_ID_LIST_ATTRID in record:
                svc_class_id_list = [ t[1] for t in \
                        record[SERVICE_CLASS_ID_LIST_ATTRID] ]
                dict["service-classes"] = svc_class_id_list
            else:
                dict["services-classes"] = []

            if BLUETOOTH_PROFILE_DESCRIPTOR_LIST_ATTRID in record:
                pdl = []
                for profile_desc in \
                        record[BLUETOOTH_PROFILE_DESCRIPTOR_LIST_ATTRID]:
                    uuidpair, versionpair = profile_desc[1]
                    pdl.append ((uuidpair[1], versionpair[1]))
                dict["profiles"] = pdl
            else:
                dict["profiles"] = []

            dict["provider"] = record.get (PROVIDER_NAME_ATTRID, None)

            dict["service-id"] = record.get (SERVICE_ID_ATTRID, None)

            # XXX the C version is buggy (retrieves an extra byte or two),
            # so get the service name here even though it may have already
            # been set
            dict["name"] = record.get (SERVICE_NAME_ATTRID, None)

            dict["handle"] = record.get (SERVICE_RECORD_HANDLE_ATTRID, None)
        
#        if LANGUAGE_BASE_ATTRID_LIST_ATTRID in record:
#            for triple in record[LANGUAGE_BASE_ATTRID_LIST_ATTRID]:
#                code_ISO639, encoding, base_offset = triple
#
#        if SERVICE_DESCRIPTION_ATTRID in record:
#            service_description = record[SERVICE_DESCRIPTION_ATTRID]

        if name is None:
            results.extend (dresults)
        else:
            results.extend ([ d for d in dresults if d["name"] == name ])
    return results

# =============== DeviceDiscoverer ==================
class DeviceDiscoverer:
    """Not implemented on Windows yet."""
    def __init__ (self):
        """No implementation yet.

        Raises
        ------
        NotImplementedError

        """
        raise NotImplementedError
