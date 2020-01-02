import array
import fcntl
import sys
import struct
from errno import (EADDRINUSE, EBUSY, EINVAL)

from bluetooth.btcommon import *
import bluetooth._bluetooth as _bt
from bluetooth._bluetooth import HCI, RFCOMM, L2CAP, SCO, SOL_L2CAP, \
                                    SOL_RFCOMM, L2CAP_OPTIONS

get_byte = int

# ============== SDP service registration and unregistration ============

def discover_devices (duration=8, flush_cache=True, lookup_names=False,
                      lookup_class=False, device_id=-1, iac=IAC_GIAC):
    if device_id == -1:
        device_id = _bt.hci_get_route()

    sock = _gethcisock (device_id)
    try:
        results = _bt.hci_inquiry (sock, duration=duration, flush_cache=True,
                                   lookup_class=lookup_class, device_id=device_id,
                                   iac=iac)
    except _bt.error as e:
        sock.close ()
        raise BluetoothError (e.args[0], "Error communicating with local "
        "bluetooth adapter: " + e.args[1])

    if lookup_names:
        pairs = []
        for item in results:
            if lookup_class:
                addr, dev_class = item
            else:
                addr = item
            timeoutms = int (10 * 1000)
            try:
                name = _bt.hci_read_remote_name (sock, addr, timeoutms)
            except _bt.error:
                # name lookup failed.  either a timeout, or I/O error
                continue
            pairs.append ((addr, name, dev_class) if lookup_class else (addr, name))
        sock.close ()
        return pairs
    else:
        sock.close ()
        return results

def read_local_bdaddr():
    try:
        hci_sock = _bt.hci_open_dev(0)
        old_filter = hci_sock.getsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, 14)
        flt = _bt.hci_filter_new()
        opcode = _bt.cmd_opcode_pack(_bt.OGF_INFO_PARAM,
                _bt.OCF_READ_BD_ADDR)
        _bt.hci_filter_set_ptype(flt, _bt.HCI_EVENT_PKT)
        _bt.hci_filter_set_event(flt, _bt.EVT_CMD_COMPLETE)
        _bt.hci_filter_set_opcode(flt, opcode)
        hci_sock.setsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, flt )

        _bt.hci_send_cmd(hci_sock, _bt.OGF_INFO_PARAM, _bt.OCF_READ_BD_ADDR )

        pkt = hci_sock.recv(255)

        status,raw_bdaddr = struct.unpack("xxxxxxB6s", pkt)
        assert status == 0

        t = [ "%02X" % get_byte(b) for b in raw_bdaddr ]
        t.reverse()
        bdaddr = ":".join(t)

        # restore old filter
        hci_sock.setsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, old_filter )
        return [bdaddr]
    except _bt.error as e:
        raise BluetoothError(*e.args)

def lookup_name (address, timeout=10):
    if not is_valid_address (address):
        raise BluetoothError (EINVAL, "%s is not a valid Bluetooth address" % address)

    sock = _gethcisock ()
    timeoutms = int (timeout * 1000)
    try:
        name = _bt.hci_read_remote_name (sock, address, timeoutms)
    except _bt.error:
        # name lookup failed.  either a timeout, or I/O error
        name = None
    sock.close ()
    return name

def set_packet_timeout (address, timeout):
    """
    Adjusts the ACL flush timeout for the ACL connection to the specified
    device.  This means that all L2CAP and RFCOMM data being sent to that
    device will be dropped if not acknowledged in timeout milliseconds (maximum
    1280).  A timeout of 0 means to never drop packets.

    Since this affects all Bluetooth connections to that device, and not just
    those initiated by this process or PyBluez, a call to this method requires
    superuser privileges.

    You must have an active connection to the specified device before invoking
    this method.

    """
    n = round (timeout / 0.625)
    write_flush_timeout (address, n)

