#!/usr/bin/env python3
"""Extract an AP and inventory its identity strings; never execute OTA scripts."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--firmware", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo.resolve() / "tools"))
    from firmware import read_ap

    ap, members = read_ap(args.firmware)
    report = {
        "input": str(args.firmware.resolve()),
        "package_sha256": hashlib.sha256(args.firmware.read_bytes()).hexdigest(),
        "ap_sha256": hashlib.sha256(ap).hexdigest(),
        "ap_size": len(ap),
        "archive_members": members,
        "header_strings": [
            {"file_offset": hex(match.start()), "text": match.group().decode("ascii")}
            for match in re.finditer(rb"[ -~]{6,96}", ap[:4096])
        ],
    }
    args.out.mkdir(parents=True, exist_ok=True)
    for name, data in (
        ("vela_ap.bin", ap),
        ("inventory.json", (json.dumps(report, indent=2) + "\n").encode()),
    ):
        with (args.out / name).open("xb") as destination:
            destination.write(data)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
