//! Bounded Thumb-2 relocation with firmware-specific guarded rewrites.

use crate::{Error, Result};

pub const PROLOGUE_SIZE: usize = 16;
pub const TRAMPOLINE_SIZE: usize = 32;

#[derive(Clone, Copy, Debug)]
pub struct Plan {
    pub patch: [u8; PROLOGUE_SIZE],
    pub saved: [u8; PROLOGUE_SIZE],
    pub patch_len: usize,
    pub trampoline: [u8; TRAMPOLINE_SIZE],
    pub trampoline_len: usize,
}

fn half(bytes: &[u8], offset: usize) -> u16 {
    u16::from_le_bytes([bytes[offset], bytes[offset + 1]])
}

fn copy_width(bytes: &[u8], offset: usize) -> Result<usize> {
    let first = half(bytes, offset);
    if first & 0xf800 >= 0xe800 {
        let second = bytes
            .get(offset + 2..offset + 4)
            .ok_or(Error::Unsupported)?;
        let second = u16::from_le_bytes([second[0], second[1]]);
        let mov = matches!(first & 0xfbf0, 0xf240 | 0xf2c0)
            && second & 0x8000 == 0
            && !matches!((second >> 8) & 15, 13 | 15);
        let push = first == 0xe92d && second & 0xa000 == 0 && second.count_ones() >= 2;
        // UBFX R0, R0, #0, #15 in the p67cn event-code getter.
        let event_code_mask = first == 0xf3c0 && second == 0x000e;
        return if mov || push || event_code_mask {
            Ok(4)
        } else {
            Err(Error::Unsupported)
        };
    }
    let safe = match first {
        0x0000..=0x43ff | 0x5000..=0x9fff => true,
        0x4400..=0x46ff => {
            let dst = (first & 7) | ((first >> 4) & 8);
            let src = (first >> 3) & 15;
            dst != 15 && src != 15
        }
        _ => {
            first & 0xf800 == 0xa800
                || first & 0xff00 == 0xb000
                || first & 0xff00 == 0xb200
                || (first & 0xfe00 == 0xb400 && first & 0x1ff != 0)
                || (first & 0xff00 == 0xbc00 && first & 0xff != 0)
                || matches!(first & 0xffc0, 0xba00 | 0xba40 | 0xbac0)
                || first == 0xbf00
        }
    };
    if safe { Ok(2) } else { Err(Error::Unsupported) }
}

fn jump(bytes: &mut [u8], offset: usize, destination: u32) {
    bytes[offset..offset + 4].copy_from_slice(&[0xdf, 0xf8, 0x00, 0xf0]);
    bytes[offset + 4..offset + 8].copy_from_slice(&(destination | 1).to_le_bytes());
}

