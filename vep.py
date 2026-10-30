#!/usr/bin/env python3
"""Veposed module compiler and .face packager."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from firmware import PROFILE
from module_builder import compile_module
from face import unpack


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    hooks = commands.add_parser(
        "hooks", help="List verified named hook points and calling contracts"
    )
    hooks.add_argument("--profile", type=Path, default=PROFILE)
    build = commands.add_parser("build", help="Compile a Python module into ARM ELF + .face")
    build.add_argument("source", type=Path)
    build.add_argument("--firmware", type=Path, required=True)
    build.add_argument("--out", type=Path, default=ROOT / "build/module")
    build.add_argument("--profile", type=Path, default=PROFILE)
    suite = commands.add_parser(
        "suite", help="Build the complete framework installation .face and SDK bundle"
    )
    suite.add_argument("--firmware", type=Path, required=True)
    suite.add_argument("--profile", type=Path, default=PROFILE)
    inspect = commands.add_parser(
        "inspect-face", help="Check .face structure and list embedded resources"
    )
    inspect.add_argument("file", type=Path)
    args = parser.parse_args()
    if args.command == "hooks":
        profile = json.loads(args.profile.read_text())
        print(profile["target"])
        for name, point in profile["named_hooks"].items():
            print(f"  {name:<30} {point['contract']}")
    elif args.command == "build":
        print(
            json.dumps(
                compile_module(args.source, args.firmware, args.out, profile_path=args.profile),
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.command == "suite":
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/build-suite.py"),
                str(args.firmware.resolve()),
                "--profile",
                str(args.profile.resolve()),
            ],
            check=True,
        )
    else:
        info = unpack(args.file.read_bytes())
        info["files"] = {name: len(blob) for name, blob in info["files"].items()}
        info.pop("preview")
        print(json.dumps(info, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"vep: {error}", file=sys.stderr)
        sys.exit(1)
