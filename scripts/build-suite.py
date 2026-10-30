#!/usr/bin/env python3
"""Build the framework/Manager face and its source, SDK and skill bundles."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_suite_support import archive_skills, archive_tree, copy_sources, digest, icon_bytes
from face import INSTALLER_FACE_ID, pack, preview, unpack
from firmware import PROFILE
from module_builder import lua


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware", type=Path)
    parser.add_argument("--profile", type=Path, default=PROFILE)
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text())
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/build-device.py"),
            str(args.firmware.resolve()),
            "--manager",
            "--profile",
            str(args.profile.resolve()),
        ],
        cwd=ROOT,
        check=True,
    )
    built = ROOT / "build" / profile["target"] / "manager"
    release_name = "Veposed-" + profile["target"].removeprefix("xiaomi-band-").replace(
        "10-pro-", "10Pro-"
    )
    folder = ROOT / "dist" / release_name
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    shutil.copyfile(built / "veposed.elf", folder / "veposed.elf")
    (folder / "manager_icon.bin").write_bytes(icon_bytes())
    resources = [
        {
            "source": "veposed.elf",
            "destination": "/data/veposed/veposed.elf",
            "size": (folder / "veposed.elf").stat().st_size,
            "elf": True,
        },
        {
            "source": "manager_icon.bin",
            "destination": "/data/veposed/manager_icon.bin",
            "size": (folder / "manager_icon.bin").stat().st_size,
            "elf": False,
        },
    ]
    for name in ("main.lua", "loader.lua", "bootstrap.lua", "recovery.lua"):
        shutil.copyfile(ROOT / "installer" / name, folder / name)
    shutil.copyfile(ROOT / "installer/README.md", folder / "README.md")
    for name in ("LICENSE", "NOTICE.md"):
        shutil.copyfile(ROOT / name, folder / name)
    shutil.copytree(ROOT / "licenses", folder / "licenses")
    shutil.copyfile(built / "report.json", folder / "build-report.json")
    shutil.copyfile(args.profile, folder / "target.json")
    bundle = {"abi": 4, "firmware": profile["version"], "resources": resources}
    (folder / "bundle.lua").write_text("return " + lua(bundle) + "\n")
    files = {
        "lua/" + name: (folder / name).read_bytes()
        for name in ("main.lua", "loader.lua", "bootstrap.lua", "recovery.lua")
    }
    face_resources = []
    for entry in resources:
        item = dict(entry)
        item["source"] = "veposed.bin" if entry["elf"] else entry["source"]
        files["lua/" + item["source"]] = (folder / entry["source"]).read_bytes()
        face_resources.append(item)
    files["lua/bundle.lua"] = (
        "return " + lua(dict(bundle, resources=face_resources)) + "\n"
    ).encode()
    install_face = folder / "installer.face"
    install_face.write_bytes(pack(files, preview(icon_bytes()), "Veposed", INSTALLER_FACE_ID))
    if unpack(install_face.read_bytes())["files"] != files:
        raise ValueError("installer face resource mismatch")
    (folder / "face-manifest.json").write_text(
        json.dumps(
            {
                "format": "Vela Lua face",
                "face_id": INSTALLER_FACE_ID,
                "entrypoint": "lua/main.lua",
                "width": 336,
                "height": 480,
                "components": ["runtime", "native-manager"],
                "files": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
                "sha256": digest(install_face),
            },
            indent=2,
        )
        + "\n"
    )
    copy_sources(ROOT, folder / "source")
    (folder / "source/generated").mkdir()
    shutil.copyfile(built / "veposed_target.h", folder / "source/generated/veposed_target.h")
    manifest = {
        "name": "Veposed",
        "version": "0.1.0",
        "target": profile["target"],
        "components": ["runtime", "native-manager", "sdk", "development-skills"],
        "manager": "native application, app ID 0xce",
        "device_validation": "pending",
        "files": {
            str(path.relative_to(folder)): digest(path)
            for path in sorted(folder.rglob("*"))
            if path.is_file()
        },
    }
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (folder / "SHA256SUMS").write_text(
        "".join(
            f"{digest(path)}  {path.relative_to(folder)}\n"
            for path in sorted(folder.rglob("*"))
            if path.is_file() and path.name != "SHA256SUMS"
        )
    )
    face_path = Path(str(folder) + ".face")
    shutil.copyfile(install_face, face_path)
    zip_path = Path(str(folder) + ".zip")
    archive_tree(folder, zip_path)
    skills_path = ROOT / "dist/Veposed-Development-Skills.zip"
    archive_skills(ROOT / "skills", skills_path)
    print(
        json.dumps(
            {
                "face": str(face_path),
                "suite": str(zip_path),
                "skills": str(skills_path),
                "suite_sha256": digest(zip_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