def get_l2cap_options (sock):
    """get_l2cap_options (sock, mtu)

    Gets L2CAP options for the specified L2CAP socket.
    Options are: omtu, imtu, flush_to, mode, fcs, max_tx, txwin_size.

    """
    # TODO this should be in the C module, because it depends
    # directly on struct l2cap_options layout.
    s = sock.getsockopt (SOL_L2CAP, L2CAP_OPTIONS, 12)
    options = list( struct.unpack ("HHHBBBH", s))
    return options

def set_l2cap_options (sock, options):
    """set_l2cap_options (sock, options)

    Sets L2CAP options for the specified L2CAP socket.
    The option list must be in the same format supplied by
    get_l2cap_options().

    """
    # TODO this should be in the C module, because it depends
    # directly on struct l2cap_options layout.
    s = struct.pack ("HHHBBBH", *options)
    sock.setsockopt (SOL_L2CAP, L2CAP_OPTIONS, s)

def set_l2cap_mtu (sock, mtu):
    """set_l2cap_mtu (sock, mtu)

    Adjusts the MTU for the specified L2CAP socket.  This method needs to be
    invoked on both sides of the connection for it to work!  The default mtu
    that all L2CAP connections start with is 672 bytes.

    mtu must be between 48 and 65535, inclusive.

    """
    options = get_l2cap_options (sock)
    options[0] = options[1] = mtu
    set_l2cap_options (sock, options)

def _get_available_ports(protocol):
    if protocol == RFCOMM:
        return range (1, 31)
    elif protocol == L2CAP:
        return range (0x1001, 0x8000, 2)
    else:
        return [0]

class BluetoothSocket:
    __doc__ = _bt.btsocket.__doc__

    def __init__ (self, proto = RFCOMM, _sock=None):
        if _sock is None:
            _sock = _bt.btsocket (proto)
        self._sock = _sock
        self._proto = proto

    def dup (self):
        """dup () -> socket object

        Return a new socket object connected to the same system resource.
        
        """
        return BluetoothSocket (proto=self._proto, _sock=self._sock)

    def accept (self):
        try:
            client, addr = self._sock.accept ()
        except _bt.error as e:
            raise BluetoothError (*e.args)
        newsock = BluetoothSocket (self._proto, client)
        return (newsock, addr)
    accept.__doc__ = _bt.btsocket.accept.__doc__

    def bind (self, addrport):
        if len (addrport) != 2 or addrport[1] != 0:
            try:
                return self._sock.bind (addrport)
            except _bt.error as e:
                raise BluetoothError (*e.args)
        addr, _ = addrport
        for port in _get_available_ports (self._proto):
            try:
                return self._sock.bind ((addr, port))
            except _bt.error as e:
                err = BluetoothError (*e.args)
                if err.errno != EADDRINUSE:
                    break
        raise err

    def get_l2cap_options(self):
        """get_l2cap_options (sock, mtu)

        Gets L2CAP options for the specified L2CAP socket.
        Options are: omtu, imtu, flush_to, mode, fcs, max_tx, txwin_size.

        """
        return get_l2cap_options(self)

    def set_l2cap_options(self, options):
        """set_l2cap_options (sock, options)

        Sets L2CAP options for the specified L2CAP socket.
        The option list must be in the same format supplied by
        get_l2cap_options().

        """
        return set_l2cap_options(self, options)

    def set_l2cap_mtu(self, mtu):
        """set_l2cap_mtu (sock, mtu)

        Adjusts the MTU for the specified L2CAP socket.  This method needs to be
        invoked on both sides of the connection for it to work!  The default mtu
        that all L2CAP connections start with is 672 bytes.

        mtu must be between 48 and 65535, inclusive.

        """
        return set_l2cap_mtu(self, mtu)

    # import methods from the wraapped socket object
    _s = ("""def %s (self, *args, **kwargs):
    try:
        return self._sock.%s (*args, **kwargs)
    except _bt.error as e:
        raise BluetoothError (*e.args)
    %s.__doc__ = _bt.btsocket.%s.__doc__\n""")
    for _m in ( 'connect', 'connect_ex', 'close',
        'fileno', 'getpeername', 'getsockname', 'gettimeout',
        'getsockopt', 'listen', 'makefile', 'recv', 'recvfrom', 'sendall',
        'send', 'sendto', 'setblocking', 'setsockopt', 'settimeout',
        'shutdown', 'setl2capsecurity'):
        exec( _s % (_m, _m, _m, _m))
    del _m, _s

    # import readonly attributes from the wrapped socket object
    _s = ("@property\ndef %s (self): \
    return self._sock.%s")
    for _m in ('family', 'type', 'proto', 'timeout'):
        exec( _s % (_m, _m))
    del _m, _s


def advertise_service (sock, name, service_id = "", service_classes = [], \
        profiles = [], provider = "", description = "", protocols = []):
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

    try:
        _bt.sdp_advertise_service (sock._sock, name, service_id, \
                service_classes, profiles, provider, description, \
                protocols)
    except _bt.error as e:
        raise BluetoothError (*e.args)

def stop_advertising (sock):
    try:
        _bt.sdp_stop_advertising (sock._sock)
    except _bt.error as e:
        raise BluetoothError (*e.args)

def find_service (name = None, uuid = None, address = None):
    if not address:
        devices = discover_devices ()
    else:
        devices = [ address ]

    results = []

    if uuid is not None and not is_valid_uuid (uuid):
        raise ValueError ("invalid UUID")

    try:
        for addr in devices:
            try:
                s = _bt.SDPSession ()
                s.connect (addr)
                matches = []
                if uuid is not None:
                    matches = s.search (uuid)
                else:
                    matches = s.browse ()
            except _bt.error:
                continue

            if name is not None:
                matches = [s for s in matches if s.get ("name", "") == name]

            for m in matches:
                m["host"] = addr

            results.extend (matches)
    except _bt.error as e:
        raise BluetoothError (*e.args)

    return results

# ================ BlueZ internal methods ================
def _gethcisock (device_id = -1):
    try:
        sock = _bt.hci_open_dev (device_id)
    except _bt.error as e:
        raise BluetoothError (e.args[0], "error accessing bluetooth device: " +
                              e.args[1])
    return sock

def get_acl_conn_handle (hci_sock, addr):
    hci_fd = hci_sock.fileno ()
    reqstr = struct.pack ("6sB17s", _bt.str2ba (addr),
            _bt.ACL_LINK, b"\0" * 17)
    request = array.array ("b", reqstr)
    try:
        fcntl.ioctl (hci_fd, _bt.HCIGETCONNINFO, request, 1)
    except OSError as e:
        raise BluetoothError (e.args[0], "There is no ACL connection to %s" % addr)

    # XXX should this be "<8xH14x"?
    handle = struct.unpack ("8xH14x", request.tostring ())[0]
    return handle

def write_flush_timeout (addr, timeout):
    hci_sock = _bt.hci_open_dev ()
    # get the ACL connection handle to the remote device
    handle = get_acl_conn_handle (hci_sock, addr)
    # XXX should this be "<HH"
    pkt = struct.pack ("HH", handle, _bt.htobs (timeout))
    response = _bt.hci_send_req (hci_sock, _bt.OGF_HOST_CTL,
        0x0028, _bt.EVT_CMD_COMPLETE, 3, pkt)
    status = get_byte(response[0])
    rhandle = struct.unpack ("H", response[1:3])[0]
    assert rhandle == handle
    assert status == 0

def read_flush_timeout (addr):
    hci_sock = _bt.hci_open_dev ()
    # get the ACL connection handle to the remote device
    handle = get_acl_conn_handle (hci_sock, addr)
    # XXX should this be "<H"?
    pkt = struct.pack ("H", handle)
    response = _bt.hci_send_req (hci_sock, _bt.OGF_HOST_CTL,
        0x0027, _bt.EVT_CMD_COMPLETE, 5, pkt)
    status = get_byte(response[0])
    rhandle = struct.unpack ("H", response[1:3])[0]
    assert rhandle == handle
    assert status == 0
    fto = struct.unpack ("H", response[3:5])[0]
    return fto

# =============== DeviceDiscoverer ==================
def byte_to_signed_int(byte_):
    if byte_ > 127:
        return byte_ - 256
    else:
        return byte_

class DeviceDiscoverer:
    """
    Skeleton class for finer control of the device discovery process.

    To implement asynchronous device discovery (e.g. if you want to do
    something *as soon as* a device is discovered), subclass
    DeviceDiscoverer and override device_discovered () and
    inquiry_complete ()
    """
    def __init__ (self, device_id=-1):
        """
        __init__ (device_id=-1)

        device_id - The ID of the Bluetooth adapter that will be used
                    for discovery.
        """
        self.sock = None
        self.is_inquiring = False
        self.lookup_names = False
        self.device_id = device_id

        self.names_to_find = {}
        self.names_found = {}

    def find_devices (self, lookup_names=True,
            duration=8,
            flush_cache=True):
        """
        find_devices (lookup_names=True, service_name=None,
                       duration=8, flush_cache=True)

        Call this method to initiate the device discovery process

        lookup_names - set to True if you want to lookup the user-friendly
                       names for each device found.

        service_name - set to the name of a service you're looking for.
                       only devices with a service of this name will be
                       returned in device_discovered () NOT YET IMPLEMENTED


        ADVANCED PARAMETERS:  (don't change these unless you know what
                            you're doing)

        duration - the number of 1.2 second units to spend searching for
                   bluetooth devices.  If lookup_names is True, then the
                   inquiry process can take a lot longer.

        flush_cache - return devices discovered in previous inquiries
        """
        if self.is_inquiring:
            raise BluetoothError (EBUSY, "Already inquiring!")

        self.lookup_names = lookup_names

        self.sock = _gethcisock (self.device_id)
        flt = _bt.hci_filter_new ()
        _bt.hci_filter_all_events (flt)
        _bt.hci_filter_set_ptype (flt, _bt.HCI_EVENT_PKT)

        try:
            self.sock.setsockopt (_bt.SOL_HCI, _bt.HCI_FILTER, flt)
        except _bt.error as e:
            raise BluetoothError (*e.args)

        # send the inquiry command
        max_responses = 255
        cmd_pkt = struct.pack ("BBBBB", 0x33, 0x8b, 0x9e, \
                duration, max_responses)

        self.pre_inquiry ()

        try:
            _bt.hci_send_cmd (self.sock, _bt.OGF_LINK_CTL, \
                    _bt.OCF_INQUIRY, cmd_pkt)
        except _bt.error as e:
            raise BluetoothError (*e.args)

        self.is_inquiring = True

        self.names_to_find = {}
        self.names_found = {}

    def cancel_inquiry (self):
        """
        Call this method to cancel an inquiry in process.  inquiry_complete
        will still be called.
        """
        self.names_to_find = {}

        if self.is_inquiring:
            try:
                _bt.hci_send_cmd (self.sock, _bt.OGF_LINK_CTL, \
                        _bt.OCF_INQUIRY_CANCEL)
            except _bt.error as e:
                self.sock.close ()
                self.sock = None
                raise BluetoothError (e.args[0],
                                      "error canceling inquiry: " +
                                      e.args[1])
            self.is_inquiring = False

    def process_inquiry (self):
        """
        Repeatedly calls process_event () until the device inquiry has
        completed.
        """
        while self.is_inquiring or len (self.names_to_find) > 0:
            self.process_event ()

    def process_event (self):
        """
        Waits for one event to happen, and proceses it.  The event will be
        either a device discovery, or an inquiry completion.
        """
        self._process_hci_event ()

    def _process_hci_event (self):
        # FIXME may not wrap _bluetooth.error properly
        if self.sock is None: return
        # voodoo magic!!!
        pkt = self.sock.recv (258)
        ptype, event, plen = struct.unpack ("BBB", pkt[:3])
        pkt = pkt[3:]
        if event == _bt.EVT_INQUIRY_RESULT:
            nrsp = get_byte(pkt[0])
            for i in range (nrsp):
                addr = _bt.ba2str (pkt[1+6*i:1+6*i+6])
                psrm = pkt[ 1+6*nrsp+i ]
                pspm = pkt[ 1+7*nrsp+i ]
                devclass_raw = struct.unpack ("BBB",
                        pkt[1+9*nrsp+3*i:1+9*nrsp+3*i+3])
                devclass = (devclass_raw[2] << 16) | \
                        (devclass_raw[1] << 8) | \
                        devclass_raw[0]
                clockoff = pkt[1+12*nrsp+2*i:1+12*nrsp+2*i+2]

                self._device_discovered (addr, devclass,
                        psrm, pspm, clockoff, None, None)
        elif event == _bt.EVT_INQUIRY_RESULT_WITH_RSSI:
            nrsp = get_byte(pkt[0])
            for i in range (nrsp):
                addr = _bt.ba2str (pkt[1+6*i:1+6*i+6])
                psrm = pkt[ 1+6*nrsp+i ]
                pspm = pkt[ 1+7*nrsp+i ]
