/*
 * Copyright (c) 2009 Bea Lam. All rights reserved.
 *
 * This file is part of LightBlue.
 *
 * LightBlue is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * LightBlue is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LightBlue.  If not, see <http://www.gnu.org/licenses/>.
*/

//
//  BBBluetoothOBEXServer.h
//  LightAquaBlue
//
//  Implements the server side of an OBEX session over a Bluetooth transport.
//
//  Generally you will use BBBluetoothOBEXServer like this:
//    1. Call registerForChannelOpenNotifications:selector:withChannelID:direction:
//       in the IOBluetoothRFCOMMChannel class in order be notified whenever
//       you receive a client connection on a particular RFCOMM channel ID.
//    2. When you are notified that a client has connected, use the provided
//       IOBluetoothRFCOMMChannel to create a a BBBluetoothOBEXServer
//       object, and then call run: on the object to start the server.
//
//  There is an example in examples/LightAquaBlue/SimpleOBEXServer that shows
//  how to use this class to run a basic OBEX server session.
//

#import <Cocoa/Cocoa.h>

#import <IOBluetooth/OBEX.h>

@class OBEXSession;
@class BBOBEXHeaderSet;
@class BBMutableOBEXHeaderSet;
@class BBOBEXRequestHandler;
@class IOBluetoothRFCOMMChannel;
@class IOBluetoothUserNotification;


@interface BBBluetoothOBEXServer : NSObject {
    IOBluetoothRFCOMMChannel *mChannel;

    OBEXSession *mSession;
    id mDelegate;
    BBOBEXRequestHandler *mCurrentRequestHandler;

    IOBluetoothUserNotification *mChannelNotif;
}

/*
 * Creates and returns a BBBluetoothOBEXServer.
 */
+ (id)serverWithIncomingRFCOMMChannel:(IOBluetoothRFCOMMChannel *)channel
                             delegate:(id)delegate;

/*
 * Initialises a BBBluetoothOBEXServer that will run on the given <channel>.
 * The <delegate> will be notified when events occur on the server.
 */
- (id)initWithIncomingRFCOMMChannel:(IOBluetoothRFCOMMChannel *)channel
                           delegate:(id)delegate;

/*
 * Starts the server. The server will now receive and process client requests.
 */
- (void)run;

/*
 * Closes the server. It cannot be started again after this.
 */
- (void)close;

/*
 * Sets <responseCode> to be the next response code to be sent for the current
 * request.
 *
 * Available response codes are listed in the OBEXOpCodeResponseValues enum in
 * <IOBluetooth/OBEX.h>. (Use the codes that end with "WithFinalBit".) For
 * example, you could set the response code to
 * kOBEXResponseCodeNotFoundWithFinalBit if a client requests a non-existent
 * file.
 */
- (void)setResponseCodeForCurrentRequest:(int)responseCode;

/*
 * Adds <responseHeaders> to the next response headers to be sent for the
 * current request.
 *
 * For example, OBEX servers commonly include a "Length" header when
 * responding to a Get request to indicate the size of the file to be
 * transferred.
 */
- (void)addResponseHeadersForCurrentRequest:(BBOBEXHeaderSet *)responseHeaders;

/*
 * Sets the server's delegate to <delegate>.
 */
- (void)setDelegate:(id)delegate;

/*
 * Returns the delegate for this server.
 */
- (id)delegate;

/*
 * Sets whether debug messages should be displayed (default is NO).
 */
+ (void)setDebug:(BOOL)debug;

@end


/*
 * This informal protocol describes the methods that can be implemented for a
 * BBBluetoothOBEXServer delegate.
 *
 * For each type of client request, there is a "...shouldHandle..." method
 * (e.g. server:shouldHandleConnectRequest:) that is called when the request
 * is received. If the delegate does not implement this method for a
 * particular type of request, the server will automatically refuse all
 * requests of this type with a "Not Implemented" response.
 */
@protocol BBBluetoothOBEXServerDelegate

/*
 * Called when an error occurs on the server. <error> is an error code from
 * <IOBluetooth/OBEX.h> and <description> is a description of the error.
 */
- (void)server:(BBBluetoothOBEXServer *)server
 errorOccurred:(OBEXError)error
   description:(NSString *)description;

/*
 * Called when a Connect request is received with the specified <requestHeaders>.
 *
 * This should return YES if the request should be allowed to continue, or NO
 * if the request should be refused. (By default, a request will be refused
 * with a 'Forbidden' response; call setResponseCodeForCurrentRequest: to set
 * a more specific response.)
 */
- (BOOL)server:(BBBluetoothOBEXServer *)server
shouldHandleConnectRequest:(BBOBEXHeaderSet *)requestHeaders;

/*
 * Called when the server finishes processing of a Connect request.
 */
- (void)serverDidHandleConnectRequest:(BBBluetoothOBEXServer *)server;

