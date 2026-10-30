"""Regress the ID mismatch against AstroBox's complete-alphanumeric-run rule."""

from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from face import INSTALLER_FACE_ID, module_face_id, pack, unpack


def astrobox_id(blob):
    # AstroBox-NG-Module-Core a15b0ba: default ResConfig scans bytes 34..58,
    # accepting complete ASCII alphanumeric runs of length 9 or 12 only.
    field = blob[34:58]
    for match in re.finditer(rb"[A-Za-z0-9]+", field):
        if len(match[0]) in (9, 12):
            return match[0].decode("ascii")
    return None


class FaceIDTests(unittest.TestCase):
    def make_face(self, face_id):
        return pack({"lua/main.lua": b'print("ok")'}, bytes(4), "Veposed", face_id, 1, 1)

    def test_astrobox_reads_full_id_without_moving_resource_offsets(self):
        sizes = []
        for value in (
            "123456789",
            "AB1234567",
            INSTALLER_FACE_ID,
            module_face_id("org.veposed.os_version"),
        ):
            with self.subTest(value=value):
                data = self.make_face(value)
                sizes.append(len(data))
                self.assertEqual(data[5], len(value))
                self.assertEqual(data[40 : 40 + len(value)], value.encode())
                self.assertEqual(astrobox_id(data), value)
                parsed = unpack(data)
                self.assertEqual(parsed["id"], value)
                self.assertEqual(parsed["files"]["lua/main.lua"], b'print("ok")')
        self.assertEqual(len(set(sizes)), 1)

    def test_invalid_ids_are_rejected_during_pack_and_inspection(self):
        for value in (
            "1900670001",
            "12345678",
            "12345678901",
            "1234567890123",
            "1234-6789",
            "１２３４５６７８９",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.make_face(value)
        data = bytearray(self.make_face(INSTALLER_FACE_ID))
        data[5] = 10
        with self.assertRaises(ValueError):
            unpack(data)
        self.assertNotEqual(INSTALLER_FACE_ID, module_face_id("org.veposed.os_version"))
        self.assertEqual(module_face_id("org.test"), module_face_id("org.test"))
