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


import _lightbluecommon

__all__ = ('OBEXResponse', 'OBEXError',
     'CONTINUE', 'OK', 'CREATED', 'ACCEPTED', 'NON_AUTHORITATIVE_INFORMATION',
     'NO_CONTENT', 'RESET_CONTENT', 'PARTIAL_CONTENT',
     'MULTIPLE_CHOICES', 'MOVED_PERMANENTLY', 'MOVED_TEMPORARILY', 'SEE_OTHER',
     'NOT_MODIFIED', 'USE_PROXY',
     'BAD_REQUEST', 'UNAUTHORIZED', 'PAYMENT_REQUIRED', 'FORBIDDEN',
     'NOT_FOUND', 'METHOD_NOT_ALLOWED', 'NOT_ACCEPTABLE',
     'PROXY_AUTHENTICATION_REQUIRED', 'REQUEST_TIME_OUT', 'CONFLICT', 'GONE',
     'LENGTH_REQUIRED', 'PRECONDITION_FAILED', 'REQUESTED_ENTITY_TOO_LARGE',
     'REQUEST_URL_TOO_LARGE', 'UNSUPPORTED_MEDIA_TYPE',
     'INTERNAL_SERVER_ERROR', 'NOT_IMPLEMENTED', 'BAD_GATEWAY',
     'SERVICE_UNAVAILABLE', 'GATEWAY_TIMEOUT', 'HTTP_VERSION_NOT_SUPPORTED',
     'DATABASE_FULL', 'DATABASE_LOCKED')


class OBEXError(_lightbluecommon.BluetoothError):
    """
    Generic exception raised for OBEX-related errors.
    """
    pass


class OBEXResponse:
    """
    Contains the OBEX response received from an OBEX server.

    When an OBEX client sends a request, the OBEX server sends back a response
    code (to indicate whether the request was successful) and a set of response
    headers (to provide other useful information).

    For example, if a client sends a 'Get' request to retrieve a file, the
    client might get a response like this:

        >>> import lightblue
        >>> client = lightblue.obex.OBEXClient("aa:bb:cc:dd:ee:ff", 10)
        >>> response = client.get({"name": "file.txt"}, file("file.txt", "w"))
        >>> print response
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={'length': 35288}>

    You can get the response code and response headers in different formats:

        >>> print response.reason
        'OK'    # a string description of the response code
        >>> print response.code
        32      # the response code (e.g. this is 0x20)
        >>> print response.headers
        {'length': 35288}   # the headers, with string keys
        >>> print response.rawheaders
        {195: 35288}        # the headers, with raw header ID keys
        >>>

    Note how the 'code' attribute does not have the final bit set - e.g. for
    OK/Success, the response code is 0x20, not 0xA0.

    The lightblue.obex module defines constants for response code values (e.g.
    lightblue.obex.OK, lightblue.obex.FORBIDDEN, etc.).
    """

    def __init__(self, code, rawheaders):
        self.__code = code
        self.__reason = _OBEX_RESPONSES.get(code, "Unknown response code")
        self.__rawheaders = rawheaders
        self.__headers = None
    code = property(lambda self: self.__code,
            doc='The response code, without the final bit set.')
    reason = property(lambda self: self.__reason,
            doc='A string description of the response code.')
    rawheaders = property(lambda self: self.__rawheaders,
            doc='The response headers, as a dictionary with header ID (unsigned byte) keys.')

    def getheader(self, header, default=None):
        '''
        Returns the response header value for the given header, which may
        either be a string (not case-sensitive) or the raw byte
        value of the header ID.

        Returns the specified default value if the header is not present.
        '''
        if isinstance(header, types.StringTypes):
            return self.headers.get(header.lower(), default)
        return self.__rawheaders.get(header, default)

    def __getheaders(self):
        if self.__headers is None:
            self.__headers = {}
            for headerid, value in self.__rawheaders.items():
                if headerid in _HEADER_IDS_TO_STRINGS:
                    self.__headers[_HEADER_IDS_TO_STRINGS[headerid]] = value
                else:
                    self.__headers["0x%02x" % headerid] = value
        return self.__headers
    headers = property(__getheaders,
            doc='The response headers, as a dictionary with string keys.')

    def __repr__(self):
        return "<OBEXResponse reason='%s' code=0x%02x (0x%02x) headers=%s>" % \
            (self.__reason, self.__code, (self.__code | 0x80), str(self.headers))


