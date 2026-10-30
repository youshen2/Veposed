import struct
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from face import pack, unpack


class FaceEntryTests(unittest.TestCase):
    def test_lua_element_points_to_main_between_other_resources(self):
        # Like compiler-generated faces containing image.lua, main.lua, root.lua.
        files = {
            "lua/image.lua": b"return {}",
            "lua/main.lua": b'print("UI")',
            "lua/root.lua": b"return {}",
            "lua/veposed.bin": b"\x7fELF",
        }
        blob = pack(files, bytes(4), "Veposed", "190067000101", 1, 1)
        table = struct.unpack_from("<I", blob, 180)[0]
        element = struct.unpack_from("<I", blob, table + 8)[0]
        target = struct.unpack_from("<I", blob, element)[0]
        self.assertEqual(target, 0x05000001)
        self.assertEqual(unpack(blob)["entrypoint"], "lua/main.lua")
        broken = bytearray(blob)
        struct.pack_into("<I", broken, element, 0x05000003)
        with self.assertRaisesRegex(ValueError, "lua/veposed.bin"):
            unpack(broken)
