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
//  BBOBEXRequestHandler.h
//  LightAquaBlue
//
//  These are internal classes used by BBBluetoothOBEXServer for handling
//  incoming client requests. Each BBOBEXRequestHandler subclass encapsulates
//  the process for handling a particular type of request.
//

#import <Foundation/Foundation.h>
#import <IOBluetooth/OBEX.h>

@class BBBluetoothOBEXServer;
@class BBOBEXHeaderSet;
@class BBMutableOBEXHeaderSet;
@class OBEXSession;


@interface BBOBEXRequestHandler : NSObject {
    BBBluetoothOBEXServer *mServer;
    SEL mServerEventSelector;
    OBEXSession *mSession;

    int mNextResponseCode;
    BBMutableOBEXHeaderSet *mNextResponseHeaders;
}

+ (void)setDebug:(BOOL)debug;

- (id)initWithServer:(BBBluetoothOBEXServer *)server
       eventSelector:(SEL)selector
             session:(OBEXSession *)session;

- (void)setNextResponseCode:(int)responseCode;

- (void)addResponseHeaders:(BBOBEXHeaderSet *)responseHeaders;

- (BOOL)handleRequestEvent:(const OBEXSessionEvent *)event;


/*** for subclasses - calls errorOccurred:description: on delegate ***/
- (void)errorOccurred:(OBEXError)error
          description:(NSString *)description;


/*** methods below must be overriden by subclasses, and should be regarded
    as 'protected' - they don't need to be called by outside classes ***/

- (BOOL)readOBEXRequestHeaders:(BBMutableOBEXHeaderSet **)requestHeaders
               andRequestFlags:(OBEXFlags *)flags
              fromSessionEvent:(const OBEXSessionEvent *)event;

- (void)prepareResponseForRequestWithHeaders:(BBMutableOBEXHeaderSet *)requestHeaders
                                       flags:(OBEXFlags)flags
                        isFinalRequestPacket:(BOOL)isFinalRequestPacket;

- (OBEXError)sendNextResponsePacket;

- (void)handleRequestAborted;

- (void)notifyRequestFinished;

@end


@interface BBOBEXConnectRequestHandler : BBOBEXRequestHandler {
    CFMutableDataRef mHeadersDataRef;
    OBEXMaxPacketLength mMaxPacketLength;
}
@end

@interface BBOBEXDisconnectRequestHandler : BBOBEXRequestHandler {
    CFMutableDataRef mHeadersDataRef;
}
@end

@interface BBOBEXPutRequestHandler : BBOBEXRequestHandler {
    CFMutableDataRef mHeadersDataRef;
    BBMutableOBEXHeaderSet *mPreviousRequestHeaders;
    NSOutputStream *mOutputStream;
    BOOL mDefinitelyIsPut;
    BOOL mAborted;
}
@end

@interface BBOBEXGetRequestHandler : BBOBEXRequestHandler {
    CFMutableDataRef mHeadersDataRef;
    NSMutableData *mSentBodyData;
    NSInputStream *mInputStream;
    BOOL mAborted;
}
@end

@interface BBOBEXSetPathRequestHandler : BBOBEXRequestHandler {
    CFMutableDataRef mHeadersDataRef;
}
@end
