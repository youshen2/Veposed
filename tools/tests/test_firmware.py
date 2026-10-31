import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from firmware import MAX_NAMED_POINTS, generate_header, resolve, validate_named_points, verify, verify_named_callers
from thumb_check import verify_runtime_profile


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
            "mappings": [{"name": "code", "execute": 0x1000, "write": 0x2000,
                          "file_offset": 14, "length": 32, "writable": True}],
            "hooks": {"sample": {"address": "0x1001", "file_offset": 14,
                                  "expected": self.ap[14:30].hex()}},
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

    def test_catalog_over_runtime_capacity_is_rejected(self):
        profile = dict(self.profile, named_hooks={f"point.{i}": {} for i in range(MAX_NAMED_POINTS + 1)})
        with self.assertRaisesRegex(ValueError, "catalog exceeds runtime capacity"):
            verify(Path("unused"), profile)

    def test_inline_recipe_requires_writable_exact_full_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ap.bin"
            path.write_bytes(self.ap)
            for mutation in ("readonly", "offset", "partial", "even", "short"):
                profile = json.loads(json.dumps(self.profile))
                if mutation == "readonly":
                    profile["mappings"][0]["writable"] = False
                elif mutation == "offset":
                    profile["hooks"]["sample"]["file_offset"] += 1
                elif mutation == "partial":
                    profile["mappings"][0]["length"] = 15
                elif mutation == "even":
                    profile["hooks"]["sample"]["address"] = "0x1000"
                else:
                    profile["hooks"]["sample"]["expected"] = self.ap[14:22].hex()
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    verify(path, profile)

    def test_inline_relocation_check_uses_runtime_planner(self):
        root = Path(__file__).resolve().parents[2]
        profile = json.loads((root / "targets/xiaomi-band-10-pro-3.101.043.json").read_text())
        hook = profile["hooks"]["lv_image_set_angle"]
        subset = {"hooks": {"angle": dict(hook)}, "mappings": profile["mappings"]}
        self.assertEqual(verify_runtime_profile(subset), 1)
        subset["hooks"]["angle"]["expected"] = "00de" + hook["expected"][4:]
        with self.assertRaisesRegex(ValueError, "angle: unsupported Thumb relocation"):
            verify_runtime_profile(subset)

    def test_catalog_rejects_conflicting_contracts_and_invalid_slots(self):
        profile = {"hooks": {"target": {"address": "0x1001"}},
                   "named_hooks": {"demo.first": {"target": "target", "contract": "void2"},
                                   "demo.second": {"target": "target", "contract": "void2"}}}
        validate_named_points(profile)
        for mutation in ("contract", "text", "misaligned", "active2", "invalid_name"):
            candidate = json.loads(json.dumps(profile))
            point = candidate["named_hooks"]["demo.second"]
            if mutation == "contract":
                point["contract"] = "word2"
            elif mutation == "text":
                point["contract"] = "word2"
                candidate["named_hooks"]["demo.first"]["contract"] = "word2"
                point["text_arg1"] = True
            elif mutation == "misaligned":
                point["quiescent_slot"] = "0x20000001"
            elif mutation == "active2":
                point["active_slot2"] = "0x20000004"
            else:
                candidate["named_hooks"]["invalid\"name"] = candidate["named_hooks"].pop("demo.second")
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_named_points(candidate)

    def test_named_slot_must_match_runtime_memory_policy(self):
        root = Path(__file__).resolve().parents[2]
        profile = json.loads((root / "targets/xiaomi-band-10-pro-3.101.043.json").read_text())
        subset = {"hooks": {"angle": profile["hooks"]["lv_image_set_angle"]},
                  "mappings": profile["mappings"],
                  "named_hooks": {"demo.angle": {"quiescent_slot": "0x3c100000"}}}
        with self.assertRaisesRegex(ValueError, "demo.angle: quiescent_slot.*runtime memory policy"):
            verify_runtime_profile(subset)

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

    def test_named_return_pc_requires_a_call_to_the_configured_target(self):
        ap = bytearray(0x100)
        ap[0:4] = bytes.fromhex("00f00ef8")  # BL 0x1020 at 0x1000
        ap[0x20:0x28] = bytes.fromhex("5ff800f051100000")  # veneer -> 0x1051
        profile = {
            "mappings": [
                {
                    "name": "text",
                    "execute": 0x1000,
                    "file_offset": 0,
                    "length": len(ap),
                    "writable": False,
                }
            ],
            "hooks": {"target": {"address": "0x1051"}},
            "named_hooks": {
                "point": {"target": "target", "caller": "0x1004", "getter_call": "0x1000"}
            },
        }
        self.assertEqual(verify_named_callers(ap, profile), 1)
        direct = json.loads(json.dumps(profile))
        direct["hooks"]["target"]["address"] = "0x1021"
        self.assertEqual(verify_named_callers(ap, direct), 1)
        wrong = json.loads(json.dumps(profile))
        wrong["hooks"]["target"]["address"] = "0x1055"
        with self.assertRaisesRegex(ValueError, "does not reach"):
            verify_named_callers(ap, wrong)
        wrong = json.loads(json.dumps(profile))
        wrong["named_hooks"]["point"]["getter_call"] = "0x1002"
        with self.assertRaisesRegex(ValueError, "declared call sites"):
            verify_named_callers(ap, wrong)
        wrong = json.loads(json.dumps(profile))
        wrong["named_hooks"]["point"]["caller2"] = wrong["named_hooks"]["point"].pop("caller")
        with self.assertRaisesRegex(ValueError, "caller2 requires caller"):
            verify_named_callers(ap, wrong)
        ap[0x24] &= ~1
        with self.assertRaisesRegex(ValueError, "does not reach"):
            verify_named_callers(ap, profile)
        ap[0x24] |= 1
        ap[0] = 0
        ap[1] = 0
        with self.assertRaisesRegex(ValueError, "does not follow Thumb BL"):
            verify_named_callers(ap, profile)

    def test_pointer_recipe_checks_initialized_slot_and_mapping(self):
        ap = bytearray(self.ap)
        ap[14:18] = (0x1051).to_bytes(4, "little")
        profile = json.loads(json.dumps(self.profile))
        profile["ap_sha256"] = hashlib.sha256(ap).hexdigest()
        profile["mappings"] = [{"name": "data", "execute": 0x2000, "write": 0x2000,
                                "file_offset": 14, "length": 16, "writable": True}]
        profile["hooks"] = {"slot": {"kind": "pointer", "address": "0x2000",
                                      "expected_pointer": "0x1051", "file_offset": 14}}
        profile["named_hooks"] = {"point": {"target": "slot", "contract": "word1"}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ap.bin"
            path.write_bytes(ap)
            verify(path, profile)
            wrong = json.loads(json.dumps(profile))
            wrong["hooks"]["slot"]["expected_pointer"] = "0x1053"
            with self.assertRaisesRegex(ValueError, "signature mismatch"):
                verify(path, wrong)
            wrong = json.loads(json.dumps(profile))
            wrong["hooks"]["slot"]["address"] = "0x2004"
            with self.assertRaisesRegex(ValueError, "mapping mismatch"):
                verify(path, wrong)
            wrong = json.loads(json.dumps(profile))
            wrong["named_hooks"]["point"]["caller"] = "0x1004"
            with self.assertRaisesRegex(ValueError, "indirect-call verification"):
                verify(path, wrong)

    def test_named_recipes_emit_individual_scope_filters(self):
        profile_path = (
            Path(__file__).resolve().parents[2] / "targets/xiaomi-band-10-pro-3.101.043.json"
        )
        profile = json.loads(profile_path.read_text())
        with tempfile.TemporaryDirectory() as directory:
            header = Path(directory) / "veposed_target.h"
            generate_header(profile, header)
            lines = header.read_text().splitlines()
            for name, point in profile["named_hooks"].items():
                recipe = next(line for line in lines if f'.name = "{name}"' in line)
                target = profile["hooks"][point["target"]]
                if target.get("kind") == "pointer":
                    self.assertIn(".kind = VEP_POINTER", recipe)
                    self.assertIn(f'.expected_pointer = {target["expected_pointer"]}u', recipe)
                for field in (
                    "caller",
                    "caller2",
                    "subject_slot",
                    "quiescent_slot",
                    "active_slot",
                    "quiescent_slot2",
                    "active_slot2",
                ):
                    if field in point:
                        self.assertIn(f".{field} = {point[field]}u", recipe)

    def test_hook_reference_covers_the_registered_names(self):
        root = Path(__file__).resolve().parents[2]
        profile = json.loads((root / "targets/xiaomi-band-10-pro-3.101.043.json").read_text())
        doc = (root / "docs/hook-points-xiaomi-band-10-pro-3.101.043.md").read_text()
        documented = set(re.findall(r"^\| `([^`]+)` \|", doc, flags=re.MULTILINE))
        self.assertTrue(set(profile["named_hooks"]).issubset(documented))

    def test_page_catalog_matches_verified_descriptor_windows(self):
        root = Path(__file__).resolve().parents[2]
        profile = json.loads((root / "targets/xiaomi-band-10-pro-3.101.043.json").read_text())
        catalog = json.loads((root / "evidence/navigation-page-ids-043.json").read_text())
        doc = (root / "docs/navigation-page-ids-xiaomi-band-10-pro-3.101.043.md").read_text()
        self.assertEqual(catalog["ap_sha256"], profile["ap_sha256"])
        windows = {window["name"]: window for window in profile["verification_windows"]}
        for page in catalog["pages"]:
            window = windows[page["verification_window"]]
            blob = bytes.fromhex(window["expected"])
            self.assertEqual(len(blob), 116)
            self.assertEqual(int(window["file_offset"], 0), int(page["descriptor_file_offset"], 0))
            self.assertEqual(resolve(profile, int(page["descriptor_address"], 0))["file_offset"],
                             int(page["descriptor_file_offset"], 0))
            self.assertEqual(struct.unpack_from("<HH", blob, 20), (page["page_id"], page["app_id"]))
            self.assertEqual(struct.unpack_from("<I", blob, 16)[0], int(page["name_data_address"], 0))
            self.assertEqual(struct.unpack_from("<I", blob, 76)[0], int(page["create"], 0))
            self.assertIn(f'| {page["title"]} | `{page["descriptor_name"]}` | '
                          f'`0x{page["app_id"]:02x}` | `0x{page["page_id"]:02x}` |', doc)

    def test_page_candidates_include_the_independently_checked_descriptors(self):
        root = Path(__file__).resolve().parents[2]
        curated = json.loads((root / "evidence/navigation-page-ids-043.json").read_text())
        candidates = json.loads((root / "evidence/navigation-page-candidates-043.json").read_text())
        self.assertEqual(candidates["ap_sha256"], curated["ap_sha256"])
        by_address = {entry["address"]: entry for entry in candidates["pages"]}
        for page in curated["pages"]:
            candidate = by_address[page["descriptor_address"]]
            self.assertEqual((candidate["app_id"], candidate["page_id"], candidate["name"], candidate["create"]),
                             (page["app_id"], page["page_id"], page["descriptor_name"], page["create"]))

    def test_page_lifecycle_slots_match_registered_descriptor_bytes(self):
        root = Path(__file__).resolve().parents[2]
        profile = json.loads((root / "targets/xiaomi-band-10-pro-3.101.043.json").read_text())
        evidence = json.loads((root / "evidence/page-lifecycle-043.json").read_text())
        windows = {entry["name"]: entry for entry in profile["verification_windows"]}
        for point in evidence["points"]:
            named = profile["named_hooks"][point["name"]]
            target = profile["hooks"][named["target"]]
            window = windows[point["descriptor_window"]]
            descriptor = bytes.fromhex(window["expected"])
            offset = 76 if point["name"].endswith(".ui_create") else 100
            self.assertEqual(int(target["address"], 0), int(point["descriptor"], 0) + offset)
            self.assertEqual(int(target["file_offset"], 0), int(window["file_offset"], 0) + offset)
            self.assertEqual(int(target["expected_pointer"], 0), struct.unpack_from("<I", descriptor, offset)[0])
            self.assertEqual(named["contract"], point["contract"])
            self.assertEqual(named["quiescent_slot"], point["quiescent_slot"])
            self.assertEqual(named.get("quiescent_slot2"), point.get("quiescent_slot2"))
            root_slot = point.get("quiescent_slot2", point["quiescent_slot"])
            self.assertEqual(int(root_slot, 0), int(point["descriptor"], 0) + 48)
            self.assertEqual(named["fields"]["page_id"]["offset"], 20)
            self.assertEqual(named["fields"]["app_id"]["offset"], 22)

    def test_lifecycle_registration_arrays_include_each_selected_descriptor(self):
        root = Path(__file__).resolve().parents[2]
        profile = json.loads((root / "targets/xiaomi-band-10-pro-3.101.043.json").read_text())
        evidence = json.loads((root / "evidence/page-lifecycle-043.json").read_text())
        windows = {entry["name"]: entry for entry in profile["verification_windows"]}
        points = {entry["name"]: entry for entry in evidence["points"]}
        for registration in evidence["additional_registration_details"]:
            prefix = "lifecycle-" + registration["page"].replace(".", "-")
            array = windows[prefix + "-page-array"]
            manifest = windows[prefix + "-manifest"]
            blob = bytes.fromhex(array["expected"])
            self.assertEqual(int(array["file_offset"], 0),
                             int(registration["page_array_file_offset"], 0))
            self.assertEqual(len(blob), 4 * registration["count"])
            descriptor = int(points[registration["page"] + ".ui_create"]["descriptor"], 0)
            self.assertIn(descriptor, struct.unpack("<" + "I" * registration["count"], blob))
            self.assertEqual(int(manifest["file_offset"], 0),
                             int(registration["manifest"], 0) - 0x0C0C0000)

    def test_lifecycle_state_audit_covers_each_destroy_hook(self):
        root = Path(__file__).resolve().parents[2]
        profile = json.loads((root / "targets/xiaomi-band-10-pro-3.101.043.json").read_text())
        lifecycle = json.loads((root / "evidence/page-lifecycle-043.json").read_text())
        audit = json.loads((root / "evidence/lifecycle-state-audit-043.json").read_text())
        destroy = {entry["name"]: entry for entry in lifecycle["points"]
                   if entry["name"].endswith(".ui_destroy")}
        windows = {entry["name"]: entry for entry in profile["verification_windows"]}
        self.assertEqual(audit["ap_sha256"], profile["ap_sha256"])
        self.assertEqual({entry["page"] + ".ui_destroy" for entry in audit["points"]},
                         set(destroy))
        for entry in audit["points"]:
            point = destroy[entry["page"] + ".ui_destroy"]
            self.assertEqual(entry["state_slot"], point["quiescent_slot"])
            self.assertEqual(entry["descriptor_root_slot"],
                             point.get("quiescent_slot2", point["quiescent_slot"]))
            self.assertEqual(entry["destroy_callback"], point["expected_pointer"])
            if entry["kind"] == "page_manager_root":
                self.assertNotIn("quiescent_slot2", point)
                self.assertEqual(entry["verification_window"], "lifecycle-root-clear")
            window = windows[entry["verification_window"]]
            start = int(window["file_offset"], 0) + 0x0C0C0000
            clear = int(entry["clear_instruction"], 0)
            self.assertLessEqual(start, clear)
            self.assertLess(clear, start + len(bytes.fromhex(window["expected"])))
