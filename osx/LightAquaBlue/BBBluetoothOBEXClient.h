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
//  BBBluetoothOBEXClient.h
//  LightAquaBlue
//
//  Implements the client side of an OBEX session over a Bluetooth transport.
//  
//  There is an example in examples/LightAquaBlue/SimpleOBEXClient that shows
//  how to use this class to connect to and send files to an OBEX server.
//

#import <Cocoa/Cocoa.h>

#import <IOBluetooth/OBEX.h>
#import <IOBluetooth/Bluetooth.h>

@class OBEXSession;
@class BBOBEXHeaderSet;
@class BBOBEXRequest;
@class IOBluetoothDevice;
@class BBOBEXResponse;
@class IOBluetoothRFCOMMChannel;

@interface BBBluetoothOBEXClient : NSObject {
    OBEXSession* mSession;
    id mDelegate;
    
    OBEXMaxPacketLength	mMaxPacketLength;
    int mLastServerResponse;
    uint32_t mConnectionID;
    BOOL mHasConnectionID;
    
    BOOL mAborting;
    
    BBOBEXRequest *mCurrentRequest;
}

/*
 * Creates a BBBluetoothOBEXClient with the given <delegate>. The client will 
 * connect to the OBEX server on the given <deviceAddress> and <channelID>.
 */
- (id)initWithRemoteDeviceAddress:(const BluetoothDeviceAddress *)deviceAddress
                        channelID:(BluetoothRFCOMMChannelID)channelID
                         delegate:(id)delegate;

/*
 * Sends a Connect request with the given <headers>. 
 * 
 * Returns kOBEXSuccess if the request was sent, or some other OBEXError value 
 * from <IOBluetooth/OBEX.h> if there was an error. The delegate is informed 
 * through client:didFinishConnectRequestWithError:responseCode:responseHeaders: 
 * when the request is finished.
 */
- (OBEXError)sendConnectRequestWithHeaders:(BBOBEXHeaderSet *)headers;

/*
 * Sends a Disconnect request with the given <headers>. 
 * 
 * Returns kOBEXSuccess if the request was sent, or some other OBEXError value 
 * from <IOBluetooth/OBEX.h> if there was an error. The delegate is informed 
 * through client:didFinishDisconnectRequestWithError:responseCode:responseHeaders: 
 * when the request is finished.
 *
 * You must have already sent a Connect request; otherwise, this fails and
 * return kOBEXSessionNotConnectedError.
 *
 * Note the Connection ID is automatically sent in the request headers if one
 * was provided by the server in a previous Connect response.
 */
- (OBEXError)sendDisconnectRequestWithHeaders:(BBOBEXHeaderSet *)headers;

/*
 * Sends a Put request with the given <headers> that will send the data from
 * the given <inputStream>. (The stream must be already open, or the request
 * will fail!) To send a Put-Delete request, set <inputStream> to nil.
 * 
 * Returns kOBEXSuccess if the request was sent, or some other OBEXError value 
 * from <IOBluetooth/OBEX.h> if there was an error. The delegate is informed 
 * through client:didFinishPutRequestForStream:error:responseCode:responseHeaders: 
 * when the request is finished.
 *
 * You must have already sent a Connect request; otherwise, this fails and
 * return kOBEXSessionNotConnectedError.
 *
 * Note the Connection ID is automatically sent in the request headers if one
 * was provided by the server in a previous Connect response.
 */
- (OBEXError)sendPutRequestWithHeaders:(BBOBEXHeaderSet *)headers
                        readFromStream:(NSInputStream *)inputStream;

/*
 * Sends a Get request with the given <headers> that will write received data
 * to the given <outputStream>. (The stream must be already open, or the request
 * will fail!)
 * 
 * Returns kOBEXSuccess if the request was sent, or some other OBEXError value 
 * from <IOBluetooth/OBEX.h> if there was an error. The delegate is informed 
 * through client:didFinishGetRequestForStream:error:responseCode:responseHeaders: 
 * when the request is finished.
 *
 * You must have already sent a Connect request; otherwise, this fails and
 * return kOBEXSessionNotConnectedError.
 *
 * Note the Connection ID is automatically sent in the request headers if one
 * was provided by the server in a previous Connect response.
 */
