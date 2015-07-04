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
//  BBOBEXRequestHandler.m
//  LightAquaBlue
//
//  Created by Bea on 3/10/07.
//  Copyright 2007 __MyCompanyName__. All rights reserved.
//

#import "BBOBEXRequestHandler.h"
#import "BBBluetoothOBEXServer.h"
#import "BBMutableOBEXHeaderSet.h"

#import <IOBluetooth/objc/OBEXSession.h>

static BOOL _debug = NO;


@implementation BBOBEXRequestHandler

+ (void)setDebug:(BOOL)debug
{
    _debug = debug;
}

- (id)initWithServer:(BBBluetoothOBEXServer *)server 
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
{
    self = [super init];
    mServer = server;  // don't retain
    mServerEventSelector = selector;
    mSession = session;    // don't retain
    mNextResponseCode = -1;
    return self;
}

- (void)setNextResponseCode:(int)responseCode;
{
    mNextResponseCode = responseCode;
}

- (int)nextResponseCode
{
    return mNextResponseCode;
}

- (void)addResponseHeaders:(BBOBEXHeaderSet *)responseHeaders
{
    if (!mNextResponseHeaders)
        mNextResponseHeaders = [[BBMutableOBEXHeaderSet alloc] init];
    
    [mNextResponseHeaders addHeadersFromHeaderSet:responseHeaders];
}

/*
    Returns whether the request has finished (i.e. sent the final response,
    or error occurred while sending a response).
 */
- (BOOL)handleRequestEvent:(const OBEXSessionEvent *)event
{
    if (_debug) NSLog(@"[BBOBEXRequestHandler] handleRequestEvent (type=%d)", event->type);
    BBMutableOBEXHeaderSet *requestHeaders = nil;
    OBEXFlags requestFlags = 0;

    if (mNextResponseHeaders) {
        [mNextResponseHeaders release];
        mNextResponseHeaders = nil;
    }
    
    // read the client request
    if (_debug) NSLog(@"[BBOBEXRequestHandler] handleRequestEvent read headers");    
    if (![self readOBEXRequestHeaders:&requestHeaders 
                      andRequestFlags:&requestFlags 
                     fromSessionEvent:event]) {
        [self errorOccurred:kOBEXInternalError 
                description:@"Wrong request handler assigned to read request headers!"];
                        // OR we got a new request before the last one finished???
        mNextResponseCode = kOBEXResponseCodeInternalServerErrorWithFinalBit;
        [self sendNextResponsePacket];
        [self notifyRequestFinished];
        return YES;
    }
    
    if (!requestHeaders) {
        [self errorOccurred:kOBEXInternalError 
                description:@"Can't read request headers!"];
        mNextResponseCode = kOBEXResponseCodeBadRequestWithFinalBit;
        [self sendNextResponsePacket];
        [self notifyRequestFinished];
        return YES;    
    }
    
    // get the response for this request
    if (_debug) NSLog(@"[BBOBEXRequestHandler] handleRequestEvent getting response");
    [self prepareResponseForRequestWithHeaders:requestHeaders
                                         flags:requestFlags
                          isFinalRequestPacket:event->isEndOfEventData];
    
    // send the response
    if (_debug) NSLog(@"[BBOBEXRequestHandler] handleRequestEvent sending response 0x%x", mNextResponseCode);
    OBEXError status = [self sendNextResponsePacket];
    
    if (status != kOBEXSuccess) {       
        [self errorOccurred:status 
                description:@"Error sending server response"];
        return YES;
    }
    
    if (mNextResponseCode != kOBEXResponseCodeContinueWithFinalBit) {
        [self notifyRequestFinished];
        return YES;
    }
    
    return NO;
}

- (void)errorOccurred:(OBEXError)error description:(NSString *)description
{
    if ([[mServer delegate] respondsToSelector:@selector(server:errorOccurred:description:)]) {
        [[mServer delegate] server:mServer
                     errorOccurred:error
                       description:description];
    }    
}

/*** methods below are to be overriden ***/

- (BOOL)readOBEXRequestHeaders:(BBMutableOBEXHeaderSet **)requestHeaders
               andRequestFlags:(OBEXFlags *)flags
              fromSessionEvent:(const OBEXSessionEvent *)event
{
    return NO;
}

