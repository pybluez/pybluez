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
//  BBDelegatingInputStream.h
//  LightAquaBlue
//
//  A NSInputStream subclass that calls readDataWithMaxLength: on the delegate
//  when data is required.
//  This class is only intended for use from the LightBlue library.
//  Most methods are not implemented, and there are no stream:HandleEvent: 
//  calls to the delegate.
//

#import <Cocoa/Cocoa.h>


@interface BBStreamingInputStream : NSInputStream {
    id mDelegate;
    NSStreamStatus mStatus;
}
- (id)initWithDelegate:(id)delegate;

@end


@protocol BBStreamingInputStreamDelegate

- (NSData *)readDataWithMaxLength:(unsigned int)maxLength;

@end

