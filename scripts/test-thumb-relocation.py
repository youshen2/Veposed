#!/usr/bin/env python3
"""Compare .043 firmware-specific trampolines with Unicorn.

Run with a Python environment containing unicorn and with rustc on PATH.
The mock callee models ABI-compliant register/flag changes; this is not a device test.
"""

import json
from pathlib import Path
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB
from unicorn.arm_const import (
    UC_ARM_REG_CPSR,
    UC_ARM_REG_LR,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_R4,
    UC_ARM_REG_R5,
    UC_ARM_REG_R6,
    UC_ARM_REG_R7,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[1]
ENTRY, RESUME, TARGET, TRAMPOLINE = 0x1C02ECF0, 0x1C02ECFA, 0x1C02B304, 0x3C271000
CODE = bytes.fromhex("f8b5054600affcf705fbaa68002a60d0")
DELETE_ENTRY = 0x1C02ECDC
DELETE_CODE = bytes.fromhex("90f83330db0600d5704780b500affff7")
CREATE_ENTRY = 0x1C028BB4
CREATE_CODE = bytes.fromhex("0246b0b506480d4600af114600f0def9")
CREATE_LITERAL = 0x1C028BD4
EVENT_SEND_ENTRY = 0x002BF690
EVENT_SEND_CODE = bytes.fromhex("b0b588b000af38b300243b7ec7e90000")
ANGLE_ENTRY = 0x1C06CAF8
ANGLE_CODE = bytes.fromhex("2de9f0418ab090f86130054603f00f03")
REGISTERS = (
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_R4,
    UC_ARM_REG_R5,
    UC_ARM_REG_R6,
    UC_ARM_REG_R7,
    UC_ARM_REG_SP,
    UC_ARM_REG_CPSR,
)


def make_trampoline(entry, code):
    thumb = json.dumps(str(ROOT / "crates/veposed-core/src/thumb.rs"))
    source = f"""#[derive(Debug)] pub enum Error {{ Argument, Unsupported }}
    pub type Result<T> = core::result::Result<T, Error>;
    #[path = {thumb}] mod thumb;
    fn main() {{
        let code = {list(code)!r};
        let plan = thumb::plan({entry | 1}, 0x3c280001, 0x3c271000, code).unwrap();
        for b in &plan.trampoline[..plan.trampoline_len] {{ print!("{{b:02x}}"); }}
    }}"""
    with tempfile.TemporaryDirectory() as directory:
        src = Path(directory) / "probe.rs"
        exe = Path(directory) / "probe"
        src.write_text(source)
        subprocess.run(
            ["rustc", "--edition", "2024", "--cap-lints", "allow", "-o", str(exe), str(src)],
            check=True,
        )
        return bytes.fromhex(subprocess.check_output([str(exe)], text=True))


def execute(start, trampoline):
    vm = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address in (0x1C02E000, 0x1C02B000, 0x3C271000, 0x20000000, 0x20001000):
        vm.mem_map(address, 0x1000)
    vm.mem_write(ENTRY, CODE)
    vm.mem_write(TARGET, bytes.fromhex("4d207047"))  # movs r0,#77; bx lr
    vm.mem_write(TRAMPOLINE, trampoline)
    vm.reg_write(UC_ARM_REG_SP, 0x20001FF0)
    vm.reg_write(UC_ARM_REG_LR, 0x20000001)
    for index, register in enumerate(REGISTERS[:8]):
        vm.reg_write(register, 0x20000080 + 4 * index)
    seen = []

    def hook(uc, address, _size, _data):
        if address == TARGET:
            seen.append("callee")
        if address == RESUME:
            seen.append("resume")
            uc.emu_stop()

    vm.hook_add(UC_HOOK_CODE, hook)
    vm.emu_start(start | 1, 0, count=30)
    assert seen == ["callee", "resume"], seen
    return [vm.reg_read(register) for register in REGISTERS], bytes(vm.mem_read(0x20001FD8, 24))


def execute_delete(start, trampoline, flag):
    vm = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address in (0x1C02E000, 0x3C271000, 0x20000000, 0x20001000):
        vm.mem_map(address, 0x1000)
    vm.mem_write(DELETE_ENTRY, DELETE_CODE)
    vm.mem_write(TRAMPOLINE, trampoline)
    vm.mem_write(0x200000B3, bytes([flag]))
    vm.reg_write(UC_ARM_REG_SP, 0x20001FF0)
    vm.reg_write(UC_ARM_REG_LR, 0x20000001)
    for index, register in enumerate(REGISTERS[:8]):
        vm.reg_write(register, 0x20000080 + 4 * index)
    seen = []

    def hook(uc, address, _size, _data):
        if address in (DELETE_ENTRY + 8, DELETE_ENTRY + 10):
            seen.append(address)
            uc.emu_stop()

    vm.hook_add(UC_HOOK_CODE, hook)
    vm.emu_start(start | 1, 0, count=20)
    assert len(seen) == 1, seen
    return seen[0], [vm.reg_read(register) for register in (*REGISTERS, UC_ARM_REG_LR)]


def execute_create(start, trampoline, literal):
    vm = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address in (0x1C028000, 0x3C271000, 0x20000000, 0x20001000):
        vm.mem_map(address, 0x1000)
    vm.mem_write(CREATE_ENTRY, CREATE_CODE)
    vm.mem_write(CREATE_LITERAL, literal.to_bytes(4, "little"))
    vm.mem_write(TRAMPOLINE, trampoline)
    vm.reg_write(UC_ARM_REG_SP, 0x20001FF0)
    vm.reg_write(UC_ARM_REG_LR, 0x20000001)
    for index, register in enumerate(REGISTERS[:8]):
        vm.reg_write(register, 0x20000080 + 4 * index)
    seen = []

    def hook(uc, address, _size, _data):
        if address == CREATE_ENTRY + 8:
            seen.append(address)
            uc.emu_stop()

    vm.hook_add(UC_HOOK_CODE, hook)
    vm.emu_start(start | 1, 0, count=20)
    assert seen == [CREATE_ENTRY + 8], seen
    return [vm.reg_read(register) for register in (*REGISTERS, UC_ARM_REG_LR)], bytes(
        vm.mem_read(0x20001FE0, 16)
    )


def execute_event_send(start, trampoline, target, flags):
    vm = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address in (0x002BF000, 0x3C271000, 0x20000000, 0x20001000):
        vm.mem_map(address, 0x1000)
    vm.mem_write(EVENT_SEND_ENTRY, EVENT_SEND_CODE)
    vm.mem_write(TRAMPOLINE, trampoline)
    vm.reg_write(UC_ARM_REG_SP, 0x20001FF0)
    vm.reg_write(UC_ARM_REG_LR, 0x20000001)
    for index, register in enumerate(REGISTERS[:8]):
        vm.reg_write(register, 0x20000080 + 4 * index)
    vm.reg_write(UC_ARM_REG_R0, target)
    vm.reg_write(UC_ARM_REG_CPSR, (vm.reg_read(UC_ARM_REG_CPSR) & 0x0fffffff) | flags)
    seen = []

    def hook(uc, address, _size, _data):
        if address in (EVENT_SEND_ENTRY + 8, EVENT_SEND_ENTRY + 0x58):
            seen.append(address)
            uc.emu_stop()

    vm.hook_add(UC_HOOK_CODE, hook)
    vm.emu_start(start | 1, 0, count=20)
    assert len(seen) == 1, seen
    return seen[0], [vm.reg_read(register) for register in (*REGISTERS, UC_ARM_REG_LR)], bytes(
        vm.mem_read(0x20001FE0, 16)
    )


def execute_angle(start, trampoline, value):
    vm = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address in (0x1C06C000, 0x3C271000, 0x20000000, 0x20001000):
        vm.mem_map(address, 0x1000)
    vm.mem_write(ANGLE_ENTRY, ANGLE_CODE)
    vm.mem_write(TRAMPOLINE, trampoline)
    vm.mem_write(0x20000080 + 0x61, bytes([value]))
    vm.reg_write(UC_ARM_REG_SP, 0x20001FF0)
    vm.reg_write(UC_ARM_REG_LR, 0x20000001)
    for index, register in enumerate(REGISTERS[:8]):
        vm.reg_write(register, 0x20000080 + 4 * index)
    seen = []

    def hook(uc, address, _size, _data):
        if address == ANGLE_ENTRY + 10:
            seen.append(address)
            uc.emu_stop()

    vm.hook_add(UC_HOOK_CODE, hook)
    vm.emu_start(start | 1, 0, count=20)
    assert seen == [ANGLE_ENTRY + 10], seen
    return [vm.reg_read(register) for register in (*REGISTERS, UC_ARM_REG_LR)], bytes(
        vm.mem_read(0x20001FD8, 24)
    )


def main():
    trampoline = make_trampoline(ENTRY, CODE)
    assert execute(ENTRY, trampoline) == execute(TRAMPOLINE, trampoline)
    print("Thumb call relocation: original and trampoline match at resume")
    trampoline = make_trampoline(DELETE_ENTRY, DELETE_CODE)
    for flag in (0, 0x10, 0x20, 0xFF):
        original = execute_delete(DELETE_ENTRY, trampoline, flag)
        relocated = execute_delete(TRAMPOLINE, trampoline, flag)
        assert original == relocated, (flag, original, relocated)
        assert original[0] == DELETE_ENTRY + (8 if flag & 0x10 else 10)
    print("Thumb conditional relocation: both object-delete paths match")
    trampoline = make_trampoline(CREATE_ENTRY, CREATE_CODE)
    for literal in (0x2CCE0308, 0x12345678):
        original = execute_create(CREATE_ENTRY, trampoline, literal)
        relocated = execute_create(TRAMPOLINE, trampoline, literal)
        assert original == relocated, (literal, original, relocated)
        assert original[0][0] == literal
    print("Thumb literal relocation: original pool value and state match")
    trampoline = make_trampoline(EVENT_SEND_ENTRY, EVENT_SEND_CODE)
    for target in (0, 0x20000080):
        for flags in (0, 0xF0000000):
            original = execute_event_send(EVENT_SEND_ENTRY, trampoline, target, flags)
            relocated = execute_event_send(TRAMPOLINE, trampoline, target, flags)
            assert original == relocated, (target, flags, original, relocated)
            assert original[0] == EVENT_SEND_ENTRY + (0x58 if target == 0 else 8)
    print("Thumb event-send relocation: null and non-null paths match")
    trampoline = make_trampoline(ANGLE_ENTRY, ANGLE_CODE)
    for value in (0, 10, 11, 255):
        assert execute_angle(ANGLE_ENTRY, trampoline, value) == execute_angle(TRAMPOLINE, trampoline, value)
    print("Thumb image-angle relocation: original and trampoline match")


if __name__ == "__main__":
    main()
