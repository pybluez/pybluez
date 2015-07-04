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
//  BBLocalDevice.m
//  LightAquaBlue
//

#import <IOBluetooth/IOBluetooth.h>

#import "BBLocalDevice.h"


@implementation BBLocalDevice

+ (NSString *)getName
{
    return [[IOBluetoothHostController defaultController] nameAsString];
}

+ (NSString *)getAddressString
{
    return [[IOBluetoothHostController defaultController] addressAsString];
}

+ (BluetoothClassOfDevice)getClassOfDevice
{
    return [[IOBluetoothHostController defaultController] classOfDevice];
}

+ (BOOL)isPoweredOn
{
	BluetoothHCIPowerState powerState = [IOBluetoothHostController defaultController].powerState;

	return powerState == kBluetoothHCIPowerStateON;
}

@end
