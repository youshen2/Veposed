#!/usr/bin/env python3
"""Create a Python module against a known profile, without overwriting source."""

import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--point", required=True)
    parser.add_argument("--mode", choices=("text", "original"), default="original")
    parser.add_argument("--text")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo.resolve() / "sdk"))
    from veposed import Module

    profile_path = args.profile or args.repo / "targets/xiaomi-band-10-pro-3.101.043.json"
    profile = json.loads(profile_path.read_text())
    module = Module(args.id, args.name)
    if args.mode == "text":
        if args.text is None:
            parser.error("--mode text requires --text")
        module.replace_text(args.point, args.text)
        action = f"module.replace_text({args.point!r}, {args.text!r})"
    else:
        module.replace(args.point).call_original()
        action = f"module.replace({args.point!r}).call_original()"
    module.emit_c(profile["named_hooks"])
    source = (
        f"from veposed import Module\n\nmodule = Module({args.id!r}, {args.name!r})\n{action}\n"
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as destination:
        destination.write(source)
    print(args.out.resolve())


if __name__ == "__main__":
    main()
