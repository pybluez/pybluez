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
//  BBMutableOBEXHeaderSet.m
//  LightAquaBlue
//

#import "BBMutableOBEXHeaderSet.h"

enum kOBEXHeaderEncoding {
    kHeaderEncodingMask = 0xc0,
    kHeaderEncodingUnicode = 0x00,
    kHeaderEncodingByteSequence = 0x40,
    kHeaderEncoding1Byte = 0x80,
    kHeaderEncoding4Byte = 0xc0
};

static NSString *LOCAL_TIME_FORMAT_STRING = @"%Y%m%dT%H%M%S";
static NSString *UTC_FORMAT_STRING = @"%Y%m%dT%H%M%SZ";


@implementation BBMutableOBEXHeaderSet

+ (id)headerSet
{
    return [[[BBMutableOBEXHeaderSet alloc] init] autorelease];
}

- (void)setValueForCountHeader:(uint32_t)count
{
    [self setValue:count for4ByteHeader:kOBEXHeaderIDCount];
}

- (void)setValueForNameHeader:(NSString *)name
{
    [self setValue:name forUnicodeHeader:kOBEXHeaderIDName];
}

- (void)setValueForTypeHeader:(NSString *)type
{
    NSMutableData *data;
    if ([type length] == 0) {
        data = [NSMutableData data];
    } else {
        const char *s = [type cStringUsingEncoding:NSASCIIStringEncoding];
        if (!s)     // cannot be converted to ascii
            return;
        // add null terminator
        data = [NSMutableData dataWithBytes:s
                                     length:[type length] + 1];
        [data resetBytesInRange:NSMakeRange([type length], 1)];
    }

    [self setValue:data forByteSequenceHeader:kOBEXHeaderIDType];
}

- (void)setValueForLengthHeader:(uint32_t)length
{
    [self setValue:length for4ByteHeader:kOBEXHeaderIDLength];
}

- (void)setValueForTimeHeader:(NSDate *)date
{
    [self setValueForTimeHeader:date isUTCTime:NO];
}

- (void)setValueForTimeHeader:(NSDate *)date isUTCTime:(BOOL)isUTCTime
{
    NSString *dateString =
        [date descriptionWithCalendarFormat: (isUTCTime ? UTC_FORMAT_STRING : LOCAL_TIME_FORMAT_STRING)
                                   timeZone: (isUTCTime ? [NSTimeZone timeZoneWithName:@"UTC"] : [NSTimeZone localTimeZone])
                                     locale: nil];
    [self setValue:[dateString dataUsingEncoding:NSASCIIStringEncoding]
    forByteSequenceHeader:kOBEXHeaderIDTimeISO];
}

- (void)setValueForDescriptionHeader:(NSString *)description
{
    [self setValue:description forUnicodeHeader:kOBEXHeaderIDDescription];
}

- (void)setValueForTargetHeader:(NSData *)target
{
    [self setValue:target forByteSequenceHeader:kOBEXHeaderIDTarget];
}

- (void)setValueForHTTPHeader:(NSData *)http
{
    [self setValue:http forByteSequenceHeader:kOBEXHeaderIDHTTP];
}

- (void)setValueForWhoHeader:(NSData *)who
{
    [self setValue:who forByteSequenceHeader:kOBEXHeaderIDWho];
}

- (void)setValueForConnectionIDHeader:(uint32_t)connectionID
{
    [self setValue:connectionID for4ByteHeader:kOBEXHeaderIDConnectionID];
}

- (void)setValueForApplicationParametersHeader:(NSData *)appParameters
{
    [self setValue:appParameters forByteSequenceHeader:kOBEXHeaderIDAppParameters];
}

- (void)setValueForAuthorizationChallengeHeader:(NSData *)authChallenge
{
    [self setValue:authChallenge forByteSequenceHeader:kOBEXHeaderIDAuthorizationChallenge];
}

- (void)setValueForAuthorizationResponseHeader:(NSData *)authResponse
{
    [self setValue:authResponse forByteSequenceHeader:kOBEXHeaderIDAuthorizationResponse];
}

- (void)setValueForObjectClassHeader:(NSData *)objectClass
{
    [self setValue:objectClass forByteSequenceHeader:0x51];
}

- (void)setValue:(NSString *)value forUnicodeHeader:(uint8_t)headerID
{
    if (!value || ((headerID & kHeaderEncodingMask) != kHeaderEncodingUnicode))
        return;
    NSNumber *key = [NSNumber numberWithUnsignedChar:headerID];
    if ([mDict objectForKey:key] == nil)
        [mKeys addObject:key];
    [mDict setObject:value forKey:key];
}

- (void)setValue:(NSData *)value forByteSequenceHeader:(uint8_t)headerID
{
    if (!value || ((headerID & kHeaderEncodingMask) != kHeaderEncodingByteSequence))
        return;
    NSNumber *key = [NSNumber numberWithUnsignedChar:headerID];
    if ([mDict objectForKey:key] == nil)
        [mKeys addObject:key];
    [mDict setObject:value forKey:key];
}