try:
    import datetime
    # as from python docs example
    class UTC(datetime.tzinfo):
        """UTC"""
    
        def utcoffset(self, dt):
            return datetime.timedelta(0)
    
        def tzname(self, dt):
            return "UTC"
    
        def dst(self, dt):
            return datetime.timedelta(0)
except:
    pass    # no datetime on pys60


_LOCAL_TIME_FORMAT = "%Y%m%dT%H%M%S"
_UTC_TIME_FORMAT = _LOCAL_TIME_FORMAT + "Z"
def _datetimefromstring(s):
    import time
    if s[-1:] == "Z":
        # add UTC() instance as tzinfo
        args = (time.strptime(s, _UTC_TIME_FORMAT)[0:6]) + (0, UTC())
        return datetime.datetime(*args)
    else:
        return datetime.datetime(*(time.strptime(s, _LOCAL_TIME_FORMAT)[0:6]))


_HEADER_STRINGS_TO_IDS = {
    "count": 0xc0,
    "name": 0x01,
    "type": 0x42,
    "length": 0xc3,
    "time": 0x44,
    "description": 0x05,
    "target": 0x46,
    "http": 0x47,
    "who": 0x4a,
    "connection-id": 0xcb,
    "application-parameters": 0x4c,
    "authentication-challenge": 0x4d,
    "authentication-response": 0x4e,
    "creator-id": 0xcf,
    "wan-uuid": 0x50,
    "object-class": 0x51,
    "session-parameters": 0x52,
    "session-sequence-number": 0x93
}

_HEADER_IDS_TO_STRINGS = {}
for key, value in _HEADER_STRINGS_TO_IDS.items():
    _HEADER_IDS_TO_STRINGS[value] = key

assert len(_HEADER_IDS_TO_STRINGS) == len(_HEADER_STRINGS_TO_IDS)

# These match the associated strings in httplib.responses, since OBEX response
# codes are matched to HTTP status codes (except for 0x60 and 0x61).
# Note these are the responses *without* the final bit set.
_OBEX_RESPONSES = {
    0x10: "Continue",
    0x20: "OK",
    0x21: "Created",
    0x22: "Accepted",
    0x23: "Non-Authoritative Information",
    0x24: "No Content",
    0x25: "Reset Content",
    0x26: "Partial Content",

    0x30: "Multiple Choices",
    0x31: "Moved Permanently",
    0x32: "Moved Temporarily",  # but is 'Found' (302) in httplib.response???
    0x33: "See Other",
    0x34: "Not Modified",
    0x35: "Use Proxy",

    0x40: "Bad Request",
    0x41: "Unauthorized",
    0x42: "Payment Required",
    0x43: "Forbidden",
    0x44: "Not Found",
    0x45: "Method Not Allowed",
    0x46: "Not Acceptable",
    0x47: "Proxy Authentication Required",
    0x48: "Request Timeout",
    0x49: "Conflict",
    0x4A: "Gone",
    0x48: "Length Required",
    0x4C: "Precondition Failed",
    0x4D: "Request Entity Too Large",
    0x4E: "Request-URI Too Long",
    0x4F: "Unsupported Media Type",

    0x50: "Internal Server Error",
    0x51: "Not Implemented",
    0x52: "Bad Gateway",
    0x53: "Service Unavailable",
    0x54: "Gateway Timeout",
    0x55: "HTTP Version Not Supported",

    0x60: "Database Full",
    0x61: "Database Locked"
}