fn call_target(entry: u32, offset: usize, code: &[u8; 16]) -> Result<u32> {
    let first = half(code, offset);
    let second = half(code, offset + 2);
    if first & 0xf800 != 0xf000 || second & 0xd000 != 0xd000 {
        return Err(Error::Unsupported);
    }
    let sign = u32::from((first >> 10) & 1);
    let i1 = u32::from(((second >> 13) & 1) ^ (sign as u16) ^ 1);
    let i2 = u32::from(((second >> 11) & 1) ^ (sign as u16) ^ 1);
    let immediate = (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (u32::from(first & 0x3ff) << 12)
        | (u32::from(second & 0x7ff) << 1);
    let displacement = ((immediate as i32) << 7) >> 7;
    let pc = i64::from(entry) + offset as i64 + 4;
    u32::try_from(pc + i64::from(displacement)).map_err(|_| Error::Unsupported)
}

fn mov_imm(bytes: &mut [u8], offset: usize, register: u16, value: u16, top: bool) {
    let opcode = if top { 0xf2c0 } else { 0xf240 };
    let first = opcode | ((value >> 12) & 0xf) | ((value >> 1) & 0x0400);
    let second = ((value & 0x0700) << 4) | (register << 8) | (value & 0x00ff);
    bytes[offset..offset + 2].copy_from_slice(&first.to_le_bytes());
    bytes[offset + 2..offset + 4].copy_from_slice(&second.to_le_bytes());
}

/// Build an absolute LDR.W PC jump and a callable original trampoline.
/// `function` may carry the Thumb bit; trampoline storage must be word aligned.
pub fn plan(function: u32, replacement: u32, trampoline: u32, code: [u8; 16]) -> Result<Plan> {
    let entry = function & !1;
    if entry == 0 || replacement & 1 == 0 || trampoline == 0 || trampoline & 3 != 0 {
        return Err(Error::Argument);
    }
    let padding = (entry & 2) as usize;
    let mut len = 0;
    let mut call = None;
    let mut object_delete_branch = false;
    let mut object_create_literal = false;
    let mut event_send_null_branch = false;
    while len < padding + 8 {
        match copy_width(&code, len) {
            Ok(width) => len += width,
            Err(Error::Unsupported)
                if entry == 0x1c06_caf8
                    && len == 6
                    && code[..10]
                        == [0x2d, 0xe9, 0xf0, 0x41, 0x8a, 0xb0, 0x90, 0xf8, 0x61, 0x30] =>
            {
                // LDRB.W R3, [R0, #0x61] is position independent.
                len += 4;
            }
            Err(Error::Unsupported)
                if entry == 0x1c02_8bb4
                    && len == 4
                    && code[..8] == [0x02, 0x46, 0xb0, 0xb5, 0x06, 0x48, 0x0d, 0x46] =>
            {
                object_create_literal = true;
                len += 2;
            }
            Err(Error::Unsupported)
                if entry == 0x1c02_ecdc
                    && len == 0
                    && code[..8] == [0x90, 0xf8, 0x33, 0x30, 0xdb, 0x06, 0x00, 0xd5] =>
            {
                object_delete_branch = true;
                len = 8;
            }
            Err(Error::Unsupported)
                if entry == 0x002b_f690
                    && len == 6
                    && code[..8] == [0xb0, 0xb5, 0x88, 0xb0, 0x00, 0xaf, 0x38, 0xb3] =>
            {
                event_send_null_branch = true;
                len = 8;
            }
            Err(Error::Unsupported)
                if entry == 0x1c02_ecf0
                    && len == 6
                    && code[..10]
                        == [0xf8, 0xb5, 0x05, 0x46, 0x00, 0xaf, 0xfc, 0xf7, 0x05, 0xfb] =>
            {
                call = Some(call_target(entry, len, &code)?);
                len += 4;
            }
            Err(error) => return Err(error),
        }
    }
    let resume = entry.checked_add(len as u32).ok_or(Error::Argument)?;
    let mut result = Plan {
        patch: [0; 16],
        saved: code,
        patch_len: len,
        trampoline: [0; 32],
        trampoline_len: ((len + 3) & !3) + 8,
    };
    for pair in result.patch[..len].chunks_exact_mut(2) {
        pair.copy_from_slice(&[0x00, 0xbf]);
    }
    jump(&mut result.patch, padding, replacement);
    if object_create_literal {
        result.trampoline[..4].copy_from_slice(&code[..4]);
        // Read the original literal pool, including any live change to its value.
        mov_imm(&mut result.trampoline, 4, 0, 0x8bd4, false);
        mov_imm(&mut result.trampoline, 8, 0, 0x1c02, true);
        result.trampoline[12..14].copy_from_slice(&[0x00, 0x68]);
        result.trampoline[14..16].copy_from_slice(&code[6..8]);
        jump(&mut result.trampoline, 16, resume);
        result.trampoline_len = 24;
        return Ok(result);
    }
    if object_delete_branch {
        result.trampoline[..6].copy_from_slice(&code[..6]);
        // BPL to the second absolute jump; fall through to the first one.
        result.trampoline[6..8].copy_from_slice(&[0x03, 0xd5]);
        jump(&mut result.trampoline, 8, entry + 8);
        jump(&mut result.trampoline, 16, entry + 10);
        result.trampoline_len = 24;
        return Ok(result);
    }
    if event_send_null_branch {
        result.trampoline[..6].copy_from_slice(&code[..6]);
        // CBZ R0 to the second jump; CBZ does not modify condition flags.
        result.trampoline[6..8].copy_from_slice(&[0x18, 0xb1]);
        jump(&mut result.trampoline, 8, entry + 8);
        jump(&mut result.trampoline, 16, entry + 0x58);
        result.trampoline_len = 24;
        return Ok(result);
    }
    if let Some(target) = call {
        if target >= entry && target < resume {
            return Err(Error::Unsupported);
        }
        let return_pc = trampoline.checked_add(24).ok_or(Error::Argument)? | 1;
        result.trampoline[..6].copy_from_slice(&code[..6]);
        mov_imm(&mut result.trampoline, 6, 14, return_pc as u16, false);
        mov_imm(
            &mut result.trampoline,
            10,
            14,
            (return_pc >> 16) as u16,
            true,
        );
        result.trampoline[14..16].copy_from_slice(&[0x00, 0xbf]);
        jump(&mut result.trampoline, 16, target);
        jump(&mut result.trampoline, 24, resume);
        result.trampoline_len = 32;
        return Ok(result);
    }
    result.trampoline[..len].copy_from_slice(&code[..len]);
    let aligned = (len + 3) & !3;
    if aligned != len {
        result.trampoline[len..aligned].copy_from_slice(&[0x00, 0xbf]);
    }
    jump(&mut result.trampoline, aligned, resume);
    Ok(result)
}
