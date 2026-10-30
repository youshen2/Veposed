#!/usr/bin/env python3
"""Exercise the public C ABI across process restarts using a real fsynced journal."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
subprocess.run(["cargo", "build", "-p", "veposed-runtime"], cwd=root, check=True)
target = Path(os.environ.get("CARGO_TARGET_DIR", root / "target"))
output = root / "build/recovery-probe"
output.parent.mkdir(exist_ok=True)
command = [
    os.environ.get("CC", "cc"),
    "-std=c11",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-I",
    str(root / "include"),
    str(root / "examples/host/recovery_probe.c"),
    str(target / "debug/libveposed_runtime.a"),
    "-o",
    str(output),
]
if sys.platform.startswith("linux"):
    command.extend(["-ldl", "-lpthread", "-lm"])
subprocess.run(command, cwd=root, check=True)


def probe(journal, mode):
    result = subprocess.run(
        [str(output), str(journal), mode], check=True, capture_output=True, text=True, timeout=10
    )
    return json.loads(result.stdout) if result.stdout.startswith("{") else None


with tempfile.TemporaryDirectory() as directory:
    folder = Path(directory)
    journal = folder / "crash.bin"
    probe(journal, "arm")
    first = probe(journal, "safe")
    second = probe(journal, "safe")
    assert first["failures"] == second["failures"] == 1
    probe(journal, "reset")
    probe(journal, "idle")
    probe(journal, "clean")
    probe(journal, "idle")
    print("crash -> safe boot -> stays safe -> explicit reset -> clean reboot: PASS")

    journal = folder / "failed-hook.bin"
    probe(journal, "hook-fail")
    assert probe(journal, "safe")["failures"] == 1
    print("failed hook -> restore existing hooks -> quarantine next boot: PASS")

    journal = folder / "torn.bin"
    journal.write_bytes(b"X" * 32)
    assert probe(journal, "safe")["reason"] == 5
    journal.write_bytes(b"X")
    assert probe(journal, "safe")["reason"] == 4
    probe(journal, "reset")
    probe(journal, "idle")
    journal.write_bytes(b"X" * 64)
    probe(journal, "safe")
    probe(journal, "reset")
    assert journal.stat().st_size == 32
    probe(journal, "idle")
    print("corrupt / truncated journal -> refuse injection: PASS")

    probe(folder / "storage.bin", "storage-fail")
    print("journal sync failure -> target remains untouched: PASS")
    probe(folder / "busy.bin", "busy-recovery")
    probe(folder / "busy.bin", "safe")
    print("recovery during callback -> bypass future callbacks -> deferred restore: PASS")
