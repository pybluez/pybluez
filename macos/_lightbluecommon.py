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

# Defines attributes with common implementations across the different
# platforms.


# public attributes
__all__ = ("L2CAP", "RFCOMM", "OBEX", "BluetoothError", "splitclass")


# Protocol/service class types, used for sockets and advertising services
L2CAP, RFCOMM, OBEX = (10, 11, 12)


class BluetoothError(IOError):
    """
    Generic exception raised for Bluetooth errors. This is not raised for
    socket-related errors; socket objects raise the socket.error and
    socket.timeout exceptions from the standard library socket module.

    Note that error codes are currently platform-independent. In particular,
    the Mac OS X implementation returns IOReturn error values from the IOKit
    framework, and OBEXError codes from <IOBluetooth/OBEX.h> for OBEX operations.
    """
    pass


def splitclass(classofdevice):
    """
    Splits the given class of device to return a 3-item tuple with the
    major service class, major device class and minor device class values.

    These values indicate the device's major services and the type of the
    device (e.g. mobile phone, laptop, etc.). If you google for
    "assigned numbers bluetooth baseband" you might find some documents
    that discuss how to extract this information from the class of device.

    Example:
        >>> splitclass(1057036)
        (129, 1, 3)
        >>>
    """
    if not isinstance(classofdevice, int):
        try:
            classofdevice = int(classofdevice)
        except (TypeError, ValueError):
            raise TypeError("Given device class '%s' cannot be split" % \
                str(classofdevice))

    data = classofdevice >> 2   # skip over the 2 "format" bits
    service = data >> 11
    major = (data >> 6) & 0x1F
    minor = data & 0x3F
    return (service, major, minor)


_validbtaddr = None
def _isbtaddr(address):
    """
    Returns whether the given address is a valid bluetooth address.
    For example, "00:0e:6d:7b:a2:0a" is a valid address.

    Returns False if the argument is None or is not a string.
    """
    # Define validity regex. Accept either ":" or "-" as separators.
    global _validbtaddr
    if _validbtaddr is None:
        import re
        _validbtaddr = re.compile(r"((\d|[a-f]){2}(:|-)){5}(\d|[a-f]){2}",
                re.IGNORECASE)
    import types
    if not isinstance(address, str):
        return False
    return _validbtaddr.match(address) is not None


# --------- other attributes ---------

def _joinclass(codtuple):
    """
    The opposite of splitclass(). Joins a (service, major, minor) class-of-
    device tuple into a whole class of device value.
    """
    if not isinstance(codtuple, tuple):
        raise TypeError("argument must be tuple, was %s" % type(codtuple))
    if len(codtuple) != 3:
        raise ValueError("tuple must have 3 items, has %d" % len(codtuple))

    serviceclass = codtuple[0] << 2 << 11
    majorclass = codtuple[1] << 2 << 6
    minorclass = codtuple[2] << 2
    return (serviceclass | majorclass | minorclass)


