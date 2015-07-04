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
//  BBOBEXRequest.h
//  LightAquaBlue
//
//  These are internal classes used by BBBluetoothOBEXClient for sending OBEX 
//  client requests. Each BBOBEXRequest subclass encapsulates the process
//  for performing a particular type of request.
//

#import <Foundation/Foundation.h>
#import <IOBluetooth/OBEX.h>

@class BBBluetoothOBEXClient;
@class BBOBEXHeaderSet;
@class BBMutableOBEXHeaderSet;
@class OBEXSession;

@interface BBOBEXRequest : NSObject
{
    BBBluetoothOBEXClient *mClient;
    SEL mClientEventSelector;
    OBEXSession *mSession;
    BOOL mFinished;
    BBMutableOBEXHeaderSet *mResponseHeaders;
}

+ (void)setDebug:(BOOL)debug;

- (id)initWithClient:(BBBluetoothOBEXClient *)client 
       eventSelector:(SEL)selector
             session:(OBEXSession *)session;

- (BOOL)isFinished;

- (OBEXError)beginWithHeaders:(BBOBEXHeaderSet *)headers;

- (void)receivedResponseWithHeaders:(BBMutableOBEXHeaderSet *)responseHeaders;

- (OBEXError)sendNextRequestPacket;

- (void)finishedWithError:(OBEXError)error responseCode:(int)responseCode;

- (BOOL)readOBEXResponseHeaders:(BBMutableOBEXHeaderSet **)responseHeaders
                andResponseCode:(int *)responseCode
               fromSessionEvent:(const OBEXSessionEvent *)event;
@end

@interface BBOBEXConnectRequest : BBOBEXRequest
{
    CFMutableDataRef mHeadersDataRef;
}
@end

@interface BBOBEXDisconnectRequest : BBOBEXRequest
{
    CFMutableDataRef mHeadersDataRef;    
}
@end

@interface BBOBEXPutRequest : BBOBEXRequest
{
    CFMutableDataRef mHeadersDataRef;
    NSMutableData *mSentBodyData;
    NSInputStream *mInputStream;
}
- (id)initWithClient:(BBBluetoothOBEXClient *)client
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
         inputStream:(NSInputStream *)inputStream;
@end

@interface BBOBEXGetRequest : BBOBEXRequest
{
    CFMutableDataRef mHeadersDataRef;
    NSOutputStream *mOutputStream;
    unsigned int mTotalGetLength;
}
- (id)initWithClient:(BBBluetoothOBEXClient *)client
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
        outputStream:(NSOutputStream *)outputStream;
@end

@interface BBOBEXSetPathRequest : BBOBEXRequest
{
    CFMutableDataRef mHeadersDataRef;
    OBEXFlags mRequestFlags;
}
- (id)initWithClient:(BBBluetoothOBEXClient *)client
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
changeToParentDirectoryFirst:(BOOL)changeToParentDirectoryFirst
createDirectoriesIfNeeded:(BOOL)createDirectoriesIfNeeded;
@end

@interface BBOBEXAbortRequest : BBOBEXRequest
{
    NSStream *mStream;
}
- (id)initWithClient:(BBBluetoothOBEXClient *)client
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
currentRequestStream:(NSStream *)stream;
@end
