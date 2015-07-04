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
//  BBOBEXRequest.m
//  LightAquaBlue
//

#import "BBOBEXRequest.h"
#import "BBBluetoothOBEXClient.h"
#import "BBMutableOBEXHeaderSet.h"
#import "BBOBEXHeaderSet.h"
#import "BBOBEXResponse.h"

#import <IOBluetooth/objc/OBEXSession.h>
#import <CoreFoundation/CoreFoundation.h>

static BOOL _debug = NO;


@implementation BBOBEXRequest

+ (void)setDebug:(BOOL)debug
{
    _debug = debug;
}

- (id)initWithClient:(BBBluetoothOBEXClient *)client 
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
{
    self = [super init];
    mClient = client;   // don't retain, avoid retaining both ways
    mClientEventSelector = selector;
    mSession = session; // don't retain
    mFinished = NO;
    return self;
}

- (BOOL)isFinished
{
    return mFinished;
}

- (OBEXError)beginWithHeaders:(BBOBEXHeaderSet *)headers
{
    return kOBEXSuccess;
}

- (void)receivedResponseWithHeaders:(BBMutableOBEXHeaderSet *)responseHeaders
{
    if (!mResponseHeaders)
        mResponseHeaders = [[BBMutableOBEXHeaderSet alloc] init];
    
    // add to current response headers
    // this way we won't lose previous response headers in multi-packet 
    // Put & Get requests
    [mResponseHeaders addHeadersFromHeaderSet:responseHeaders];
}

- (OBEXError)sendNextRequestPacket
{
    return kOBEXSuccess;
}

- (void)finishedWithError:(OBEXError)error responseCode:(int)responseCode
{
}

- (BOOL)readOBEXResponseHeaders:(BBMutableOBEXHeaderSet **)responseHeaders
                andResponseCode:(int *)responseCode
               fromSessionEvent:(const OBEXSessionEvent *)event
{
    return YES;
}

- (void)dealloc
{
    [mResponseHeaders release];
    [super dealloc];
}


@end


@implementation BBOBEXConnectRequest

- (OBEXError)beginWithHeaders:(BBOBEXHeaderSet *)headers
{
    if (_debug) NSLog(@"[BBOBEXConnectRequest] beginWithHeaders (%d headers)", [headers count]);
    CFMutableDataRef bytes = (CFMutableDataRef)[headers toBytes];
    if (!bytes && [headers count] > 0)
        return kOBEXInternalError;
    
	OBEXError status = [mSession OBEXConnect:(OBEXFlags)kOBEXConnectFlagNone
                             maxPacketLength:[mClient maximumPacketLength]
                             optionalHeaders:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL)
                       optionalHeadersLength:(bytes ? CFDataGetLength(bytes) : 0)
                               eventSelector:mClientEventSelector
                              selectorTarget:mClient
                                      refCon:NULL];
    if (bytes)
        mHeadersDataRef = bytes;
	
    return status;
}

- (void)finishedWithError:(OBEXError)error responseCode:(int)responseCode
{
    if (_debug) NSLog(@"[BBOBEXConnectRequest] finishedWithError %@: %d", [mClient delegate], error);
    
    mFinished = YES;    
    if ([[mClient delegate] respondsToSelector:@selector(client:didFinishConnectRequestWithError:response:)]) {
        [[mClient delegate] client:mClient
  didFinishConnectRequestWithError:error
                          response:[BBOBEXResponse responseWithCode:responseCode headers:mResponseHeaders]];
    }
}

- (BOOL)readOBEXResponseHeaders:(BBMutableOBEXHeaderSet **)responseHeaders
                andResponseCode:(int *)responseCode
               fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (event->type != kOBEXSessionEventTypeConnectCommandResponseReceived)
        return NO;
    const OBEXConnectCommandResponseData *resp = &event->u.connectCommandResponseData;
    *responseCode = resp->serverResponseOpCode;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:resp->headerDataPtr 
                                    length:resp->headerDataLength]) {
        *responseHeaders = headers;
    }
    return YES;
}

- (void)dealloc
{
    if (mHeadersDataRef)
        CFRelease(mHeadersDataRef);
    [super dealloc];
}

@end


@implementation BBOBEXDisconnectRequest

- (OBEXError)beginWithHeaders:(BBOBEXHeaderSet *)headers
{
    if (_debug) NSLog(@"[BBOBEXDisconnectRequest] beginWithHeaders (%d headers)", [headers count]);
    
    CFMutableDataRef bytes = (CFMutableDataRef)[headers toBytes];
    if (!bytes && [headers count] > 0)
        return kOBEXInternalError;
    
	OBEXError status = [mSession OBEXDisconnect:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL)
                          optionalHeadersLength:(bytes ? CFDataGetLength(bytes) : 0)
                                  eventSelector:mClientEventSelector
                                 selectorTarget:mClient
                                         refCon:NULL];
    if (bytes)
        mHeadersDataRef = bytes;
    return status;
}

