import objc
from Foundation import NSObject

objc.registerMetaDataForSelector(
    b"NSObject",   # Name of the class, I use NSObject for selectors from protocols to automatically do the right thing
    b"rfcommChannelData:data:length:",   # Selector name
    {
       "arguments": {
         3: { "type": b"n^v", "c_array_length_in_arg": 4 },  # 0, 1 are implicit arguments, 2 is ``channel``, 3 is ``data``
         4: { "type": b"Q" } # ``length``
       }
    }
)

objc.registerMetaDataForSelector(
    b"IOBluetoothRFCOMMChannel", 
    b"writeSync:length:",   # Selector name
    {
       "arguments": {
         2: { "type_modifier": objc._C_IN, "c_array_length_in_arg": 3},
       }
     }
)


class BluezBluetoothChannelDelegate(NSObject):
    channeldataselector = "channelData:data:"
    channelClosedSelector = "channelClosed:"

    def init(self) -> None:
        self = super().init()
        return self
    
    def initWithDelegate_(self, delegate):
        self = super().init()
        self._delegate = delegate
        return self

    def rfcommChannelData_data_length_(self, channel, data, length):
        if self._delegate and self._delegate.respondsToSelector_(self.channeldataselector):
            self._delegate.channelData_data_(channel, data)

    def rfcommChannelClosed_(self, channel):
        #     if (m_delegate && [m_delegate respondsToSelector:channelClosedSelector]) {
        #         [m_delegate channelClosed:rfcommChannel];
        #     }
        if self._delegate and self._delegate.respondsToSelector_(self.channelClosedSelector):
            self._delegate.channelClosed_(channel)

    def l2capChannelData_data_length_(self, channel, data, length):
        if self._delegate and self._delegate.respondsToSelector_(self.channeldataselector):
            self._delegate.channelData_data_(channel, data)

    def l2capChannelClosed_(self, channel):
        #     if (m_delegate && [m_delegate respondsToSelector:channelClosedSelector]) {
        #         [m_delegate channelClosed:l2capChannel];
        #     }
        if self._delegate and self._delegate.respondsToSelector_(self.channelClosedSelector):
            self._delegate.channelClosed_(channel)

    @staticmethod
    def synchronouslyWriteData_toRFCOMMChannel_(data, channel):
        #     return [channel writeSync:(void *)[data bytes] length:[data length]];
        return channel.writeSync_length_(data.bytes(), len(data))

    @staticmethod
    def synchronouslyWriteData_toL2CAPChannel_(data, channel):
        return channel.writeSync_length_(data.bytes(), len(data))
        
