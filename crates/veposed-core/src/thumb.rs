//! Bounded Thumb-2 relocation: only position-independent prologues are copied.

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
        return if mov || push {
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

/// Build an absolute LDR.W PC jump and a callable original trampoline.
/// `function` may carry the Thumb bit; trampoline storage must be word aligned.
pub fn plan(function: u32, replacement: u32, trampoline: u32, code: [u8; 16]) -> Result<Plan> {
    let entry = function & !1;
    if entry == 0 || replacement & 1 == 0 || trampoline == 0 || trampoline & 3 != 0 {
        return Err(Error::Argument);
    }
    let padding = (entry & 2) as usize;
    let mut len = 0;
    while len < padding + 8 {
        len += copy_width(&code, len)?;
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
    result.trampoline[..len].copy_from_slice(&code[..len]);
    let aligned = (len + 3) & !3;
    if aligned != len {
        result.trampoline[len..aligned].copy_from_slice(&[0x00, 0xbf]);
    }
    jump(&mut result.trampoline, aligned, resume);
    Ok(result)
}