- (void)prepareResponseForRequestWithHeaders:(BBMutableOBEXHeaderSet *)requestHeaders
                                       flags:(OBEXFlags)flags
                        isFinalRequestPacket:(BOOL)isFinalRequestPacket
{
    mNextResponseCode = kOBEXResponseCodeInternalServerErrorWithFinalBit;
}

- (void)handleRequestAborted
{
    [mSession OBEXAbortResponse:kOBEXResponseCodeSuccessWithFinalBit
                optionalHeaders:NULL 
          optionalHeadersLength:0
                  eventSelector:mServerEventSelector
                 selectorTarget:mServer 
                         refCon:NULL];
}

- (OBEXError)sendNextResponsePacket
{
    return kOBEXInternalError;
}

- (void)notifyRequestFinished
{
}

- (void)dealloc
{
    [mNextResponseHeaders release];
    [super dealloc];
}

@end


@implementation BBOBEXConnectRequestHandler

- (BOOL)readOBEXRequestHeaders:(BBMutableOBEXHeaderSet **)requestHeaders
               andRequestFlags:(OBEXFlags *)flags
              fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (_debug) NSLog(@"[BBOBEXConnectRequestHandler] readOBEXRequestHeaders");

    if (event->type != kOBEXSessionEventTypeConnectCommandReceived)
        return NO;
    const OBEXConnectCommandData *request = &event->u.connectCommandData;
    *flags = request->flags;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:request->headerDataPtr 
                                    length:request->headerDataLength]) {
        *requestHeaders = headers;
    }
    
    // note the request max packet size
    mMaxPacketLength = request->maxPacketSize;
    
    return YES;
}

- (void)prepareResponseForRequestWithHeaders:(BBMutableOBEXHeaderSet *)requestHeaders
                                       flags:(OBEXFlags)flags
                        isFinalRequestPacket:(BOOL)isFinalRequestPacket
{
    if (_debug) NSLog(@"[BBOBEXConnectRequestHandler] prepareResponseForRequestWithHeaders");

    if (![[mServer delegate] respondsToSelector:@selector(server:shouldHandleConnectRequest:)]) {
        mNextResponseCode = kOBEXResponseCodeNotImplementedWithFinalBit;
        return;
    }
    
    // ask delegate to accept/deny request and set the response code & headers
    mNextResponseCode = -1;
    BOOL accept = [[mServer delegate] server:mServer
                  shouldHandleConnectRequest:requestHeaders];
    if (mNextResponseCode == -1) {
        mNextResponseCode = (accept ? kOBEXResponseCodeSuccessWithFinalBit : 
                kOBEXResponseCodeForbiddenWithFinalBit);
    }
}


- (OBEXError)sendNextResponsePacket
{ 
    if (_debug) NSLog(@"[BBOBEXConnectRequestHandler] sendNextResponsePacket");
    
    CFMutableDataRef bytes = NULL;
    if (mNextResponseHeaders) {
        bytes = (CFMutableDataRef)[mNextResponseHeaders toBytes];
        if (!bytes && [mNextResponseHeaders count] > 0)
            return kOBEXInternalError;
    }
    
    OBEXError status = 
        [mSession OBEXConnectResponse:mNextResponseCode
                                flags:0
                      maxPacketLength:mMaxPacketLength
                      optionalHeaders:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL)
                optionalHeadersLength:(bytes ? CFDataGetLength(bytes) : 0)
                        eventSelector:mServerEventSelector
                       selectorTarget:mServer 
                               refCon:NULL];
    if (bytes)
        mHeadersDataRef = bytes;
    return status;    
}

- (void)notifyRequestFinished
{
    if (_debug) NSLog(@"[BBOBEXConnectRequestHandler] notifyRequestFinished");

    if ([[mServer delegate] respondsToSelector:@selector(serverDidHandleConnectRequest:)]) {
        [[mServer delegate] serverDidHandleConnectRequest:mServer];
    }
}

- (void)dealloc
{
    if (mHeadersDataRef)
        CFRelease(mHeadersDataRef);
    [super dealloc];
}

