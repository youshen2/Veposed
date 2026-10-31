#!/usr/bin/env python3
"""Build and inspect an exact-firmware, zero-import ARM loadable module."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from firmware import PROFILE, generate_header, verify
from thumb_check import verify_runtime_profile
from elf import inspect
from build_device_support import executable


def command(*args):
    subprocess.run([str(a) for a in args], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware", type=Path)
    parser.add_argument(
        "--image-probe",
        action="store_true",
        help="Build the typed PSRAM image-create observation hook",
    )
    parser.add_argument(
        "--publisher", type=Path, help="Board cache-coherency C source exporting vep_board_publish"
    )
    parser.add_argument(
        "--manager", action="store_true", help="Build the native Manager and p67cn cache publisher"
    )
    parser.add_argument("--profile", type=Path, default=PROFILE)
    args = parser.parse_args()
    if args.image_probe and not args.publisher:
        parser.error(
            "--image-probe requires --publisher implementing PSRAM instruction/data cache synchronization"
        )
    if args.image_probe and args.manager:
        parser.error("Select --image-probe or --manager")
    if args.manager and args.publisher is None:
        args.publisher = ROOT / "platform/p67cn/publisher.c"
    profile = json.loads(args.profile.read_text())
    _, firmware_report = verify(args.firmware, profile)
    firmware_report["inline_relocations_verified"] = verify_runtime_profile(profile)
    variant = "manager" if args.manager else "image-probe" if args.image_probe else "self-test"
    output = ROOT / "build" / profile["target"] / variant
    output.mkdir(parents=True, exist_ok=True)
    generate_header(profile, output / "veposed_target.h")
    command(
        "cargo", "build", "--release", "-p", "veposed-runtime", "--target", profile["rust_target"]
    )
    cc, ld, objcopy = (executable(n) for n in ("clang", "ld.lld", "llvm-objcopy"))
    flags = [
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
        ROOT / "include",
        "-I",
        output,
    ]
    if args.image_probe:
        flags += ["-DVEP_IMAGE_PROBE", "-DVEP_BOARD_PUBLISHER"]
    elif args.publisher:
        flags += ["-DVEP_BOARD_PUBLISHER"]
    if args.manager:
        flags += ["-DVEP_NATIVE_MANAGER"]
    sources = [
        ROOT / "platform/p67cn/runtime.c",
        ROOT / "platform/aeabi.c",
        ROOT / "platform/p67cn/recovery_store.c",
    ]
    if args.publisher:
        sources.append(args.publisher.resolve())
    if args.manager:
        sources.append(ROOT / "manager/native.c")
    objects = []
    for i, source in enumerate(sources):
        obj = output / f"module-{i}.o"
        command(cc, *flags, "-c", source, "-o", obj)
        objects.append(obj)
    target_root = Path(os.environ.get("CARGO_TARGET_DIR", ROOT / "target"))
    library = target_root / profile["rust_target"] / "release/libveposed_runtime.a"
    unstripped = output / "veposed.unstripped.elf"
    artifact = output / "veposed.elf"
    api = [
        "init",
        "register",
        "replace",
        "attach",
        "detach",
        "set_enabled",
        "unregister",
        "get_api",
        "recovery_status",
        "enter_safe_mode",
        "recovery_reset",
        "list_modules",
        "attach_named",
        "hook_text",
        "list_hook_points",
        "call_original",
        "call_named",
    ]
    roots = [flag for name in api for flag in ("-u", f"veposed_{name}")]
    command(
        ld,
        "-r",
        "--gc-sections",
        *roots,
        "-T",
        ROOT / "scripts/module.ld",
        "-o",
        unstripped,
        *objects,
        library,
    )
    command(
        objcopy,
        "--strip-debug",
        "--strip-unneeded",
        "--remove-section=.llvmbc",
        "--remove-section=.llvmcmd",
        unstripped,
        artifact,
    )
    blob = artifact.read_bytes()
    result = inspect(blob)
    client_object = output / "client.o"
    client_artifact = output / "client.elf"
    command(cc, *flags, "-c", ROOT / "examples/device/client.c", "-o", client_object)
    command(
        ld,
        "-r",
        "--gc-sections",
        "-T",
        ROOT / "scripts/module.ld",
        "-o",
        client_artifact,
        client_object,
    )
    client_report = inspect(client_artifact.read_bytes(), required_exports=())
    result["client"] = {
        "artifact": str(client_artifact),
        "file_bytes": client_report["file_bytes"],
        "sha256": hashlib.sha256(client_artifact.read_bytes()).hexdigest(),
        "undefined_symbols": client_report["undefined_symbols"],
    }
    result.update(
        {
            "target": profile["target"],
            "variant": variant,
            "sha256": hashlib.sha256(blob).hexdigest(),
            "firmware": firmware_report,
            "device_validation": "pending",
            "artifact": str(artifact),
        }
    )
    (output / "report.json").write_text(json.dumps(result, indent=2) + "\n")
    shutil.copyfile(ROOT / "installer/bootstrap.lua", output / "bootstrap.lua")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key not in ("exports", "firmware")},
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"build-device: {error}", file=sys.stderr)
        sys.exit(1)
