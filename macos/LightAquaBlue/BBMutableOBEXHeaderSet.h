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
//  BBMutableOBEXHeaderSet.h
//  LightAquaBlue
//
//  A mutable version of BBOBEXHeaderSet that allows adding and removing
//  of headers.
//

#import "BBOBEXHeaderSet.h"


@interface BBMutableOBEXHeaderSet : BBOBEXHeaderSet {
    CFMutableDictionaryRef mMutableDict;
}

/*
 * Creates and returns an empty header set.
 */
+ (id)headerSet;

/*
 * Removes the header <headerID> from this header set.
 */
- (void)removeValueForHeader:(uint8_t)headerID;

/*
 * Sets the value for the Name header to <name>, overriding any existing
 * value for this header.
 */
- (void)setValueForNameHeader:(NSString *)name;

/*
 * Sets the value for the Type header to <type>, overriding any existing
 * value for this header.
 */
- (void)setValueForTypeHeader:(NSString *)type;

/*
 * Sets the value for the Length header to <length>, overriding any existing
 * value for this header.
 */
- (void)setValueForLengthHeader:(uint32_t)length;

/*
 * Sets the value for the Time (0x44) header to <date>, overriding any
 * existing value for this header. Assumes <date> is in local time.
 */
- (void)setValueForTimeHeader:(NSDate *)date;

/*
 * Sets the value for the Time (0x44) header to <date>, overriding any
 * existing value for this header. If <isUTCTime> is YES, the time value is
 * marked as UTC time, otherwise it is marked as local time.
 */
- (void)setValueForTimeHeader:(NSDate *)date isUTCTime:(BOOL)isUTCTime;

/*
 * Sets the value for the Description header to <description>, overriding
 * any existing value for this header.
 */
- (void)setValueForDescriptionHeader:(NSString *)description;

/*
 * Sets the value for the Target header to <target>, overriding
 * any existing value for this header.
 */
- (void)setValueForTargetHeader:(NSData *)target;

/*
 * Sets the value for the HTTP header to <http>, overriding
 * any existing value for this header.
 */
- (void)setValueForHTTPHeader:(NSData *)http;

/*
 * Sets the value for the Who header to <who>, overriding
 * any existing value for this header.
 */
- (void)setValueForWhoHeader:(NSData *)who;

/*
 * Sets the value for the Connection Id header to <connectionID>, overriding
 * any existing value for this header.
 */
- (void)setValueForConnectionIDHeader:(uint32_t)connectionID;

/*
 * Sets the value for the Application Parameters header to <appParameters>,
 * overriding any existing value for this header.
 */
- (void)setValueForApplicationParametersHeader:(NSData *)appParameters;

/*
 * Sets the value for the Authorization Challenge header to <authChallenge>,
 * overriding any existing value for this header.
 */
- (void)setValueForAuthorizationChallengeHeader:(NSData *)authChallenge;

/*
 * Sets the value for the Authorization Response header to <authResponse>,
 * overriding any existing value for this header.
 */
- (void)setValueForAuthorizationResponseHeader:(NSData *)authResponse;

/*
 * Sets the value for the Object Class header to <objectClass>,
 * overriding any existing value for this header.
 */
- (void)setValueForObjectClassHeader:(NSData *)objectClass;

/*
 * Sets the value for the unicode-encoded header <headerID> to <value>,
 * overriding any existing value for this header.
 */
- (void)setValue:(NSString *)value forUnicodeHeader:(uint8_t)headerID;

/*
 * Sets the value for the byte-sequence-encoded header <headerID> to <value>,
 * overriding any existing value for this header.
 */
- (void)setValue:(NSData *)value forByteSequenceHeader:(uint8_t)headerID;

/*
 * Sets the value for the 4-byte-header <headerID> to <value>,
 * overriding any existing value for this header.
 */
- (void)setValue:(uint32_t)value for4ByteHeader:(uint8_t)headerID;

/*
 * Sets the value for the 1-byte-encoded header <headerID> to <value>,
 * overriding any existing value for this header.
 */
- (void)setValue:(uint8_t)value for1ByteHeader:(uint8_t)headerID;

/*
 * Adds the headers from <headerSet> to this header set.
 */
- (void)addHeadersFromHeaderSet:(BBOBEXHeaderSet *)headerSet;

/*
 * Adds the headers from <headersData> to this header set. <length> specifies
 * the size of <headersData>.
 *
 * Returns NO if there was an error parsing the <headersData>.
 */
- (BOOL)addHeadersFromHeadersData:(const uint8_t *)headersData
                           length:(size_t)length;

@end