- (OBEXError)sendGetRequestWithHeaders:(BBOBEXHeaderSet *)headers
                         writeToStream:(NSOutputStream *)outputStream;

/*
 * Sends a SetPath request with the given <headers>. Set
 * <changeToParentDirectoryFirst> to YES if you want to move up one directory
 * (i.e. "..") before changing to the directory specified in the headers. Set
 * <createDirectoriesIfNeeded> to YES if you want to create a directory 
 * (instead of receiving an error response) if it does not currently exist.
 * 
 * Returns kOBEXSuccess if the request was sent, or some other OBEXError value 
 * from <IOBluetooth/OBEX.h> if there was an error. The delegate is informed 
 * through client:didFinishSetPathRequestWithError:responseCode:responseHeaders: 
 * when the request is finished.
 *
 * You must have already sent a Connect request; otherwise, this fails and
 * return kOBEXSessionNotConnectedError.
 *
 * Note the Connection ID is automatically sent in the request headers if one
 * was provided by the server in a previous Connect response.
 */
- (OBEXError)sendSetPathRequestWithHeaders:(BBOBEXHeaderSet *)headers
              changeToParentDirectoryFirst:(BOOL)changeToParentDirectoryFirst
                 createDirectoriesIfNeeded:(BOOL)createDirectoriesIfNeeded;

/*
 * Aborts the current request if a Put or Get request is currently in progress.
 *
 * This schedules an Abort request to be sent when possible (i.e. when the 
 * client next receives a server response).
 *
 * Returns kOBEXSuccess if the request was sent, or some other OBEXError value 
 * from <IOBluetooth/OBEX.h> if there was an error. The delegate is informed 
 * through client:didFinishAbortRequestWithError:responseCode:forStream:
 * when the Abort request is finished.
 */
- (void)abortCurrentRequest;

/*
 * Returns whether the OBEX session is connected (i.e. whether a Connect
 * request has been sent, without a following Disconnect request).
 */
- (BOOL)isConnected;

/*
 * Returns the Connection ID for the OBEX session, if one was received in a
 * response to a previous Connect request.
 *
 * This is automatically sent by the client for each request; you do not need
 * to add it to the request headers yourself.
 */
- (uint32_t)connectionID;

/*
 * Returns the RFCOMM channel for the client.
 */
- (IOBluetoothRFCOMMChannel *)RFCOMMChannel;

/*
 * Returns whether this client has a Connection ID.
 */
- (BOOL)hasConnectionID;

/*
 * Returns the maximum packet length for the OBEX session.
 */
- (OBEXMaxPacketLength)maximumPacketLength;

/*
 * Sets the client delegate to <delegate>.
 */
- (void)setDelegate:(id)delegate;

/*
 * Returns the delegate for this client.
 */
- (id)delegate;

/*
 * Sets whether debug messages should be displayed (default is NO).
 */
+ (void)setDebug:(BOOL)debug;

@end



/*
 * This informal protocol describes the methods that can be implemented for a 
 * BBBluetoothOBEXClient delegate.
 */
@protocol BBBluetoothOBEXClientDelegate

/*
 * Called when a Connect request is completed. <error> is set to kOBEXSuccess 
 * if the request finished without an error, or some other OBEXError value
 * from <IOBluetooth/OBEX.h> if an error occured. <response> contains the
 * response code and headers.
 *
 * The <error> only indicates whether the request was processed successfully;
 * use the response code in <response> to see whether the request was actually
 * accepted by the OBEX server.
 */
- (void)client:(BBBluetoothOBEXClient *)client
didFinishConnectRequestWithError:(OBEXError)error 
      response:(BBOBEXResponse *)response;

