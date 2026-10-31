"""Compile the host Python module DSL into a zero-import ARM ELF and install face."""

import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdk"))
from veposed import Module
from firmware import PROFILE, generate_header, verify
from thumb_check import verify_runtime_profile
from elf import inspect
from face import pack, unpack, preview, module_face_id
from build_device_support import executable


def lua(value):
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "{" + ",".join(map(lua, value)) + "}"
    return "{" + ",".join(key + "=" + lua(item) for key, item in value.items()) + "}"


def compile_module(source, firmware, output, *, face=True, profile_path=PROFILE):
    source, firmware, output = (
        Path(source).resolve(),
        Path(firmware).resolve(),
        Path(output).resolve(),
    )
    profile = json.loads(Path(profile_path).read_text())
    _, verified = verify(firmware, profile)
    verified["inline_relocations_verified"] = verify_runtime_profile(profile)
    namespace = runpy.run_path(str(source))
    module = namespace.get("module")
    if not isinstance(module, Module):
        raise ValueError("Python file must define module = Module(...)")
    if not module.status_path.startswith("/data/") or any(
        c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_.-"
        for c in module.status_path
    ):
        raise ValueError("status path must be a plain /data/ path")
    output.mkdir(parents=True, exist_ok=True)
    generated = output / "module.c"
    generated.write_text(module.emit_c(profile["named_hooks"]))
    generate_header(profile, output / "veposed_target.h")
    cc, ld, objcopy = (executable(name) for name in ("clang", "ld.lld", "llvm-objcopy"))
    obj = output / "module.o"
    artifact = output / "module.elf"
    subprocess.run(
        [
            cc,
            "--target=arm-none-eabi",
            f"-mcpu={profile['cpu']}",
            "-mthumb",
            "-mfloat-abi=soft",
            "-ffreestanding",
            "-fno-builtin",
            "-fno-stack-protector",
            "-fno-unwind-tables",
            "-fno-asynchronous-unwind-tables",
            "-Os",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(ROOT / "include"),
            "-I",
            str(output),
            "-c",
            str(generated),
            "-o",
            str(obj),
        ],
        check=True,
    )
    subprocess.run(
        [
            ld,
            "-r",
            "--gc-sections",
            "-u",
            "vep_module_status",
            "-T",
            str(ROOT / "scripts/module.ld"),
            "-o",
            str(artifact),
            str(obj),
        ],
        check=True,
    )
    subprocess.run([objcopy, "--strip-debug", "--strip-unneeded", str(artifact)], check=True)
    blob = artifact.read_bytes()
    report = inspect(blob, required_exports=("vep_module_status",))
    manifest = {
        "id": module.id,
        "name": module.name,
        "version": module.version,
        "abi": 4,
        "target": profile["target"],
        "default_enabled": False,
        "binary": artifact.name,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "hooks": [rule[0] if isinstance(rule, tuple) else rule.point for rule in module.rules],
        "device_validation": "pending",
    }
    report.update({"firmware": verified, "device_validation": "pending"})
    (output / "build-report.json").write_text(json.dumps(report, indent=2) + "\n")
    if face:
        from build_suite_support import icon_bytes

        identity = hashlib.sha256(module.id.encode()).hexdigest()[:16]
        config = {
            "name": module.name if module.name.isascii() else module.id,
            "size": len(blob),
            "destination": "/data/veposed/" + identity + ".elf",
            "loader_name": "vep_" + identity,
            "status": module.status_path,
        }
        files = {
            "lua/main.lua": (ROOT / "installer/module.lua").read_bytes(),
            "lua/module.bin": blob,
            "lua/module_config.lua": ("return " + lua(config) + "\n").encode(),
        }
        # Keep framework/module face IDs separate; reproducible per module ID.
        face_id = module_face_id(module.id)
        face_path = output / "module.face"
        face_path.write_bytes(
            pack(files, preview(icon_bytes(), "MODULE"), "Veposed Module", face_id)
        )
        checked = unpack(face_path.read_bytes())
        if checked["files"] != files:
            raise ValueError("face resource round-trip failed")
        manifest["face"] = face_path.name
        manifest["face_id"] = face_id
        manifest["face_sha256"] = hashlib.sha256(face_path.read_bytes()).hexdigest()
    (output / "module.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest
