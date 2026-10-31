from __future__ import annotations

import binascii
from typing import Dict, List, Sequence, Tuple, Union

L2CAP=0
RFCOMM=3

PORT_ANY=0

# Service Class IDs
SDP_SERVER_CLASS = "1000"
BROWSE_GRP_DESC_CLASS = "1001"
PUBLIC_BROWSE_GROUP = "1002"
SERIAL_PORT_CLASS = "1101"
LAN_ACCESS_CLASS = "1102"
DIALUP_NET_CLASS = "1103"
IRMC_SYNC_CLASS = "1104"
OBEX_OBJPUSH_CLASS = "1105"
OBEX_FILETRANS_CLASS = "1106"
IRMC_SYNC_CMD_CLASS = "1107"
HEADSET_CLASS = "1108"
CORDLESS_TELEPHONY_CLASS = "1109"
AUDIO_SOURCE_CLASS = "110a"
AUDIO_SINK_CLASS = "110b"
AV_REMOTE_TARGET_CLASS = "110c"
ADVANCED_AUDIO_CLASS = "110d"
AV_REMOTE_CLASS = "110e"
VIDEO_CONF_CLASS = "110f"
INTERCOM_CLASS = "1110"
FAX_CLASS = "1111"
HEADSET_AGW_CLASS = "1112"
WAP_CLASS = "1113"
WAP_CLIENT_CLASS = "1114"
PANU_CLASS = "1115"
NAP_CLASS = "1116"
GN_CLASS = "1117"
DIRECT_PRINTING_CLASS = "1118"
REFERENCE_PRINTING_CLASS = "1119"
IMAGING_CLASS = "111a"
IMAGING_RESPONDER_CLASS = "111b"
IMAGING_ARCHIVE_CLASS = "111c"
IMAGING_REFOBJS_CLASS = "111d"
HANDSFREE_CLASS = "111e"
HANDSFREE_AGW_CLASS = "111f"
DIRECT_PRT_REFOBJS_CLASS = "1120"
REFLECTED_UI_CLASS = "1121"
BASIC_PRINTING_CLASS = "1122"
PRINTING_STATUS_CLASS = "1123"
HID_CLASS = "1124"
HCR_CLASS = "1125"
HCR_PRINT_CLASS = "1126"
HCR_SCAN_CLASS = "1127"
CIP_CLASS = "1128"
VIDEO_CONF_GW_CLASS = "1129"
UDI_MT_CLASS = "112a"
UDI_TA_CLASS = "112b"
AV_CLASS = "112c"
SAP_CLASS = "112d"
PNP_INFO_CLASS = "1200"
GENERIC_NETWORKING_CLASS = "1201"
GENERIC_FILETRANS_CLASS = "1202"
GENERIC_AUDIO_CLASS = "1203"
GENERIC_TELEPHONY_CLASS = "1204"
UPNP_CLASS = "1205"
UPNP_IP_CLASS = "1206"
UPNP_PAN_CLASS = "1300"
UPNP_LAP_CLASS = "1301"
UPNP_L2CAP_CLASS = "1302"
VIDEO_SOURCE_CLASS = "1303"
VIDEO_SINK_CLASS = "1304"

