import re

re_hex_pair = "([0-9A-Fa-f]){2}"
# 0f:0f:0f:0f:0f:0f = 5x(0f:)+(0f)
re_address = re.compile(fr"({re_hex_pair}(:|-)){{5}}{re_hex_pair}",
                re.IGNORECASE)

def validate(address: str):
    if not isinstance(address, str):
        return False

    return re_address.match(address) is not None


def is_valid_uuid (uuid):
    """
    is_valid_uuid (uuid) -> bool

    returns True if uuid is a valid 128-bit UUID.

    valid UUIDs are always strings taking one of the following forms:
    XXXX
    XXXXXXXX
    XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    where each X is a hexadecimal digit (case insensitive)

    """
    try:
        if len (uuid) == 4:
            if int (uuid, 16) < 0: return False
        elif len (uuid) == 8:
            if int (uuid, 16) < 0: return False
        elif len (uuid) == 36:
            pieces = uuid.split ("-")
            if len (pieces) != 5 or \
                    len (pieces[0]) != 8 or \
                    len (pieces[1]) != 4 or \
                    len (pieces[2]) != 4 or \
                    len (pieces[3]) != 4 or \
                    len (pieces[4]) != 12:
                return False
            [ int (p, 16) for p in pieces ]
        else:
            return False
    except ValueError: 
        return False
    except TypeError:
        return False
    return True

def to_full_uuid (uuid):
    """
    converts a short 16-bit or 32-bit reserved UUID to a full 128-bit Bluetooth
    UUID.

    """
    if not is_valid_uuid (uuid): raise ValueError ("invalid UUID")
    if len (uuid) == 4:
        return "0000%s-0000-1000-8000-00805F9B34FB" % uuid
    elif len (uuid) == 8:
        return "%s-0000-1000-8000-00805F9B34FB" % uuid
    else:
        return uuid
