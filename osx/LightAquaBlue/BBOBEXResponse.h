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
//  BBOBEXResponse.h
//  LightAquaBlue
//
//  Contains the details for an OBEX server response.
//
//  This is used by BBBluetoothOBEXClient to pass the details of an OBEX
//  server response to its delegate.
//

#import <Cocoa/Cocoa.h>

@class BBOBEXHeaderSet;

@interface BBOBEXResponse : NSObject {
    int mCode;
    BBOBEXHeaderSet *mHeaders;
}

+ (id)responseWithCode:(int)responseCode
               headers:(BBOBEXHeaderSet *)headers;

- (id)initWithCode:(int)responseCode
           headers:(BBOBEXHeaderSet *)headers;

/*
 * Returns the response code.
 *
 * Use the response codes listed in the OBEXOpCodeResponseValues enum in
 * <IOBluetooth/OBEX.h> to match against this response code. If the client
 * request was accepted by the OBEX server, this response code will be
 * kOBEXResponseCodeSuccessWithFinalBit. Otherwise, it will be set to one of
 * the other response codes that end with "WithFinalBit".
 */
- (int)responseCode;

/*
 * Returns a string description of the response code. E.g.
 * kOBEXResponseCodeSuccessWithFinalBit translates to "Success".
 */
- (NSString *)responseCodeDescription;

/*
 * Returns the response headers.
 */
- (BBOBEXHeaderSet *)allHeaders;

@end