# Bluetooth Profile Descriptors
SDP_SERVER_PROFILE = ( SDP_SERVER_CLASS, 0x0100)
BROWSE_GRP_DESC_PROFILE = ( BROWSE_GRP_DESC_CLASS, 0x0100)
SERIAL_PORT_PROFILE = ( SERIAL_PORT_CLASS, 0x0100)
LAN_ACCESS_PROFILE = ( LAN_ACCESS_CLASS, 0x0100)
DIALUP_NET_PROFILE = ( DIALUP_NET_CLASS, 0x0100)
IRMC_SYNC_PROFILE = ( IRMC_SYNC_CLASS, 0x0100)
OBEX_OBJPUSH_PROFILE = ( OBEX_OBJPUSH_CLASS, 0x0100)
OBEX_FILETRANS_PROFILE = ( OBEX_FILETRANS_CLASS, 0x0100)
IRMC_SYNC_CMD_PROFILE = ( IRMC_SYNC_CMD_CLASS, 0x0100)
HEADSET_PROFILE = ( HEADSET_CLASS, 0x0100)
CORDLESS_TELEPHONY_PROFILE = ( CORDLESS_TELEPHONY_CLASS, 0x0100)
AUDIO_SOURCE_PROFILE = ( AUDIO_SOURCE_CLASS, 0x0100)
AUDIO_SINK_PROFILE = ( AUDIO_SINK_CLASS, 0x0100)
AV_REMOTE_TARGET_PROFILE = ( AV_REMOTE_TARGET_CLASS, 0x0100)
ADVANCED_AUDIO_PROFILE = ( ADVANCED_AUDIO_CLASS, 0x0100)
AV_REMOTE_PROFILE = ( AV_REMOTE_CLASS, 0x0100)
VIDEO_CONF_PROFILE = ( VIDEO_CONF_CLASS, 0x0100)
INTERCOM_PROFILE = ( INTERCOM_CLASS, 0x0100)
FAX_PROFILE = ( FAX_CLASS, 0x0100)
HEADSET_AGW_PROFILE = ( HEADSET_AGW_CLASS, 0x0100)
WAP_PROFILE = ( WAP_CLASS, 0x0100)
WAP_CLIENT_PROFILE = ( WAP_CLIENT_CLASS, 0x0100)
PANU_PROFILE = ( PANU_CLASS, 0x0100)
NAP_PROFILE = ( NAP_CLASS, 0x0100)
GN_PROFILE = ( GN_CLASS, 0x0100)
DIRECT_PRINTING_PROFILE = ( DIRECT_PRINTING_CLASS, 0x0100)
REFERENCE_PRINTING_PROFILE = ( REFERENCE_PRINTING_CLASS, 0x0100)
IMAGING_PROFILE = ( IMAGING_CLASS, 0x0100)
IMAGING_RESPONDER_PROFILE = ( IMAGING_RESPONDER_CLASS, 0x0100)
IMAGING_ARCHIVE_PROFILE = ( IMAGING_ARCHIVE_CLASS, 0x0100)
IMAGING_REFOBJS_PROFILE = ( IMAGING_REFOBJS_CLASS, 0x0100)
HANDSFREE_PROFILE = ( HANDSFREE_CLASS, 0x0100)
HANDSFREE_AGW_PROFILE = ( HANDSFREE_AGW_CLASS, 0x0100)
DIRECT_PRT_REFOBJS_PROFILE = ( DIRECT_PRT_REFOBJS_CLASS, 0x0100)
REFLECTED_UI_PROFILE = ( REFLECTED_UI_CLASS, 0x0100)
BASIC_PRINTING_PROFILE = ( BASIC_PRINTING_CLASS, 0x0100)
PRINTING_STATUS_PROFILE = ( PRINTING_STATUS_CLASS, 0x0100)
HID_PROFILE = ( HID_CLASS, 0x0100)
HCR_PROFILE = ( HCR_SCAN_CLASS, 0x0100)
HCR_PRINT_PROFILE = ( HCR_PRINT_CLASS, 0x0100)
HCR_SCAN_PROFILE = ( HCR_SCAN_CLASS, 0x0100)
CIP_PROFILE = ( CIP_CLASS, 0x0100)
VIDEO_CONF_GW_PROFILE = ( VIDEO_CONF_GW_CLASS, 0x0100)
UDI_MT_PROFILE = ( UDI_MT_CLASS, 0x0100)
UDI_TA_PROFILE = ( UDI_TA_CLASS, 0x0100)
AV_PROFILE = ( AV_CLASS, 0x0100)
SAP_PROFILE = ( SAP_CLASS, 0x0100)
PNP_INFO_PROFILE = ( PNP_INFO_CLASS, 0x0100)
GENERIC_NETWORKING_PROFILE = ( GENERIC_NETWORKING_CLASS, 0x0100)
GENERIC_FILETRANS_PROFILE = ( GENERIC_FILETRANS_CLASS, 0x0100)
GENERIC_AUDIO_PROFILE = ( GENERIC_AUDIO_CLASS, 0x0100)
GENERIC_TELEPHONY_PROFILE = ( GENERIC_TELEPHONY_CLASS, 0x0100)
UPNP_PROFILE = ( UPNP_CLASS, 0x0100)
UPNP_IP_PROFILE = ( UPNP_IP_CLASS, 0x0100)
UPNP_PAN_PROFILE = ( UPNP_PAN_CLASS, 0x0100)
UPNP_LAP_PROFILE = ( UPNP_LAP_CLASS, 0x0100)
UPNP_L2CAP_PROFILE = ( UPNP_L2CAP_CLASS, 0x0100)
VIDEO_SOURCE_PROFILE = ( VIDEO_SOURCE_CLASS, 0x0100)
VIDEO_SINK_PROFILE = ( VIDEO_SINK_CLASS, 0x0100)

