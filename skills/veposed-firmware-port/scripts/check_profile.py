#!/usr/bin/env python3
"""Check profile/AP consistency and report the evidence still needed on device."""

import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--firmware", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo.resolve() / "tools"))
    from firmware import number, resolve, verify

    profile = json.loads(args.profile.read_text())
    ap, identity = verify(args.firmware, profile)
    errors, hooks, symbols = [], {}, {}
    for mapping in profile["mappings"]:
        start, length = number(mapping["file_offset"]), number(mapping["length"])
        if start < 0 or length <= 0 or start + length > len(ap):
            errors.append(f"{mapping['name']}: mapping leaves the AP")
        for key in ("execute", "write"):
            if (
                key in mapping
                and not 0 <= number(mapping[key]) < number(mapping[key]) + length <= 2**32
            ):
                errors.append(f"{mapping['name']}: invalid {key} address range")
    for name, hook in profile["hooks"].items():
        try:
            address = number(hook["address"])
            mapped = resolve(profile, address)
            if address & 1 != 1:
                errors.append(f"{name}: Thumb callable must be odd")
            if mapped["file_offset"] != number(hook["file_offset"]):
                errors.append(f"{name}: address maps to a different file offset")
            if len(bytes.fromhex(hook["expected"])) != 16:
                errors.append(f"{name}: runtime expected_code is exactly 16 bytes")
            if mapped["write"] is None:
                errors.append(f"{name}: inline hook is outside a writable mapping")
            hooks[name] = mapped
        except ValueError as error:
            errors.append(f"{name}: {error}")
    for name, point in profile["named_hooks"].items():
        if len(name.encode()) > 47 or "\0" in name:
            errors.append(f"{name}: invalid named-point length")
        if point["target"] not in hooks:
            errors.append(f"{name}: unknown target")
        if point["contract"] not in ("void2", "word2", "word4"):
            errors.append(f"{name}: unsupported contract")
        target = profile["hooks"].get(point["target"], {})
        if "os_setter_return" in point and number(point["os_setter_return"]) & 1:
            errors.append(f"{name}: normalized return-PC filter must be even")
        hooks[name] = {
            "contract": point["contract"],
            "target": point["target"],
            "prototype": target.get("prototype", "unrecorded"),
        }
    for name, address in profile["symbols"].items():
        try:
            symbols[name] = resolve(profile, number(address))
        except ValueError:
            # Theme globals and other BSS have no bytes in an AP mapping.
            symbols[name] = {"address": address, "requires_runtime_region_evidence": True}
    umem = profile["runtime_memory"]["umem"]
    data_start, data_end = number(umem["data_start"]), number(umem["data_end"])
    exec_start, exec_end = number(umem["execute_start"]), number(umem["execute_end"])
    if not (
        0 <= data_start < data_end <= 2**32
        and 0 <= exec_start < exec_end <= 2**32
        and data_end - data_start == exec_end - exec_start
    ):
        errors.append("Umem ranges must be positive, 32-bit and equal-sized aliases")
    report = {
        "target": profile["target"],
        "identity": identity,
        "errors": errors,
        "hook_mappings": hooks,
        "symbols": symbols,
        "device_validation": profile["device_validation"],
        "scope": "Byte/address consistency; function identity, ABI, heap bounds and device behavior require separate evidence.",
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    print(rendered, end="")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
