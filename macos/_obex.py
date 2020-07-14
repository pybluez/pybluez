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

import datetime
import time
import types

import objc
from Foundation import NSObject, NSDate

from ._IOBluetooth import OBEXSession, IOBluetoothDevice, \
        IOBluetoothRFCOMMChannel
from ._LightAquaBlue import BBBluetoothOBEXClient, BBBluetoothOBEXServer, \
        BBStreamingInputStream, BBStreamingOutputStream, \
        BBMutableOBEXHeaderSet, \
        BBLocalDevice
from . import _lightbluecommon
from . import _obexcommon
from . import _macutil

from ._obexcommon import OBEXError

# from <IOBluetooth/OBEX.h>
_kOBEXSuccess = 0
_kOBEXGeneralError = -21850
_kOBEXSessionNotConnectedError = -21876
_kOBEXSessionAlreadyConnectedError = -21882
_kOBEXSessionNoTransportError = -21879
_kOBEXSessionTransportDiedError = -21880
_OBEX_FINAL_MASK = 0x80

_HEADER_MASK = 0xc0
_HEADER_UNICODE = 0x00
_HEADER_BYTE_SEQ = 0x40
_HEADER_1BYTE = 0x80
_HEADER_4BYTE = 0xc0

# public attributes
__all__ = ("OBEXClient", "sendfile", "recvfile")


_obexerrorcodes = { 0: "no error", -21850: "general error", -21851: "no resources", -21852: "operation not supported", -21853: "internal error", -21854: "bad argument", -21855: "timeout", -21856: "bad request", -21857: "cancelled", -21875: "session is busy", -21876: "OBEX session not connected", -21877: "bad request in OBEX session", -21878: "bad response from other party", -21879: "Bluetooth transport not available", -21880: "Bluetooth transport connection died", -21881: "OBEX session timed out", -21882: "OBEX session already connected" }

def errdesc(errorcode):
    return _obexerrorcodes.get(errorcode, str(errorcode))


# OBEXSession provides response codes with the final bit set, but OBEXResponse
# class expects the response code to not have the final bit set.
def _cutresponsefinalbit(responsecode):
    return (responsecode & ~_OBEX_FINAL_MASK)


def _headersdicttoset(headers):
    headerset = BBMutableOBEXHeaderSet.alloc().init()
    for header, value in list(headers.items()):
        if isinstance(header, str):
            hid = _obexcommon._HEADER_STRINGS_TO_IDS.get(header.lower())
        else:
            hid = header
        if hid is None:
            raise ValueError("unknown header '%s'" % header)
        if isinstance(value, datetime.datetime):
            value = value.strftime("%Y%m%dT%H%M%S")
        mask = hid & _HEADER_MASK
        if mask == _HEADER_UNICODE:
            if not isinstance(value, str):
                raise TypeError("value for '%s' must be string, was %s" %
                    (str(header), type(value)))
            headerset.setValue_forUnicodeHeader_(value, hid)
        elif mask == _HEADER_BYTE_SEQ:
            try:
                value = memoryview(value.encode())
            except:
                raise TypeError("value for '{}' must be string, array or other buffer type, was {}".format(str(header), type(value)))
            headerset.setValue_forByteSequenceHeader_(value, hid)
        elif mask == _HEADER_1BYTE:
            if not isinstance(value, int):
                raise TypeError("value for '%s' must be int, was %s" %
                    (str(header), type(value)))
            headerset.setValue_for1ByteHeader_(value, hid)
        elif mask == _HEADER_4BYTE:
            if not isinstance(value, int) and not isinstance(value, int):
                raise TypeError("value for '%s' must be int, was %s" %
                    (str(header), type(value)))
            headerset.setValue_for4ByteHeader_(value, hid)
        if not headerset.containsValueForHeader_(hid):
            raise ValueError("cannot set OBEX header value for '%s'" % header)
    return headerset


# returns in { header-id: value } form.
def _headersettodict(headerset):
    headers = {}
    for number in headerset.allHeaders():
        hid = number.unsignedCharValue()
        mask = hid & _HEADER_MASK
        if mask == _HEADER_UNICODE:
            value = headerset.valueForUnicodeHeader_(hid)
        elif mask == _HEADER_BYTE_SEQ:
            value = headerset.valueForByteSequenceHeader_(hid)[:]
            if hid == 0x42:     # type
                if len(value) > 0 and value[-1] == '\0':
                    value = value[:-1]  # remove null byte
            elif hid == 0x44:     # time iso-8601 string
                value = _obexcommon._datetimefromstring(value)
        elif mask == _HEADER_1BYTE:
            value = headerset.valueFor1ByteHeader_(hid)
        elif mask == _HEADER_4BYTE:
            value = headerset.valueFor4ByteHeader_(hid)
        headers[hid] = value
    return headers


