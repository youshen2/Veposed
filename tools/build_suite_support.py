"""Shared artwork, source staging and archive helpers for release bundles."""

import hashlib
from pathlib import Path
import shutil
import struct
import zipfile

SOURCE_DIRS = (
    "assets",
    "crates",
    "docs",
    "evidence",
    "examples",
    "include",
    "installer",
    "licenses",
    "manager",
    "modules",
    "platform",
    "scripts",
    "sdk",
    "skills",
    "targets",
    "tests",
    "tools",
)
SOURCE_FILES = (
    ".editorconfig",
    ".gitignore",
    "Cargo.lock",
    "Cargo.toml",
    "LICENSE",
    "Makefile",
    "NOTICE.md",
    "README.md",
    "pyproject.toml",
    "requirements-dev.txt",
    "vep.py",
)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def copy_sources(root, destination):
    destination.mkdir(parents=True, exist_ok=True)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
    for name in SOURCE_DIRS:
        source = root / name
        if source.exists():
            shutil.copytree(source, destination / name, ignore=ignore)
    for name in SOURCE_FILES:
        shutil.copyfile(root / name, destination / name)


def archive_tree(folder, output):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(folder.parent))


def archive_skills(skills, output):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skills.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                archive.write(path, path.relative_to(skills))


def icon_bytes(size=64):
    def distance(x, y, ax, ay, bx, by):
        t = max(
            0,
            min(
                1, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)
            ),
        )
        return ((x - ax - t * (bx - ax)) ** 2 + (y - ay - t * (by - ay)) ** 2) ** 0.5

    pixels = bytearray()
    for y in range(size):
        for x in range(size):
            totals = [0, 0, 0, 0]
            for dy in (0.125, 0.375, 0.625, 0.875):
                for dx in (0.125, 0.375, 0.625, 0.875):
                    px, py = x + dx, y + dy
                    cx, cy = max(15, min(49, px)), max(15, min(49, py))
                    inside = (px - cx) ** 2 + (py - cy) ** 2 <= 225
                    white = (
                        min(distance(px, py, 18, 18, 32, 47), distance(px, py, 32, 47, 47, 18))
                        <= 3.5
                    )
                    color = (
                        (255, 255, 255, 255)
                        if white
                        else (217, 87, 101, 255)
                        if inside
                        else (0, 0, 0, 0)
                    )
                    totals = [a + b for a, b in zip(totals, color)]
            samples = totals[3] / 255
            pixels.extend(
                [round(value / samples) if samples else 0 for value in totals[:3]]
                + [round(totals[3] / 16)]
            )
    return struct.pack("<BBHHHHH", 0x19, 0x10, 0, size, size, size * 4, 0) + pixels
