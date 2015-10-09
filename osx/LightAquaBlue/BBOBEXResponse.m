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
//  BBOBEXResponse.m
//  LightAquaBlue
//

#import "BBOBEXResponse.h"
#import "BBOBEXHeaderSet.h"

@implementation BBOBEXResponse

+ (id)responseWithCode:(int)responseCode
               headers:(BBOBEXHeaderSet *)headers
{
    return [[[BBOBEXResponse alloc] initWithCode:responseCode
                                         headers:headers] autorelease];
}

- (id)initWithCode:(int)responseCode
           headers:(BBOBEXHeaderSet *)headers
{
    self = [super init];

    mCode = responseCode;
    mHeaders = [headers retain];

    return self;
}

- (int)responseCode
{
    return mCode;
}

- (NSString *)responseCodeDescription
{
    switch (mCode) {
        case kOBEXResponseCodeContinueWithFinalBit:
            return @"Continue";
        case kOBEXResponseCodeSuccessWithFinalBit:
            return @"Success";
        case kOBEXResponseCodeCreatedWithFinalBit:
            return @"Created";
        case kOBEXResponseCodeAcceptedWithFinalBit:
            return @"Accepted";
        case kOBEXResponseCodeNonAuthoritativeInfoWithFinalBit:
            return @"Non-authoritative info";
        case kOBEXResponseCodeNoContentWithFinalBit:
            return @"No content";
        case kOBEXResponseCodeResetContentWithFinalBit:
            return @"Reset content";
        case kOBEXResponseCodePartialContentWithFinalBit:
            return @"Partial content";
        case kOBEXResponseCodeMultipleChoicesWithFinalBit:
            return @"Multiple choices";
        case kOBEXResponseCodeMovedPermanentlyWithFinalBit:
            return @"Moved permanently";
        case kOBEXResponseCodeMovedTemporarilyWithFinalBit:
            return @"Moved temporarily";
        case kOBEXResponseCodeSeeOtherWithFinalBit:
            return @"See other";
        case kOBEXResponseCodeNotModifiedWithFinalBit:
            return @"Code not modified";
        case kOBEXResponseCodeUseProxyWithFinalBit:
            return @"Use proxy";
        case kOBEXResponseCodeBadRequestWithFinalBit:
            return @"Bad request";
        case kOBEXResponseCodeUnauthorizedWithFinalBit:
            return @"Unauthorized";
        case kOBEXResponseCodePaymentRequiredWithFinalBit:
            return @"Payment required";
        case kOBEXResponseCodeForbiddenWithFinalBit:
            return @"Forbidden";
        case kOBEXResponseCodeNotFoundWithFinalBit:
            return @"Not found";
        case kOBEXResponseCodeMethodNotAllowedWithFinalBit:
            return @"Method not allowed";
        case kOBEXResponseCodeNotAcceptableWithFinalBit:
            return @"Not acceptable";
        case kOBEXResponseCodeProxyAuthenticationRequiredWithFinalBit:
            return @"Proxy authentication required";
        case kOBEXResponseCodeRequestTimeOutWithFinalBit:
            return @"Request time out";
        case kOBEXResponseCodeConflictWithFinalBit:
            return @"Conflict";
        case kOBEXResponseCodeGoneWithFinalBit:
            return @"Gone";
        case kOBEXResponseCodeLengthRequiredFinalBit:
            return @"Length required";
        case kOBEXResponseCodePreconditionFailedWithFinalBit:
            return @"Precondition failed";
        case kOBEXResponseCodeRequestedEntityTooLargeWithFinalBit:
            return @"Requested entity too large";
        case kOBEXResponseCodeRequestURLTooLargeWithFinalBit:
            return @"Requested URL too large";
        case kOBEXResponseCodeUnsupportedMediaTypeWithFinalBit:
            return @"Unsupported media type";
        case kOBEXResponseCodeInternalServerErrorWithFinalBit:
            return @"Internal server error";
        case kOBEXResponseCodeNotImplementedWithFinalBit:
            return @"Not implemented";
        case kOBEXResponseCodeBadGatewayWithFinalBit:
            return @"Bad gateway";
        case kOBEXResponseCodeServiceUnavailableWithFinalBit:
            return @"Service unavailable";
        case kOBEXResponseCodeGatewayTimeoutWithFinalBit:
            return @"Gateway timeout";
        case kOBEXResponseCodeHTTPVersionNotSupportedWithFinalBit:
            return @"HTTP version not supported";
        case kOBEXResponseCodeDatabaseFullWithFinalBit:
            return @"Database full";
        case kOBEXResponseCodeDatabaseLockedWithFinalBit:
            return @"Database locked";
        default:
            return @"Unknown response";
    }
}

- (BBOBEXHeaderSet *)allHeaders
{
    return mHeaders;
}

- (void)dealloc
{
    [mHeaders release];
    [super dealloc];
}

@end
