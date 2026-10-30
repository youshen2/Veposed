//! Exact p67cn .043 memory policy. Umem comes from up_allocate_heap at
//! 0x0c19d4fc; modlib_load allocates text/data through kumm_memalign.
use veposed_core::CodeMemory;

pub(crate) const UMEM_START: usize = 0x3c27_1400;
pub(crate) const UMEM_END: usize = 0x3dfc_0000;
const PSRAM_ALIAS: usize = 0x2000_0000;

fn contains(start: usize, end: usize, address: usize, length: usize) -> bool {
    address >= start
        && address
            .checked_add(length)
            .is_some_and(|limit| limit <= end)
}

pub(crate) fn writable(address: usize, length: usize) -> bool {
    contains(0x2000_0000, 0x2040_0000, address, length)
        || contains(0x3c00_0000, 0x3c08_0500, address, length)
        || contains(UMEM_START, UMEM_END, address, length)
}

pub(crate) fn code(execute: usize, length: usize) -> Option<CodeMemory> {
    let write = if contains(0x1c00_0000, 0x1c08_0500, execute, length)
        || contains(
            UMEM_START - PSRAM_ALIAS,
            UMEM_END - PSRAM_ALIAS,
            execute,
            length,
        ) {
        execute + PSRAM_ALIAS
    } else if contains(0x0020_0000, 0x0040_0000, execute, length) {
        execute + 0x1fe0_0000
    } else if contains(0x2000_0000, 0x2040_0000, execute, length)
        || contains(UMEM_START, UMEM_END, execute, length)
    {
        execute
    } else {
        return None;
    };
    Some(CodeMemory { execute, write })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn module_heap_is_writable_and_executable_through_both_aliases() {
        // This valid dynamic allocation was outside the old startup-only gate.
        let data = 0x3c30_0040;
        assert!(writable(data, 4));
        let direct = code(data, 32).unwrap();
        assert_eq!((direct.execute, direct.write), (data, data));
        let alias = code(data - PSRAM_ALIAS, 32).unwrap();
        assert_eq!((alias.execute, alias.write), (0x1c30_0040, data));
        assert!(writable(alias.write, 32));
    }

    #[test]
    fn code_windows_do_not_grant_access_to_holes_or_past_the_heap() {
        assert!(writable(UMEM_END - 4, 4));
        assert!(!writable(UMEM_END - 4, 5));
        assert!(!writable(0x3c10_0000, 4));
        assert!(!writable(0x3c08_04fe, 4));
        assert!(!writable(usize::MAX - 2, 4));
        assert!(code(UMEM_END - PSRAM_ALIAS - 16, 16).is_some());
        assert!(code(UMEM_END - PSRAM_ALIAS - 16, 17).is_none());
        assert!(code(0x1c10_0000, 4).is_none());
        assert!(code(0x0c54_d3ee, 16).is_none());
    }
}
