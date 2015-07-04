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
//  BBBluetoothChannelDelegate.h
//  LightAquaBlue
//
//	Provides a delegate for RFCOMM and L2CAP channels. This is only intended
//  for use from the LightBlue library.
//

#include <Foundation/Foundation.h>

@class IOBluetoothRFCOMMChannel;
@class IOBluetoothL2CAPChannel;


@interface BBBluetoothChannelDelegate : NSObject {
    id m_delegate;
}

- (id)initWithDelegate:(id)delegate;

+ (IOReturn)synchronouslyWriteData:(NSData *)data
                   toRFCOMMChannel:(IOBluetoothRFCOMMChannel *)channel;
                   
+ (IOReturn)synchronouslyWriteData:(NSData *)data
                    toL2CAPChannel:(IOBluetoothL2CAPChannel *)channel;                   

@end


/*
 * These are the methods that should be implemented by the delegate of this
 * delegate (very awkward, but that's what it is).
 */
@protocol BBBluetoothChannelDelegateObserver

- (void)channelData:(id)channel data:(NSData *)data;
- (void)channelClosed:(id)channel;

@end
