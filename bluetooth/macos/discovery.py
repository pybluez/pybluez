import asyncio
import time
import objc
from Foundation import NSObject, IOBluetoothDeviceInquiry, NSRunLoop, NSDate

from bluetooth.device import Device
from bluetooth.macos.loop import Loop
from libdispatch import dispatch_queue_create, DISPATCH_QUEUE_SERIAL


class DeviceDiscoverer():
    delay = 0.05
    def __init__(self, duration=8, create_loop=True) -> None:
        self.delegate = DeviceInquiryDelegate.alloc().init(create_loop)
        self.delegate.set_duration(duration)
        self.t_start = None

    async def start(self):
        result = self.delegate._inquiry.start()
        self.t_start  = time.time()
        while not self.delegate.running:
            await Loop().wait(self.delay)

        return result

    async def stop(self):
        result = self.delegate._inquiry.stop()
        while self.delegate.running:
            await Loop().wait(self.delay)
        
        return result

    async def get_devices(self):
        if self.t_start is None:
            await self.start()

        while self.delegate.running:
            await Loop().wait(self.delay)

        return self.delegate.devices

        
    
    def get_devices_sync(self):
        event_loop = asyncio.get_event_loop()
        
        return event_loop.run_until_complete(self.get_devices())



class DeviceInquiryDelegate(NSObject):

    # NSObject init
    def init(self, create_loop=True):
        self = super().init()
        self.queue = dispatch_queue_create(b"bleak.corebluetooth", DISPATCH_QUEUE_SERIAL)
        self._inquiry = IOBluetoothDeviceInquiry.inquiryWithDelegate_(self)
        self.set_updatenames(False)

        self.running = False
        self.t_start = None

        return self

    # length property
    @objc.python_method
    def set_duration(self, length):
        self._inquiry.setInquiryLength_(length)

    @objc.python_method
    def get_duration(self):
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

    #def __del__(self):
    #    super().dealloc()

    # Delegate methods:
    # https://developer.apple.com/documentation/iobluetooth/iobluetoothdeviceinquiry
    # https://developer.apple.com/documentation/iobluetooth/iobluetoothdeviceinquirydelegate
    def deviceInquiryDeviceFound_device_(self, inquiry, device):
        pass

    def deviceInquiryComplete_error_aborted_(self, inquiry, err, aborted):
        # device enquiry is complete
        print("complete", err, aborted)
        devices = inquiry.foundDevices()

        self.devices = [
            Device(name=device.nameOrAddress(), address=device.addressString().replace("-", ":"))
            for device in devices
        ]

        self.running = False

    def deviceInquiryStarted_(self, inquiry):
        print("started")
        self.running = True

    def deviceInquiryDeviceNameUpdated_device_devicesRemaining_(self, sender,
                                                              device,
                                                              devicesRemaining):
        pass

    # - (void)deviceInquiryUpdatingDeviceNamesStarted:devicesRemaining:
    def deviceInquiryUpdatingDeviceNamesStarted_devicesRemaining_(self, sender,
                                                                devicesRemaining):
        pass