#                devclass_raw = pkt[1+8*nrsp+3*i:1+8*nrsp+3*i+3]
#                devclass = struct.unpack ("I", "%s\0" % devclass_raw)[0]
                devclass_raw = struct.unpack ("BBB",
                        pkt[1+8*nrsp+3*i:1+8*nrsp+3*i+3])
                devclass = (devclass_raw[2] << 16) | \
                        (devclass_raw[1] << 8) | \
                        devclass_raw[0]
                clockoff = pkt[1+11*nrsp+2*i:1+11*nrsp+2*i+2]
                rssi = byte_to_signed_int(get_byte(pkt[1+13*nrsp+i]))

                self._device_discovered (addr, devclass,
                        psrm, pspm, clockoff, rssi, None)
        elif _bt.HAVE_EVT_EXTENDED_INQUIRY_RESULT and event == _bt.EVT_EXTENDED_INQUIRY_RESULT:
            nrsp = get_byte(pkt[0])
            for i in range (nrsp):
                addr = _bt.ba2str (pkt[1+6*i:1+6*i+6])
                psrm = pkt[ 1+6*nrsp+i ]
                pspm = pkt[ 1+7*nrsp+i ]
                devclass_raw = struct.unpack ("BBB",
                        pkt[1+8*nrsp+3*i:1+8*nrsp+3*i+3])
                devclass = (devclass_raw[2] << 16) | \
                        (devclass_raw[1] << 8) | \
                        devclass_raw[0]
                clockoff = pkt[1+11*nrsp+2*i:1+11*nrsp+2*i+2]
                rssi = byte_to_signed_int(get_byte(pkt[1+13*nrsp+i]))

                data_len = _bt.EXTENDED_INQUIRY_INFO_SIZE - _bt.INQUIRY_INFO_WITH_RSSI_SIZE
                data = pkt[1+14*nrsp+i:1+14*nrsp+i+data_len]
                name = None
                pos = 0
                while(pos <= len(data)):
                    struct_len = get_byte(data[pos])
                    if struct_len == 0:
                        break
                    eir_type = get_byte(data[pos+1])
                    if eir_type == 0x09: # Complete local name
                        name = data[pos+2:pos+struct_len+1]
                    pos += struct_len + 2

                self._device_discovered (addr, devclass,
                        psrm, pspm, clockoff, rssi, name)
        elif event == _bt.EVT_INQUIRY_COMPLETE or event == _bt.EVT_CMD_COMPLETE:
            self.is_inquiring = False
            if len (self.names_to_find) == 0:
#                print "inquiry complete (evt_inquiry_complete)"
                self.sock.close ()
                self._inquiry_complete ()
            else:
                self._send_next_name_req ()

        elif event == _bt.EVT_CMD_STATUS:
            # XXX shold this be "<BBH"
            status, ncmd, opcode = struct.unpack ("BBH", pkt[:4])
            if status != 0:
                self.is_inquiring = False
                self.sock.close ()

#                print "inquiry complete (bad status 0x%X 0x%X 0x%X)" % \
#                        (status, ncmd, opcode)
                self.names_to_find = {}
                self._inquiry_complete ()
        elif event == _bt.EVT_REMOTE_NAME_REQ_COMPLETE:
            status = get_byte(pkt[0])
            addr = _bt.ba2str (pkt[1:7])
            if status == 0:
                try:
                    name = pkt[7:].split ('\0')[0]
                except IndexError:
                    name = ''
                if addr in self.names_to_find:
                    device_class, rssi = self.names_to_find[addr][:2]
                    self.device_discovered (addr, device_class, rssi, name)
                    del self.names_to_find[addr]
                    self.names_found[addr] = ( device_class, rssi, name)
                else:
                    pass
            else:
                if addr in self.names_to_find: del self.names_to_find[addr]
                # XXX should we do something when a name lookup fails?
#                print "name req unsuccessful %s - %s" % (addr, status)

            if len (self.names_to_find) == 0:
                self.is_inquiring = False
                self.sock.close ()
                self.inquiry_complete ()
#                print "inquiry complete (name req complete)"
            else:
                self._send_next_name_req ()
        else:
            pass
#            print "unrecognized packet type 0x%02x" % ptype

    def _device_discovered (self, address, device_class,
            psrm, pspm, clockoff, rssi, name):
        if self.lookup_names:
            if name is not None:
                self.device_discovered (address, device_class, rssi, name)
            elif address not in self.names_found and \
                address not in self.names_to_find:

                self.names_to_find[address] = \
                    (device_class, rssi, psrm, pspm, clockoff)
        else:
            self.device_discovered (address, device_class, rssi, None)

    def _send_next_name_req (self):
        assert len (self.names_to_find) > 0
        address = list(self.names_to_find.keys ())[0]
        device_class, rssi, psrm, pspm, clockoff = self.names_to_find[address]
        bdaddr = _bt.str2ba (address) #TODO not supported in python3

        cmd_pkt = "{}{}\0{}".format(bdaddr, psrm, clockoff)

        try:
            _bt.hci_send_cmd (self.sock, _bt.OGF_LINK_CTL, \
                    _bt.OCF_REMOTE_NAME_REQ, cmd_pkt)
        except _bt.error as e:
            raise BluetoothError (e.args[0],
                                  "error request name of %s - %s:" %
                    (address, e.args[1]))

    def fileno (self):
        if not self.sock: return None
        return self.sock.fileno ()

    def pre_inquiry (self):
        """
        Called just after find_devices is invoked, but just before the
        inquiry is started.

        This method exists to be overriden
        """

    def device_discovered (self, address, device_class, rssi, name):
        """
        Called when a bluetooth device is discovered.

        address is the bluetooth address of the device

        device_class is the Class of Device, as specified in [1]
                     passed in as a 3-byte string

        name is the user-friendly name of the device if lookup_names was
        set when the inquiry was started.  otherwise None

        This method exists to be overriden.

        [1] https://www.bluetooth.org/foundry/assignnumb/document/baseband
        """
        if name:
            print("found: {} - {} (class 0x{:X}, rssi {})".format(
                address, name, device_class, rssi))
        else:
            print("found: {} (class 0x{:X})".format(address, device_class))
            print("found: {} (class 0x{:X}, rssi {})".format(
                address, device_class, rssi))

    def _inquiry_complete (self):
        """
        Called when an inquiry started by find_devices has completed.
        """
        self.sock.close ()
        self.sock = None
        self.inquiry_complete()

    def inquiry_complete (self):
        """
        Called when an inquiry started by find_devices has completed.
        """
        print("inquiry complete")
