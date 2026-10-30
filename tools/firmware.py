#!/usr/bin/env python3
"""Read-only firmware inspection and exact target verification (Python stdlib)."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "targets/xiaomi-band-10-pro-3.101.043.json"


def number(value):
    return int(value, 0) if isinstance(value, str) else value


def read_ap(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            member = archive.getinfo("vela_ap.bin")
            if member.file_size > 32 * 1024 * 1024:
                raise ValueError("AP image exceeds 32 MiB")
            ap = archive.read(member)
            files = [{"name": i.filename, "size": i.file_size} for i in archive.infolist()]
    else:
        if path.stat().st_size > 32 * 1024 * 1024:
            raise ValueError("Input is neither an OTA ZIP nor an AP image under 32 MiB")
        ap, files = path.read_bytes(), []
    return ap, files


def verify(path, profile):
    ap, files = read_ap(path)
    digest = hashlib.sha256(ap).hexdigest()
    if len(ap) != profile["ap_size"] or digest != profile["ap_sha256"]:
        raise ValueError(f"AP identity mismatch: size={len(ap)}, sha256={digest}")
    for key in ("version", "build"):
        offset = number(profile["identity"][key]["file_offset"])
        expected = profile[key].encode() + b"\0"
        if ap[offset : offset + len(expected)] != expected:
            raise ValueError(f"{key} marker mismatch")
    for name, hook in profile["hooks"].items():
        offset = number(hook["file_offset"])
        expected = bytes.fromhex(hook["expected"])
        if ap[offset : offset + len(expected)] != expected:
            raise ValueError(f"{name} signature mismatch")
    for window in profile.get("verification_windows", []):
        offset = number(window["file_offset"])
        expected = bytes.fromhex(window["expected"])
        if ap[offset : offset + len(expected)] != expected:
            raise ValueError(f"{window['name']} evidence mismatch")
    return ap, {
        "target": profile["target"],
        "ap_size": len(ap),
        "ap_sha256": digest,
        "version": profile["version"],
        "build": profile["build"],
        "verified": True,
        "device_validation": profile["device_validation"],
        "files": files,
    }


def resolve(profile, address):
    address &= ~1
    # The copied executable aliases take precedence over the storage view.
    for mapping in sorted(profile["mappings"], key=lambda m: not m["writable"]):
        start, length = number(mapping["execute"]), number(mapping["length"])
        if start <= address < start + length:
            delta = address - start
            return {
                "mapping": mapping["name"],
                "execute": hex(address),
                "file_offset": number(mapping["file_offset"]) + delta,
                "write": hex(number(mapping["write"]) + delta) if mapping["writable"] else None,
            }
    raise ValueError(f"Address {address:#x} is outside the target mappings")


def generate_header(profile, output):
    hook = profile["hooks"]["lv_image_create"]
    signature = ", ".join(f"0x{b:02x}" for b in bytes.fromhex(hook["expected"]))
    label = profile["hooks"]["lvx_label_set_text"]
    label_signature = ", ".join(f"0x{b:02x}" for b in bytes.fromhex(label["expected"]))
    recipes = []
    for name, point in profile["named_hooks"].items():
        raw = profile["hooks"][point["target"]]
        expected = ", ".join(f"0x{b:02x}" for b in bytes.fromhex(raw["expected"]))
        contract = {"void2": "VEP_VOID2", "word2": "VEP_WORD2", "word4": "VEP_WORD4"}[
            point["contract"]
        ]
        recipes.append(
            '    { .name = "'
            + name
            + '", .contract = '
            + contract
            + ", .target = { .kind = VEP_INLINE, .address = "
            + raw["address"]
            + "u, .expected_code = { "
            + expected
            + " } }, .caller = "
            + point.get("os_setter_return", "0")
            + "u, .subject_slot = "
            + point.get("os_label_slot", "0")
            + "u, .quiescent_slot = "
            + point.get("about_root", "0")
            + "u }"
        )
    output.write_text(
        "/* Generated from an exact, verified AP image by tools/firmware.py. */\n"
        "#ifndef VEPOSED_TARGET_H\n#define VEPOSED_TARGET_H\n"
        f'#define VEP_TARGET_ID "{profile["target"]}"\n'
        + "".join(
            f"#define VEP_FW_{key.upper()} {address}u\n"
            for key, address in profile["symbols"].items()
        )
        + f"#define VEP_UMEM_START {profile['runtime_memory']['umem']['data_start']}u\n"
        + f"#define VEP_UMEM_END {profile['runtime_memory']['umem']['data_end']}u\n"
        + f"#define VEP_IMAGE_CREATE {hook['address']}u\n"
        + f"#define VEP_IMAGE_SIGNATURE {{ {signature} }}\n"
        + f"#define VEP_LABEL_SET_TEXT {label['address']}u\n"
        + f"#define VEP_LABEL_SIGNATURE {{ {label_signature} }}\n"
        + "static const vep_named_point vep_named_points[] = {\n"
        + ",\n".join(recipes)
        + "\n};\n"
        + "#define VEP_NAMED_POINTS vep_named_points\n#define VEP_NAMED_POINT_COUNT (sizeof(vep_named_points)/sizeof(vep_named_points[0]))\n"
        + "static inline int vep_target_matches(void) {\n"
        + "".join(
            f"    const volatile uint8_t *{key} = (const volatile uint8_t *){profile['identity'][key]['address']}u;\n"
            f'    const char expected_{key}[] = "{profile[key]}";\n'
            f"    for (size_t i = 0; i < sizeof(expected_{key}); ++i) if ({key}[i] != (uint8_t)expected_{key}[i]) return 0;\n"
            for key in ("version", "build")
        )
        + "    return 1;\n}\n#endif\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["inspect", "verify", "address", "extract", "header"])
    parser.add_argument("firmware", type=Path)
    parser.add_argument("--profile", type=Path, default=PROFILE)
    parser.add_argument("--address", type=lambda s: int(s, 0))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text())
    if args.command == "inspect":
        ap, files = read_ap(args.firmware)
        result = {"ap_size": len(ap), "ap_sha256": hashlib.sha256(ap).hexdigest(), "files": files}
    else:
        ap, result = verify(args.firmware, profile)
        if args.command == "address":
            if args.address is None:
                parser.error("address requires --address")
            result = resolve(profile, args.address)
            offset = result["file_offset"]
            result["bytes"] = ap[offset : offset + 16].hex()
            result["file_offset"] = hex(offset)
        elif args.command == "extract":
            if args.output is None:
                parser.error("extract requires --output")
            args.output.write_bytes(ap)
            result["extracted"] = str(args.output.resolve())
        elif args.command == "header":
            if args.output is None:
                parser.error("header requires --output")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            generate_header(profile, args.output)
            result["header"] = str(args.output.resolve())
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        print(f"firmware: {error}", file=sys.stderr)
        sys.exit(1)
