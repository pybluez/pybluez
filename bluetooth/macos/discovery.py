import asyncio

import objc
from Foundation import NSObject
from IOBluetooth import IOBluetoothDeviceInquiry

class DeviceDiscoverer():
    def __init__(self, duration=8) -> None:
        self.delegate = DeviceInquiryDelegate.alloc().init()
        self.delegate.set_duration(duration)
        self.delegate.start()

    async def stop(self):
        result = self.delegate._inquiry.stop()
        while self.delegate.running:
            asyncio.sleep(0.1)
        
        return result

    async def get_devices(self):
        while self.delegate.running:
            asyncio.sleep(0.1)
        
        devices = self.delegate._inquiry.foundDevices()

        device_tuples = [
            (device.addressString, device.nameOrAddress, device.classOfDevice)
            for device in devices
        ]
        return device_tuples
    
    def get_devices_sync(self):
        if not self.delegate.running:
            self.delegate.start()
        
        event_loop = asyncio.get_event_loop()
        return event_loop.run_until_complete(self.get_devices())



class DeviceInquiryDelegate(NSObject):

    # NSObject init
    def init(self):
        self = super().init()
        self._inquiry = IOBluetoothDeviceInquiry.alloc().initWithDelegate_(self)

        self.running = False

        return self

    # length property
    @objc.python_method
    def set_duration(self, length):
        self._inquiry.setInquiryLength_(length)

    @objc.python_method
    def get_duration(self, length):
        return self._inquiry.inquiryLength()

    @objc.python_method
    def set_updatenames(self, value: bool):
        self._inquiry.setUpdateNewDeviceNames_(value)

    # updatenames property
    @objc.python_method
    def _setupdatenames(self, update):
        self._inquiry.setUpdateNewDeviceNames_(update)
    
    @objc.python_method
    def _getupdatenames(self):
        return self._inquiry.updateNewDeviceNames()

    # returns error code
    def start(self):
        return self._inquiry.start()

    def __del__(self):
        super().dealloc()

    # Delegate methods:
    # https://developer.apple.com/documentation/iobluetooth/iobluetoothdeviceinquiry
    # https://developer.apple.com/documentation/iobluetooth/iobluetoothdeviceinquirydelegate
    def deviceInquiryDeviceFound_device_(self, inquiry, device):
        pass

    def deviceInquiryComplete_error_aborted_(self, inquiry, err, aborted):
        # device enquiry is complete
        self.running = False

    def deviceInquiryStarted_(self, inquiry):
        self.running = True

    def deviceInquiryDeviceNameUpdated_device_devicesRemaining_(self, sender,
                                                              device,
                                                              devicesRemaining):
        pass

    # - (void)deviceInquiryUpdatingDeviceNamesStarted:devicesRemaining:
    def deviceInquiryUpdatingDeviceNamesStarted_devicesRemaining_(self, sender,
                                                                devicesRemaining):
        pass
