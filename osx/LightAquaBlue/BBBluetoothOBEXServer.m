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
//  BBBluetoothOBEXServer.m
//  LightAquaBlue
//

#import "BBBluetoothOBEXServer.h"
#import "BBOBEXRequestHandler.h"
#import "BBOBEXHeaderSet.h"

#import <IOBluetooth/objc/OBEXSession.h>
#import <IOBluetooth/objc/IOBluetoothOBEXSession.h>

#define DEBUG_NAME @"[BBBluetoothOBEXServer] "

static BOOL _debug = NO;


@implementation BBBluetoothOBEXServer

- (void)errorOccurred:(OBEXError)error description:(NSString *)description
{
    if (_debug) NSLog(DEBUG_NAME @"errorOccurred: %d description: %@", error, description);

    if ([mDelegate respondsToSelector:@selector(server:errorOccurred:description:)]) {
        [mDelegate server:self
            errorOccurred:error
              description:description];
    }
}


+ (id)serverWithIncomingRFCOMMChannel:(IOBluetoothRFCOMMChannel *)channel
                             delegate:(id)delegate
{
    return [[[BBBluetoothOBEXServer alloc] initWithIncomingRFCOMMChannel:channel
                                                                delegate:delegate] autorelease];
}

- (id)initWithIncomingRFCOMMChannel:(IOBluetoothRFCOMMChannel *)channel
                           delegate:(id)delegate
{
    self = [super init];

    mChannel = [channel retain];
    mDelegate = delegate;

    return self;
}

- (BBOBEXRequestHandler *)handlerForEventType:(OBEXSessionEventType)type
{
    BBOBEXRequestHandler *handler = nil;
    SEL selector = @selector(handleSessionEvent:);

    switch (type) {
        case kOBEXSessionEventTypeConnectCommandReceived:
            handler = [[BBOBEXConnectRequestHandler alloc] initWithServer:self
                                                            eventSelector:selector
                                                                  session:mSession];
            break;
        case kOBEXSessionEventTypeDisconnectCommandReceived:
            handler = [[BBOBEXDisconnectRequestHandler alloc] initWithServer:self
                                                               eventSelector:selector
                                                                     session:mSession];
            break;
        case kOBEXSessionEventTypePutCommandReceived:
            handler = [[BBOBEXPutRequestHandler alloc] initWithServer:self
                                                        eventSelector:selector
                                                              session:mSession];
            break;
        case kOBEXSessionEventTypeGetCommandReceived:
            handler = [[BBOBEXGetRequestHandler alloc] initWithServer:self
                                                        eventSelector:selector
                                                              session:mSession];
            break;
        case kOBEXSessionEventTypeSetPathCommandReceived:
            handler = [[BBOBEXSetPathRequestHandler alloc] initWithServer:self
                                                            eventSelector:selector
                                                                  session:mSession];
            break;
    }
    [handler autorelease];
    return handler;
}

- (void)channelClosed:(IOBluetoothUserNotification *)notification
              channel:(IOBluetoothRFCOMMChannel *)channel
{
    if (_debug) NSLog(DEBUG_NAME @"RFCOMM channel closed!");

    if (mSession) {
        [self errorOccurred:kOBEXSessionTransportDiedError
                description:@"Bluetooth transport connection died"];
    }

    if (channel == mChannel)
        [self close];
}

- (void)run
{
    if (mChannel) {
        IOBluetoothOBEXSession *session =
            [IOBluetoothOBEXSession withIncomingRFCOMMChannel:mChannel
                                                eventSelector:@selector(handleSessionEvent:)
                                               selectorTarget:self
                                                       refCon:NULL];
        mSession = [session retain];

        mChannelNotif = [mChannel registerForChannelCloseNotification:self
                                                             selector:@selector(channelClosed:channel:)];

    } else if (mSession) {
        // for internal testing

        //NSLog(@"send dummy event");

        // dummy event - event selector doesn't seem to get set otherwise if
        // I just call setEventSelector:target:refCon:
        [mSession OBEXConnectResponse:kOBEXResponseCodeSuccessWithFinalBit
                                flags:0
                      maxPacketLength:1024
                      optionalHeaders:NULL
                optionalHeadersLength:0
                        eventSelector:@selector(handleSessionEvent:)
                       selectorTarget:self
                               refCon:NULL];
    }
}

- (void)close
{
    if (_debug) NSLog(DEBUG_NAME @"close");

    [mChannelNotif unregister];
    mChannelNotif = nil;

    // must set the event selector and target to NULL, otherwise the
    // OBEXSession might continue to try to send us events (e.g. if there's
    // a link error)
    if (mSession)
        [mSession setEventSelector:NULL target:nil refCon:NULL];

    [mCurrentRequestHandler release];
    mCurrentRequestHandler = nil;

    [mChannel release];
    mChannel = nil;

    [mSession release];
    mSession = nil;
}

- (void)setResponseCodeForCurrentRequest:(int)responseCode
{
    if (mCurrentRequestHandler)
        [mCurrentRequestHandler setNextResponseCode:responseCode];
}

- (void)addResponseHeadersForCurrentRequest:(BBOBEXHeaderSet *)responseHeaders
{
    if (mCurrentRequestHandler)
        [mCurrentRequestHandler addResponseHeaders:responseHeaders];
}

- (void)handleSessionEvent:(const OBEXSessionEvent *)event
{
    if (_debug) NSLog(DEBUG_NAME @"handleSessionEvent %d", event->type);

    if (event->type == kOBEXSessionEventTypeError) {
        if (mCurrentRequestHandler) {
            [self errorOccurred:event->u.errorData.error
                    description:@"Error occurred during client request"];
        } else {
            [self errorOccurred:event->u.errorData.error
                    description:@"Error occurred while server was idle"];
        }

    } else if (event->type == kOBEXSessionEventTypeAbortCommandReceived) {
        if (mCurrentRequestHandler) {
            if (_debug) NSLog(DEBUG_NAME @"Aborting current request...");
            [mCurrentRequestHandler handleRequestAborted];
        } else {
            if (_debug) NSLog(DEBUG_NAME @"Got Abort request, but no request to abort");
            // not really an error, so errorOccurred: not called
        }

    } else {
        if (_debug) NSLog(DEBUG_NAME @"Received client request");
        if (!mCurrentRequestHandler) {
            mCurrentRequestHandler = [self handlerForEventType:event->type];
            if (!mCurrentRequestHandler) {
                [self errorOccurred:kOBEXGeneralError
                        description:[NSString stringWithFormat:@"Server received unknown event: %d", event->type]];
                return;
            }
            [mCurrentRequestHandler retain];
        }

        if (_debug) NSLog(DEBUG_NAME @"Found handler, %@", mCurrentRequestHandler);
        BOOL requestFinished = [mCurrentRequestHandler handleRequestEvent:event];
        if (requestFinished) {
            if (_debug) NSLog(DEBUG_NAME @"Finished request");
            [mCurrentRequestHandler release];
            mCurrentRequestHandler = nil;
        }
    }
}

- (void)setOBEXSession:(OBEXSession *)session
{
    [session retain];
    [mSession release];
    mSession = session;
}

- (void)setDelegate:(id)delegate
{
    mDelegate = delegate;
}

- (id)delegate
{
    return mDelegate;
}

+ (void)setDebug:(BOOL)debug
{
    _debug = debug;
    [BBOBEXRequestHandler setDebug:debug];
}

- (void)dealloc
{
    [self close];
    [super dealloc];
}

@end