- (void)finishedWithError:(OBEXError)error responseCode:(int)responseCode
{
    if (_debug) NSLog(@"[BBOBEXDisconnectRequest] finishedWithError: %d", error);
    
    mFinished = YES;
    if ([[mClient delegate] respondsToSelector:@selector(client:didFinishDisconnectRequestWithError:response:)]) {
        [[mClient delegate] client:mClient
       didFinishDisconnectRequestWithError:error
                          response:[BBOBEXResponse responseWithCode:responseCode headers:mResponseHeaders]];
    }
}

- (BOOL)readOBEXResponseHeaders:(BBMutableOBEXHeaderSet **)responseHeaders
                andResponseCode:(int *)responseCode
               fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (event->type != kOBEXSessionEventTypeDisconnectCommandResponseReceived)
        return NO;
    const OBEXDisconnectCommandResponseData *resp = &event->u.disconnectCommandResponseData;
    *responseCode = resp->serverResponseOpCode;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:resp->headerDataPtr 
                                    length:resp->headerDataLength]) {
        *responseHeaders = headers;
    }
    return YES;
}

- (void)dealloc
{
    if (mHeadersDataRef)
        CFRelease(mHeadersDataRef);
    [super dealloc];
}

@end


@implementation BBOBEXPutRequest

- (id)initWithClient:(BBBluetoothOBEXClient *)client 
        eventSelector:(SEL)selector
             session:(OBEXSession *)session
          inputStream:(NSInputStream *)inputStream
{
    self = [super initWithClient:client eventSelector:selector session:session];
    mInputStream = [inputStream retain];
    return self;
}

- (NSMutableData *)readNextChunkForHeaderLength:(size_t)headersLength
                                    isLastChunk:(BOOL *)outIsLastChunk
{ 
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
    
    if (_debug) NSLog(@"[BBOBEXPutRequest] read %d bytes (maxBodySize = %d)", len, maxBodySize);
    
    // is last packet if there wasn't enough body data to fill up the packet
    if (len >= 0)
        *outIsLastChunk = (len < maxBodySize);

    [data setLength:len];
    return data;
}

+ (OBEXError)appendEmptyEndOfBodyHeaderToData:(CFMutableDataRef)headerData
{
    if (!headerData) 
        return kOBEXInternalError;
    
    // can't see to add the data using raw bytes, so make a dictionary 
    // and use OBEXHeadersToBytes() to get the end of body header bytes
    
    CFMutableDictionaryRef mutableDict = CFDictionaryCreateMutable(NULL, 1, 
            &kCFTypeDictionaryKeyCallBacks, &kCFTypeDictionaryValueCallBacks);    
    OBEXError status = OBEXAddBodyHeader(NULL, 0, TRUE, mutableDict);
    if (status == kOBEXSuccess) {    
        CFMutableDataRef bodyData = OBEXHeadersToBytes(mutableDict);
        if (bodyData == NULL) {
            CFRelease(mutableDict);
            return kOBEXGeneralError;
        }
        CFDataAppendBytes(headerData, CFDataGetBytePtr(bodyData), 
                          CFDataGetLength(bodyData));
        CFRelease(bodyData);
    }
    
    CFRelease(mutableDict);
    return status;
}

