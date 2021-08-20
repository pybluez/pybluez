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
         2: { "type_modifier": objc._C_ID, "c_array_length_in_arg": 4 },
         3: { "type_modifier": b"Q"},

         
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
        #data = bytearray(data)
        print("send", data, type(data))
        return channel.writeSync_length_(data, len(data))

    @staticmethod
    def synchronouslyWriteData_toL2CAPChannel_(data, channel):
        #data = bytes(data)
        return channel.writeSync_length_(data, len(data))
        


# static SEL channelDataSelector;
# static SEL channelClosedSelector;


# @implementation BBBluetoothChannelDelegate

# + (void)initialize
# {
#     channelDataSelector = @selector(channelData:data:);
#     channelClosedSelector = @selector(channelClosed:);
# }

# - (id)initWithDelegate:(id)delegate
# {
#     self = [super init];
#     m_delegate = delegate;
#     return self;
# }

# - (void)rfcommChannelData:(IOBluetoothRFCOMMChannel *)rfcommChannel
#                      data:(void *)dataPointer
#                    length:(size_t)dataLength
# {
#     if (m_delegate && [m_delegate respondsToSelector:channelDataSelector]) {
#         [m_delegate channelData:rfcommChannel
#                            data:[NSData dataWithBytes:dataPointer length:dataLength]];
#     }
# }

# - (void)rfcommChannelClosed:(IOBluetoothRFCOMMChannel *)rfcommChannel
# {
#     if (m_delegate && [m_delegate respondsToSelector:channelClosedSelector]) {
#         [m_delegate channelClosed:rfcommChannel];
#     }
# }

# - (void)l2capChannelData:(IOBluetoothL2CAPChannel *)l2capChannel
#                     data:(void *)dataPointer
#                   length:(size_t)dataLength
# {
#     if (m_delegate && [m_delegate respondsToSelector:channelDataSelector]) {
#         [m_delegate channelData:l2capChannel
#                            data:[NSData dataWithBytes:dataPointer length:dataLength]];
#     }
# }

# - (void)l2capChannelClosed:(IOBluetoothL2CAPChannel *)l2capChannel
# {
#     if (m_delegate && [m_delegate respondsToSelector:channelClosedSelector]) {
#         [m_delegate channelClosed:l2capChannel];
#     }
# }

# + (IOReturn)synchronouslyWriteData:(NSData *)data
#                    toRFCOMMChannel:(IOBluetoothRFCOMMChannel *)channel
# {
#     return [channel writeSync:(void *)[data bytes] length:[data length]];
# }

# + (IOReturn)synchronouslyWriteData:(NSData *)data
#                     toL2CAPChannel:(IOBluetoothL2CAPChannel *)channel
# {
#     return [channel writeSync:(void *)[data bytes] length:[data length]];
# }

# @end