@end


@implementation BBOBEXDisconnectRequestHandler

- (BOOL)readOBEXRequestHeaders:(BBMutableOBEXHeaderSet **)requestHeaders
               andRequestFlags:(OBEXFlags *)flags
              fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (_debug) NSLog(@"[BBOBEXDisconnectRequestHandler] readOBEXRequestHeaders");

    if (event->type != kOBEXSessionEventTypeDisconnectCommandReceived)
        return NO;
    const OBEXDisconnectCommandData *request = &event->u.disconnectCommandData;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:request->headerDataPtr 
                                    length:request->headerDataLength]) {
        *requestHeaders = headers;
    }
    return YES;
}

- (void)prepareResponseForRequestWithHeaders:(BBMutableOBEXHeaderSet *)requestHeaders
                                       flags:(OBEXFlags)flags
                        isFinalRequestPacket:(BOOL)isFinalRequestPacket
{
    if (_debug) NSLog(@"[BBOBEXDisconnectRequestHandler] prepareResponseForRequestWithHeaders");

    if (![[mServer delegate] respondsToSelector: @selector(server:shouldHandleDisconnectRequest:)]) {
        mNextResponseCode = kOBEXResponseCodeNotImplementedWithFinalBit;
        return;
    }
    
    // ask delegate to accept/deny request and set the response code & headers
    mNextResponseCode = -1;
    BOOL accept = [[mServer delegate] server:mServer
               shouldHandleDisconnectRequest:requestHeaders];
    if (mNextResponseCode == -1) {
        mNextResponseCode = (accept ? kOBEXResponseCodeSuccessWithFinalBit : 
                             kOBEXResponseCodeForbiddenWithFinalBit);
    }
}

- (OBEXError)sendNextResponsePacket
{
    if (_debug) NSLog(@"[BBOBEXDisconnectRequestHandler] sendNextResponsePacket");
    
    CFMutableDataRef bytes = NULL;
    if (mNextResponseHeaders) {
        bytes = (CFMutableDataRef)[mNextResponseHeaders toBytes];
        if (!bytes && [mNextResponseHeaders count] > 0)
            return kOBEXInternalError;
    }
    
    OBEXError status = 
        [mSession OBEXDisconnectResponse:mNextResponseCode
                         optionalHeaders:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL)
                   optionalHeadersLength:(bytes ? CFDataGetLength(bytes) : 0)
                           eventSelector:mServerEventSelector
                          selectorTarget:mServer 
                                  refCon:NULL];
    if (bytes)
        mHeadersDataRef = bytes;
    return status;
}

- (void)notifyRequestFinished
{
    if ([[mServer delegate] respondsToSelector:@selector(serverDidHandleDisconnectRequest:)]) {
        [[mServer delegate] serverDidHandleDisconnectRequest:mServer];
    }
}

- (void)dealloc
{
    if (mHeadersDataRef)
        CFRelease(mHeadersDataRef);
    [super dealloc];
}

@end


@implementation BBOBEXPutRequestHandler

- (id)initWithServer:(BBBluetoothOBEXServer *)server 
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
{
    self = [super initWithServer:server eventSelector:selector session:session];
    mDefinitelyIsPut = NO;
    mAborted = NO;
    return self;
}

- (BOOL)readOBEXRequestHeaders:(BBMutableOBEXHeaderSet **)requestHeaders
               andRequestFlags:(OBEXFlags *)flags
              fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (_debug) NSLog(@"[BBOBEXPutRequestHandler] readOBEXRequestHeaders");

    if (event->type != kOBEXSessionEventTypePutCommandReceived)
        return NO;
    const OBEXPutCommandData *request = &event->u.putCommandData;
    
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:request->headerDataPtr 
                                    length:request->headerDataLength]) {
        *requestHeaders = headers;
    }
    
    return YES;
}

