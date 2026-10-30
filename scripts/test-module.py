#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "tools"))
from firmware import generate_header, PROFILE

output = root / "build/module-test"
output.mkdir(parents=True, exist_ok=True)
generate_header(json.loads(PROFILE.read_text()), output / "veposed_target.h")
subprocess.run(
    [
        "cc",
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-DVEP_PUBLISH_TEST",
        "-I",
        str(root / "include"),
        "-I",
        str(root / "modules/os_version"),
        "-I",
        str(output),
        str(root / "tests/module_scope.c"),
        str(root / "platform/p67cn/publisher.c"),
        "-o",
        str(output / "scope"),
    ],
    check=True,
)
subprocess.run([str(output / "scope")], check=True)
