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
//  BBBluetoothOBEXClient.m
//  LightAquaBlue
//

#import "BBBluetoothOBEXClient.h"
#import "BBMutableOBEXHeaderSet.h"
#import "BBOBEXRequest.h"

#import <IOBluetooth/objc/OBEXSession.h>
#import <IOBluetooth/objc/IOBluetoothDevice.h>
#import <IOBluetooth/objc/IOBluetoothOBEXSession.h>
#import <CoreFoundation/CoreFoundation.h>

#define DEBUG_NAME @"[BBBluetoothOBEXClient] "

static BOOL _debug = NO;


@implementation BBBluetoothOBEXClient


- (id)initWithRemoteDeviceAddress:(const BluetoothDeviceAddress *)deviceAddress
                        channelID:(BluetoothRFCOMMChannelID)channelID
                         delegate:(id)delegate;
{
    self = [super init];
    
    mSession = [[IOBluetoothOBEXSession alloc] initWithDevice:[IOBluetoothDevice withAddress:deviceAddress]
                                                    channelID:channelID];
    mDelegate = delegate;    
    
    mMaxPacketLength = 0x2000;
    mLastServerResponse = kOBEXResponseCodeSuccessWithFinalBit;
    
    mConnectionID = 0;
    mHasConnectionID = NO;
    
    mAborting = NO;
    
    mCurrentRequest = nil;
    
    return self;
    
}

- (BBOBEXHeaderSet *)addConnectionIDToHeaders:(BBOBEXHeaderSet *)headers
{
    if (!mHasConnectionID) 
        return headers;
    
    BBMutableOBEXHeaderSet *modifiedHeaders = [BBMutableOBEXHeaderSet headerSet];
    [modifiedHeaders addHeadersFromHeaderSet:headers];
    [modifiedHeaders setValueForConnectionIDHeader:mConnectionID];
    return modifiedHeaders;
}

- (OBEXError)sendConnectRequestWithHeaders:(BBOBEXHeaderSet *)headers
{
    if (mCurrentRequest && ![mCurrentRequest isFinished])
        return kOBEXSessionBusyError;
    
    BBOBEXConnectRequest *request = 
        [[BBOBEXConnectRequest alloc] initWithClient:self 
                                       eventSelector:@selector(handleSessionEvent:)
                                             session:mSession];
    OBEXError status = [request beginWithHeaders:headers];
    if (status == kOBEXSuccess) {
        [mCurrentRequest release];
        mCurrentRequest = request;
    } else {
        [request release];
    }
    return status;
}

- (OBEXError)sendDisconnectRequestWithHeaders:(BBOBEXHeaderSet *)headers
{
    if (mCurrentRequest && ![mCurrentRequest isFinished])
        return kOBEXSessionBusyError;
    
    BBOBEXDisconnectRequest *request = 
        [[BBOBEXDisconnectRequest alloc] initWithClient:self 
                                          eventSelector:@selector(handleSessionEvent:)
                                                session:mSession];
    BBOBEXHeaderSet *realHeaders = (mHasConnectionID ?
            [self addConnectionIDToHeaders:headers] : headers);
    OBEXError status = [request beginWithHeaders:realHeaders];    
    if (status == kOBEXSuccess) {
        [mCurrentRequest release];
        mCurrentRequest = request;
    } else {
        [request release];
    }
    return status;
}

- (OBEXError)sendPutRequestWithHeaders:(BBOBEXHeaderSet *)headers
                        readFromStream:(NSInputStream *)inputStream
{
    if (mCurrentRequest && ![mCurrentRequest isFinished])
        return kOBEXSessionBusyError;
    
    BBOBEXPutRequest *request = 
        [[BBOBEXPutRequest alloc] initWithClient:self 
                                   eventSelector:@selector(handleSessionEvent:)
                                         session:mSession
                                     inputStream:inputStream];
    BBOBEXHeaderSet *realHeaders = (mHasConnectionID ?
            [self addConnectionIDToHeaders:headers] : headers);    
    OBEXError status = [request beginWithHeaders:realHeaders];    
    if (status == kOBEXSuccess) {
        [mCurrentRequest release];
        mCurrentRequest = request;
    } else {
        [request release];
    }
    return status;
}

