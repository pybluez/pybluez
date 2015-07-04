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
//  BBOBEXHeaderSet.m
//  LightAquaBlue
//

#import "BBOBEXHeaderSet.h"

enum kOBEXHeaderEncoding {
    kHeaderEncodingMask = 0xc0,
    kHeaderEncodingUnicode = 0x00,
    kHeaderEncodingByteSequence = 0x40,
    kHeaderEncoding1Byte = 0x80,
    kHeaderEncoding4Byte = 0xc0
};

static NSString *DATE_FORMAT_STRING = @"%Y%m%dT%H%M%S";  // no 'Z' at end

static const uint8_t NULL_TERMINATORS[2] = { 0x00, 0x00 };


@implementation BBOBEXHeaderSet

+ (id)headerSet
{
    return [[[BBOBEXHeaderSet alloc] init] autorelease];
}

- (id)init
{    
    self = [super init];
    mDict = [[NSMutableDictionary alloc] initWithCapacity:0];
    mKeys = [[NSMutableArray alloc] initWithCapacity:0];
    return self;
}

- (BOOL)containsValueForHeader:(uint8_t)headerID
{
    return ([mDict objectForKey:[NSNumber numberWithUnsignedChar:headerID]] != nil);
}


#pragma mark -

- (unsigned int)valueForCountHeader
{
    return [self valueFor4ByteHeader:kOBEXHeaderIDCount];
}

- (NSString *)valueForNameHeader
{
    return [self valueForUnicodeHeader:kOBEXHeaderIDName];
}

- (NSString *)valueForTypeHeader
{
    NSData *data = [self valueForByteSequenceHeader:kOBEXHeaderIDType];
    if (!data)
        return nil;
    if ([data length] == 0)
        return [NSString string];
    
    const char *s = (const char *)[data bytes];
    if (s[[data length]-1] == '\0') {
        return [NSString stringWithCString:(const char *)[data bytes]
                                  encoding:NSASCIIStringEncoding];
    }
    
    return [[[NSString alloc] initWithBytes:[data bytes]
                                     length:[data length]
                                   encoding:NSASCIIStringEncoding] autorelease];
}

- (unsigned int)valueForLengthHeader
{
    return [self valueFor4ByteHeader:kOBEXHeaderIDLength];
}

- (NSDate *)valueForTimeHeader
{
    NSData *data = [self valueForByteSequenceHeader:kOBEXHeaderIDTimeISO];
    if (data && [data length] > 0) {
        NSString *s = [[[NSString alloc] initWithBytes:[data bytes]
                                                length:[data length]
                                              encoding:NSASCIIStringEncoding] autorelease];
        NSCalendarDate *calendarDate = nil;
        if ([s characterAtIndex:[s length]-1] == 'Z') {
            calendarDate = [NSCalendarDate dateWithString:[s substringToIndex:[s length]-1]
                                           calendarFormat:DATE_FORMAT_STRING];
            [calendarDate setTimeZone:[NSTimeZone timeZoneWithName:@"UTC"]];
        } else {
            calendarDate = [NSCalendarDate dateWithString:s
                                           calendarFormat:DATE_FORMAT_STRING];            
            [calendarDate setTimeZone:[NSTimeZone localTimeZone]];
        }
        return calendarDate;        
    } else {
        uint32_t time = [self valueFor4ByteHeader:kOBEXHeaderIDTime4Byte];
        return [NSDate dateWithTimeIntervalSince1970:time];
    }
    return nil;
}

- (NSString *)valueForDescriptionHeader
{
    return [self valueForUnicodeHeader:kOBEXHeaderIDDescription];
}

- (NSData *)valueForTargetHeader
{
    return [self valueForByteSequenceHeader:kOBEXHeaderIDTarget];
}

- (NSData *)valueForHTTPHeader
{
    return [self valueForByteSequenceHeader:kOBEXHeaderIDHTTP];
}

- (NSData *)valueForWhoHeader
{
    return [self valueForByteSequenceHeader:kOBEXHeaderIDWho];
}

- (uint32_t)valueForConnectionIDHeader
{
    return [self valueFor4ByteHeader:kOBEXHeaderIDConnectionID];
}

- (NSData *)valueForApplicationParametersHeader
{
    return [self valueForByteSequenceHeader:kOBEXHeaderIDAppParameters];
}

- (NSData *)valueForAuthorizationChallengeHeader
{
    return [self valueForByteSequenceHeader:kOBEXHeaderIDAuthorizationChallenge];
}

