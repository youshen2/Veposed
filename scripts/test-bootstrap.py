#!/usr/bin/env python3
"""Run the real Lua bootstrap against temporary storage and a mocked insmod."""

import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--lua", default="lua")
args = parser.parse_args()
bootstrap = Path(__file__).resolve().parents[1] / "installer/bootstrap.lua"
harness_source = r"""
local root, bootstrap, scenario = arg[1], arg[2], arg[3]
local real_open = io.open
io.open = function(path, mode)
    if scenario == "read-error" and mode == "rb" then return nil, "permission denied", 13 end
    if scenario == "write-error" and mode == "wb" then return nil, "disk full", 28 end
    local file, message, code = real_open(root .. path, mode)
    if not file or (scenario ~= "io-no-return" and scenario ~= "flush-error") then return file, message, code end
    return {
        read=function(_,...) return file:read(...) end,
        write=function(_,...) return file:write(...) end,
        flush=function()
            file:flush()
            if scenario=="flush-error" then return nil,"I/O error",5 end
        end,
        close=function() file:close() end,
    }
end
os.execute = function(command)
    assert(command == "insmod /data/veposed/veposed.elf veposed")
    local log = assert(real_open(root .. "/calls", "a"))
    log:write("insmod\n"); log:close()
    if scenario == "crash" then error("simulated native constructor fault") end
    if scenario == "load-error" then return nil, "exit", 1 end
    return true, "exit", 0
end
dofile(bootstrap)
"""

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    harness = root / "harness.lua"
    harness.write_text(harness_source)

    def run(case, scenario="ok", success=True):
        folder = root / case
        (folder / "data").mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [args.lua, str(harness), str(folder), str(bootstrap), scenario],
            text=True,
            capture_output=True,
            timeout=10,
        )
        assert (result.returncode == 0) == success, result.stderr
        log = folder / "calls"
        return folder, log.read_text().count("insmod") if log.exists() else 0

    folder, calls = run("normal")
    assert calls == 1
    assert run("normal")[1] == 1
    assert (folder / "data/veposed-load.pending").exists()
    print("successful load leaves a one-shot latch; next boot skips native load: PASS")
    for scenario in ("crash", "load-error"):
        _, calls = run(scenario, scenario, success=scenario != "crash")
        assert calls == 1
        assert run(scenario)[1] == 1
    print("constructor crash / failed insmod cannot cause repeated autoload: PASS")
    _, calls = run("io-no-return", "io-no-return")
    assert calls == 1
    print("no-value flush/close succeeds after verifying the persistent latch: PASS")
    for scenario in ("read-error", "write-error", "flush-error"):
        assert run(scenario, scenario)[1] == 0
    folder = root / "disabled"
    (folder / "data").mkdir(parents=True)
    (folder / "data/veposed.disable").write_text("1")
    assert run("disabled")[1] == 0
    print("I/O failure and external disable marker block native load: PASS")
