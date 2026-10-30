#!/usr/bin/env python3
"""Exercise native manager events with a host model of the firmware widgets."""

import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="veposed-manager-") as work:
    work = Path(work)
    # Firmware bindings are supplied by tests/manager_ui.c; production uses
    # the generated exact-target header and validates its 32-bit ABI at build.
    (work / "veposed_target.h").write_text("/* Host widget bindings. */\n")
    binary = work / "manager-ui"
    subprocess.run(
        [
            os.environ.get("CC", "cc"),
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(root / "include"),
            "-I",
            str(work),
            str(root / "tests/manager_ui.c"),
            "-o",
            str(binary),
        ],
        check=True,
    )
    subprocess.run([str(binary)], check=True)
