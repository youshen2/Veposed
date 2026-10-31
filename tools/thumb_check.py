"""Check profile inline entries against the actual runtime Thumb planner."""

import json
from pathlib import Path
import subprocess
import tempfile

from firmware import number, resolve

ROOT = Path(__file__).resolve().parents[1]


def verify_runtime_profile(profile):
    hooks = [(name, hook) for name, hook in profile["hooks"].items()
             if hook.get("kind", "inline") == "inline"]
    rows = []
    for index, (_, hook) in enumerate(hooks):
        entry = int(hook["address"], 0) if isinstance(hook["address"], str) else hook["address"]
        code = bytes.fromhex(hook["expected"])
        if not 0 < entry < 2**32 or len(code) != 16:
            raise ValueError("invalid inline address or signature")
        rows.append(f"({index}usize, {entry}u32, {list(code)!r})")
    checks, labels = [], []
    for name, hook in profile["hooks"].items():
        address = number(hook["address"])
        if hook.get("kind", "inline") == "pointer":
            condition = f"memory_map::writable({address}usize, 4)"
        else:
            mapped = resolve(profile, address)
            write = number(mapped["write"])
            condition = (f"memory_map::code({address & ~1}usize, 16)"
                         f".is_some_and(|m| m.write == {write}usize)")
        labels.append(f"{name}: target is outside the runtime memory policy")
        checks.append(f'if !({condition}) {{ eprintln!("M {len(labels)-1}"); std::process::exit(1); }}')
    slots = ("subject_slot", "quiescent_slot", "quiescent_slot2", "active_slot", "active_slot2")
    seen_slots = set()
    for name, point in profile.get("named_hooks", {}).items():
        for key in slots:
            value = point.get(key, point.get({"subject_slot": "os_label_slot",
                                               "quiescent_slot": "about_root"}.get(key, ""), 0))
            slot = number(value)
            if slot and slot not in seen_slots:
                seen_slots.add(slot)
                labels.append(f"{name}: {key} is outside the runtime memory policy")
                checks.append(f'if !memory_map::writable({slot}usize, 4) '
                              f'{{ eprintln!("M {len(labels)-1}"); std::process::exit(1); }}')
    path = json.dumps(str(ROOT / "crates/veposed-core/src/thumb.rs"))
    memory_path = json.dumps(str(ROOT / "crates/veposed-runtime/src/memory_map.rs"))
    source = f'''#[derive(Debug)] pub enum Error {{ Argument, Unsupported }}
pub type Result<T> = core::result::Result<T, Error>;
extern crate self as veposed_core;
pub struct CodeMemory {{ pub execute: usize, pub write: usize }}
#[path = {path}] mod thumb;
#[path = {memory_path}] mod memory_map;
fn main() {{
    {''.join(checks)}
    let hooks: &[(usize, u32, [u8; 16])] = &[{','.join(rows)}];
    for (index, entry, code) in hooks {{
        if let Err(error) = thumb::plan(*entry, 0x3c280001, 0x3c271000, *code) {{
            eprintln!("T {{index}} {{error:?}}"); std::process::exit(1);
        }}
    }}
}}
'''
    with tempfile.TemporaryDirectory(prefix="veposed-thumb-") as directory:
        root = Path(directory)
        src, exe = root / "check.rs", root / "check"
        src.write_text(source)
        try:
            subprocess.run(["rustc", "--edition", "2024", "--cap-lints", "allow", str(src),
                            "-o", str(exe)], check=True, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise ValueError("rustc is required to verify inline relocations") from exc
        except subprocess.CalledProcessError as exc:
            raise ValueError("cannot build Thumb relocation checker: " + exc.stderr.strip()) from exc
        result = subprocess.run([str(exe)], capture_output=True, text=True)
    if result.returncode:
        parts = result.stderr.strip().split(maxsplit=2)
        if len(parts) >= 2 and parts[1].isdigit():
            index = int(parts[1])
            if parts[0] == "M" and index < len(labels):
                raise ValueError(labels[index])
            if parts[0] == "T" and index < len(hooks):
                raise ValueError(f"{hooks[index][0]}: unsupported Thumb relocation ({parts[2]})")
        raise ValueError("Thumb relocation checker failed: " + result.stderr.strip())
    return len(hooks)
