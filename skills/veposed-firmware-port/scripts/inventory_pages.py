#!/usr/bin/env python3
"""Inventory candidate p67cn page/app descriptors in verified startup data.

The patterns are specific to this firmware. Output is a research index, not a
proof that candidates are registered or that page semantics are understood.
"""

import argparse
import json
from pathlib import Path
import re
import struct
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--firmware", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.repo.resolve() / "tools"))
    from firmware import number, verify

    profile = json.loads(args.profile.read_text())
    if profile["target"] != "xiaomi-band-10-pro-3.101.043":
        raise ValueError("descriptor patterns are specific to p67cn 3.101.043")
    ap, _ = verify(args.firmware, profile)
    mapping = next(m for m in profile["mappings"] if m["name"] == "startup-data")
    start = number(mapping["file_offset"])
    end = start + number(mapping["length"])
    runtime = number(mapping["execute"])
    flash = next(m for m in profile["mappings"] if m["name"] == "flash-xip")
    execute = number(flash["execute"])
    flash_end = execute + number(flash["length"])
    data_alias = execute + 0x20000000

    def string(pointer, pattern):
        pos = pointer - data_alias
        if not 0 <= pos < len(ap):
            return None
        value = ap[pos : min(pos + 100, len(ap))].split(b"\0", 1)[0]
        if not re.fullmatch(pattern, value):
            return None
        return value.decode("ascii")

    apps, pages = [], []
    for offset in range(start, end - 63, 4):
        words = struct.unpack_from("<16I", ap, offset)
        app_id = struct.unpack_from("<H", ap, offset + 16)[0]
        package = string(words[2], rb"(?:com|org)\.[a-zA-Z0-9_.-]{3,90}")
        if app_id <= 512 and package:
            apps.append({"app_id": app_id, "package": package,
                         "address": hex(runtime + offset - start), "file_offset": hex(offset)})

    by_id = {}
    for app in apps:
        by_id.setdefault(app["app_id"], []).append(app["package"])
    for offset in range(start, end - 115, 4):
        words = struct.unpack_from("<29I", ap, offset)
        page_id, app_id = struct.unpack_from("<HH", ap, offset + 20)
        name = string(words[4], rb"[a-zA-Z][a-zA-Z0-9_.-]{0,63}")
        create = words[19]
        if not (words[0] in (0, 0x200EB708) and words[11] in (0, 0x200EB684)
                and page_id <= 512 and app_id <= 512 and name
                and create & 1 and execute <= (create & ~1) < flash_end):
            continue
        packages = by_id.get(app_id, [])
        pages.append({"app_id": app_id, "page_id": page_id, "name": name,
                      "package_candidate": packages[0] if len(packages) == 1 else None,
                      "address": hex(runtime + offset - start), "file_offset": hex(offset),
                      "create": hex(create)})
    report = {"target": profile["target"], "ap_sha256": profile["ap_sha256"],
              "status": "heuristic candidates; not independently verified",
              "scope": "initialized SRAM copied from the exact AP; fixed p67cn descriptor patterns",
              "limitations": "Names, IDs, packages and create pointers are candidate associations; independently verify each lifecycle and runtime registration. Only descriptors with an XIP create callback and matching patterns are included. This is not a complete inventory.",
              "applications": apps, "pages": pages}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    if args.markdown:
        lines = ["# 小米手环 10 Pro / 3.101.043 页面描述符候选目录", "",
                 "以下为启动数据的启发式扫描结果，名称、ID 与包名关联尚需逐条验证；不是设备实测结果。仅列出符合当前扫描规则的候选，不代表完整目录。已交叉核对的页面见[导航页面 ID 对照表](navigation-page-ids-xiaomi-band-10-pro-3.101.043.md)。", "",
                 "| 应用 ID | 包名候选 | 页面 ID | 名称候选 | 描述符 RAM 地址 | 创建函数 |",
                 "| --- | --- | --- | --- | --- | --- |"]
        for page in sorted(pages, key=lambda p: (p["app_id"], p["page_id"], p["address"])):
            package = f'`{page["package_candidate"]}`' if page["package_candidate"] else "待确认"
            lines.append(f'| `0x{page["app_id"]:02x}` | {package} | `0x{page["page_id"]:02x}` | `{page["name"]}` | `{page["address"]}` | `{page["create"]}` |')
        lines.extend(["", "提取规则、文件偏移和原始候选清单见 [navigation-page-candidates-043.json](../evidence/navigation-page-candidates-043.json)。"])
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text("\n".join(lines) + "\n")
    print(json.dumps({"applications": len(apps), "pages": len(pages),
                      "out": str(args.out), "markdown": str(args.markdown) if args.markdown else None}))


if __name__ == "__main__":
    main()
