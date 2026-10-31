"""Actual SDP wire-format regressions; no adapter or SDP server is accessed."""
import concurrent.futures
import unittest

from bluetooth import btcommon as sdp


class SDPCodecTest(unittest.TestCase):
    def test_utf8_length_is_encoded_byte_count(self):
        for text in ("StableKite", "Крыло", "طائرة", "🪁"):
            encoded = text.encode("utf8")
            wire = sdp.sdp_make_data_element("String", text)
            self.assertEqual(wire, b"\x25" + bytes([len(encoded)]) + encoded)
            self.assertEqual(sdp.sdp_parse_data_element(wire), ("String", encoded, len(wire)))

    def test_integer_widths_signed_boundaries_and_booleans(self):
        for bits in (8, 16, 32, 64, 128):
            for signed in (False, True):
                kind = ("SInt" if signed else "UInt") + str(bits)
                values = (-1, -(1 << (bits - 1)), (1 << (bits - 1)) - 1) if signed else (0, (1 << bits) - 1)
                for value in values:
                    with self.subTest(kind=kind, value=value):
                        wire = sdp.sdp_make_data_element(kind, value)
                        self.assertEqual(wire[1:], value.to_bytes(bits // 8, "big", signed=signed))
                        self.assertEqual(sdp.sdp_parse_data_element(wire), (kind, value, len(wire)))
        for value, byte in ((False, 0), (True, 1)):
            self.assertEqual(sdp.sdp_make_data_element("Bool", value), bytes([0x28, byte]))

    def test_uuid_forms_and_raw_record(self):
        for uuid, decoded in (("1101", b"1101"), ("01234567", b"01234567"),
                              ("00112233-4455-6677-8899-AABBCCDDEEFF", "00112233-4455-6677-8899-AABBCCDDEEFF")):
            wire = sdp.sdp_make_data_element("UUID", uuid)
            self.assertEqual(sdp.sdp_parse_data_element(wire), ("UUID", decoded, len(wire)))
        wire = sdp.sdp_make_data_element("ElemSeq", [
            ("UInt16", sdp.SERVICE_NAME_ATTRID), ("String", "Крыло"),
            ("UInt16", sdp.SERVICE_CLASS_ID_LIST_ATTRID), ("ElemSeq", [("UUID", "1101")]),
        ])
        self.assertEqual(sdp.sdp_parse_raw_record(wire), {
            sdp.SERVICE_NAME_ATTRID: "Крыло".encode(),
            sdp.SERVICE_CLASS_ID_LIST_ATTRID: [("UUID", b"1101")],
        })

    def test_sequence_length_boundaries_and_url(self):
        self.assertEqual(sdp.sdp_parse_size_desc(b"\x25\x03"), (4, 3, 2))
        for size in (0, 1, 255, 256, 65535, 65536):
            wire = sdp.sdp_make_data_element("URL", b"x" * size)
            self.assertEqual(sdp.sdp_parse_data_element(wire), ("URL", b"x" * size, len(wire)))

    def test_invalid_format_reports_errors(self):
        for wire in (b"", b"\x25", b"\x26\x00", b"\x25\x03x", b"\xf8", b"\x0b\x01"):
            with self.subTest(wire=wire), self.assertRaises(ValueError):
                sdp.sdp_parse_data_element(wire)
        for uuid in ("+101", " 101", "0x01", "00112233-4455-6677-8899-AABBCCDDEEFG"):
            self.assertFalse(sdp.is_valid_uuid(uuid))
        self.assertFalse(sdp.is_valid_address("1:23:45:67:89:AB"))
        self.assertTrue(sdp.is_valid_address("01:23:45:67:89:AB"))
        with self.assertRaises(ValueError):
            sdp.sdp_parse_raw_record(b"\x35\x02\x08\x01")

    def test_parallel_real_encoders_and_parsers(self):
        def worker(index):
            for value in range(128):
                message = "Крыло-%d-%d" % (index, value)
                wire = sdp.sdp_make_data_element("ElemSeq", [("String", message), ("UInt64", value)])
                self.assertEqual(sdp.sdp_parse_data_element(wire)[1], [("String", message.encode()), ("UInt64", value)])
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(worker, range(8)))


if __name__ == "__main__":
    unittest.main()
