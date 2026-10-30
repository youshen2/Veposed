"""Small ELF32 relocatable verifier for the exact p67cn stock modlib profile."""

import struct

ALLOWED_RELOCATIONS = {0, 2, 10, 23, 30, 38, 42, 47, 48}


def inspect(
    data,
    required_exports=("veposed_init", "veposed_replace", "veposed_attach", "veposed_unregister"),
):
    if data[:7] != b"\x7fELF\x01\x01\x01" or len(data) < 52:
        raise ValueError("Expected ELF32 little-endian")
    kind, machine = struct.unpack_from("<HH", data, 16)
    if (kind, machine) != (1, 40):
        raise ValueError("Expected ARM ET_REL")
    flags = struct.unpack_from("<I", data, 36)[0]
    if flags & 0x400:
        raise ValueError("Hard-float ABI is incompatible with this target")
    shoff = struct.unpack_from("<I", data, 32)[0]
    entsize, count, names_index = struct.unpack_from("<HHH", data, 46)
    if entsize != 40 or not count or shoff + count * entsize > len(data) or names_index >= count:
        raise ValueError("Invalid section table")
    headers = [struct.unpack_from("<10I", data, shoff + i * entsize) for i in range(count)]

    def payload(section):
        offset, size = section[4:6]
        if offset + size > len(data):
            raise ValueError("Section exceeds file size")
        return data[offset : offset + size]

    def string(table, offset):
        if offset >= len(table):
            raise ValueError("Invalid string offset")
        end = table.find(b"\0", offset)
        if end < 0:
            raise ValueError("Unterminated ELF string")
        return table[offset:end].decode("utf-8")

    names = payload(headers[names_index])
    relocations, exports, undefined = set(), set(), []
    allocated = 0
    sections = []
    for section in headers:
        name = string(names, section[0])
        sections.append(name)
        if section[2] & 2:
            allocated += section[5]
        if section[1] == 9:  # SHT_REL
            if section[9] != 8 or section[5] % 8:
                raise ValueError("Malformed relocation section")
            for _, info in struct.iter_unpack("<II", payload(section)):
                relocations.add(info & 0xFF)
        if section[1] == 4:
            raise ValueError("SHT_RELA is unsupported by the target loader")
        if section[1] == 2:
            if section[9] != 16 or section[5] % 16 or section[6] >= count:
                raise ValueError("Malformed symbol table")
            strings = payload(headers[section[6]])
            for offset, _, _, info, _, shndx in struct.iter_unpack("<IIIBBH", payload(section)):
                name = string(strings, offset)
                if name and shndx == 0:
                    undefined.append(name)
                if name and shndx and info >> 4 == 1:
                    exports.add(name)
    if undefined:
        raise ValueError("Unresolved imports: " + ", ".join(sorted(set(undefined))))
    if relocations - ALLOWED_RELOCATIONS:
        raise ValueError(
            f"Unsupported ARM relocations: {sorted(relocations - ALLOWED_RELOCATIONS)}"
        )
    if ".init_array" not in sections or ".fini_array" not in sections:
        raise ValueError("Module must contain init/fini arrays")
    for name in required_exports:
        if name not in exports:
            raise ValueError(f"Missing runtime export: {name}")
    return {
        "elf": "ARM ELF32 ET_REL",
        "float_abi": "soft",
        "file_bytes": len(data),
        "resident_section_bytes": allocated,
        "relocations": sorted(relocations),
        "undefined_symbols": undefined,
        "exports": sorted(exports),
    }
