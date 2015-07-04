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
//  BBOBEXHeaderSet.h
//  LightAquaBlue
//
//  A collection of unique OBEX headers. 
// 
//  The mutable counterpart to this class is BBMutableOBEXHeaderSet.
//

#import <Cocoa/Cocoa.h>
#import <CoreFoundation/CoreFoundation.h>

#import <IOBluetooth/OBEX.h>

@interface BBOBEXHeaderSet : NSObject {
    NSMutableDictionary *mDict;
    NSMutableArray *mKeys;
}

/*
 * Creates and returns an empty header set.
 */
+ (id)headerSet;

/*
 * Returns whether this header set contains the header with <headerID>.
 * 
 * Common header IDs are defined in the OBEXHeaderIdentifiers enum in
 * <IOBluetooth/OBEX.h> (for example, kOBEXHeaderIDName).
 */
- (BOOL)containsValueForHeader:(uint8_t)headerID;

/*
 * Returns the number of headers in this header set.
 */
- (unsigned)count;

/*
 * Returns the "Count" header value, or 0 if the header is not present or cannot
 * be read.
 */
- (unsigned int)valueForCountHeader;

/*
 * Returns the value for the Name header, or nil if the header is not present or 
 * cannot be read.
 */
- (NSString *)valueForNameHeader;

/*
 * Returns the value for the Type header, or nil if the header is not present or 
 * cannot be read.
 */
- (NSString *)valueForTypeHeader;

/*
 * Returns the value for the Length header, or 0 if the header is not present or
 * cannot be read.
 */
- (unsigned int)valueForLengthHeader;

/*
 * Returns the value for the 0x44 Time header, or the 0xC4 value if the 0x44 
 * header is not present, or nil if neither header is present or cannot be read.
 */
- (NSDate *)valueForTimeHeader;

/*
 * Returns the value for the Description header, or nil if the header is not
 * present or cannot be read.
 */
- (NSString *)valueForDescriptionHeader;

/*
 * Returns the value for the Target header, or nil if the header is not present
 * or cannot be read.
 */
- (NSData *)valueForTargetHeader;

/*
 * Returns the value for the HTTP header, or nil if the header is not present
 * or cannot be read.
 */
- (NSData *)valueForHTTPHeader;

/*
 * Returns the value for the Who header, or nil if the header is not present
 * or cannot be read.
 */
- (NSData *)valueForWhoHeader;

/*
 * Returns the value for the Connection Id header, or 0 if the header is not
 * present or cannot be read.
 */
- (uint32_t)valueForConnectionIDHeader;

/*
 * Returns the value for the Application Parameters header, or nil if the 
 * header is not present or cannot be read.
 */
- (NSData *)valueForApplicationParametersHeader;

/*
 * Returns the value for the Authorization Challenge header, or nil if the 
 * header is not present or cannot be read.
 */
- (NSData *)valueForAuthorizationChallengeHeader;

/*
 * Returns the value for the Authorization Response header, or nil if the 
 * header is not present or cannot be read.
 */
- (NSData *)valueForAuthorizationResponseHeader;

/*
 * Returns the value for the Object Class header, or nil if the 
 * header is not present or cannot be read.
 */
- (NSData *)valueForObjectClassHeader;

/*
 * Returns the value for the 4-byte header <headerID>, or 0 if the header is 
 * not present or cannot be read as a 4-byte value.
 */
- (unsigned int)valueFor4ByteHeader:(uint8_t)headerID;

/*
 * Returns the value for the byte-sequence header <headerID>, or nil if the
 * header is not present or cannot be read as a byte-sequence value.
 */
 - (NSData *)valueForByteSequenceHeader:(uint8_t)headerID;

/*
 * Returns the value for the 1-byte header <headerID>, or 0 if the header is 
 * not present or cannot be read as a 1-byte value.
 */
- (uint8_t)valueFor1ByteHeader:(uint8_t)headerID;

/*
 * Returns the value for the unicode header <headerID>, or nil if the
 * header is not present or cannot be read as a unicode value.
 */
- (NSString *)valueForUnicodeHeader:(uint8_t)headerID;

/*
 * Returns all the headers in the header set as a list of NSNumber objects.
 * Each NSNumber contains an unsigned char value (the header ID).
 *
 * The headers are returned in the order in which they were added.
 */
- (NSArray *)allHeaders;

/*
 * Returns a stream of bytes that contain the headers in this header set, as
 * specified by the IrOBEX specification (section 2.1).
 */
- (NSMutableData *)toBytes;

@end