- (void)setValue:(uint32_t)value for4ByteHeader:(uint8_t)headerID
{
    if ((headerID & kHeaderEncodingMask) != kHeaderEncoding4Byte)
        return;
    NSNumber *key = [NSNumber numberWithUnsignedChar:headerID];
    if ([mDict objectForKey:key] == nil)
        [mKeys addObject:key];
    [mDict setObject:[NSNumber numberWithUnsignedInt:value] forKey:key];
}

- (void)setValue:(uint8_t)value for1ByteHeader:(uint8_t)headerID
{
    if ((headerID & kHeaderEncodingMask) != kHeaderEncoding1Byte)
        return;
    NSNumber *key = [NSNumber numberWithUnsignedChar:headerID];
    if ([mDict objectForKey:key] == nil)
        [mKeys addObject:key];
    [mDict setObject:[NSNumber numberWithUnsignedChar:value] forKey:key];
}

- (void)addHeadersFromHeaderSet:(BBOBEXHeaderSet *)headerSet
{
    NSDictionary *dict = [headerSet valueForKey:@"mDict"];
    [mDict addEntriesFromDictionary:dict];

    NSArray *keys = [headerSet allHeaders];
    int i;
    for (i=0; i<[keys count]; i++) {
        if (![mKeys containsObject:[keys objectAtIndex:i]]) {
            [mKeys addObject:[keys objectAtIndex:i]];
        }
    }
}

static uint16_t parseUInt16(const uint8_t *bytes)
{
    uint16_t value;
    memcpy((void *)&value, bytes, sizeof(value));
	return NSSwapBigShortToHost(value);
}

static uint32_t parseUInt32(const uint8_t *bytes)
{
    uint32_t value;
    memcpy((void *)&value, bytes, sizeof(value));
	return NSSwapBigIntToHost(value);
}

static NSString *parseString(const uint8_t *bytes, unsigned int length)
{
	NSString *s = [[NSString alloc] initWithBytes:bytes
										   length:length
										 encoding:NSUnicodeStringEncoding];
	return [s autorelease];
}

static NSData *parseData(const uint8_t *bytes, unsigned int length)
{
    return [NSData dataWithBytes:bytes length:length];
}

- (BOOL)addHeadersFromHeadersData:(const uint8_t *)headersData
                           length:(size_t)length
{
    if (length == 0)    // nothing to add
        return YES;

    if (length == 1)    // must have at least 2 headersData
        return NO;

    NSNumber *hi;
    uint16_t hlen;

	//NSLog(@"reading %d bytes", length);

    int i = 0;
    while (i < length) {
        hi = [NSNumber numberWithUnsignedChar:headersData[i]];
        //NSLog(@"Next header: %d", headersData[i]);
        switch (headersData[i] & kHeaderEncodingMask) {
            case kHeaderEncoding4Byte:  // ID V V V V
            {
                //NSLog(@"\tint:");
                hlen = 5;
                if (i + hlen > length)
                    return NO;
                [self setValue:parseUInt32(&headersData[i+1]) for4ByteHeader:headersData[i]];
                break;
            }
            case kHeaderEncoding1Byte: // ID V
            {
                //NSLog(@"\tbyte:");
                hlen = 2;
                if (i + hlen > length)
                    return NO;
                [self setValue:headersData[i+1] for1ByteHeader:headersData[i]];
                break;
            }
            case kHeaderEncodingUnicode:  // ID L L V V .. .. O O
            {
                //NSLog(@"\tunicode:");
                if (i + 3 > length)
                    return NO;
                hlen = parseUInt16(&headersData[i+1]);
                if (i + hlen > length)
                    return NO;
                NSString *s = nil;
                if (hlen - 3 == 0) {  // empty string (3 headersData is for ID + length)
                    s = [NSString string];
                } else {
                    // account for 3 headersData of ID + length
                    s = parseString(&headersData[i+3], (hlen - 3 - 2));
                }
                if (!s)
                    return NO;
                [self setValue:s forUnicodeHeader:headersData[i]];
                break;
            }
            case kHeaderEncodingByteSequence:  // ID L L V ..
            {
                //NSLog(@"\tbyte stream:");
                if (i + 3 > length)
                    return NO;
                hlen = parseUInt16(&headersData[i+1]);
				//NSLog(@"\tbytes length: %d", hlen);
                if (i + hlen > length)
                    return NO;
                NSData *data = nil;
                if (hlen - 3 == 0) {
                    data = [NSData data];
                } else {
                    // account for 3 headersData of ID + length
                    data = parseData(&headersData[i+3], hlen-3);
                }
				//NSLog(@"\tread bytes");
                if (!data)
                    return NO;
                [self setValue:data forByteSequenceHeader:headersData[i]];
                break;
            }
        }
        i += hlen;
        //NSLog(@"\tRead header ok, now to index %d...", i);
    }

    //NSLog(@"\tFinished reading headers");

    return YES;

}

- (void)removeValueForHeader:(uint8_t)headerID
{
    NSNumber *number = [NSNumber numberWithUnsignedChar:headerID];
    [mDict removeObjectForKey:number];
    [mKeys removeObject:number];
}

@end