class OBEXClient:
    __doc__ = _obexcommon._obexclientclassdoc

    def __init__(self, address, channel):
        if not _lightbluecommon._isbtaddr(address):
            raise TypeError("address '%s' is not a valid bluetooth address"
                % address)
        if not type(channel) == int:
            raise TypeError("channel must be int, was %s" % type(channel))
        if channel < 0:
            raise ValueError("channel cannot be negative")

        self.__serveraddr = (address, channel)
        self.__busy = False
        self.__client = None
        self.__obexsession = None   # for testing
        #BBBluetoothOBEXClient.setDebug_(True)


    def connect(self, headers={}):
        if self.__client is None:
            if not BBLocalDevice.isPoweredOn():
                raise OBEXError(_kOBEXSessionNoTransportError,
                        "Bluetooth device not available")
            self.__delegate = _BBOBEXClientDelegate.alloc().initWithCallback_(
                    self._finishedrequest)
            self.__client = BBBluetoothOBEXClient.alloc().initWithRemoteDeviceAddress_channelID_delegate_(
                    _macutil.createbtdevaddr(self.__serveraddr[0]),
                        self.__serveraddr[1], self.__delegate)
            if self.__obexsession is not None:
                self.__client.performSelector_withObject_("setOBEXSession:",
                        self.__obexsession)

        self.__reset()
        headerset = _headersdicttoset(headers)
        r = self.__client.sendConnectRequestWithHeaders_(headerset)
        if r != _kOBEXSuccess:
            self.__closetransport()
            raise OBEXError(r, "error starting Connect request (%s)" %
                    errdesc(r))

        _macutil.waituntil(self._done)
        if self.__error != _kOBEXSuccess:
            self.__closetransport()
            raise OBEXError(self.__error, "error during Connect request (%s)" %
                    errdesc(self.__error))

        resp = self.__getresponse()
        if resp.code != _obexcommon.OK:
            self.__closetransport()
        return resp


    def disconnect(self, headers={}):
        self.__checkconnected()
        self.__reset()
        try:
            headerset = _headersdicttoset(headers)
            r = self.__client.sendDisconnectRequestWithHeaders_(headerset)
            if r != _kOBEXSuccess:
                raise OBEXError(r, "error starting Disconnect request (%s)" %
                        errdesc(r))

            _macutil.waituntil(self._done)
            if self.__error != _kOBEXSuccess:
                raise OBEXError(self.__error,
                        "error during Disconnect request (%s)" %
                        errdesc(self.__error))
        finally:
            # close channel regardless of disconnect result
            self.__closetransport()
        return self.__getresponse()


    def put(self, headers, fileobj):
        if not hasattr(fileobj, "read"):
            raise TypeError("file-like object must have read() method")
        self.__checkconnected()
        self.__reset()

        headerset = _headersdicttoset(headers)
        self.fileobj = fileobj
        self.__fileobjdelegate = _macutil.BBFileLikeObjectReader.alloc().initWithFileLikeObject_(fileobj)
        self.instream = BBStreamingInputStream.alloc().initWithDelegate_(self.__fileobjdelegate)
        self.instream.open()
        r = self.__client.sendPutRequestWithHeaders_readFromStream_(
                headerset, self.instream)
        if r != _kOBEXSuccess:
            raise OBEXError(r, "error starting Put request (%s)" % errdesc(r))
        _macutil.waituntil(self._done)
        if self.__error != _kOBEXSuccess:
            raise OBEXError(self.__error, "error during Put request (%s)" %
                    errdesc(self.__error))
        return self.__getresponse()


    def delete(self, headers):
        self.__checkconnected()
        self.__reset()
        headerset = _headersdicttoset(headers)
        r = self.__client.sendPutRequestWithHeaders_readFromStream_(headerset,
                None)
        if r != _kOBEXSuccess:
            raise OBEXError(r, "error starting Delete request (%s)" %
                    errdesc(r))

        _macutil.waituntil(self._done)
        if self.__error != _kOBEXSuccess:
            raise OBEXError(self.__error, "error during Delete request (%s)" %
                    errdesc(self.__error))
        return self.__getresponse()


    def get(self, headers, fileobj):
        if not hasattr(fileobj, "write"):
            raise TypeError("file-like object must have write() method")

        self.__checkconnected()
        self.__reset()
        headerset = _headersdicttoset(headers)
        delegate = _macutil.BBFileLikeObjectWriter.alloc().initWithFileLikeObject_(fileobj)
        outstream = BBStreamingOutputStream.alloc().initWithDelegate_(delegate)
        outstream.open()
        r = self.__client.sendGetRequestWithHeaders_writeToStream_(
                headerset, outstream)
        if r != _kOBEXSuccess:
            raise OBEXError(r, "error starting Get request (%s)" % errdesc(r))

        _macutil.waituntil(self._done)
        if self.__error != _kOBEXSuccess:
            raise OBEXError(self.__error, "error during Get request (%s)" %
                    errdesc(self.__error))
        return self.__getresponse()


    def setpath(self, headers, cdtoparent=False, createdirs=False):
        self.__checkconnected()
        self.__reset()
        headerset = _headersdicttoset(headers)
        r = self.__client.sendSetPathRequestWithHeaders_changeToParentDirectoryFirst_createDirectoriesIfNeeded_(headerset, cdtoparent, createdirs)
        if r != _kOBEXSuccess:
            raise OBEXError(r, "error starting SetPath request (%s)" %
                    errdesc(r))

        _macutil.waituntil(self._done)
        if self.__error != _kOBEXSuccess:
            raise OBEXError(self.__error, "error during SetPath request (%s)" %
                    errdesc(self.__error))
        return self.__getresponse()


    def _done(self):
        return not self.__busy

    def _finishedrequest(self, error, response):
        if error in (_kOBEXSessionNoTransportError,
                     _kOBEXSessionTransportDiedError):
            self.__closetransport()
        self.__error = error
        self.__response = response
        self.__busy = False
        _macutil.interruptwait()

    def _setobexsession(self, session):
        self.__obexsession = session

    # Note that OBEXSession returns kOBEXSessionNotConnectedError if you don't
    # send CONNECT before sending any other requests; this means the OBEXClient
    # must send connect() before other requests, so this restriction is enforced
    # in the Linux version as well, for consistency.
    def __checkconnected(self):
        if self.__client is None:
            raise OBEXError(_kOBEXSessionNotConnectedError,
                    "must connect() before sending other requests")

    def __closetransport(self):
        if self.__client is not None:
            try:
                self.__client.RFCOMMChannel().closeChannel()
                self.__client.RFCOMMChannel().getDevice().closeConnection()
            except:
                pass
        self.__client = None

    def __reset(self):
        self.__busy = True
        self.__error = None
        self.__response = None

    def __getresponse(self):
        code = self.__response.responseCode()
        rawheaders = _headersettodict(self.__response.allHeaders())
        return _obexcommon.OBEXResponse(_cutresponsefinalbit(code), rawheaders)

    def __del__(self):
        if self.__client is not None:
            self.__client.__del__()
        super().__del__()

    # set method docstrings
    definedmethods = locals()   # i.e. defined methods in OBEXClient
    for name, doc in list(_obexcommon._obexclientdocs.items()):
        try:
            definedmethods[name].__doc__ = doc
        except KeyError:
            pass