/*
 * Called when a Disconnect request is received with the specified <requestHeaders>.
 *
 * This should return YES if the request should be allowed to continue, or NO
 * if the request should be refused. (By default, a request will be refused
 * with a 'Forbidden' response; call setResponseCodeForCurrentRequest: to set
 * a more specific response.)
 */
- (BOOL)server:(BBBluetoothOBEXServer *)server
shouldHandleDisconnectRequest:(BBOBEXHeaderSet *)requestHeaders;

/*
 * Called when the server finishes processing of a Disconnect request.
 */
- (void)serverDidHandleDisconnectRequest:(BBBluetoothOBEXServer *)server;

/*
 * Called when a Put request is received with the specified <requestHeaders>.
 *
 * This should return an opened NSOutputStream if the request should be allowed
 * to continue, or nil if the request should be refused. (By default, a request
 * will be refused with a 'Forbidden' response; call
 * setResponseCodeForCurrentRequest: to set a more specific response.)
 *
 * Note the returned stream *must* be open, or the request will fail.
 */
- (NSOutputStream *)server:(BBBluetoothOBEXServer *)server
    shouldHandlePutRequest:(BBOBEXHeaderSet *)requestHeaders;

/*
 * Called each time a chunk of data is received during a Put request.
 * The <length> indicates the number of bytes received, and <isLastPacket> is
 * set to YES if all the data has now been received and the server is about to
 * send the final response for the request.
 */
- (void)server:(BBBluetoothOBEXServer *)server
didReceiveDataOfLength:(unsigned)length
  isLastPacket:(BOOL)isLastPacket;

/*
 * Called when the server finishes processing of a Put request. The
 * <outputStream> is the stream originally provided from
 * server:shouldHandlePutRequest: and <aborted> is set to YES if the client
 * sent an Abort request to cancel the Put request before it was completed.
 */
- (void)server:(BBBluetoothOBEXServer *)server
didHandlePutRequestForStream:(NSOutputStream *)outputStream
    requestWasAborted:(BOOL)aborted;

/*
 * Called when a Put-Delete request is received with the specified <requestHeaders>.
 *
 * This should return YES if the request should be allowed to continue, or NO
 * if the request should be refused. (By default, a request will be refused
 * with a 'Forbidden' response; call setResponseCodeForCurrentRequest: to set
 * a more specific response.)
 */
- (BOOL)server:(BBBluetoothOBEXServer *)server
shouldHandlePutDeleteRequest:(BBOBEXHeaderSet *)requestHeaders;

/*
 * Called when the server finishes processing of a Put-Delete request.
 */
- (void)serverDidHandlePutDeleteRequest:(BBBluetoothOBEXServer *)server;

/*
 * Called when a Get request is received with the specified <requestHeaders>.
 *
 * This should return an opened NSInputStream if the request should be allowed
 * to continue, or nil if the request should be refused. (By default, a request
 * will be refused with a 'Forbidden' response; call
 * setResponseCodeForCurrentRequest: to set a more specific response.)
 *
 * Note the returned stream *must* be open, or the request will fail.
 */
- (NSInputStream *)server:(BBBluetoothOBEXServer *)server
   shouldHandleGetRequest:(BBOBEXHeaderSet *)requestHeaders;

/*
 * Called each time a chunk of data is sent during a Get request.
 * The <length> indicates the number of bytes sent.
 */
- (void)server:(BBBluetoothOBEXServer *)server
didSendDataOfLength:(NSUInteger)length;

/*
 * Called when the server finishes processing of a Get request. The
 * <outputStream> is the stream originally provided from
 * server:shouldHandleGetRequest: and <aborted> is set to YES if the client
 * sent an Abort request to cancel the Get request before it was completed.
 */
- (void)server:(BBBluetoothOBEXServer *)server
didHandleGetRequestForStream:(NSInputStream *)inputStream
    requestWasAborted:(BOOL)aborted;

/*
 * Called when a SetPath request is received with the specified <requestHeaders>
 * and SetPath <flags>. The first two bits of the flags are significant
 * for the SetPath operation:
 *      - Bit 0 is set if the server should back up one level (i.e. "..")
 *        before applying the requested path name
 *      - Bit 1 is set if the server should respond with an error instead of
 *        creating a directory if the specified directory does not exist
 *
 * This should return YES if the request should be allowed to continue, or NO
 * if the request should be refused. (By default, a request will be refused
 * with a 'Forbidden' response; call setResponseCodeForCurrentRequest: to set
 * a more specific response.)
 */
- (BOOL)server:(BBBluetoothOBEXServer *)server
shouldHandleSetPathRequest:(BBOBEXHeaderSet *)requestHeaders
     withFlags:(OBEXFlags)flags;

/*
 * Called when the server finishes processing of a SetPath request.
 */
- (void)serverDidHandleSetPathRequest:(BBBluetoothOBEXServer *)server;

@end