/*
 * Called when a Disconnect request is completed. <error> is set to kOBEXSuccess 
 * if the request finished without an error, or some other OBEXError value
 * from <IOBluetooth/OBEX.h> if an error occured. <response> contains the
 * response code and headers.
 *
 * The <error> only indicates whether the request was processed successfully;
 * use the response code in <response> to see whether the request was actually
 * accepted by the OBEX server.
 */
- (void)client:(BBBluetoothOBEXClient *)client
didFinishDisconnectRequestWithError:(OBEXError)error 
      response:(BBOBEXResponse *)response;

/*
 * Called when a Put request is completed. <error> is set to kOBEXSuccess 
 * if the request finished without an error, or some other OBEXError value
 * from <IOBluetooth/OBEX.h> if an error occured. The <inputStream> is the
 * stream originally passed to sendPutRequestWithHeaders:readFromStream:, and
 * <response> contains the response code and headers.
 *
 * The <error> only indicates whether the request was processed successfully;
 * use the response code in <response> to see whether the request was actually
 * accepted by the OBEX server.
 */
- (void)client:(BBBluetoothOBEXClient *)client
didFinishPutRequestForStream:(NSInputStream *)inputStream
         error:(OBEXError)error
      response:(BBOBEXResponse *)response;

/*
 * Called each time the client sends another chunk of data to the OBEX server
 * during a Put request. <length> is the number of bytes sent.
 */
- (void)client:(BBBluetoothOBEXClient *)client
  didSendDataOfLength:(unsigned)length;

/*
 * Called each time the client receives another chunk of data from the OBEX
 * server during a Get request. <length> is the number of bytes received, and
 * <totalLength> is the total number of bytes the client expects to receive
 * for the request. <totalLength> is zero if the total length is unknown.
 */
- (void)client:(BBBluetoothOBEXClient *)session
didReceiveDataOfLength:(unsigned)length
    ofTotalLength:(unsigned)totalLength;

/*
 * Called when a Get request is completed. <error> is set to kOBEXSuccess 
 * if the request finished without an error, or some other OBEXError value
 * from <IOBluetooth/OBEX.h> if an error occured. The <outputStream> is the
 * stream originally passed to sendGetRequestWithHeaders:writeToStream:, and
 * <response> contains the response code and headers. 
 *
 * The <error> only indicates whether the request was processed successfully;
 * use the response code in <response> to see whether the request was actually
 * accepted by the OBEX server.
 */
- (void)client:(BBBluetoothOBEXClient *)client
didFinishGetRequestForStream:(NSOutputStream *)outputStream
         error:(OBEXError)error
      response:(BBOBEXResponse *)response;

/*
 * Called when a SetPath request is completed. <error> is set to kOBEXSuccess 
 * if the request finished without an error, or some other OBEXError value
 * from <IOBluetooth/OBEX.h> if an error occured. <response> contains the
 * response code and headers.
 *
 * The <error> only indicates whether the request was processed successfully;
 * use the response code in <response> to see whether the request was actually
 * accepted by the OBEX server.
 */
- (void)client:(BBBluetoothOBEXClient *)client
    didFinishSetPathRequestWithError:(OBEXError)error 
      response:(BBOBEXResponse *)response;

/*
 * Called when an Abort request is completed following a call to 
 * abortCurrentRequest:. <error> is set to kOBEXSuccess 
 * if the request finished without an error, or some other OBEXError value
 * from <IOBluetooth/OBEX.h> if an error occured. The <stream> is the
 * stream originally passed to sendPutRequestWithHeaders:readFromStream: or
 * sendGetRequestWithHeaders:writeToStream:, and <response> contains the
 * response code and headers.
 *
 * The <error> only indicates whether the request was processed successfully;
 * use the response code in <response> to see whether the request was actually
 * accepted by the OBEX server.
 */
- (void)client:(BBBluetoothOBEXClient *)session
didAbortRequestWithStream:(NSStream *)stream
         error:(OBEXError)error
      response:(BBOBEXResponse *)response;

@end