# Universal Service Attribute IDs
SERVICE_RECORD_HANDLE_ATTRID = 0x0000
SERVICE_CLASS_ID_LIST_ATTRID = 0x0001
SERVICE_RECORD_STATE_ATTRID = 0x0002
SERVICE_ID_ATTRID = 0x0003
PROTOCOL_DESCRIPTOR_LIST_ATTRID = 0x0004
BROWSE_GROUP_LIST_ATTRID = 0x0005
LANGUAGE_BASE_ATTRID_LIST_ATTRID = 0x0006
SERVICE_INFO_TIME_TO_LIVE_ATTRID = 0x0007
SERVICE_AVAILABILITY_ATTRID = 0x0008
BLUETOOTH_PROFILE_DESCRIPTOR_LIST_ATTRID = 0x0009
DOCUMENTATION_URL_ATTRID = 0x000a
CLIENT_EXECUTABLE_URL_ATTRID = 0x000b
ICON_URL_ATTRID = 0x000c
SERVICE_NAME_ATTRID = 0x0100
SERVICE_DESCRIPTION_ATTRID = 0x0101
PROVIDER_NAME_ATTRID = 0x0102

# Protocol UUIDs
SDP_UUID       = "0001"
UDP_UUID       = "0002"
RFCOMM_UUID    = "0003"
TCP_UUID       = "0004"
TCS_BIN_UUID   = "0005"
TCS_AT_UUID    = "0006"
OBEX_UUID      = "0008"
IP_UUID        = "0009"
FTP_UUID       = "000a"
HTTP_UUID      = "000c"
WSP_UUID       = "000e"
BNEP_UUID      = "000f"
UPNP_UUID      = "0010"
HIDP_UUID      = "0011"
HCRP_CTRL_UUID = "0012"
HCRP_DATA_UUID = "0014"
HCRP_NOTE_UUID = "0016"
AVCTP_UUID     = "0017"
AVDTP_UUID     = "0019"
CMTP_UUID      = "001b"
UDI_UUID       = "001d"
L2CAP_UUID     = "0100"

# Inquiry Access Codes
IAC_GIAC = 0x9e8b33
IAC_LIAC = 0x9e8b00

class BluetoothError(IOError):
    pass


def is_valid_address(s: object) -> bool:
    """Return whether *s* contains six colon-separated hexadecimal octets."""
    if not isinstance(s, str):
        return False
    pairs = s.split(":")
    return len(pairs) == 6 and all(
        len(pair) == 2 and all(c in "0123456789abcdefABCDEF" for c in pair)
        for pair in pairs
    )


def is_valid_uuid(uuid: object) -> bool:
    """Accept the Bluetooth 16-bit, 32-bit and canonical 128-bit UUID forms."""
    if not isinstance(uuid, str):
        return False
    if len(uuid) in (4, 8):
        digits = uuid
    elif len(uuid) == 36:
        if tuple(map(len, uuid.split("-"))) != (8, 4, 4, 4, 12):
            return False
        digits = uuid.replace("-", "")
    else:
        return False
    return all(c in "0123456789abcdefABCDEF" for c in digits)


def to_full_uuid(uuid: str) -> str:
    """Expand a reserved UUID into the Bluetooth base UUID."""
    if not is_valid_uuid(uuid):
        raise ValueError("invalid UUID")
    if len(uuid) == 4:
        return "0000%s-0000-1000-8000-00805F9B34FB" % uuid
    if len(uuid) == 8:
        return "%s-0000-1000-8000-00805F9B34FB" % uuid
    return uuid


# SDP strings remain bytes when decoded, as in the original public helpers.
# Sequence elements retain their descriptor names and recursive value shape.
SDPValue = Union[None, bool, int, str, bytes, Sequence["SDPElement"]]
SDPElement = Tuple[str, SDPValue]


def sdp_parse_size_desc(data: bytes) -> Tuple[int, int, int]:
    if not data:
        raise ValueError("missing SDP type/size descriptor")
    dtype, descriptor = data[0] >> 3, data[0] & 7
    if dtype > 8:
        raise ValueError("invalid SDP data type")
    start = 1
    if dtype == 0:
        size = 0
    elif descriptor <= 4:
        size = 1 << descriptor
    else:
        width = 1 << (descriptor - 5)
        start += width
        if len(data) < start:
            raise ValueError("truncated SDP size descriptor")
        size = int.from_bytes(data[1:start], "big")
    return dtype, size, start


def sdp_parse_uuid(data: bytes, size: int) -> Union[bytes, str]:
    if len(data) != size:
        raise ValueError("truncated SDP UUID")
    if size in (2, 4):
        return binascii.hexlify(data)
    if size == 16:
        text = data.hex().upper()
        return "%s-%s-%s-%s-%s" % (
            text[:8], text[8:12], text[12:16], text[16:20], text[20:]
        )
    raise ValueError("invalid UUID size")


