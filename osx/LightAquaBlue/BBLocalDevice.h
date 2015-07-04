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
//  BBLocalDevice.h
//  LightAquaBlue
//
//	Provides information about the local Bluetooth device.
//

#import <Cocoa/Cocoa.h>
#import <IOBluetooth/Bluetooth.h>

@interface BBLocalDevice : NSObject {
	//
}

/*
 * Returns the local device name, or nil if it can't be read.
 */
+ (NSString *)getName;

/*
 * Returns the local device address as a string, or nil if it can't be read.
 * The address is separated by hyphens, e.g. "00-11-22-33-44-55".
 */
+ (NSString *)getAddressString;

/*
 * Returns the local device's class of device, or -1 if it can't be read.
 */
+ (BluetoothClassOfDevice)getClassOfDevice;

/*
 * Returns YES if the local device is available and switched on.
 */
+ (BOOL)isPoweredOn;

@end