- (OBEXError)beginWithHeaders:(BBOBEXHeaderSet *)headers
{
    if (_debug) NSLog(@"[BBOBEXPutRequest] beginWithHeaders (%d headers)", [headers count]);    
    
    // there's no stream if it's a Put-Delete
    // but if there is a stream, it must be open
    if (mInputStream && [mInputStream streamStatus] != NSStreamStatusOpen) {
        if (_debug) NSLog(@"[BBOBEXPutRequest] given input stream not opened!");
        return kOBEXBadArgumentError;
    }
    
    CFMutableDataRef bytes = (CFMutableDataRef)[headers toBytes];
    if (!bytes && [headers count] > 0)
        return kOBEXInternalError;
        
    BOOL isLastChunk = YES;
    NSMutableData *mutableData = nil;

    if (mInputStream != nil) {
        mutableData = [self readNextChunkForHeaderLength:(bytes ? CFDataGetLength(bytes) : 0)
                                             isLastChunk:&isLastChunk];
        if (!mutableData) {
            if (_debug) NSLog(@"[BBOBEXPutRequest] error reading from stream!");
            if (bytes)
                CFRelease(bytes);
            return kOBEXInternalError; 
        }

        // If zero data read, then this must be a Create-Empty (IrOBEX 3.3.3.6) 
        // so add an empty End-of-Body header, because OBEXPut: won't add body
        // headers if bodyDataLength is zero, in which case the server will 
        // think it's a Put-Delete instead of a Put.
        if ([mutableData length] == 0) {
            if (!bytes)
                bytes = CFDataCreateMutable(NULL, 0);
            OBEXError status = [BBOBEXPutRequest appendEmptyEndOfBodyHeaderToData:bytes];
            if (status != kOBEXSuccess) {
                if (_debug) NSLog(@"[BBOBEXPutRequest] error adding empty end of body");
                CFRelease(bytes);
                return status;
            }
        }
    }
    
    OBEXError status;
    status = [mSession OBEXPut:isLastChunk
                   headersData:(bytes ? (void*)CFDataGetBytePtr(bytes) : NULL)
             headersDataLength:(bytes ? CFDataGetLength(bytes) : 0)
                      bodyData:(mutableData ? [mutableData mutableBytes] : NULL)
                bodyDataLength:(mutableData ? [mutableData length] : 0)
                 eventSelector:mClientEventSelector
                selectorTarget:mClient
                        refCon:NULL];
    if (bytes)
        mHeadersDataRef = bytes;
    
    if (mutableData) {
        [mutableData retain];
        [mSentBodyData release];
        mSentBodyData = mutableData;
        
        if (status == kOBEXSuccess) {
            if ([[mClient delegate] respondsToSelector:@selector(client:didSendDataOfLength:)]) {
                [[mClient delegate] client:mClient
                       didSendDataOfLength:[mutableData length]];
            }
        }            
    }
    
    return status;    
}

- (OBEXError)sendNextRequestPacket
{
    if (_debug) NSLog(@"[BBOBEXPutRequest] sendNextRequestPacket");
    
    BOOL isLastChunk;
    NSMutableData *mutableData = [self readNextChunkForHeaderLength:0
                                         isLastChunk:&isLastChunk];   
    
    if (!mutableData)
        return kOBEXInternalError; 
    OBEXError status = [mSession OBEXPut:isLastChunk
                             headersData:NULL
                       headersDataLength:0
                                bodyData:[mutableData mutableBytes]
                          bodyDataLength:[mutableData length]
                           eventSelector:mClientEventSelector
                          selectorTarget:mClient
                                  refCon:NULL];
    
    [mutableData retain];
    [mSentBodyData release];
    mSentBodyData = mutableData;
    
    if (status == kOBEXSuccess) {
        if ([[mClient delegate] respondsToSelector:@selector(client:didSendDataOfLength:)]) {
            [[mClient delegate] client:mClient
                   didSendDataOfLength:[mutableData length]];
        }
    }
    return status;
}

- (void)finishedWithError:(OBEXError)error responseCode:(int)responseCode
{
    if (_debug) NSLog(@"[BBOBEXPutRequest] finishedWithError: %d", error);
    
    mFinished = YES;    
    if ([[mClient delegate] respondsToSelector:@selector(client:didFinishPutRequestForStream:error:response:)]) {
        [[mClient delegate] client:mClient
      didFinishPutRequestForStream:mInputStream
                             error:error
                          response:[BBOBEXResponse responseWithCode:responseCode headers:mResponseHeaders]];
    }
}

- (BOOL)readOBEXResponseHeaders:(BBMutableOBEXHeaderSet **)responseHeaders
                andResponseCode:(int *)responseCode
               fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (event->type != kOBEXSessionEventTypePutCommandResponseReceived)
        return NO;
    const OBEXPutCommandResponseData *resp = &event->u.putCommandResponseData;
    *responseCode = resp->serverResponseOpCode;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:resp->headerDataPtr 
                                    length:resp->headerDataLength]) {
        *responseHeaders = headers;
    }
    return YES;
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


@implementation BBOBEXGetRequest

- (id)initWithClient:(BBBluetoothOBEXClient *)client 
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
        outputStream:(NSOutputStream *)outputStream
{
    self = [super initWithClient:client eventSelector:selector session:session];
    mOutputStream = [outputStream retain];
    return self;
}