- (void)preparePutResponseForRequestWithHeaders:(BBMutableOBEXHeaderSet *)requestHeaders
                           isFinalRequestPacket:(BOOL)isFinalRequestPacket
{
    if (_debug) NSLog(@"[BBOBEXPutRequestHandler] preparePutResponseForRequestWithHeaders");    
    
    // don't pass body & end of body headers onto delegate
    NSData *bodyData = [requestHeaders valueForByteSequenceHeader:kOBEXHeaderIDBody];
    NSData *endOfBodyData = [requestHeaders valueForByteSequenceHeader:kOBEXHeaderIDEndOfBody];
    [requestHeaders removeValueForHeader:kOBEXHeaderIDBody];
    [requestHeaders removeValueForHeader:kOBEXHeaderIDEndOfBody];
    
    if (!mOutputStream) {
        if (![[mServer delegate] respondsToSelector:@selector(server:shouldHandlePutRequest:)]) {
            mNextResponseCode = kOBEXResponseCodeNotImplementedWithFinalBit;
            return;
        }
        
        // ask delegate to accept/deny request and set the response code & headers
        BBOBEXHeaderSet *allRequestHeaders;
        if (mPreviousRequestHeaders) {
            [mPreviousRequestHeaders addHeadersFromHeaderSet:requestHeaders];
            allRequestHeaders = mPreviousRequestHeaders;
        } else {
            allRequestHeaders = requestHeaders;
        }
        mNextResponseCode = -1;
        NSOutputStream *outputStream = [[mServer delegate] server:mServer
                                           shouldHandlePutRequest:allRequestHeaders];
        [mPreviousRequestHeaders release];
        mPreviousRequestHeaders = nil;
        
        // see if delegate accepted request
        BOOL accept = (outputStream != nil);
        if (mNextResponseCode == -1) {
            if (accept) {
                mNextResponseCode = (isFinalRequestPacket ? 
                     kOBEXResponseCodeSuccessWithFinalBit : kOBEXResponseCodeContinueWithFinalBit);
            } else {
                mNextResponseCode = kOBEXResponseCodeForbiddenWithFinalBit;
            }
        }
        
        // delegate refused request?
        if (mNextResponseCode != kOBEXResponseCodeContinueWithFinalBit
                && mNextResponseCode != kOBEXResponseCodeSuccessWithFinalBit) {
            outputStream = nil;
            return;
        }
        
        if (!outputStream) {
            [self errorOccurred:kOBEXInternalError 
                    description:@"Put request error: delegate accepted request but returned nil NSOutputStream"];
            mNextResponseCode = kOBEXResponseCodeInternalServerErrorWithFinalBit;
            return;
        }
        if ([outputStream streamStatus] != NSStreamStatusOpen) {
            [self errorOccurred:kOBEXInternalError 
                    description:@"Put request error: output stream specified by delegate must be opened"];
            mNextResponseCode =  kOBEXResponseCodeInternalServerErrorWithFinalBit;
            return;
        }        
        mOutputStream = [outputStream retain];
    }
    
    int dataLength = 0;
    if (bodyData) {
        if ([mOutputStream write:[bodyData bytes] maxLength:[bodyData length]] < 0)
            dataLength = -1;
        else
            dataLength += [bodyData length];
    }
    
    if (endOfBodyData && dataLength != -1) {
        if ([mOutputStream write:[endOfBodyData bytes] maxLength:[endOfBodyData length]] < 0)
            dataLength = -1;
        else
            dataLength += [endOfBodyData length];
    }    
    
    if (dataLength < 0) {
        [self errorOccurred:kOBEXGeneralError 
                description:@"Put request error: can't write body data to output stream"];        
        mNextResponseCode = kOBEXResponseCodeInternalServerErrorWithFinalBit;
        return;
    }
    
    // will notify delegate even if data length is zero
    if ([[mServer delegate] respondsToSelector:@selector(server:didReceiveDataOfLength:isLastPacket:)]) {
        [[mServer delegate] server:mServer
            didReceiveDataOfLength:dataLength
                      isLastPacket:isFinalRequestPacket];
    }

    if (mNextResponseCode == -1 || mNextResponseCode == kOBEXResponseCodeContinueWithFinalBit ||
                mNextResponseCode == kOBEXResponseCodeSuccessWithFinalBit) {
        mNextResponseCode = (isFinalRequestPacket ? 
             kOBEXResponseCodeSuccessWithFinalBit : kOBEXResponseCodeContinueWithFinalBit);        
    }
}

