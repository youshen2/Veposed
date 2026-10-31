"""Vela Lua .face container (single screen, 32-bit BGRA preview).

Layout adapted from AIR-pixel/miband11-watchface-maker's documented compiler
format (MIT); see licenses/face-format-MIT.txt. The target preview is 336 x 480 for Band 10 Pro.
"""

from pathlib import PurePosixPath
import struct
import hashlib

MAGIC = bytes.fromhex("5aa53412")
INSTALLER_FACE_ID = "190067000101"
ID_OFFSET = 0x28
ID_FIELD_SIZE = 24
VALID_ID_LENGTHS = (9, 12)


def encode_face_id(face_id):
    encoded = str(face_id).encode("ascii")
    if len(encoded) not in VALID_ID_LENGTHS or not encoded.isalnum():
        raise ValueError("AstroBox face ID must have 9 or 12 ASCII letters/digits")
    return encoded


def module_face_id(module_id):
    # Stable 12-digit local ID; the native module's package ID stays separate.
    value = int.from_bytes(hashlib.sha256(module_id.encode()).digest()[:8], "big")
    return f"19{value % 10**10:010d}"


def pack(files, preview, title, face_id, width=336, height=480):
    encoded_id = encode_face_id(face_id)
    encoded_title = title.encode("ascii")
    if len(encoded_title) > 15:
        raise ValueError("ASCII title must fit 15 bytes")
    if len(preview) != width * height * 4:
        raise ValueError("invalid BGRA preview size")
    files = sorted(files.items())
    if not any(name == "lua/main.lua" for name, _ in files):
        raise ValueError("missing lua/main.lua")
    if not 1 <= len(files) <= 65535:
        raise ValueError("invalid resource count")
    index_end = 272 + 16 * len(files)
    offset = index_end + 16
    entries, payload = [], bytearray()
    for i, (name, data) in enumerate(files):
        path = PurePosixPath(name)
        name = name.encode("ascii")
        if path.parts[0] != "lua" or ".." in path.parts or len(name) > 255 or len(data) >= 2**24:
            raise ValueError("invalid watchface resource")
        entry = len(data).to_bytes(3, "little") + bytes([len(name)]) + bytes(16) + name + data
        entries.append(struct.pack("<HHIII", i, 0x0500, 0, offset, len(entry)))
        padding = bytes((-len(entry)) % 4)
        payload += entry + padding
        offset += len(entry) + len(padding)
    header = bytearray(172)
    header[:4] = MAGIC
    header[5] = len(encoded_id)
    struct.pack_into("<I", header, 16, 0x800)
    struct.pack_into("<I", header, 28, 1)
    struct.pack_into("<I", header, 32, offset)
    header[ID_OFFSET : ID_OFFSET + len(encoded_id)] = encoded_id
    header[104 : 104 + len(encoded_title)] = encoded_title
    meta = [offset, 1, 256, 0, 272, 0, 272, 0, 272, 0, 272, len(files), 272, 0]
    meta += [index_end, 0] * 4 + [0, index_end, 16]
    output = header + struct.pack("<25I", *meta) + b"".join(entries)
    # Element 0's payload points to the Lua entry in the resource table.
    # It is not a table terminator: binaries can sort after main.lua.
    main_index = next(i for i, (name, _) in enumerate(files) if name == "lua/main.lua")
    output += struct.pack("<HHIII", main_index, 0x0500, 0, 0, 0) + payload
    output += struct.pack("<IHHI", 0, width, height, len(preview)) + preview
    return bytes(output)