def sdp_parse_int(data: bytes, size: int, signed: bool) -> int:
    if size not in (1, 2, 4, 8, 16) or len(data) != size:
        raise ValueError("invalid or truncated SDP integer")
    return int.from_bytes(data, "big", signed=signed)


def sdp_parse_data_elementSequence(data: bytes) -> List[SDPElement]:
    result: List[SDPElement] = []
    pos = 0
    while pos < len(data):
        kind, value, consumed = sdp_parse_data_element(data[pos:])
        pos += consumed
        result.append((kind, value))
    return result


def sdp_parse_data_element(data: bytes) -> Tuple[str, SDPValue, int]:
    dtype, size, start = sdp_parse_size_desc(data)
    if len(data) - start < size:
        raise ValueError("truncated SDP data element")
    element = data[start:start + size]
    value: SDPValue
    if dtype == 0:
        kind, value = "Nil", None
    elif dtype in (1, 2):
        kind = ("UInt" if dtype == 1 else "SInt") + str(size * 8)
        value = sdp_parse_int(element, size, dtype == 2)
    elif dtype == 3:
        kind, value = "UUID", sdp_parse_uuid(element, size)
    elif dtype == 4:
        kind, value = "String", element
    elif dtype == 5:
        if size != 1:
            raise ValueError("an SDP Boolean occupies one byte")
        kind, value = "Bool", bool(element[0])
    elif dtype in (6, 7):
        kind = "ElemSeq" if dtype == 6 else "AltElemSeq"
        value = sdp_parse_data_elementSequence(element)
    else:
        kind, value = "URL", element
    return kind, value, start + size


def sdp_parse_raw_record(data: bytes) -> Dict[int, SDPValue]:
    dtype, size, start = sdp_parse_size_desc(data)
    if len(data) - start < size:
        raise ValueError("truncated SDP record")
    if dtype != 6:
        raise ValueError("an SDP record must be an element sequence")
    pos, end = start, start + size
    record: Dict[int, SDPValue] = {}
    while pos < end:
        kind, attribute, consumed = sdp_parse_data_element(data[pos:end])
        if kind != "UInt16" or not isinstance(attribute, int):
            raise ValueError("an SDP attribute identifier must be UInt16")
        pos += consumed
        _, value, consumed = sdp_parse_data_element(data[pos:end])
        pos += consumed
        record[attribute] = value
    return record


def sdp_make_data_element(type: str, value: SDPValue) -> bytes:
    def fixed(descriptor: int, size: int) -> bytes:
        return bytes([(descriptor << 3) | size])

    def variable(descriptor: int, payload: bytes) -> bytes:
        size = len(payload)
        for width, size_descriptor in ((1, 5), (2, 6), (4, 7)):
            if size < 1 << (width * 8):
                return fixed(descriptor, size_descriptor) + size.to_bytes(width, "big") + payload
        raise OverflowError("SDP element exceeds its 32-bit length range")

    integer_types = {
        "UInt8": (1, 0), "UInt16": (1, 1), "UInt32": (1, 2),
        "UInt64": (1, 3), "UInt128": (1, 4),
        "SInt8": (2, 0), "SInt16": (2, 1), "SInt32": (2, 2),
        "SInt64": (2, 3), "SInt128": (2, 4),
    }
    if type == "Nil":
        return fixed(0, 0)
    if type in integer_types:
        if not isinstance(value, int):
            raise TypeError("an SDP integer requires an integer value")
        descriptor, size = integer_types[type]
        return fixed(descriptor, size) + value.to_bytes(1 << size, "big", signed=descriptor == 2)
    if type == "UUID":
        if not isinstance(value, str) or not is_valid_uuid(value):
            raise ValueError("invalid SDP UUID")
        payload = binascii.unhexlify(value.replace("-", ""))
        return fixed(3, {2: 1, 4: 2, 16: 4}[len(payload)]) + payload
    if type in ("String", "URL"):
        if not isinstance(value, (str, bytes)):
            raise TypeError("an SDP string requires text or bytes")
        payload = value.encode("utf-8") if isinstance(value, str) else value
        return variable(4 if type == "String" else 8, payload)
    if type == "Bool":
        return fixed(5, 0) + bytes([bool(value)])
    if type in ("ElemSeq", "AltElemSeq"):
        if value is None or isinstance(value, (int, str, bytes)):
            raise TypeError("an SDP sequence requires descriptor/value pairs")
        payload = b"".join(sdp_make_data_element(kind, item) for kind, item in tuple(value))
        return variable(6 if type == "ElemSeq" else 7, payload)
    raise ValueError("invalid SDP type %s" % type)