- (OBEXError)beginWithHeaders:(BBOBEXHeaderSet *)headers
{
    if (_debug) NSLog(@"[BBOBEXGetRequest] beginWithHeaders (%d headers)", [headers count]);    
    
    if (mOutputStream == nil || [mOutputStream streamStatus] != NSStreamStatusOpen)
        return kOBEXBadArgumentError;
    
    mTotalGetLength = 0;
    
    CFMutableDataRef bytes = (CFMutableDataRef)[headers toBytes];
    if (!bytes && [headers count] > 0)
        return kOBEXInternalError;
    
    OBEXError status = [mSession OBEXGet:YES
                                 headers:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL)
                           headersLength:(bytes ? CFDataGetLength(bytes) : 0)
                           eventSelector:mClientEventSelector
                          selectorTarget:mClient
                                  refCon:NULL];
    if (bytes)
        mHeadersDataRef = bytes;
    return status;        
}

- (void)receivedResponseWithHeaders:(BBMutableOBEXHeaderSet *)responseHeaders
{
    if (_debug) NSLog(@"[BBOBEXGetRequest] receivedResponseWithHeaders");
    
    // don't pass body/end-of-body headers onto client delegate
    NSData *bodyData = [responseHeaders valueForByteSequenceHeader:kOBEXHeaderIDBody];
    NSData *endOfBodyData = [responseHeaders valueForByteSequenceHeader:kOBEXHeaderIDEndOfBody];
    [responseHeaders removeValueForHeader:kOBEXHeaderIDBody];
    [responseHeaders removeValueForHeader:kOBEXHeaderIDEndOfBody];     
    
    // super impl. stores response headers to pass them onto delegate later
    [super receivedResponseWithHeaders:responseHeaders];
    
    int totalBytesReceived = 0;
    
    if (bodyData) {
        if ([mOutputStream write:[bodyData bytes] maxLength:[bodyData length]] < 0)
            totalBytesReceived = -1;
        else
            totalBytesReceived += [bodyData length];
    }
    
    if (endOfBodyData && totalBytesReceived != -1) {
        if ([mOutputStream write:[endOfBodyData bytes] maxLength:[endOfBodyData length]] < 0)
            totalBytesReceived = -1;
        else
            totalBytesReceived += [endOfBodyData length];
    }     
    
    if (totalBytesReceived < 0) {
        if (_debug) NSLog(@"[BBOBEXGetRequest] error writing to output stream");
        return;
    }
    
    // read length (in initial headers) - ok if zero (key not present)
    mTotalGetLength = [mResponseHeaders valueForLengthHeader];  
    
    if (totalBytesReceived > 0) {
        if ([[mClient delegate] respondsToSelector:@selector(client:didReceiveDataOfLength:ofTotalLength:)]) {
            [[mClient delegate] client:mClient
                        didReceiveDataOfLength:totalBytesReceived
                                 ofTotalLength:mTotalGetLength];
        }
    }
}

- (OBEXError)sendNextRequestPacket
{
    // Previous GET request packet was successful, and we need to send another
    // packet to get more data.
    return [mSession OBEXGet:YES
                     headers:NULL
               headersLength:0
               eventSelector:mClientEventSelector
              selectorTarget:mClient
                      refCon:NULL];
}

- (void)finishedWithError:(OBEXError)error responseCode:(int)responseCode
{
    if (_debug) NSLog(@"[BBOBEXGetRequest] finishedWithError: %d", error);
    
    mFinished = YES;
    if ([[mClient delegate] respondsToSelector:@selector(client:didFinishGetRequestForStream:error:response:)]) {
        [[mClient delegate] client:mClient
      didFinishGetRequestForStream:mOutputStream
                             error:error
                          response:[BBOBEXResponse responseWithCode:responseCode headers:mResponseHeaders]];
    }
}

- (BOOL)readOBEXResponseHeaders:(BBMutableOBEXHeaderSet **)responseHeaders
                andResponseCode:(int *)responseCode
               fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (event->type != kOBEXSessionEventTypeGetCommandResponseReceived)
        return NO;
    const OBEXGetCommandResponseData *resp = &event->u.getCommandResponseData;
    *responseCode = resp->serverResponseOpCode;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:resp->headerDataPtr 
                                    length:resp->headerDataLength]) {
        *responseHeaders = headers;
    }
    return YES;
}

- (void)dealloc
{
    if (mHeadersDataRef)
        CFRelease(mHeadersDataRef);
    [mOutputStream release];
    [super dealloc];
}

@end


@implementation BBOBEXSetPathRequest

- (id)initWithClient:(BBBluetoothOBEXClient *)client 
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
changeToParentDirectoryFirst:(BOOL)changeToParentDirectoryFirst
createDirectoriesIfNeeded:(BOOL)createDirectoriesIfNeeded
{
    self = [super initWithClient:client eventSelector:selector session:session];
    
    mRequestFlags = 0;
    if (changeToParentDirectoryFirst)
        mRequestFlags |= 1;
    if (!createDirectoriesIfNeeded)
        mRequestFlags |= 2;    
    
    return self;
}