- (OBEXError)sendGetRequestWithHeaders:(BBOBEXHeaderSet *)headers
                         writeToStream:(NSOutputStream *)outputStream
{
    if (mCurrentRequest && ![mCurrentRequest isFinished])
        return kOBEXSessionBusyError;
    
    BBOBEXGetRequest *request =
        [[BBOBEXGetRequest alloc] initWithClient:self 
                                   eventSelector:@selector(handleSessionEvent:)
                                         session:mSession
                                    outputStream:outputStream];
    BBOBEXHeaderSet *realHeaders = (mHasConnectionID ?
            [self addConnectionIDToHeaders:headers] : headers);    
    OBEXError status = [request beginWithHeaders:realHeaders];    
    if (status == kOBEXSuccess) {
        [mCurrentRequest release];
        mCurrentRequest = request;
    } else {
        [request release];
    }
    return status;
}

- (OBEXError)sendSetPathRequestWithHeaders:(BBOBEXHeaderSet *)headers
              changeToParentDirectoryFirst:(BOOL)changeToParentDirectoryFirst
                 createDirectoriesIfNeeded:(BOOL)createDirectoriesIfNeeded
{
    if (mCurrentRequest && ![mCurrentRequest isFinished])
        return kOBEXSessionBusyError;
    
    BBOBEXSetPathRequest *request = 
        [[BBOBEXSetPathRequest alloc] initWithClient:self 
                                       eventSelector:@selector(handleSessionEvent:)
                                             session:mSession
                        changeToParentDirectoryFirst:changeToParentDirectoryFirst
                           createDirectoriesIfNeeded:createDirectoriesIfNeeded];
    BBOBEXHeaderSet *realHeaders = (mHasConnectionID ?
            [self addConnectionIDToHeaders:headers] : headers);    
    OBEXError status = [request beginWithHeaders:realHeaders];    
    if (status == kOBEXSuccess) {
        [mCurrentRequest release];
        mCurrentRequest = request;
    } else {
        [request release];
    }
    return status;
}

- (void)abortCurrentRequest
{
    if (_debug) NSLog(DEBUG_NAME @"[abortCurrentRequest]");

    if (!mCurrentRequest || [mCurrentRequest isFinished] || mAborting)
        return;

    if (_debug) NSLog(DEBUG_NAME @"Aborting later...");
    
	// Just set an abort flag -- can't send OBEXAbort right away because we 
	// might be in the middle of a transaction, and we must wait our turn to 
	// send the abort (i.e. wait until after we've received a server response)    
    mAborting = YES;
}


#pragma mark -

- (void)finishedCurrentRequestWithError:(OBEXError)error responseCode:(int)responseCode
{
    if (_debug) NSLog(DEBUG_NAME @"[finishedCurrentRequestWithError] %d 0x%02x", error, responseCode);
    
    mAborting = NO;
    [mCurrentRequest finishedWithError:error responseCode:responseCode];
    
    [mCurrentRequest release];
    mCurrentRequest = nil;
}

- (void)performAbort
{
    if (_debug) NSLog(DEBUG_NAME @"[performAbort]");
    
    [mCurrentRequest release];
    
    mCurrentRequest = [[BBOBEXAbortRequest alloc] initWithClient:self
                                                   eventSelector:@selector(handleSessionEvent:)
                                                         session:mSession];
    
    OBEXError status = [mCurrentRequest beginWithHeaders:nil];
    if (status != kOBEXSuccess)
        [self finishedCurrentRequestWithError:status responseCode:0];
}