_obexclientclassdoc = \
    """
    An OBEX client class. (Note this is not available on Python for Series 60.)

    For example, to connect to an OBEX server and send a file:
        >>> import lightblue
        >>> client = lightblue.obex.OBEXClient("aa:bb:cc:dd:ee:ff", 10)
        >>> client.connect()
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>> client.put({"name": "photo.jpg"}, file("photo.jpg", "rb"))
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>> client.disconnect()
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>>

    A client must call connect() to establish a connection before it can send
    any other requests.

    The connect(), disconnect(), put(), delete(), get() and setpath() methods
    all accept the request headers as a dictionary of header-value mappings. The
    request headers are used to provide the server with additional information 
    for the request. For example, this sends a Put request that includes Name,
    Type and Length headers in the request headers, to provide details about
    the transferred file:
    
        >>> f = file("file.txt")
        >>> client.put({"name": "file.txt", "type": "text/plain",
        ...         "length": 5192}, f)
        >>>


    Here is a list of all the different string header keys that you can use in
    the request headers, and the expected type of the value for each header:
    
        - "name" -> a string
        - "type" -> a string
        - "length" -> an int
        - "time" -> a datetime object from the datetime module
        - "description" -> a string
        - "target" -> a string or buffer
        - "http" -> a string or buffer
        - "who" -> a string or buffer
        - "connection-id" -> an int
        - "application-parameters" -> a string or buffer
        - "authentication-challenge" -> a string or buffer
        - "authentication-response" -> a string or buffer
        - "creator-id" -> an int
        - "wan-uuid" -> a string or buffer
        - "object-class" -> a string or buffer
        - "session-parameters" -> a string or buffer
        - "session-sequence-number" -> an int less than 256
        
    (The string header keys are not case-sensitive.)

    Alternatively, you can use raw header ID values instead of the above
    convenience strings. So, the previous example can be rewritten as:
    
        >>> client.put({0x01: "file.txt", 0x42: "text/plain", 0xC3: 5192},
        ...     fileobject)
        >>>

    This is also useful for inserting custom headers. For example, a PutImage
    request for a Basic Imaging client requires the Img-Descriptor (0x71) 
    header:
        >>> client.put({"type": "x-bt/img-img", 
        ...     "name": "photo.jpg", 
        ...     0x71: '<image-descriptor version="1.0"><image encoding="JPEG" pixel="160*120" size="37600"/></image-descriptor>'}, 
        ...     file('photo.jpg', 'rb'))
        >>>

    Notice that the connection-id header is not sent, because this is
    automatically included by OBEXClient in the request headers if a
    connection-id was received in a previous Connect response.

    See the included src/examples/obex_ftp_client.py for an example of using
    OBEXClient to implement a File Transfer client for browsing the files on a
    remote device.
    """

