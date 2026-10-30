#!/usr/bin/env python3
"""Build an analysis ELF from explicitly recovered firmware memory mappings."""

import argparse
import hashlib
import json
from pathlib import Path
import struct


def number(value):
    return int(value, 0) if isinstance(value, str) else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ap", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--flash-data-alias", type=lambda value: int(value, 0))
    args = parser.parse_args()
    ap = args.ap.read_bytes()
    profile = json.loads(args.profile.read_text())
    if hashlib.sha256(ap).hexdigest() != profile["ap_sha256"]:
        raise ValueError("AP hash differs from the supplied mapping profile")
    segments = []
    for mapping in profile["mappings"]:
        offset, length = number(mapping["file_offset"]), number(mapping["length"])
        if length <= 0 or offset < 0 or offset + length > len(ap):
            raise ValueError(f"Invalid file range: {mapping['name']}")
        segments.append((number(mapping["execute"]), offset, length, 5))
        if mapping["writable"]:
            segments.append((number(mapping["write"]), offset, length, 6))
        elif args.flash_data_alias is not None:
            segments.append((args.flash_data_alias + offset, offset, length, 4))
    for index, (address, _, length, _) in enumerate(segments):
        if address < 0 or address + length > 2**32:
            raise ValueError("Segment is outside the 32-bit address space")
        for other, _, other_length, _ in segments[:index]:
            if max(address, other) < min(address + length, other + other_length):
                raise ValueError("Virtual segments overlap; correct the supplied mappings")
    header_size, ph_size = 52, 32
    data_start = (header_size + len(segments) * ph_size + 4095) & ~4095
    ident = b"\x7fELF\x01\x01\x01" + bytes(9)
    header = struct.pack(
        "<16sHHIIIIIHHHHHH",
        ident,
        2,
        40,
        1,
        0,
        header_size,
        0,
        0x05000000,
        header_size,
        ph_size,
        len(segments),
        0,
        0,
        0,
    )
    program_headers = b"".join(
        struct.pack("<IIIIIIII", 1, data_start + offset, address, address, length, length, flags, 1)
        for address, offset, length, flags in segments
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("xb") as destination:
        destination.write(header + program_headers)
        destination.write(bytes(data_start - header_size - len(program_headers)))
        destination.write(ap)
    print(
        json.dumps(
            {
                "analysis_elf": str(args.out.resolve()),
                "segments": len(segments),
                "ap_sha256": profile["ap_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