- (void)processResponseWithHeaders:(BBMutableOBEXHeaderSet *)responseHeaders
                      responseCode:(int)responseCode
{
    if (_debug) NSLog(DEBUG_NAME @"processResponseWithHeaders 0x%x", responseCode);
    
    if (responseCode == kOBEXResponseCodeContinueWithFinalBit) {
        if (mAborting) {
            [self performAbort];
            return;
        }
        
        [mCurrentRequest receivedResponseWithHeaders:responseHeaders];
        
        OBEXError status = [mCurrentRequest sendNextRequestPacket];
        if (status != kOBEXSuccess) {
            [self finishedCurrentRequestWithError:status responseCode:responseCode];
            return;
        }
    } else {
        [mCurrentRequest receivedResponseWithHeaders:responseHeaders];
        mLastServerResponse = responseCode;
        [self finishedCurrentRequestWithError:kOBEXSuccess responseCode:responseCode];
    }
}

- (void)handleSessionEvent:(const OBEXSessionEvent *)event
{
    if (_debug) NSLog(DEBUG_NAME @"[handleSessionEvent] event %d (current request=%@)", 
                     event->type, mCurrentRequest);   
        
    if (mCurrentRequest) {
        if (event->type == kOBEXSessionEventTypeError) { 
            if (_debug) NSLog(DEBUG_NAME @"[handleSessionEvent] error occurred %d", event->u.errorData.error);
            [self finishedCurrentRequestWithError:event->u.errorData.error
                                     responseCode:0];
            return;
        }
        
        int responseCode;
        BBMutableOBEXHeaderSet *responseHeaders = nil;
        if ([mCurrentRequest readOBEXResponseHeaders:&responseHeaders
                                     andResponseCode:&responseCode 
                                    fromSessionEvent:event]) {
            if (!responseHeaders)
                responseHeaders = [BBMutableOBEXHeaderSet headerSet];
            
            if (event->type == kOBEXSessionEventTypeConnectCommandResponseReceived) {
                // note any received connection id so it can be sent with later
                // requests
                if ([responseHeaders containsValueForHeader:kOBEXHeaderIDConnectionID]) {
                    mConnectionID = [responseHeaders valueForConnectionIDHeader];
                    mHasConnectionID = YES;
                }
            } else if (event->type == kOBEXSessionEventTypeDisconnectCommandResponseReceived) {
                // disconnected, can clear connection id now
                mConnectionID = 0;
                mHasConnectionID = NO;
            }
            
            [self processResponseWithHeaders:responseHeaders 
                                responseCode:responseCode];
        } else {
            // unable to read response / response didn't match current request
            if (_debug) NSLog(DEBUG_NAME @"[handleSessionEvent] can't parse event!");            
            [self finishedCurrentRequestWithError:kOBEXSessionBadResponseError
                                     responseCode:0];
        }
    } else {
        if (_debug) NSLog(DEBUG_NAME @"ignoring event received while idle: %d", 
              event->type);
    }    
}

- (int)serverResponseForLastRequest
{
    return mLastServerResponse;
}

// for internal testing
- (void)setOBEXSession:(OBEXSession *)session
{
    [session retain];
    [mSession release];
    mSession = session;
}

- (BOOL)isConnected
{
    if (mSession)
        return [mSession hasOpenOBEXConnection];
    return NO;
}

- (IOBluetoothRFCOMMChannel *)RFCOMMChannel
{
    if (mSession && [mSession isKindOfClass:[IOBluetoothOBEXSession class]]) {
        IOBluetoothOBEXSession *session = (IOBluetoothOBEXSession *)mSession;
        return [session getRFCOMMChannel];
    }
    return nil;
}

- (uint32_t)connectionID
{
    return mConnectionID;
}

- (BOOL)hasConnectionID
{
    return mHasConnectionID;
}

- (OBEXMaxPacketLength)maximumPacketLength
{
    return mMaxPacketLength;
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
    [BBOBEXRequest setDebug:debug];
}

- (void)dealloc
{
    [mSession setEventSelector:NULL target:nil refCon:NULL];
    [mCurrentRequest release];
    mCurrentRequest = nil; // if client is deleted during a delegate callback
    [mSession closeTransportConnection];
    [mSession release];
    mSession = nil;
    [super dealloc];
}
@end