- (void)preparePutDeleteResponseForRequestWithHeaders:(BBOBEXHeaderSet *)requestHeaders
{
    if (_debug) NSLog(@"[BBOBEXPutRequestHandler] preparePutDeleteResponseForRequestWithHeaders");
    if (![[mServer delegate] respondsToSelector:@selector(server:shouldHandlePutDeleteRequest:)]) {
        mNextResponseCode = kOBEXResponseCodeNotImplementedWithFinalBit;
        return;
    }    
    
    // ask delegate to accept/deny request and set the response code & headers
    BBOBEXHeaderSet *allRequestHeaders;
    if (mPreviousRequestHeaders) {
        [mPreviousRequestHeaders addHeadersFromHeaderSet:requestHeaders];
        allRequestHeaders = mPreviousRequestHeaders;
    } else {
        allRequestHeaders = requestHeaders;
    }
    
    BOOL accept = [[mServer delegate] server:mServer
                shouldHandlePutDeleteRequest:allRequestHeaders];
    
    [mPreviousRequestHeaders release];
    mPreviousRequestHeaders = nil;
    
    if (mNextResponseCode == -1 || mNextResponseCode == kOBEXResponseCodeContinueWithFinalBit ||
                mNextResponseCode == kOBEXResponseCodeSuccessWithFinalBit) {
        mNextResponseCode = (accept ? kOBEXResponseCodeSuccessWithFinalBit : 
                             kOBEXResponseCodeForbiddenWithFinalBit);
    }
}

- (void)prepareResponseForRequestWithHeaders:(BBMutableOBEXHeaderSet *)requestHeaders
                                       flags:(OBEXFlags)flags
                        isFinalRequestPacket:(BOOL)isFinalRequestPacket
{    
    if (_debug) NSLog(@"[BBOBEXPutRequestHandler] prepareResponseForRequestWithHeaders");
    
    BOOL hasBodyData = ( requestHeaders &&
                        ([requestHeaders containsValueForHeader:kOBEXHeaderIDBody] ||
                        [requestHeaders containsValueForHeader:kOBEXHeaderIDEndOfBody]) );
    if (hasBodyData)
        mDefinitelyIsPut = YES;
    
    if (mDefinitelyIsPut) {
        [self preparePutResponseForRequestWithHeaders:requestHeaders
                                 isFinalRequestPacket:isFinalRequestPacket];
    } else {
        if (isFinalRequestPacket) {
            [self preparePutDeleteResponseForRequestWithHeaders:requestHeaders];
        } else {
            if (_debug) NSLog(@"[BBOBEXPutRequestHandler] don't know if it's a Put or Put-Delete, so just continue");
            mNextResponseCode = kOBEXResponseCodeContinueWithFinalBit;
            
            // keep request headers so they can be passed to delegate later
            if (!mPreviousRequestHeaders)
                mPreviousRequestHeaders = [[BBMutableOBEXHeaderSet alloc] init];
            [mPreviousRequestHeaders addHeadersFromHeaderSet:requestHeaders];
        }
    }
}

- (OBEXError)sendNextResponsePacket
{
    if (_debug) NSLog(@"[BBOBEXPutRequestHandler] sendNextResponsePacket");
    
    CFMutableDataRef bytes = NULL;
    if (mNextResponseHeaders) {
        bytes = (CFMutableDataRef)[mNextResponseHeaders toBytes];
        if (!bytes && [mNextResponseHeaders count] > 0)
            return kOBEXInternalError;
    }  
    
    OBEXError status = 
        [mSession OBEXPutResponse:mNextResponseCode
                  optionalHeaders:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL)
            optionalHeadersLength:(bytes ? CFDataGetLength(bytes) : 0)
                    eventSelector:mServerEventSelector 
                   selectorTarget:mServer 
                           refCon:NULL];
    if (bytes) {
        if (mHeadersDataRef)
            CFRelease(mHeadersDataRef);
        mHeadersDataRef = bytes;
    }
    return status;
}