# Docstrings for socket objects.
# Based on std lib socket docs.
_socketdocs = {
"accept":
    """
    accept() -> (socket object, address info)

    Wait for an incoming connection. Return a new socket representing the
    connection, and the address of the client. For RFCOMM sockets, the address
    info is a pair (hostaddr, channel).

    The socket must be bound and listening before calling this method.
    """,
"bind":
    """
    bind(address)

    Bind the socket to a local address. For RFCOMM sockets, the address is a
    pair (host, channel); the host must refer to the local host.

    A port value of 0 binds the socket to a dynamically assigned port.
    (Note that on Mac OS X, the port value must always be 0.)

    The socket must not already be bound.
    """,
"close":
    """
    close()

    Close the socket.  It cannot be used after this call.
    """,
"connect":
    """
    connect(address)

    Connect the socket to a remote address. The address should be a
    (host, channel) pair for RFCOMM sockets, and a (host, PSM) pair for L2CAP
    sockets.

    The socket must not be already connected.
    """,
"connect_ex":
    """
    connect_ex(address) -> errno

    This is like connect(address), but returns an error code instead of raising
    an exception when an error occurs.
    """,
"dup":
    """
    dup() -> socket object

    Returns a new socket object connected to the same system resource.
    """,
"fileno":
    """
    fileno() -> integer

    Return the integer file descriptor of the socket.

    Raises NotImplementedError on Mac OS X and Python For Series 60.
    """,
"getpeername":
    """
    getpeername() -> address info

    Return the address of the remote endpoint. The address info is a
    (host, channel) pair for RFCOMM sockets, and a (host, PSM) pair for L2CAP
    sockets.

    If the socket has not been connected, socket.error will be raised.
    """,
"getsockname":
    """
    getsockname() -> address info

    Return the address of the local endpoint. The address info is a
    (host, channel) pair for RFCOMM sockets, and a (host, PSM) pair for L2CAP
    sockets.

    If the socket has not been connected nor bound, this returns the tuple
    ("00:00:00:00:00:00", 0).
    """,
"getsockopt":
    """
    getsockopt(level, option[, bufsize]) -> value

    Get a socket option.  See the Unix manual for level and option.
    If a nonzero buffersize argument is given, the return value is a
    string of that length; otherwise it is an integer.

    Currently support for socket options are platform independent -- i.e.
    depends on the underlying Series 60 or BlueZ socket options support.
    The Mac OS X implementation currently does not support any options at
    all and automatically raises socket.error.
    """,
"gettimeout":
    """
    gettimeout() -> timeout

    Returns the timeout in floating seconds associated with socket
    operations. A timeout of None indicates that timeouts on socket
    operations are disabled.

    Currently not supported on Python For Series 60 implementation, which
    will always return None.
    """,
"listen":
    """
    listen(backlog)

    Enable a server to accept connections. The backlog argument must be at
    least 1; it specifies the number of unaccepted connection that the system
    will allow before refusing new connections.

    The socket must not be already listening.

    Currently not implemented on Mac OS X.
    """,
"makefile":
    """
    makefile([mode[, bufsize]]) -> file object

    Returns a regular file object corresponding to the socket.  The mode
    and bufsize arguments are as for the built-in open() function.
    """,
"recv":
    """
    recv(bufsize[, flags]) -> data

    Receive up to bufsize bytes from the socket.  For the optional flags
    argument, see the Unix manual.  When no data is available, block until
    at least one byte is available or until the remote end is closed.  When
    the remote end is closed and all data is read, return the empty string.

    Currently the flags argument has no effect on Mac OS X.
    """,
"recvfrom":
    """
    recvfrom(bufsize[, flags]) -> (data, address info)

    Like recv(buffersize, flags) but also return the sender's address info.
    """,
"send":
    """
    send(data[, flags]) -> count

    Send a data string to the socket.  For the optional flags
    argument, see the Unix manual.  Return the number of bytes
    sent.

    The socket must be connected to a remote socket.

    Currently the flags argument has no effect on Mac OS X.
    """,
"sendall":
    """
    sendall(data[, flags])

    Send a data string to the socket.  For the optional flags
    argument, see the Unix manual.  This calls send() repeatedly
    until all data is sent.  If an error occurs, it's impossible
    to tell how much data has been sent.
    """,
"sendto":
    """
    sendto(data[, flags], address) -> count

    Like send(data, flags) but allows specifying the destination address.
    For RFCOMM sockets, the address is a pair (hostaddr, channel).
    """,
"setblocking":
    """
    setblocking(flag)

    Set the socket to blocking (flag is true) or non-blocking (false).
    setblocking(True) is equivalent to settimeout(None);
    setblocking(False) is equivalent to settimeout(0.0).

    Initially a socket is in blocking mode. In non-blocking mode, if a
    socket operation cannot be performed immediately, socket.error is raised.

    The underlying implementation on Python for Series 60 only supports
    non-blocking mode for send() and recv(), and ignores it for connect() and
    accept().
    """,
"setsockopt":
    """
    setsockopt(level, option, value)

    Set a socket option.  See the Unix manual for level and option.
    The value argument can either be an integer or a string.

    Currently support for socket options are platform independent -- i.e.
    depends on the underlying Series 60 or BlueZ socket options support.
    The Mac OS X implementation currently does not support any options at
    all and automatically raise socket.error.
    """,
"settimeout":
    """
    settimeout(timeout)

    Set a timeout on socket operations.  'timeout' can be a float,
    giving in seconds, or None.  Setting a timeout of None disables
    the timeout feature and is equivalent to setblocking(1).
    Setting a timeout of zero is the same as setblocking(0).

    If a timeout is set, the connect, accept, send and receive operations will
    raise socket.timeout if a timeout occurs.

    Raises NotImplementedError on Python For Series 60.
    """,
"shutdown":
    """
    shutdown(how)

    Shut down the reading side of the socket (flag == socket.SHUT_RD), the
    writing side of the socket (flag == socket.SHUT_WR), or both ends
    (flag == socket.SHUT_RDWR).
    """
}