- (NSData *)valueForAuthorizationResponseHeader
{
    return [self valueForByteSequenceHeader:kOBEXHeaderIDAuthorizationResponse];
}

- (NSData *)valueForObjectClassHeader
{
    return [self valueForByteSequenceHeader:0x51];
}

#pragma mark -

- (unsigned int)valueFor4ByteHeader:(uint8_t)headerID
{
    NSNumber *number = [mDict objectForKey:[NSNumber numberWithUnsignedChar:headerID]];
    if (number)
        return [number unsignedIntValue];
    return 0;
}

- (NSData *)valueForByteSequenceHeader:(uint8_t)headerID
{
    return [mDict objectForKey:[NSNumber numberWithUnsignedChar:headerID]];
}

- (uint8_t)valueFor1ByteHeader:(uint8_t)headerID
{
    NSNumber *number = [mDict objectForKey:[NSNumber numberWithUnsignedChar:headerID]];
    if (number)
        return [number unsignedCharValue];
    return 0;    
}

- (NSString *)valueForUnicodeHeader:(uint8_t)headerID
{
    return [mDict objectForKey:[NSNumber numberWithUnsignedChar:headerID]];    
}

- (NSArray *)allHeaders
{
    return mKeys;
}

#pragma mark -

static void addUInt16Bytes(uint16_t value, NSMutableData *data)
{
    uint16_t swapped = NSSwapHostShortToBig(value);
	[data appendBytes:&swapped length:sizeof(swapped)];    
}

static NSMutableData *stringHeaderBytes(uint8_t hid, NSString *s)
{
    NSMutableData *bytes = [NSMutableData dataWithBytes:&hid length:1];   	
	if ([s length] == 0) {	
		addUInt16Bytes(3, bytes);	// empty string == header length of 3
		return bytes;
	}
	
	CFStringEncoding encoding;
#if __BIG_ENDIAN__
	encoding = kCFStringEncodingUnicode;
#elif __LITTLE_ENDIAN__
	encoding = kCFStringEncodingUTF16BE;	// not in 10.3
#endif
	
	CFDataRef encodedString = CFStringCreateExternalRepresentation(NULL, 
			(CFStringRef)s, encoding, '?');
	if (encodedString) {
	    // CFStringCreateExternalRepresentation() may insert 2-byte BOM
	    if (CFDataGetLength(encodedString) >= 2) {
	        const uint8_t *bytePtr = CFDataGetBytePtr(encodedString);
            CFIndex length = CFDataGetLength(encodedString);
	        if ( (bytePtr[0] == 0xFE && bytePtr[1] == 0xFF) ||
	             (bytePtr[0] == 0xFF && bytePtr[1] == 0xFE) ) {
	            bytePtr = &CFDataGetBytePtr(encodedString)[2];
                length -= 2;
            }
            addUInt16Bytes(length + 2 + 3, bytes);
            [bytes appendBytes:bytePtr
                        length:length];
            [bytes appendBytes:NULL_TERMINATORS length:2];
        }
        CFRelease(encodedString);
	}
	
    return bytes;
}

static NSData *byteSequenceHeaderBytes(uint8_t hid, NSData *data)
{
    NSMutableData *headerBytes = [NSMutableData dataWithBytes:&hid length:1];
    uint16_t headerLength = ([data length] + 3);
	addUInt16Bytes(headerLength, headerBytes);

    if ([data length] == 0)
        return headerBytes;
    
    [headerBytes appendData:data];
    return headerBytes;
}

static NSData *fourByteHeaderBytes(uint8_t hid, uint32_t value)
{
    NSMutableData *bytes = [NSMutableData dataWithBytes:&hid length:1];
    uint32_t swapped = NSSwapHostIntToBig(value);
	[bytes appendBytes:&swapped length:sizeof(swapped)];
    return bytes;
}

static NSData *oneByteHeaderBytes(uint8_t hid, uint8_t value)
{
    NSMutableData *bytes = [NSMutableData dataWithBytes:&hid length:1];
    [bytes appendBytes:&value length:1];
    return bytes;
}