- (void)handleRequestAborted
{
    if (_debug) NSLog(@"[BBOBEXPutRequestHandler] handleRequestAborted");

    mAborted = YES;
    mDefinitelyIsPut = YES; // can't abort Delete ops, so this must be a Put
    
    [super handleRequestAborted];
    [self notifyRequestFinished];
}

- (void)notifyRequestFinished
{
    if (_debug) NSLog(@"[BBOBEXPutRequestHandler] notifyRequestFinished");

    if (mDefinitelyIsPut) {
        if ([[mServer delegate] respondsToSelector:@selector(server:didHandlePutRequestForStream:requestWasAborted:)]) {
            [[mServer delegate] server:mServer
                  didHandlePutRequestForStream:mOutputStream
                             requestWasAborted:mAborted];
        }
    } else {
        if ([[mServer delegate] respondsToSelector:@selector(serverDidHandlePutDeleteRequest:)]) {
            [[mServer delegate] serverDidHandlePutDeleteRequest:mServer];
        }
    }
    
    [mOutputStream release];
    mOutputStream = nil;
    mDefinitelyIsPut = NO;
    mAborted = NO;
}

- (void)dealloc
{
    if (mHeadersDataRef)
        CFRelease(mHeadersDataRef);
    [mPreviousRequestHeaders release];
    [mOutputStream release];
    [super dealloc];
}

@end



@implementation BBOBEXGetRequestHandler

- (id)initWithServer:(BBBluetoothOBEXServer *)server 
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
{
    self = [super initWithServer:server eventSelector:selector session:session];
    mAborted = NO;
    return self;
}

- (BOOL)readOBEXRequestHeaders:(BBMutableOBEXHeaderSet **)requestHeaders
               andRequestFlags:(OBEXFlags *)flags
              fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (_debug) NSLog(@"[BBOBEXGetRequestHandler] readOBEXRequestHeaders");

    if (event->type != kOBEXSessionEventTypeGetCommandReceived)
        return NO;
    const OBEXGetCommandData *request = &event->u.getCommandData;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:request->headerDataPtr 
                                    length:request->headerDataLength]) {
        *requestHeaders = headers;
    }
    return YES;
}

- (NSMutableData *)readNextChunkForHeaderLength:(size_t)headersLength
                                    isLastChunk:(BOOL *)outIsLastChunk
{ 
    if (_debug) NSLog(@"[BBOBEXGetRequestHandler] readNextChunkForHeaderLength");

    if (mInputStream == nil)
        return nil;
    
    OBEXMaxPacketLength	maxPacketSize = 
        [mSession getAvailableCommandPayloadLength:kOBEXOpCodePut];
    if (maxPacketSize == 0 || headersLength > maxPacketSize)
        return nil;
    
	OBEXMaxPacketLength maxBodySize = maxPacketSize - headersLength;
    
    NSMutableData *data = [NSMutableData dataWithLength:maxBodySize];
    int len = [mInputStream read:[data mutableBytes]
                       maxLength:maxBodySize];
    
    if (_debug) NSLog(@"[BBOBEXGetRequestHandler] read %d bytes (maxBodySize = %d)", len, maxBodySize);
    
    // is last packet if there wasn't enough body data to fill up the packet
    if (len >= 0)
        *outIsLastChunk = (len < maxBodySize);
    
    [data setLength:len];
    return data;
}