class _BBOBEXClientDelegate(NSObject):

    def initWithCallback_(self, cb_requestdone):
        self = super().init()
        self._cb_requestdone = cb_requestdone
        return self
    initWithCallback_ = objc.selector(initWithCallback_, signature=b"@@:@")

    def __del__(self):
        super().dealloc()

    #
    # Delegate methods follow. objc signatures for all methods must be set
    # using objc.selector or else may get bus error.
    #

    # - (void)client:(BBBluetoothOBEXClient *)client
    #    didFinishConnectRequestWithError:(OBEXError)error
    #       response:(BBOBEXResponse *)response;
    def client_didFinishConnectRequestWithError_response_(self, client, error,
            response):
        self._cb_requestdone(error, response)
    client_didFinishConnectRequestWithError_response_ = objc.selector(
        client_didFinishConnectRequestWithError_response_, signature=b"v@:@i@")

    # - (void)client:(BBBluetoothOBEXClient *)client
    #    didFinishDisconnectRequestWithError:(OBEXError)error
    #       response:(BBOBEXResponse *)response;
    def client_didFinishDisconnectRequestWithError_response_(self, client,
            error, response):
        self._cb_requestdone(error, response)
    client_didFinishDisconnectRequestWithError_response_ = objc.selector(
        client_didFinishDisconnectRequestWithError_response_,signature=b"v@:@i@")

    # - (void)client:(BBBluetoothOBEXClient *)client
    # didFinishPutRequestForStream:(NSInputStream *)inputStream
    #         error:(OBEXError)error
    #       response:(BBOBEXResponse *)response;
    def client_didFinishPutRequestForStream_error_response_(self, client,
            instream, error, response):
        self._cb_requestdone(error, response)
    client_didFinishPutRequestForStream_error_response_ = objc.selector(
        client_didFinishPutRequestForStream_error_response_,signature=b"v@:@@i@")

    # - (void)client:(BBBluetoothOBEXClient *)client
    # didFinishGetRequestForStream:(NSOutputStream *)outputStream
    #         error:(OBEXError)error
    #       response:(BBOBEXResponse *)response;
    def client_didFinishGetRequestForStream_error_response_(self, client,
            outstream, error, response):
        self._cb_requestdone(error, response)
    client_didFinishGetRequestForStream_error_response_ = objc.selector(
        client_didFinishGetRequestForStream_error_response_,signature=b"v@:@@i@")

    # - (void)client:(BBBluetoothOBEXClient *)client
    #    didFinishSetPathRequestWithError:(OBEXError)error
    #       response:(BBOBEXResponse *)response;
    def client_didFinishSetPathRequestWithError_response_(self, client, error,
            response):
        self._cb_requestdone(error, response)
    client_didFinishSetPathRequestWithError_response_ = objc.selector(
        client_didFinishSetPathRequestWithError_response_, signature=b"v@:@i@")

    # client:didAbortRequestWithStream:error:response: not
    # implemented since OBEXClient does not allow abort requests