_obexclientdocs = {
"__init__":
    """
    Creates an OBEX client.

    Arguments:
        - address: the address of the remote device
        - channel: the RFCOMM channel of the remote OBEX service
    """,
"connect":
    """
    Establishes the Bluetooth connection to the remote OBEX server and sends
    a Connect request to open the OBEX session. Returns an OBEXResponse 
    instance containing the server response.
    
    Raises lightblue.obex.OBEXError if the session is already connected, or if
    an error occurs during the request.
    
    If the server refuses the Connect request (i.e. if it sends a response code
    other than OK/Success), the Bluetooth connection will be closed.

    Arguments:
        - headers={}: the headers to send for the Connect request
    """,
"disconnect":
    """
    Sends a Disconnect request to end the OBEX session and closes the Bluetooth
    connection to the remote OBEX server. Returns an OBEXResponse 
    instance containing the server response.
    
    Raises lightblue.obex.OBEXError if connect() has not been called, or if an
    error occurs during the request.

    Note that you don't need to send any connection-id headers - this is
    automatically included if the client received one in a Connect response.

    Arguments:
        - headers={}: the headers to send for the request
    """,
"put":
    """
    Sends a Put request. Returns an OBEXResponse instance containing the
    server response.
    
    Raises lightblue.obex.OBEXError if connect() has not been called, or if an
    error occurs during the request.

    Note that you don't need to send any connection-id headers - this is
    automatically included if the client received one in a Connect response.

    Arguments:
        - headers: the headers to send for the request
        - fileobj: a file-like object containing the file data to be sent for
          the request

    For example, to send a file named 'photo.jpg', using the request headers 
    to notify the server of the file's name, MIME type and length:
        
        >>> client = lightblue.obex.OBEXClient("aa:bb:cc:dd:ee:ff", 10)
        >>> client.connect()
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>> client.put({"name": "photo.jpg", "type": "image/jpeg", 
                "length": 28566}, file("photo.jpg", "rb"))
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>>
    """,
"delete":
    """
    Sends a Put-Delete request in order to delete a file or folder on the remote
    server. Returns an OBEXResponse instance containing the server response.
    
    Raises lightblue.obex.OBEXError if connect() has not been called, or if an
    error occurs during the request.

    Note that you don't need to send any connection-id headers - this is
    automatically included if the client received one in a Connect response.

    Arguments:
        - headers: the headers to send for the request - you should use the
          'name' header to specify the file you want to delete

    If the file on the server can't be deleted because it's a read-only file,
    you might get an 'Unauthorized' response, like this:

        >>> client = lightblue.obex.OBEXClient("aa:bb:cc:dd:ee:ff", 10)
        >>> client.connect()
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>> client.delete({"name": "random_file.txt"})
        <OBEXResponse reason='Unauthorized' code=0x41 (0xc1) headers={}>
        >>>
    """,
"get":
    """
    Sends a Get request. Returns an OBEXResponse instance containing the server 
    response.
    
    Raises lightblue.obex.OBEXError if connect() has not been called, or if an
    error occurs during the request.

    Note that you don't need to send any connection-id headers - this is
    automatically included if the client received one in a Connect response.

    Arguments:
        - headers: the headers to send for the request - you should use these
          to specify the file you want to retrieve
        - fileobj: a file-like object, to which the received data will be
          written

    An example:
        >>> client = lightblue.obex.OBEXClient("aa:bb:cc:dd:ee:ff", 10)
        >>> client.connect()
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>> f = file("received_file.txt", "w+")
        >>> client.get({"name": "testfile.txt"}, f)
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={'length':9}>
        >>> f.seek(0)
        >>> f.read()
        'test file'
        >>>
    """,
"setpath":
    """
    Sends a SetPath request in order to set the "current path" on the remote
    server for file transfers. Returns an OBEXResponse instance containing the 
    server response.
    
    Raises lightblue.obex.OBEXError if connect() has not been called, or if an
    error occurs during the request.

    Note that you don't need to send any connection-id headers - this is
    automatically included if the client received one in a Connect response.

    Arguments:
        - headers: the headers to send for the request - you should use the
          'name' header to specify the directory you want to change to
        - cdtoparent=False: True if the remote server should move up one
          directory before applying the specified directory (i.e. 'cd
          ../dirname')
        - createdirs=False: True if the specified directory should be created
          if it doesn't exist (if False, the server will return an error
          response if the directory doesn't exist)

    For example:

        # change to the "images" subdirectory
        >>> client.setpath({"name": "images"})
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>>

        # change to the parent directory
        >>> client.setpath({}, cdtoparent=True)
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>>

        # create a subdirectory "My_Files"
        >>> client.setpath({"name": "My_Files"}, createdirs=True)
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>>

        # change to the root directory - you can use an empty "name" header
        # to specify this
        >>> client.setpath({"name": ""})
        <OBEXResponse reason='OK' code=0x20 (0xa0) headers={}>
        >>>
    """
}


# response constants
CONTINUE = 0x10
OK = 0x20
CREATED = 0x21
ACCEPTED = 0x22
NON_AUTHORITATIVE_INFORMATION = 0x23
NO_CONTENT = 0x24
RESET_CONTENT = 0x25
PARTIAL_CONTENT = 0x26

MULTIPLE_CHOICES = 0x30
MOVED_PERMANENTLY = 0x31
MOVED_TEMPORARILY = 0x32
SEE_OTHER = 0x33
NOT_MODIFIED = 0x34
USE_PROXY = 0x35

BAD_REQUEST = 0x40
UNAUTHORIZED = 0x41
PAYMENT_REQUIRED = 0x42
FORBIDDEN = 0x43
NOT_FOUND = 0x44
METHOD_NOT_ALLOWED = 0x45
NOT_ACCEPTABLE = 0x46
PROXY_AUTHENTICATION_REQUIRED = 0x47
REQUEST_TIME_OUT = 0x48
CONFLICT = 0x49
GONE = 0x4A
LENGTH_REQUIRED = 0x4B
PRECONDITION_FAILED = 0x4C
REQUESTED_ENTITY_TOO_LARGE = 0x4D
REQUEST_URL_TOO_LARGE = 0x4E
UNSUPPORTED_MEDIA_TYPE = 0x4F

INTERNAL_SERVER_ERROR = 0x50
NOT_IMPLEMENTED = 0x51
BAD_GATEWAY = 0x52
SERVICE_UNAVAILABLE = 0x53
GATEWAY_TIMEOUT = 0x54
HTTP_VERSION_NOT_SUPPORTED = 0x55

DATABASE_FULL = 0x60
DATABASE_LOCKED = 0x61
