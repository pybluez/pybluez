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
//  BBBluetoothChannelDelegate.m
//  LightAquaBlue
//

#import "BBBluetoothChannelDelegate.h"

#import <IOBluetooth/objc/IOBluetoothRFCOMMChannel.h>
#import <IOBluetooth/objc/IOBluetoothL2CAPChannel.h>

static SEL channelDataSelector;
static SEL channelClosedSelector;


@implementation BBBluetoothChannelDelegate

+ (void)initialize
{
    channelDataSelector = @selector(channelData:data:);
    channelClosedSelector = @selector(channelClosed:);
}

- (id)initWithDelegate:(id)delegate
{
    self = [super init];
    m_delegate = delegate;
    return self;
}

- (void)rfcommChannelData:(IOBluetoothRFCOMMChannel *)rfcommChannel 
                     data:(void *)dataPointer 
                   length:(size_t)dataLength
{
    if (m_delegate && [m_delegate respondsToSelector:channelDataSelector]) {
        [m_delegate channelData:rfcommChannel 
                           data:[NSData dataWithBytes:dataPointer length:dataLength]];
    }
}

- (void)rfcommChannelClosed:(IOBluetoothRFCOMMChannel *)rfcommChannel
{
    if (m_delegate && [m_delegate respondsToSelector:channelClosedSelector]) {
        [m_delegate channelClosed:rfcommChannel];
    }        
}

- (void)l2capChannelData:(IOBluetoothL2CAPChannel *)l2capChannel 
                    data:(void *)dataPointer 
                  length:(size_t)dataLength
{
    if (m_delegate && [m_delegate respondsToSelector:channelDataSelector]) {
        [m_delegate channelData:l2capChannel 
                           data:[NSData dataWithBytes:dataPointer length:dataLength]];
    }    
}

- (void)l2capChannelClosed:(IOBluetoothL2CAPChannel *)l2capChannel
{
    if (m_delegate && [m_delegate respondsToSelector:channelClosedSelector]) {
        [m_delegate channelClosed:l2capChannel];
    }            
}

+ (IOReturn)synchronouslyWriteData:(NSData *)data
                   toRFCOMMChannel:(IOBluetoothRFCOMMChannel *)channel
{
    return [channel writeSync:(void *)[data bytes] length:[data length]];
}
                   
+ (IOReturn)synchronouslyWriteData:(NSData *)data
                    toL2CAPChannel:(IOBluetoothL2CAPChannel *)channel
{
    return [channel writeSync:(void *)[data bytes] length:[data length]];
}

@end