# ------------------------------------------------------------------

def sendfile(address, channel, source):
    if not _lightbluecommon._isbtaddr(address):
        raise TypeError("address '%s' is not a valid bluetooth address" %
                address)
    if not isinstance(channel, int):
        raise TypeError("channel must be int, was %s" % type(channel))
    if not isinstance(source, str) and \
            not hasattr(source, "read"):
        raise TypeError("source must be string or file-like object with read() method")

    if isinstance(source, str):
        headers = {"name": source}
        fileobj = open(source, "rb")
        closefileobj = True
    else:
        if hasattr(source, "name"):
            headers = {"name": source.name}
        fileobj = source
        closefileobj = False

    client = OBEXClient(address, channel)
    client.connect()

    try:
        resp = client.put(headers, fileobj)
    finally:
        if closefileobj:
            fileobj.close()
        try:
            client.disconnect()
        except:
            pass    # always ignore disconnection errors

    if resp.code != _obexcommon.OK:
        raise OBEXError("server denied the Put request")


# ------------------------------------------------------------------


class BBOBEXObjectPushServer(NSObject):

    def initWithChannel_fileLikeObject_(self, channel, fileobject):
        if not isinstance(channel, IOBluetoothRFCOMMChannel) and \
                not isinstance(channel, OBEXSession):
            raise TypeError("internal error, channel is of wrong type %s" %
                    type(channel))
        if not hasattr(fileobject, "write"):
            raise TypeError("fileobject must be file-like object with write() method")

        self = super().init()
        self.__fileobject = fileobject
        self.__server = BBBluetoothOBEXServer.alloc().initWithIncomingRFCOMMChannel_delegate_(channel, self)
        #BBBluetoothOBEXServer.setDebug_(True)

        self.__error = None
        self.__gotfile = False
        self.__gotdisconnect = False
        self.__disconnected = False

        # for internal testing
        if isinstance(channel, OBEXSession):
            self.__server.performSelector_withObject_("setOBEXSession:",
                    channel)
        return self
    initWithChannel_fileLikeObject_ = objc.selector(
        initWithChannel_fileLikeObject_, signature=b"@@:i@")


    def run(self):
        self.__server.run()

        # wait until client sends a file, or an error occurs
        _macutil.waituntil(lambda: self.__gotfile or self.__error is not None)

        # wait briefly for a disconnect request (client may have decided to just
        # close the connection without sending a disconnect request)
        if self.__error is None:
            ok = _macutil.waituntil(lambda: self.__gotdisconnect, 3)
            if ok:
                _macutil.waituntil(lambda: self.__disconnected)

        # only raise OBEXError if file was not received
        if not self.__gotfile:
            if self.__error is not None:
                raise OBEXError(self.__error[0], self.__error[1])

            # if client connected but didn't send PUT
            raise OBEXError(_kOBEXGeneralError, "client did not send a file")

    def __del__(self):
        super().dealloc()

    #
    # BBBluetoothOBEXClientDelegate methods follow.
    # These enable this class to get callbacks when some event occurs on the
    # server (e.g. got a new client request, or an error occurred, etc.).
    #

    # - (BOOL)server:(BBBluetoothOBEXServer *)server
    # shouldHandleConnectRequest:(BBOBEXHeaderSet *)requestHeaders;
    def server_shouldHandleConnectRequest_(self, server, requestheaders):
        return True
    server_shouldHandleConnectRequest_ = objc.selector(
        server_shouldHandleConnectRequest_, signature=b"c@:@@")

    # - (BOOL)server:(BBBluetoothOBEXServer *)server
    # shouldHandleDisconnectRequest:(BBOBEXHeaderSet *)requestHeaders;
    def server_shouldHandleDisconnectRequest_(self, server, requestheaders):
        self.__gotdisconnect = True
        _macutil.interruptwait()
        return True
    server_shouldHandleDisconnectRequest_ = objc.selector(
        server_shouldHandleDisconnectRequest_, signature=b"c@:@@")

    # - (void)serverDidHandleDisconnectRequest:(BBBluetoothOBEXServer *)server;
    def serverDidHandleDisconnectRequest_(self, server):
        self.__disconnected = True
        _macutil.interruptwait()
    serverDidHandleDisconnectRequest_ = objc.selector(
        serverDidHandleDisconnectRequest_, signature=b"v@:@")

    # - (NSOutputStream *)server:(BBBluetoothOBEXServer *)server
    # shouldHandlePutRequest:(BBOBEXHeaderSet *)requestHeaders;
    def server_shouldHandlePutRequest_(self, server, requestheaders):
        #print "Incoming file:", requestHeaders.valueForNameHeader()
        self.delegate = _macutil.BBFileLikeObjectWriter.alloc().initWithFileLikeObject_(self.__fileobject)
        outstream = BBStreamingOutputStream.alloc().initWithDelegate_(self.delegate)
        outstream.open()
        return outstream
    server_shouldHandlePutRequest_ = objc.selector(
        server_shouldHandlePutRequest_, signature=b"@@:@@")

    # - (void)server:(BBBluetoothOBEXServer *)server
    # didHandlePutRequestForStream:(NSOutputStream *)outputStream
    #   requestWasAborted:(BOOL)aborted;
    def server_didHandlePutRequestForStream_requestWasAborted_(self, server,
            stream, aborted):
        if aborted:
            self.__error = (_kOBEXGeneralError, "client aborted file transfer")
        else:
            self.__gotfile = True
        _macutil.interruptwait()
    server_didHandlePutRequestForStream_requestWasAborted_ = objc.selector(
        server_didHandlePutRequestForStream_requestWasAborted_,
        signature=b"v@:@@c")

    # - (void)server:(BBBluetoothOBEXServer *)server
    # errorOccurred:(OBEXError)error
    #   description:(NSString *)description;
    def server_errorOccurred_description_(self, server, error, desc):
        self.__error = (error, desc)
        _macutil.interruptwait()
    server_errorOccurred_description_ = objc.selector(
        server_errorOccurred_description_, signature=b"v@:@i@")



# ------------------------------------------------------------------

def recvfile(sock, dest):
    if sock is None:
        raise TypeError("Given socket is None")
    if not isinstance(dest, (str, types.FileType)):
        raise TypeError("dest must be string or file-like object with write() method")

    if isinstance(dest, str):
        fileobj = open(dest, "wb")
        closefileobj = True
    else:
        fileobj = dest
        closefileobj = False

    try:
        sock.listen(1)
        conn, addr = sock.accept()
        #print "A client connected:", addr
        server = BBOBEXObjectPushServer.alloc().initWithChannel_fileLikeObject_(
                conn._getchannel(), fileobj)
        server.run()
        conn.close()
    finally:
        if closefileobj:
            fileobj.close()
