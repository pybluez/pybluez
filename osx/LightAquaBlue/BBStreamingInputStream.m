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
//  BBDelegatingInputStream.m
//  LightAquaBlue
//

#import "BBStreamingInputStream.h"


@implementation BBStreamingInputStream

- (id)initWithDelegate:(id)delegate
{
    self = [super init];
    
    mDelegate = delegate;
    mStatus = NSStreamStatusNotOpen;
    
    return self;
}

- (int)read:(uint8_t *)buffer maxLength:(unsigned int)maxLength
{
    NSData *data = [mDelegate readDataWithMaxLength:maxLength];
    if (!data) 
        return -1;

    int copyLength = [data length] < maxLength ? [data length] : maxLength;
    [data getBytes:buffer length:copyLength];
    return copyLength;
}

- (BOOL)getBuffer:(uint8_t **)buffer length:(unsigned int *)len
{
    // we cannot access buffer data without calling read:maxLength:
    return NO;
}

- (BOOL)hasBytesAvailable
{
    // don't know whether bytes are available until read:maxLength: is called
    return YES;
}

- (void)open
{
    mStatus = NSStreamStatusOpen;
}

- (void)close
{
    mStatus = NSStreamStatusClosed;
}

- (void)setDelegate:(id)delegate
{
    mDelegate = delegate;
}

- (id)delegate
{
    return mDelegate;
}

- (void)scheduleInRunLoop:(NSRunLoop *)aRunLoop forMode:(NSString *)mode
{
}

- (void)removeFromRunLoop:(NSRunLoop *)aRunLoop forMode:(NSString *)mode
{
}

- (BOOL)setProperty:(id)property forKey:(NSString *)key
{
    return NO;
}

- (id)propertyForKey:(NSString *)key
{
    return nil;
}

- (NSStreamStatus)streamStatus
{
    return mStatus;
}

@end
