import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from firmware import resolve, verify


class FirmwareTests(unittest.TestCase):
    def setUp(self):
        self.ap = b"version\0build\0" + bytes(range(32))
        self.profile = {
            "target": "fixture",
            "version": "version",
            "build": "build",
            "ap_size": len(self.ap),
            "ap_sha256": hashlib.sha256(self.ap).hexdigest(),
            "identity": {"version": {"file_offset": 0}, "build": {"file_offset": 8}},
            "hooks": {"sample": {"file_offset": 14, "expected": self.ap[14:30].hex()}},
            "device_validation": "pending",
        }

    def test_raw_and_ota_are_verified_by_ap_content(self):
        with tempfile.TemporaryDirectory() as directory:
            for zipped in (False, True):
                path = Path(directory) / ("ota.bin" if zipped else "ap.bin")
                if zipped:
                    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                        archive.writestr("vela_ap.bin", self.ap)
                        archive.writestr("ota.sh", "exit 99")
                else:
                    path.write_bytes(self.ap)
                data, report = verify(path, self.profile)
                self.assertEqual(data, self.ap)
                self.assertTrue(report["verified"])

    def test_tampering_and_stale_signatures_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ap.bin"
            path.write_bytes(self.ap[:-1] + b"x")
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                verify(path, self.profile)
            path.write_bytes(self.ap)
            profile = json.loads(json.dumps(self.profile))
            profile["hooks"]["sample"]["expected"] = "00" * 16
            with self.assertRaisesRegex(ValueError, "signature mismatch"):
                verify(path, profile)

    def test_real_target_execution_alias_resolves_to_ap_offset(self):
        profile_path = (
            Path(__file__).resolve().parents[2] / "targets/xiaomi-band-10-pro-3.101.043.json"
        )
        profile = json.loads(profile_path.read_text())
        mapped = resolve(profile, 0x1C06CAC1)
        self.assertEqual(mapped["file_offset"], 0xB9F00)
        self.assertEqual(mapped["write"], "0x3c06cac0")
        self.assertEqual(resolve(profile, 0x0C588D59)["file_offset"], 0x4C8D58)
        with self.assertRaises(ValueError):
            resolve(profile, 0xDEADBEEF)
