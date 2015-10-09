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
//  BBServiceAdvertiser.h
//  LightAquaBlue
//
//	Provides some basic operations for advertising Bluetooth services.
//

#import <IOBluetooth/Bluetooth.h>
@class IOBluetoothSDPUUID;

@interface BBServiceAdvertiser : NSObject {
	//
}

/*
 * Returns a ready-made dictionary for advertising a service with the Serial
 * Port Profile.
 */
+ (NSDictionary *)serialPortProfileDictionary;

/*
 * Returns a ready-made dictionary for advertising a service with the OBEX
 * Object Push Profile.
 */
+ (NSDictionary *)objectPushProfileDictionary;

/*
 * Returns a ready-made dictionary for advertising a service with the OBEX
 * File Transfer Profile.
 */
+ (NSDictionary *)fileTransferProfileDictionary;

/*
 * Advertise a RFCOMM-based (i.e. RFCOMM or OBEX) service.
 *
 * Arguments:
 *	- dict: the dictionary containing the service details.
 *	- serviceName: the service name to advertise, which will be added to the
 *	  dictionary. Can be nil.
 *	- uuid: the custom UUID to advertise for the service, which will be added to
 *	  the dictionary. Can be nil.
 *	- outChannelID: once the service is advertised, this will be set to the
 *	  RFCOMM channel ID that was used to advertise the service.
 *	- outServiceRecordHandle: once the service is advertised, this will be set
 *    to the service record handle which identifies the service.
 */
+ (IOReturn)addRFCOMMServiceDictionary:(NSDictionary *)dict
							  withName:(NSString *)serviceName
								  UUID:(NSString *)uuid
							 channelID:(BluetoothRFCOMMChannelID *)outChannelID
				   serviceRecordHandle:(BluetoothSDPServiceRecordHandle *)outServiceRecordHandle;


/*
 * Stop advertising a service.
 */
+ (IOReturn)removeService:(BluetoothSDPServiceRecordHandle)handle;

@end
