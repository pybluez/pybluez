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
//  BBServiceAdvertiser.m
//  LightAquaBlue
//


#import <IOBluetooth/IOBluetoothUserLib.h>
#import <IOBluetooth/objc/IOBluetoothSDPServiceRecord.h>
#import <IOBluetooth/objc/IOBluetoothSDPUUID.h>

#import "BBServiceAdvertiser.h"


static NSString *kServiceItemKeyServiceClassIDList;
static NSString *kServiceItemKeyServiceName;
static NSString *kServiceItemKeyProtocolDescriptorList;

// template service dictionaries for each pre-defined profile
static NSDictionary *serialPortProfileDict;
static NSDictionary *objectPushProfileDict;
static NSDictionary *fileTransferProfileDict;


@implementation BBServiceAdvertiser

+ (void)initialize
{
	kServiceItemKeyServiceClassIDList = @"0001 - ServiceClassIDList";
	kServiceItemKeyServiceName = @"0100 - ServiceName*";
	kServiceItemKeyProtocolDescriptorList = @"0004 - ProtocolDescriptorList";

	// initialize the template service dictionaries
	NSBundle *classBundle = [NSBundle bundleForClass:[BBServiceAdvertiser class]];
	serialPortProfileDict =
		[[NSDictionary alloc] initWithContentsOfFile:[classBundle pathForResource:@"SerialPortDictionary"
                                                                           ofType:@"plist"]];
	objectPushProfileDict =
		[[NSDictionary alloc] initWithContentsOfFile:[classBundle pathForResource:@"OBEXObjectPushDictionary"
                                                                           ofType:@"plist"]];
	fileTransferProfileDict =
		[[NSDictionary alloc] initWithContentsOfFile:[classBundle pathForResource:@"OBEXFileTransferDictionary"
                                                                           ofType:@"plist"]];

	//kRFCOMMChannelNone = 0;
	//kRFCOMM_UUID = [[IOBluetoothSDPUUID uuid16:kBluetoothSDPUUID16RFCOMM] retain];
}

+ (NSDictionary *)serialPortProfileDictionary
{
	return serialPortProfileDict;
}

+ (NSDictionary *)objectPushProfileDictionary
{
	return objectPushProfileDict;
}

+ (NSDictionary *)fileTransferProfileDictionary
{
	return fileTransferProfileDict;
}


+ (void)updateServiceDictionary:(NSMutableDictionary *)sdpEntries
					   withName:(NSString *)serviceName
					   withUUID:(IOBluetoothSDPUUID *)uuid
{
	if (sdpEntries == nil) return;

	// set service name
	if (serviceName != nil) {
		[sdpEntries setObject:serviceName forKey:kServiceItemKeyServiceName];
	}

	// set service uuid if given
	if (uuid != nil) {

		NSMutableArray *currentServiceList =
		[sdpEntries objectForKey:kServiceItemKeyServiceClassIDList];

		if (currentServiceList == nil) {
			currentServiceList = [NSMutableArray array];
		}

		[currentServiceList addObject:[NSData dataWithBytes:[uuid bytes] length:[uuid length]]];

		// update dict
		[sdpEntries setObject:currentServiceList forKey:kServiceItemKeyServiceClassIDList];
	}
}


+ (IOReturn)addRFCOMMServiceDictionary:(NSDictionary *)dict
							  withName:(NSString *)serviceName
								  UUID:(NSString *)uuid
							 channelID:(BluetoothRFCOMMChannelID *)outChannelID
				   serviceRecordHandle:(BluetoothSDPServiceRecordHandle *)outServiceRecordHandle
{
	if (dict == nil)
		return kIOReturnError;

	NSMutableDictionary *sdpEntries = [NSMutableDictionary dictionaryWithDictionary:dict];


	NSUUID * uuid_ = [[NSUUID alloc] initWithUUIDString:uuid];
	uuid_t uuidbuf;
	[uuid_ getUUIDBytes:uuidbuf];
	IOBluetoothSDPUUID * uuidBlutooth = [IOBluetoothSDPUUID uuidWithBytes:uuidbuf length:16];
	[BBServiceAdvertiser updateServiceDictionary:sdpEntries
										withName:serviceName
										withUUID:uuidBlutooth];

	// publish the service
	IOBluetoothSDPServiceRecord *serviceRecord;
    serviceRecord = [IOBluetoothSDPServiceRecord publishedServiceRecordWithDictionary:sdpEntries];
	[uuid_ autorelease];

    IOReturn status = kIOReturnSuccess;
	if (serviceRecord != nil) {
		// get service channel ID & service record handle
		status = [serviceRecord getRFCOMMChannelID:outChannelID];
		if (status == kIOReturnSuccess) {
			status = [serviceRecord getServiceRecordHandle:outServiceRecordHandle];
		}

		// cleanup
        [serviceRecord release];
	}

	return status;
}


+ (IOReturn)removeService:(BluetoothSDPServiceRecordHandle)handle
{
    // TODO: We should switch to using [IOBluetoothSDPServiceRecord removeServiceRecord]
    // but we don't know how to get an IOBluetoothSDPServiceRecord instance from a handle.
#if __MAC_OS_X_VERSION_MAX_ALLOWED >= 1050
    return kIOReturnUnsupported;
#else
    return IOBluetoothRemoveServiceWithRecordHandle(handle);
#endif
}

@end
