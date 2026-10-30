#!/usr/bin/env python3
"""Link a C client to the real Rust static library and exercise the public ABI."""

import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
subprocess.run(["cargo", "build", "-p", "veposed-runtime"], cwd=root, check=True)
target = Path(os.environ.get("CARGO_TARGET_DIR", root / "target"))
output = root / "build/host-smoke"
output.parent.mkdir(exist_ok=True)
command = [
    os.environ.get("CC", "cc"),
    "-std=c11",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-I",
    str(root / "include"),
    str(root / "examples/host/main.c"),
    str(target / "debug/libveposed_runtime.a"),
    "-o",
    str(output),
]
if sys.platform.startswith("linux"):
    command.extend(["-ldl", "-lpthread", "-lm"])
subprocess.run(command, cwd=root, check=True)
subprocess.run([str(output)], cwd=root, check=True)

command[command.index(str(root / "examples/host/main.c"))] = str(root / "tests/named_api.c")
command[command.index(str(output))] = str(output) + "-named"
subprocess.run(command, cwd=root, check=True)
subprocess.run([str(output) + "-named"], cwd=root, check=True)