- (void)prepareResponseForRequestWithHeaders:(BBMutableOBEXHeaderSet *)requestHeaders
                                       flags:(OBEXFlags)flags
                        isFinalRequestPacket:(BOOL)isFinalRequestPacket
{
    if (_debug) NSLog(@"[BBOBEXGetRequestHandler] prepareResponseForRequestWithHeaders");

    if (!mInputStream) {
        if (![[mServer delegate] respondsToSelector:@selector(server:shouldHandleGetRequest:)]) {
            mNextResponseCode = kOBEXResponseCodeNotImplementedWithFinalBit;
            return;
        }
        
        // ask delegate to accept/deny request and set the response code & headers
        mNextResponseCode = -1;
        NSInputStream *inputStream = [[mServer delegate] server:mServer
                                         shouldHandleGetRequest:requestHeaders];
        BOOL accept = (inputStream != nil);
        if (mNextResponseCode == -1) {
            mNextResponseCode = (accept ? kOBEXResponseCodeSuccessWithFinalBit : 
                    kOBEXResponseCodeForbiddenWithFinalBit);
        }

        // delegate refused request?
        if (mNextResponseCode != kOBEXResponseCodeContinueWithFinalBit
                && mNextResponseCode != kOBEXResponseCodeSuccessWithFinalBit) {
            inputStream = nil;
            return;
        }
        
        if (!inputStream) {
            [self errorOccurred:kOBEXInternalError 
                    description:@"Get request error: delegate accepted request but returned nil NSInputStream"];
            mNextResponseCode = kOBEXResponseCodeInternalServerErrorWithFinalBit;
            return;
        }
        if ([inputStream streamStatus] != NSStreamStatusOpen) {
            [self errorOccurred:kOBEXInternalError 
                    description:@"Get request error: input stream specified by delegate must be opened"];
            mNextResponseCode = kOBEXResponseCodeInternalServerErrorWithFinalBit;
            return;
        }                
        mInputStream = [inputStream retain];
    }
    
    if (!mNextResponseHeaders)
        mNextResponseHeaders = [[BBMutableOBEXHeaderSet alloc] init];
    CFMutableDataRef tempHeaderBytes = (CFMutableDataRef)[mNextResponseHeaders toBytes];
    int currentHeaderLength = 0; 
    if (tempHeaderBytes) {
        currentHeaderLength = CFDataGetLength(tempHeaderBytes);
        CFRelease(tempHeaderBytes);
    }
    
    BOOL isLastChunk = YES;
    
    // the GET headers seem to need 3 bytes padding, maybe for the response code
    // plus packet length in the headers.
    NSMutableData *mutableData = [self readNextChunkForHeaderLength:currentHeaderLength + 3
                                                        isLastChunk:&isLastChunk];
    
    if (!mutableData) {
        [self errorOccurred:kOBEXInternalError 
                description:@"Get request error: can't read data from input stream"];
        mNextResponseCode = kOBEXResponseCodeInternalServerErrorWithFinalBit;
        return;
    }
    
    uint8_t headerID = (isLastChunk ? kOBEXHeaderIDBody : kOBEXHeaderIDEndOfBody);
    [mNextResponseHeaders setValue:mutableData forByteSequenceHeader:headerID];
    if (![mNextResponseHeaders containsValueForHeader:headerID]) {
        [self errorOccurred:kOBEXInternalError 
                description:@"Get request error: can't add body data to response headers"];                    
        mNextResponseCode = kOBEXResponseCodeInternalServerErrorWithFinalBit;
        return;
    }
    
    [mutableData retain];
    [mSentBodyData release];
    mSentBodyData = mutableData;

    if (mNextResponseCode == -1 || mNextResponseCode == kOBEXResponseCodeContinueWithFinalBit ||
                mNextResponseCode == kOBEXResponseCodeSuccessWithFinalBit) {
        if (isLastChunk)
            mNextResponseCode = kOBEXResponseCodeSuccessWithFinalBit;
        else
            mNextResponseCode = kOBEXResponseCodeContinueWithFinalBit;
    }
}

- (OBEXError)sendNextResponsePacket
{   
    if (_debug) NSLog(@"[BBOBEXGetRequestHandler] sendNextResponsePacket");

    CFMutableDataRef bytes = NULL;
    if (mNextResponseHeaders) {
        bytes = (CFMutableDataRef)[mNextResponseHeaders toBytes];
        if (!bytes && [mNextResponseHeaders count] > 0)
            return kOBEXInternalError;
    }   
    
    OBEXError status = 
        [mSession OBEXGetResponse:mNextResponseCode 
                  optionalHeaders:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL) 
            optionalHeadersLength:(bytes ? CFDataGetLength(bytes) : 0)
                    eventSelector:mServerEventSelector 
                   selectorTarget:mServer 
                           refCon:NULL];
    
    if (bytes) {
        if (mHeadersDataRef) 
            CFRelease(mHeadersDataRef);
        mHeadersDataRef = bytes;
    }
    
    
    if (mSentBodyData && [[mServer delegate] respondsToSelector:@selector(server:didSendDataOfLength:)]) {
        [[mServer delegate] server:mServer 
               didSendDataOfLength:[mSentBodyData length]];
    }    
    
    return status;
}