- (OBEXError)beginWithHeaders:(BBOBEXHeaderSet *)headers
{   
    if (_debug) NSLog(@"[BBOBEXSetPathRequest] beginWithHeaders (%d headers)", [headers count]);    
    
    CFMutableDataRef bytes = (CFMutableDataRef)[headers toBytes];
    if (!bytes && [headers count] > 0)
        return kOBEXInternalError;
    
    OBEXError status = [mSession OBEXSetPath:mRequestFlags
                                   constants:0
                             optionalHeaders:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL)
                       optionalHeadersLength:(bytes ? CFDataGetLength(bytes) : 0)
                               eventSelector:mClientEventSelector
                              selectorTarget:mClient
                                      refCon:NULL];
    if (bytes)
        mHeadersDataRef = bytes;
    return status;        
}

- (void)finishedWithError:(OBEXError)error responseCode:(int)responseCode
{
    if (_debug) NSLog(@"[BBOBEXSetPathRequest] finishedWithError: %d", error);
    
    mFinished = YES;    
    if ([[mClient delegate] respondsToSelector:@selector(client:didFinishSetPathRequestWithError:response:)]) {
        [[mClient delegate] client:mClient
  didFinishSetPathRequestWithError:error
                          response:[BBOBEXResponse responseWithCode:responseCode headers:mResponseHeaders]];
    }
}

- (BOOL)readOBEXResponseHeaders:(BBMutableOBEXHeaderSet **)responseHeaders
                andResponseCode:(int *)responseCode
               fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (event->type != kOBEXSessionEventTypeSetPathCommandResponseReceived)
        return NO;
    const OBEXSetPathCommandResponseData *resp = &event->u.setPathCommandResponseData;
    *responseCode = resp->serverResponseOpCode;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:resp->headerDataPtr 
                                    length:resp->headerDataLength]) {
        *responseHeaders = headers;
    }
    return YES;
}

- (void)dealloc
{
    if (mHeadersDataRef)
        CFRelease(mHeadersDataRef);
    [super dealloc];
}

@end


@implementation BBOBEXAbortRequest

- (id)initWithClient:(BBBluetoothOBEXClient *)client 
       eventSelector:(SEL)selector
             session:(OBEXSession *)session
currentRequestStream:(NSStream *)stream
{
    self = [super initWithClient:client eventSelector:selector session:session];
    mStream = [stream retain];
    return self;
}

- (OBEXError)beginWithHeaders:(BBOBEXHeaderSet *)headers
{
    if (_debug) NSLog(@"[BBOBEXAbortRequest] beginWithHeaders (%d headers)", [headers count]);
    
    CFMutableDataRef bytes = (CFMutableDataRef)[headers toBytes];
    if (!bytes && [headers count] > 0)
        return kOBEXInternalError;
    
	return [mSession OBEXAbort:(bytes ? (void *)CFDataGetBytePtr(bytes) : NULL)
         optionalHeadersLength:(bytes ? CFDataGetLength(bytes) : 0)
                 eventSelector:mClientEventSelector
                selectorTarget:mClient
                        refCon:NULL];
}

- (void)finishedWithError:(OBEXError)error responseCode:(int)responseCode
{
    if (_debug) NSLog(@"[BBOBEXAbortRequest] finishedWithError: %d", error);
    mFinished = YES;
    if ([[mClient delegate] respondsToSelector:@selector(client:didAbortRequestWithStream:error:response:)]) {
        [[mClient delegate] client:mClient
         didAbortRequestWithStream:mStream
                             error:error
                          response:[BBOBEXResponse responseWithCode:responseCode headers:mResponseHeaders]];
    }
}

- (BOOL)readOBEXResponseHeaders:(BBMutableOBEXHeaderSet **)responseHeaders
                andResponseCode:(int *)responseCode
               fromSessionEvent:(const OBEXSessionEvent *)event
{
    if (event->type != kOBEXSessionEventTypeAbortCommandResponseReceived)
        return NO;
    const OBEXAbortCommandResponseData *resp = &event->u.abortCommandResponseData;
    *responseCode = resp->serverResponseOpCode;
    BBMutableOBEXHeaderSet *headers = [BBMutableOBEXHeaderSet headerSet];
    if ([headers addHeadersFromHeadersData:resp->headerDataPtr 
                                    length:resp->headerDataLength]) {
        *responseHeaders = headers;
    }
    return YES;
}

- (void)dealloc
{
    [mStream release];
    [super dealloc];
}

@end

