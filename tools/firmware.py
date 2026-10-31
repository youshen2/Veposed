#!/usr/bin/env python3
"""Read-only firmware inspection and exact target verification (Python stdlib)."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "targets/xiaomi-band-10-pro-3.101.043.json"
MAX_NAMED_POINTS = 2048


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


def verify_named_callers(ap, profile):
    """Verify direct Thumb BL calls and the supported absolute-jump veneers."""

    def read(address, size):
        mapped = resolve(profile, address)
        mapping = next(m for m in profile["mappings"] if m["name"] == mapped["mapping"])
        start = number(mapping["execute"])
        if address < start or address + size > start + number(mapping["length"]):
            raise ValueError(f"address range {address:#x}+{size} leaves mapping")
        offset = mapped["file_offset"]
        result = ap[offset : offset + size]
        if len(result) != size:
            raise ValueError(f"address range {address:#x}+{size} leaves AP")
        return result

    verified = 0
    for name, point in profile.get("named_hooks", {}).items():
        caller = number(point.get("caller", point.get("os_setter_return", 0)))
        caller2 = number(point.get("caller2", 0))
        if profile["hooks"][point["target"]].get("kind", "inline") == "pointer" and (caller or caller2):
            raise ValueError(f"{name}: pointer caller filters need indirect-call verification")
        if caller2 and not caller:
            raise ValueError(f"{name}: caller2 requires caller")
        target = number(profile["hooks"][point["target"]]["address"]) & ~1
        for ret in (caller, caller2):
            if not ret:
                continue
            if ret & 1 or ret < 4:
                raise ValueError(f"{name}: caller must be an even return PC")
            call = ret - 4
            instruction = read(call, 4)
            first = int.from_bytes(instruction[:2], "little")
            second = int.from_bytes(instruction[2:], "little")
            if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
                raise ValueError(f"{name}: return PC {ret:#x} does not follow Thumb BL")
            sign = (first >> 10) & 1
            i1 = ((second >> 13) & 1) ^ sign ^ 1
            i2 = ((second >> 11) & 1) ^ sign ^ 1
            offset = (sign << 24) | (i1 << 23) | (i2 << 22)
            offset |= ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
            if sign:
                offset -= 1 << 25
            destination = call + 4 + offset
            if destination != target:
                veneer = read(destination, 8)
                jump_target = int.from_bytes(veneer[4:], "little")
                if (
                    destination & 3
                    or veneer[:4] != bytes.fromhex("5ff800f0")
                    or not jump_target & 1
                    or jump_target & ~1 != target
                ):
                    raise ValueError(f"{name}: call at {call:#x} does not reach {target:#x}")
            verified += 1
        declared = {
            number(point[key])
            for key in ("setter_call", "getter_call", "os_setter_call")
            if key in point
        }
        for key in ("setter_calls", "getter_calls"):
            declared.update(number(value) for value in point.get(key, []))
        if declared and declared != {ret - 4 for ret in (caller, caller2) if ret}:
            raise ValueError(f"{name}: declared call sites do not match caller filters")
    return verified


def validate_named_points(profile):
    """Enforce the generated catalog's runtime and SDK contracts before building."""
    contracts = {f"{kind}{count}" for kind in ("void", "word") for count in range(5)}
    site_contracts = {}
    for name, point in profile.get("named_hooks", {}).items():
        if not re.fullmatch(r"[a-z][a-z0-9_.]*", name) or len(name.encode("utf-8")) > 47:
            raise ValueError(f"{name}: invalid named-point name")
        target = profile["hooks"].get(point.get("target"))
        if target is None:
            raise ValueError(f"{name}: unknown target")
        contract = point.get("contract")
        if contract not in contracts:
            raise ValueError(f"{name}: unsupported contract")
        key = (target.get("kind", "inline"), number(target["address"]) & ~1)
        previous = site_contracts.setdefault(key, contract)
        if previous != contract:
            raise ValueError(f"{name}: conflicting contracts for shared target")
        text = point.get("text_arg1", False)
        if not isinstance(text, bool) or (text and contract != "void2"):
            raise ValueError(f"{name}: text_arg1 requires a void2 text setter")
        if number(point.get("active_slot2", 0)) and not number(point.get("active_slot", 0)):
            raise ValueError(f"{name}: active_slot2 requires active_slot")
        for key in ("subject_slot", "quiescent_slot", "quiescent_slot2", "active_slot",
                    "active_slot2", "os_label_slot", "about_root"):
            slot = number(point.get(key, 0))
            if not isinstance(slot, int) or not 0 <= slot <= 0xFFFFFFFC or slot % 4:
                raise ValueError(f"{name}: invalid {key}")
        argc = int(contract[-1])
        for field_name, spec in point.get("fields", {}).items():
            index, offset, width, size = (spec.get(k) for k in ("arg", "offset", "width", "size"))
            if not (isinstance(field_name, str) and re.fullmatch(r"[a-z][a-z0-9_]*", field_name)
                    and isinstance(index, int) and 0 <= index < argc
                    and isinstance(offset, int) and offset >= 0 and width in (1, 2, 4)
                    and isinstance(size, int) and offset + width <= size):
                raise ValueError(f"{name}: invalid field {field_name}")