- (NSMutableData *)toBytes
{
    if ([mDict count] == 0)
        return NULL;
    
    NSMutableData *headerBytes = [[NSMutableData alloc] initWithLength:0];
    
    if ([self containsValueForHeader:kOBEXHeaderIDTarget]) {
        NSData *bytes;
        NSData *target = [self valueForTargetHeader];
        if (target)
            bytes = byteSequenceHeaderBytes(kOBEXHeaderIDTarget, target);
        if (!bytes)
            return NULL;
        [headerBytes appendData:bytes];
    }
    
    if ([self containsValueForHeader:kOBEXHeaderIDConnectionID]) {
        NSData *bytes = fourByteHeaderBytes(kOBEXHeaderIDConnectionID, 
                                            [self valueForConnectionIDHeader]);
        if (!bytes)
            return NULL;
        [headerBytes appendData:bytes];
    }    
    
    NSArray *headers = [self allHeaders];
    uint8_t rawHeaderID;
    int i;
    for (i=0; i<[headers count]; i++) {
        rawHeaderID = [(NSNumber *)[headers objectAtIndex:i] unsignedCharValue];
        //NSLog(@"--- toBytes() writing header 0x%02x", rawHeaderID);
        
        if (rawHeaderID == kOBEXHeaderIDTarget || rawHeaderID == kOBEXHeaderIDConnectionID)
            continue;   // already handled these
            
        NSData *bytes = nil;
        switch (rawHeaderID & kHeaderEncodingMask) {
            case kHeaderEncodingUnicode:
            {
                NSString *s = [self valueForUnicodeHeader:rawHeaderID];
                if (!s)
                    return NULL;
                bytes = stringHeaderBytes(rawHeaderID, s);
                break;
            }
            case kHeaderEncodingByteSequence:
            {
                NSData *data = [self valueForByteSequenceHeader:rawHeaderID];
                if (!data)
                    return NULL;
                bytes = byteSequenceHeaderBytes(rawHeaderID, data);
                break;
            }
            case kHeaderEncoding1Byte:
            {
                bytes = oneByteHeaderBytes(rawHeaderID, [self valueFor1ByteHeader:rawHeaderID]);
                break;
            }
            case kHeaderEncoding4Byte:
            {
                bytes = fourByteHeaderBytes(rawHeaderID, [self valueFor4ByteHeader:rawHeaderID]);
                break;
            }
            default:
                return NULL;
        }
        if (bytes == nil)
            return NULL;
        [headerBytes appendData:bytes];
    }
	
	return headerBytes;
}

- (unsigned)count
{
    return [mDict count];
}


#pragma mark -

static NSString *getHeaderDescription(uint8_t headerID)
{
    switch (headerID) {
        case kOBEXHeaderIDCount:
            return @"Count";
        case kOBEXHeaderIDName:
            return @"Name";
        case kOBEXHeaderIDDescription:
            return @"Description";
        case kOBEXHeaderIDType:
            return @"Type";
        case kOBEXHeaderIDLength:
            return @"Length";
        case kOBEXHeaderIDTimeISO:
        case kOBEXHeaderIDTime4Byte:
            return @"Time";
        case kOBEXHeaderIDTarget:
            return @"Target";
        case kOBEXHeaderIDHTTP:
            return @"HTTP";
        case kOBEXHeaderIDBody:
            return @"Body";
        case kOBEXHeaderIDEndOfBody:
            return @"End of Body";
        case kOBEXHeaderIDWho:
            return @"Who";
        case kOBEXHeaderIDConnectionID:
            return @"Connection ID";
        case kOBEXHeaderIDAppParameters:
            return @"Application Parameters";
        case kOBEXHeaderIDAuthorizationChallenge:
            return @"Authorization Challenge";
        case kOBEXHeaderIDAuthorizationResponse:
            return @"Authorization Response";
        case 0x51:
            return @"Object Class";
        case 0x52:
            return @"Session-Parameters";
        case 0x93:
            return @"Session-Sequence-Number";
        default:
            return [NSString stringWithFormat:@"0x%02x", headerID];
    }
}

- (NSString *)description
{
    NSMutableString *string = [NSMutableString stringWithCapacity:0];
    [string appendString:@"{"];
    NSNumber *n;
    int i;
    for (i=0; i<[mKeys count]; i++) {
        n = [mKeys objectAtIndex:i];
        [string appendFormat:@"%@: %@%@", 
                getHeaderDescription([n unsignedCharValue]),
                [mDict objectForKey:n],
                (i == [mKeys count]-1 ? @"" : @", ")];
    }
    
    [string appendString:@"}"];
    return string; 
}

- (void)dealloc
{
    [mDict release];
    [mKeys release];
    [super dealloc];
}

@end