- (void)handleRequestAborted
{
    if (_debug) NSLog(@"[BBOBEXGetRequestHandler] handleRequestAborted");

    mAborted = YES;
    [super handleRequestAborted];    
    [self notifyRequestFinished];
}

- (void)notifyRequestFinished
{
    if ([[mServer delegate] respondsToSelector:@selector(server:didHandleGetRequestForStream:requestWasAborted:)]) {
        [[mServer delegate] server:mServer
      didHandleGetRequestForStream:mInputStream
                 requestWasAborted:mAborted];
    }
    
    [mInputStream release];
    mInputStream = nil;
    mAborted = NO;
}

- (void)dealloc
{
    if (mHeadersDataRef)
        CFRelease(mHeadersDataRef);
    [mSentBodyData release];
    [mInputStream release];
    [super dealloc];
}

@end



@implementation BBOBEXSetPathRequestHandler

- (BOOL)readOBEXRequestHeaders:(BBMutableOBEXHeaderSet **)requestHeaders
               andRequestFlags:(OBEXFlags *)flags
              fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (_debug) NSLog(@"[BBOBEXSetPathRequestHandler] readOBEXRequestHeaders");

    if (event->type != kOBEXSessionEventTypeSetPathCommandReceived)
        return NO;
    const OBEXSetPathCommandData *request = &event->u.setPathCommandData;
    *flags = request->flags;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:request->headerDataPtr 
                                    length:request->headerDataLength]) {
        *requestHeaders = headers;
    }
    return YES;
}

- (void)prepareResponseForRequestWithHeaders:(BBMutableOBEXHeaderSet *)requestHeaders
                                       flags:(OBEXFlags)flags
                        isFinalRequestPacket:(BOOL)isFinalRequestPacket
{   
    if (_debug) NSLog(@"[BBOBEXSetPathRequestHandler] prepareResponseForRequestWithHeaders");

    if (![[mServer delegate] respondsToSelector:@selector(server:shouldHandleSetPathRequest:withFlags:)]) {    
        mNextResponseCode = kOBEXResponseCodeNotImplementedWithFinalBit;    
        return;
    }
    
    //BOOL changeToParentDirectoryFirst = (flags & 1) != 0;
    //BOOL createDirectoriesIfNeeded = (flags & 2) == 0;
    
    // ask delegate to accept/deny request and set the response code & headers
    mNextResponseCode = -1;
    BOOL accept = [[mServer delegate] server:mServer
                  shouldHandleSetPathRequest:requestHeaders
                                   withFlags:flags];
    if (mNextResponseCode == -1) {
        mNextResponseCode = (accept ? kOBEXResponseCodeSuccessWithFinalBit : 
                             kOBEXResponseCodeForbiddenWithFinalBit);
    }
}

- (OBEXError)sendNextResponsePacket
{    
    if (_debug) NSLog(@"[BBOBEXSetPathRequestHandler] sendNextResponsePacket");
    
    CFMutableDataRef bytes = NULL;
    if (mNextResponseHeaders) {
        bytes = (CFMutableDataRef)[mNextResponseHeaders toBytes];
        if (!bytes && [mNextResponseHeaders count] > 0)
            return kOBEXInternalError;
    }
    
    OBEXError status = 
        [mSession OBEXSetPathResponse:mNextResponseCode 
                      optionalHeaders:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL) 
                optionalHeadersLength:(bytes ? CFDataGetLength(bytes) : 0)
                        eventSelector:mServerEventSelector 
                       selectorTarget:mServer 
                               refCon:NULL];
    if (bytes)
        mHeadersDataRef = bytes;
    return status;
}

- (void)notifyRequestFinished
{
    if ([[mServer delegate] respondsToSelector:@selector(serverDidHandleSetPathRequest:)])
        [[mServer delegate] serverDidHandleSetPathRequest:mServer];
}

- (void)dealloc
{
    if (mHeadersDataRef)
        CFRelease(mHeadersDataRef);
    [super dealloc];
}

@end