#!/usr/bin/env python3
"""Emulate the p67cn zero-fill helper for lifecycle cleanup lengths."""
import argparse
import json
from pathlib import Path
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from firmware import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware", type=Path)
    args = parser.parse_args()
    profile = json.loads((ROOT / "targets/xiaomi-band-10-pro-3.101.043.json").read_text())
    ap, _ = verify(args.firmware, profile)
    for length in (4, 40, 76):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x270000, 0x50000)
        uc.mem_write(0x2765C0, ap[0x23A4 : 0x23A4 + 0x3A328])
        uc.mem_map(0x20200000, 0x2000)
        uc.mem_map(0x300000, 0x1000)
        buf = 0x20200400
        uc.mem_write(buf - 4, b"\xa5" * (length + 8))
        uc.reg_write(UC_ARM_REG_SP, 0x20201FF0)
        uc.reg_write(UC_ARM_REG_R0, buf)
        uc.reg_write(UC_ARM_REG_R1, 0)
        uc.reg_write(UC_ARM_REG_R2, length)
        uc.reg_write(UC_ARM_REG_LR, 0x300001)
        uc.emu_start(0x27676D, 0x300000, count=10000)
        if uc.reg_read(UC_ARM_REG_PC) != 0x300000:
            raise AssertionError(f"zero-fill length {length} did not return")
        actual = bytes(uc.mem_read(buf - 4, length + 8))
        if actual != b"\xa5" * 4 + b"\0" * length + b"\xa5" * 4:
            raise AssertionError(f"unexpected memory after zero-fill length {length}")
        print(f"length {length}: zeroed target and preserved guards")


if __name__ == "__main__":
    main()
