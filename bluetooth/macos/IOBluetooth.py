# This file wraps the IOBluetooth module
import objc

if hasattr(objc, 'ObjCLazyModule'):
    # `ObjCLazyModule` function is available for PyObjC version >= 2.4
    io_bluetooth = objc.ObjCLazyModule("IOBluetooth",
                                       frameworkIdentifier="com.apple.IOBluetooth",
                                       frameworkPath=objc.pathForFramework(
                                           "/System/Library/Frameworks/IOBluetooth.framework"
                                       ),
                                       metadict=globals())

    objc.registerMetaDataForSelector(b"IOBluetoothSDPServiceRecord",
                                     b"getRFCOMMChannelID:",
                                     dict(
                                         arguments={
                                             2: dict(type=objc._C_PTR + objc._C_CHAR_AS_INT, type_modifier=objc._C_OUT),
                                         }
                                     ))

    objc.registerMetaDataForSelector(b"IOBluetoothSDPServiceRecord",
                                     b"getL2CAPPSM:",
                                     dict(
                                         arguments={
                                             2: dict(type=objc._C_PTR + objc._C_CHAR_AS_INT, type_modifier=objc._C_OUT),
                                         }
                                     ))

    objc.registerMetaDataForSelector(b"IOBluetoothDevice",
                                     b"openRFCOMMChannelSync:withChannelID:delegate:",
                                     dict(
                                         arguments={
                                             2: dict(type=objc._C_PTR + objc._C_CHAR_AS_INT, type_modifier=objc._C_OUT),
                                             2 + 1: dict(type_modifier=objc._C_IN, null_accepted=False),
                                             2 + 3: dict(type_modifier=objc._C_IN, null_accepted=False),
                                         }
                                     ))

    objc.registerMetaDataForSelector(b"IOBluetoothDevice",
                                     b"openL2CAPChannelSync:withPSM:delegate:",
                                     dict(
                                         arguments={
                                             2: dict(type=objc._C_PTR + objc._C_CHAR_AS_INT, type_modifier=objc._C_OUT),
                                             2 + 1: dict(type_modifier=objc._C_IN, null_accepted=False),
                                             2 + 3: dict(type_modifier=objc._C_IN, null_accepted=False),
                                         }
                                     ))

    # This still doesn't seem to work since it's expecting (BluetoothDeviceAddress *)
    # objc.registerMetaDataForSelector(b"IOBluetoothDevice",
    #                                  b"withAddress:",
    #                                  dict(
    #                                      arguments={
    #                                          2+0: dict(type_modifier=objc._C_IN, c_array_of_fixed_length=6, null_accepted=False)
    #                                      }
    #                                  ))

    locals_ = locals()
    for variable_name in dir(io_bluetooth):
        locals_[variable_name] = getattr(io_bluetooth, variable_name)

else:
    try:
        # mac os 10.5 loads frameworks using bridgesupport metadata
        __bundle__ = objc.initFrameworkWrapper("IOBluetooth",
                                               frameworkIdentifier="com.apple.IOBluetooth",
                                               frameworkPath=objc.pathForFramework(
                                                   "/System/Library/Frameworks/IOBluetooth.framework"),
                                               globals=globals())

    except (AttributeError, ValueError):
        # earlier versions use loadBundle() and setSignatureForSelector()

        objc.loadBundle("IOBluetooth", globals(),
                        bundle_path=objc.pathForFramework('/System/Library/Frameworks/IOBluetooth.framework'))

        # Sets selector signatures in order to receive arguments correctly from
        # PyObjC methods. These MUST be set, otherwise the method calls won't work
        # at all, mostly because you can't pass by pointers in Python.

        # set to return int, and take an unsigned char output arg
        # i.e. in python: return (int, unsigned char) and accept no args
        objc.setSignatureForSelector("IOBluetoothSDPServiceRecord",
                                     "getRFCOMMChannelID:", "i12@0:o^C")

        # set to return int, and take an unsigned int output arg
        # i.e. in python: return (int, unsigned int) and accept no args
        objc.setSignatureForSelector("IOBluetoothSDPServiceRecord",
                                     "getL2CAPPSM:", "i12@0:o^S")

        # set to return int, and take (output object, unsigned char, object) args
        # i.e. in python: return (int, object) and accept (unsigned char, object)
        objc.setSignatureForSelector("IOBluetoothDevice",
                                     "openRFCOMMChannelSync:withChannelID:delegate:", "i16@0:o^@C@")

        # set to return int, and take (output object, unsigned int, object) args
        # i.e. in python: return (int, object) and accept (unsigned int, object)
        objc.setSignatureForSelector("IOBluetoothDevice",
                                     "openL2CAPChannelSync:withPSM:delegate:", "i20@0:o^@I@")

        # set to return int, take a const 6-char array arg
        # i.e. in python: return object and accept 6-char list
        # this seems to work even though the selector doesn't take a char aray,
        # it takes a struct 'BluetoothDeviceAddress' which contains a char array.
        objc.setSignatureForSelector("IOBluetoothDevice",
                                     "withAddress:", '@12@0:r^[6C]')

del objc