def unpack(blob):
    """Parse resource extents independently of pack() and verify all boundaries."""
    if len(blob) < 288 or blob[:4] != MAGIC:
        raise ValueError("invalid face header")
    screens, preview_at = struct.unpack_from("<II", blob, 28)
    if screens != 1:
        raise ValueError("expected single-screen Lua face")
    count = struct.unpack_from("<I", blob, 216)[0]
    start = struct.unpack_from("<I", blob, 212)[0]
    if not 0 < count <= 65535 or start + count * 16 > preview_at:
        raise ValueError("invalid resource table")
    files, extents = {}, []
    for i in range(count):
        number, kind, _, at, size = struct.unpack_from("<HHIII", blob, start + i * 16)
        if number != i or kind != 0x500 or at % 4 or size < 20 or at + size > preview_at:
            raise ValueError("invalid resource extent")
        data_size = int.from_bytes(blob[at : at + 3], "little")
        name_size = blob[at + 3]
        if data_size + name_size + 20 != size:
            raise ValueError("resource length mismatch")
        name = blob[at + 20 : at + 20 + name_size].decode("ascii")
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or name in files:
            raise ValueError("invalid resource path")
        files[name] = blob[at + 20 + name_size : at + size]
        extents.append((at, at + size))
    if any(a[1] > b[0] for a, b in zip(sorted(extents), sorted(extents)[1:])):
        raise ValueError("overlapping resources")
    element_count, element_table = struct.unpack_from("<II", blob, 176)
    if element_count != 1 or element_table + 16 > preview_at:
        raise ValueError("invalid Lua element table")
    _, _, element_at, element_size = struct.unpack_from("<4I", blob, element_table)
    if element_size != 16 or element_at + element_size > preview_at:
        raise ValueError("invalid Lua element payload")
    target = struct.unpack_from("<I", blob, element_at)[0]
    entry_index = target & 0xFFFF
    names = list(files)
    if target >> 24 != 5 or entry_index >= len(names):
        raise ValueError("invalid Lua entry point")
    entrypoint = names[entry_index]
    if entrypoint != "lua/main.lua":
        raise ValueError("Lua entry points to " + entrypoint + ", expected lua/main.lua")
    if preview_at + 12 > len(blob):
        raise ValueError("missing preview")
    fmt, width, height, size = struct.unpack_from("<IHHI", blob, preview_at)
    if fmt != 0 or size != width * height * 4 or preview_at + 12 + size != len(blob):
        raise ValueError("invalid BGRA preview")
    face_id = blob[ID_OFFSET : ID_OFFSET + blob[5]].decode("ascii")
    encode_face_id(face_id)
    return {
        "id": face_id,
        "entrypoint": entrypoint,
        "title": blob[104:120].split(b"\0")[0].decode("ascii"),
        "width": width,
        "height": height,
        "files": files,
        "preview": blob[preview_at + 12 :],
    }


def preview(icon, label="VEPOSED"):
    """Render a native-size preview using the suite's existing vector-derived icon."""
    width, height = 336, 480
    pixels = bytearray(bytes([28, 20, 16, 255]) * width * height)
    # The LVGL icon has a 12-byte header and straight-alpha BGRA pixels.
    for y in range(128):
        for x in range(128):
            src = 12 + ((y // 2) * 64 + x // 2) * 4
            b, g, r, a = icon[src : src + 4]
            dst = ((y + 100) * width + x + 104) * 4
            base = pixels[dst : dst + 3]
            pixels[dst : dst + 4] = bytes(
                [(v * a + old * (255 - a)) // 255 for v, old in zip((b, g, r), base)] + [255]
            )
    glyphs = {
        "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
        "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
        "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
        "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
        "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
        "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
        "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
        "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
        "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    }
    scale = 5
    left = (width - (len(label) * 6 - 1) * scale) // 2
    for i, ch in enumerate(label):
        for y, row in enumerate(glyphs[ch]):
            for x, on in enumerate(row):
                if on != "1":
                    continue
                for dy in range(scale):
                    for dx in range(scale):
                        dst = ((280 + y * scale + dy) * width + left + (i * 6 + x) * scale + dx) * 4
                        pixels[dst : dst + 4] = b"\xff\xff\xff\xff"
    return bytes(pixels)