def verify(path, profile):
    if len(profile.get("named_hooks", {})) > MAX_NAMED_POINTS:
        raise ValueError(f"named hook catalog exceeds runtime capacity ({MAX_NAMED_POINTS})")
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
        kind = hook.get("kind", "inline")
        if kind == "pointer":
            address = number(hook["address"])
            pointer = number(hook["expected_pointer"])
            if address & 3 or pointer & 1 != 1 or not 0 < pointer < 2**32:
                raise ValueError(f"{name} invalid pointer target")
            mapped = resolve(profile, address)
            mapping = next(m for m in profile["mappings"] if m["name"] == mapped["mapping"])
            if (mapped["file_offset"] != offset or mapped["write"] != hex(address)
                    or address + 4 > number(mapping["execute"]) + number(mapping["length"])):
                raise ValueError(f"{name} pointer slot mapping mismatch")
            expected = pointer.to_bytes(4, "little")
        elif kind == "inline":
            expected = bytes.fromhex(hook["expected"])
            address = number(hook["address"])
            if address & 1 != 1 or len(expected) != 16:
                raise ValueError(f"{name} inline target needs a Thumb address and 16-byte signature")
            mapped = resolve(profile, address)
            mapping = next(m for m in profile["mappings"] if m["name"] == mapped["mapping"])
            entry = address & ~1
            if (mapped["file_offset"] != offset or mapped["write"] is None
                    or entry + len(expected) > number(mapping["execute"]) + number(mapping["length"])):
                raise ValueError(f"{name} inline target mapping mismatch")
        else:
            raise ValueError(f"{name} unsupported target kind")
        if ap[offset : offset + len(expected)] != expected:
            raise ValueError(f"{name} signature mismatch")
    for window in profile.get("verification_windows", []):
        offset = number(window["file_offset"])
        expected = bytes.fromhex(window["expected"])
        if ap[offset : offset + len(expected)] != expected:
            raise ValueError(f"{window['name']} evidence mismatch")
    validate_named_points(profile)
    callers = verify_named_callers(ap, profile)
    return ap, {
        "target": profile["target"],
        "ap_size": len(ap),
        "ap_sha256": digest,
        "version": profile["version"],
        "build": profile["build"],
        "verified": True,
        "caller_filters_verified": callers,
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
        if raw.get("kind", "inline") == "pointer":
            target = (".kind = VEP_POINTER, .address = " + raw["address"]
                      + "u, .expected_pointer = " + raw["expected_pointer"] + "u")
        else:
            expected = ", ".join(f"0x{b:02x}" for b in bytes.fromhex(raw["expected"]))
            target = (".kind = VEP_INLINE, .address = " + raw["address"]
                      + "u, .expected_code = { " + expected + " }")
        contract = {
            f"{kind}{count}": f"VEP_{kind.upper()}{count}"
            for kind in ("void", "word")
            for count in range(5)
        }[point["contract"]]
        recipes.append(
            '    { .name = "'
            + name
            + '", .contract = '
            + contract
            + ", .target = { "
            + target
            + " }, .caller = "
            + point.get("caller", point.get("os_setter_return", "0"))
            + "u, .caller2 = "
            + point.get("caller2", "0")
            + "u, .subject_slot = "
            + point.get("subject_slot", point.get("os_label_slot", "0"))
            + "u, .quiescent_slot = "
            + point.get("quiescent_slot", point.get("about_root", "0"))
            + "u, .active_slot = "
            + point.get("active_slot", "0")
            + "u, .quiescent_slot2 = "
            + point.get("quiescent_slot2", "0")
            + "u, .active_slot2 = "
            + point.get("active_slot2", "0")
            + "u, .text_arg1 = "
            + ("1" if point.get("text_arg1", False) else "0")
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
