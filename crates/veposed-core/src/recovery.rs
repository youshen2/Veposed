//! A durable lease is written before patching. An unclosed lease quarantines
//! the next session; time elapsed is deliberately not proof of safe execution.
use crate::{Error, Result};

pub const RECORD_SIZE: usize = 32;
pub const CLEAN: u32 = 0;
pub const ARMED: u32 = 1;
pub const LOCKED: u32 = 2;
pub const PREVIOUS_SESSION: u32 = 1;
pub const HOOK_FAILURE: u32 = 2;
pub const MANUAL: u32 = 3;
pub const STORAGE_FAILURE: u32 = 4;
pub const CORRUPT_RECORD: u32 = 5;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Record {
    pub sequence: u32,
    pub phase: u32,
    pub failures: u32,
    pub reason: u32,
    pub last_error: i32,
}

impl Record {
    pub const fn clean() -> Self {
        Self {
            sequence: 0,
            phase: CLEAN,
            failures: 0,
            reason: 0,
            last_error: 0,
        }
    }

    pub fn encode(self) -> [u8; RECORD_SIZE] {
        let words = [
            0x4750_4556,
            1,
            self.sequence,
            self.phase,
            self.failures,
            self.reason,
            self.last_error as u32,
        ];
        let mut bytes = [0; RECORD_SIZE];
        for (word, out) in words.into_iter().zip(bytes.chunks_exact_mut(4)) {
            out.copy_from_slice(&word.to_le_bytes());
        }
        let checksum = crc32(&bytes[..28]);
        bytes[28..].copy_from_slice(&checksum.to_le_bytes());
        bytes
    }

    pub fn decode(bytes: &[u8; RECORD_SIZE]) -> Result<Self> {
        let word = |offset| u32::from_le_bytes(bytes[offset..offset + 4].try_into().unwrap());
        if word(0) != 0x4750_4556
            || word(4) != 1
            || word(12) > LOCKED
            || word(28) != crc32(&bytes[..28])
        {
            return Err(Error::Storage);
        }
        Ok(Self {
            sequence: word(8),
            phase: word(12),
            failures: word(16),
            reason: word(20),
            last_error: word(24) as i32,
        })
    }
}

fn crc32(bytes: &[u8]) -> u32 {
    let mut crc = u32::MAX;
    for byte in bytes {
        crc ^= *byte as u32;
        for _ in 0..8 {
            crc = (crc >> 1) ^ (0xedb8_8320 & 0u32.wrapping_sub(crc & 1));
        }
    }
    !crc
}

#[derive(Clone, Copy, Debug)]
pub struct Guard {
    pub record: Record,
    /// A manual reset updates the next boot only; this session stays quarantined.
    pub safe: bool,
}

impl Guard {
    pub const fn fresh() -> Self {
        Self {
            record: Record::clean(),
            safe: false,
        }
    }

    /// Read status: 0 = full record, 1 = missing, 2 = external disable marker,
    /// negative = I/O failure. Unknown positive statuses are I/O failures.
    pub fn boot(status: i32, bytes: &[u8; RECORD_SIZE]) -> (Self, bool) {
        match status {
            1 => (Self::fresh(), false),
            2 => (Self::fresh().lock(MANUAL, 0), true),
            0 => match Record::decode(bytes) {
                Ok(record) if record.phase == ARMED => (
                    Self {
                        record,
                        safe: false,
                    }
                    .lock(PREVIOUS_SESSION, 0),
                    true,
                ),
                Ok(record) => (
                    Self {
                        safe: record.phase == LOCKED,
                        record,
                    },
                    false,
                ),
                Err(_) => (
                    Self::fresh().lock(CORRUPT_RECORD, Error::Storage as i32),
                    true,
                ),
            },
            _ => (
                Self::fresh().lock(STORAGE_FAILURE, Error::Storage as i32),
                false,
            ),
        }
    }

    pub fn arm(mut self) -> Result<Self> {
        if self.safe {
            return Err(Error::SafeMode);
        }
        self.record.sequence = self.record.sequence.wrapping_add(1);
        self.record.phase = ARMED;
        Ok(self)
    }

    pub fn lock(mut self, reason: u32, error: i32) -> Self {
        if !self.safe && matches!(reason, PREVIOUS_SESSION | HOOK_FAILURE) {
            self.record.failures = self.record.failures.saturating_add(1);
        }
        self.safe = true;
        self.record.sequence = self.record.sequence.wrapping_add(1);
        self.record.phase = LOCKED;
        self.record.reason = reason;
        self.record.last_error = error;
        self
    }

    pub fn close(mut self) -> Self {
        self.record.sequence = self.record.sequence.wrapping_add(1);
        self.record.phase = CLEAN;
        self.record.reason = 0;
        self.record.last_error = 0;
        self
    }
}
