import binascii
import struct



# =============== parsing and constructing raw SDP records ============

def sdp_parse_size_desc (data):
    dts = struct.unpack ("B", data[0:1])[0]
    dtype, dsizedesc = dts >> 3, dts & 0x7
    dstart = 1
    if   dtype == 0:     dsize = 0
    elif dsizedesc == 0: dsize = 1
    elif dsizedesc == 1: dsize = 2
    elif dsizedesc == 2: dsize = 4
    elif dsizedesc == 3: dsize = 8
    elif dsizedesc == 4: dsize = 16
    elif dsizedesc == 5:
        dsize = struct.unpack ("B", data[1:2])[0]
        dstart += 1
    elif dsizedesc == 6:
        dsize = struct.unpack ("!H", data[1:3])[0]
        dstart += 2
    elif dsizedesc == 7:
        dsize == struct.unpack ("!I", data[1:5])[0]
        dstart += 4

    if dtype > 8:
        raise ValueError ("Invalid TypeSizeDescriptor byte %s %d, %d" \
                % (binascii.hexlify (data[0:1]), dtype, dsizedesc))

    return dtype, dsize, dstart

def sdp_parse_uuid (data, size):
    if size == 2:
        return binascii.hexlify (data)
    elif size == 4:
        return binascii.hexlify (data)
    elif size == 16:
        return "%08X-%04X-%04X-%04X-%04X%08X" % struct.unpack ("!IHHHHI", data)
    else: return ValueError ("invalid UUID size")

def sdp_parse_int (data, size, signed):
    fmts = { 1 : "!b" , 2 : "!h" , 4 : "!i" , 8 : "!q" , 16 : "!qq" }
    fmt = fmts[size]
    if not signed: fmt = fmt.upper ()
    if fmt in [ "!qq", "!QQ" ]:
        upp, low = struct.unpack ("!QQ", data)
        result = ( upp << 64) | low
        if signed:
            result=- ((~ (result-1))&0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        return result
    else:
        return struct.unpack (fmt, data)[0]

def sdp_parse_data_elementSequence (data):
    result = []
    pos = 0
    datalen = len (data)
    while pos < datalen:
        rtype, rval, consumed = sdp_parse_data_element (data[pos:])
        pos += consumed
        result.append ( (rtype, rval))
    return result

def sdp_parse_data_element (data):
    dtype, dsize, dstart = sdp_parse_size_desc (data)
    elem = data[dstart:dstart+dsize]

    if dtype == 0:
        rtype, rval = "Nil", None
    elif dtype == 1:
        rtype, rval = "UInt%d"% (dsize*8), sdp_parse_int (elem, dsize, False)
    elif dtype == 2:
        rtype, rval = "SInt%d"% (dsize*8), sdp_parse_int (elem, dsize, True)
    elif dtype == 3:
        rtype, rval = "UUID", sdp_parse_uuid (elem, dsize)
    elif dtype == 4:
        rtype, rval = "String", elem
    elif dtype == 5:
        rtype, rval = "Bool", (struct.unpack ("B", elem)[0] != 0)
    elif dtype == 6:
        rtype, rval = "ElemSeq", sdp_parse_data_elementSequence (elem)
    elif dtype == 7:
        rtype, rval = "AltElemSeq", sdp_parse_data_elementSequence (elem)
    elif dtype == 8:
        rtype, rval = "URL", elem

    return rtype, rval, dstart+dsize

def sdp_parse_raw_record (data):
    dtype, dsize, dstart = sdp_parse_size_desc (data)
    assert dtype == 6

    pos = dstart
    datalen = len (data)
    record = {}
    while pos < datalen:
        type, attrid, consumed = sdp_parse_data_element (data[pos:])
        assert type == "UInt16"
        pos += consumed
        type, attrval, consumed = sdp_parse_data_element (data[pos:])
        pos += consumed
        record[attrid] = attrval
    return record

def sdp_make_data_element (type, value):
    def maketsd (tdesc, sdesc):
        return struct.pack ("B", (tdesc << 3) | sdesc)
    def maketsdl (tdesc, size):
        if   size < (1<<8):  return struct.pack ("!BB", tdesc << 3 | 5, size)
        elif size < (1<<16): return struct.pack ("!BH", tdesc << 3 | 6, size)
        else:                return struct.pack ("!BI", tdesc << 3 | 7, size)

    easyinttypes = { "UInt8"   : (1, 0, "!B"),  "UInt16"  : (1, 1, "!H"),
                     "UInt32"  : (1, 2, "!I"),  "UInt64"  : (1, 3, "!Q"),
                     "SInt8"   : (2, 0, "!b"),  "SInt16"  : (2, 1, "!h"),
                     "SInt32"  : (2, 2, "!i"),  "SInt64"  : (2, 3, "!q"),
                     }

    if type == "Nil": 
        return maketsd (0, 0)
    elif type in easyinttypes:
        tdesc, sdesc, fmt = easyinttypes[type]
        return maketsd (tdesc, sdesc) + struct.pack (fmt, value)
    elif type == "UInt128":
        ts = maketsd (1, 4)
        upper = ts >> 64
        lower = (ts & 0xFFFFFFFFFFFFFFFF)
        return ts + struct.pack ("!QQ", upper, lower)
    elif type == "SInt128":
        ts = maketsd (2, 4)
        # FIXME
        raise NotImplementedError ("128-bit signed int NYI!")
    elif type == "UUID":
        if len (value) == 4:
            return maketsd (3, 1) + binascii.unhexlify (value)
        elif len (value) == 8:
            return maketsd (3, 2) + binascii.unhexlify (value)
        elif len (value) == 36:
            return maketsd (3, 4) + binascii.unhexlify (value.replace ("-",""))
    elif type == "String":
        return maketsdl (4, len (value)) + str.encode(value)
    elif type == "Bool":
        return maketsd (5,0) + (value and "\x01" or "\x00")
    elif type == "ElemSeq":
        packedseq = bytes()
        for subtype, subval in value:
            nextelem = sdp_make_data_element (subtype, subval)
            packedseq = packedseq + nextelem
        return maketsdl (6, len (packedseq)) + packedseq
    elif type == "AltElemSeq":
        packedseq = bytes()
        for subtype, subval in value:
            packedseq = packedseq + sdp_make_data_element (subtype, subval)
        return maketsdl (7, len (packedseq)) + packedseq
    elif type == "URL":
        return maketsdl (8, len (value)) + value
    else:
        raise ValueError ("invalid type %s" % type)

