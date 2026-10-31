use std::ffi::c_void;
use veposed_core::{
    CallContext, Callbacks, CodeMemory, Engine, Error, MAX_SITES, Memory, Result, Target, thumb,
};

#[test]
fn compass_image_angle_prologue_is_signature_bound() {
    let code = [
        0x2d, 0xe9, 0xf0, 0x41, 0x8a, 0xb0, 0x90, 0xf8, 0x61, 0x30, 0x05, 0x46, 0x03, 0xf0, 0x0f,
        0x03,
    ];
    let plan = thumb::plan(0x1c06_caf9, 0x3c28_0001, 0x3c27_1000, code).unwrap();
    assert_eq!(plan.patch_len, 10);
    assert_eq!(&plan.trampoline[..10], &code[..10]);
    assert_eq!(&plan.trampoline[16..20], &0x1c06_cb03u32.to_le_bytes());
    let mut changed = code;
    changed[8] ^= 1;
    assert_eq!(
        thumb::plan(0x1c06_caf9, 0x3c28_0001, 0x3c27_1000, changed).unwrap_err(),
        Error::Unsupported
    );
    assert_eq!(
        thumb::plan(0x1c06_cb01, 0x3c28_0001, 0x3c27_1000, code).unwrap_err(),
        Error::Unsupported
    );
}

#[test]
fn class_allocation_and_event_registration_prologues_relocate() {
    for (entry, code) in [
        (
            0x1c02_8f81,
            [
                0xf0, 0xb5, 0x83, 0xb0, 0x06, 0x46, 0x0d, 0x46, 0x02, 0xaf, 0x50, 0xb1, 0x03, 0x46,
                0x35, 0x4c,
            ],
        ),
        (
            0x002b_f7ad,
            [
                0x2d, 0xe9, 0xf0, 0x41, 0x80, 0x46, 0x0c, 0x46, 0x15, 0x46, 0x1e, 0x46, 0x00, 0xaf,
                0x03, 0xf0,
            ],
        ),
        (
            0x002b_f811,
            [
                0x2d, 0xe9, 0xf0, 0x41, 0x05, 0x46, 0x80, 0x68, 0x00, 0xaf, 0xa0, 0xb1, 0x0c, 0x30,
                0x88, 0x46,
            ],
        ),
    ] {
        let plan = thumb::plan(entry, 0x1c27_0001, 0x1c28_0000, code).unwrap();
        assert_eq!(plan.patch_len, 8);
        assert_eq!(&plan.trampoline[..8], &code[..8]);
        assert_eq!(&plan.trampoline[12..16], &(entry + 8).to_le_bytes());
    }
}

#[test]
fn object_create_entry_reads_its_original_literal_pool() {
    let code = [
        0x02, 0x46, 0xb0, 0xb5, 0x06, 0x48, 0x0d, 0x46, 0x00, 0xaf, 0x11, 0x46, 0x00, 0xf0, 0xde,
        0xf9,
    ];
    let plan = thumb::plan(0x1c02_8bb5, 0x3c28_0001, 0x3c27_1000, code).unwrap();
    assert_eq!(plan.patch_len, 8);
    assert_eq!(plan.trampoline_len, 24);
    assert_eq!(&plan.trampoline[..4], &code[..4]);
    assert_eq!(&plan.trampoline[12..16], &[0x00, 0x68, 0x0d, 0x46]);
    assert_eq!(&plan.trampoline[20..24], &0x1c02_8bbdu32.to_le_bytes());
    let mut changed = code;
    changed[4] = 7;
    assert_eq!(
        thumb::plan(0x1c02_8bb5, 0x3c28_0001, 0x3c27_1000, changed).unwrap_err(),
        Error::Unsupported
    );
    assert_eq!(
        thumb::plan(0x1c02_8b01, 0x3c28_0001, 0x3c27_1000, code).unwrap_err(),
        Error::Unsupported
    );
}

#[test]
fn event_send_entry_relocation_is_bound_to_signature_and_address() {
    let code = [
        0xb0, 0xb5, 0x88, 0xb0, 0x00, 0xaf, 0x38, 0xb3, 0x00, 0x24, 0x3b, 0x7e, 0xc7, 0xe9, 0x00,
        0x00,
    ];
    let plan = thumb::plan(0x002b_f691, 0x3c28_0001, 0x3c27_1000, code).unwrap();
    assert_eq!(plan.patch_len, 8);
    assert_eq!(plan.trampoline_len, 24);
    let mut changed = code;
    changed[6] ^= 8;
    assert_eq!(
        thumb::plan(0x002b_f691, 0x3c28_0001, 0x3c27_1000, changed).unwrap_err(),
        Error::Unsupported
    );
    assert_eq!(
        thumb::plan(0x002b_f701, 0x3c28_0001, 0x3c27_1000, code).unwrap_err(),
        Error::Unsupported
    );
}

#[test]
fn object_delete_entry_rewrites_both_branch_destinations() {
    let code = [
        0x90, 0xf8, 0x33, 0x30, 0xdb, 0x06, 0x00, 0xd5, 0x70, 0x47, 0x80, 0xb5, 0x00, 0xaf, 0xff,
        0xf7,
    ];
    let plan = thumb::plan(0x1c02_ecdd, 0x3c28_0001, 0x3c27_1000, code).unwrap();
    assert_eq!(plan.patch_len, 8);
    assert_eq!(plan.trampoline_len, 24);
    assert_eq!(&plan.trampoline[..6], &code[..6]);
    assert_eq!(&plan.trampoline[6..8], &[0x03, 0xd5]);
    assert_eq!(&plan.trampoline[12..16], &0x1c02_ece5u32.to_le_bytes());
    assert_eq!(&plan.trampoline[20..24], &0x1c02_ece7u32.to_le_bytes());
    let mut changed = code;
    changed[6] = 1;
    assert_eq!(
        thumb::plan(0x1c02_ecdd, 0x3c28_0001, 0x3c27_1000, changed).unwrap_err(),
        Error::Unsupported
    );
    assert_eq!(
        thumb::plan(0x1c02_ed01, 0x3c28_0001, 0x3c27_1000, code).unwrap_err(),
        Error::Unsupported
    );
}

#[test]
fn object_clean_entry_rewrites_relative_call_without_range_limit() {
    let code = [
        0xf8, 0xb5, 0x05, 0x46, 0x00, 0xaf, 0xfc, 0xf7, 0x05, 0xfb, 0xaa, 0x68, 0x00, 0x2a, 0x60,
        0xd0,
    ];
    let plan = thumb::plan(0x1c02_ecf1, 0x3c28_0001, 0x3c27_1000, code).unwrap();
    assert_eq!(plan.patch_len, 10);
    assert_eq!(plan.trampoline_len, 32);
    assert_eq!(&plan.trampoline[..6], &code[..6]);
    assert_eq!(&plan.trampoline[20..24], &0x1c02_b305u32.to_le_bytes());
    assert_eq!(&plan.trampoline[28..32], &0x1c02_ecfbu32.to_le_bytes());
    assert_eq!(
        thumb::plan(0x1c02_ed01, 0x3c28_0001, 0x3c27_1000, code).unwrap_err(),
        Error::Unsupported
    );
    let mut no_saved_lr = code;
    no_saved_lr[1] = 0xb4;
    assert_eq!(
        thumb::plan(0x1c02_ecf1, 0x3c28_0001, 0x3c27_1000, no_saved_lr).unwrap_err(),
        Error::Unsupported
    );
    let mut self_call = code;
    self_call[6..10].copy_from_slice(&[0xff, 0xf7, 0xfe, 0xff]);
    assert_eq!(
        thumb::plan(0x1c02_ecf1, 0x3c28_0001, 0x3c27_1000, self_call).unwrap_err(),
        Error::Unsupported
    );
}

#[test]
fn object_flag_and_state_getters_resume_at_conditional_instruction() {
    for (entry, code) in [
        (
            0x1c02_8d95,
            [
                0x80, 0xb4, 0xc3, 0x6a, 0x00, 0xaf, 0x99, 0x43, 0x0c, 0xbf, 0x01, 0x20, 0x00, 0x20,
                0xbd, 0x46,
            ],
        ),
        (
            0x1c02_8dd5,
            [
                0x80, 0xb4, 0x03, 0x8e, 0x00, 0xaf, 0x19, 0x42, 0x14, 0xbf, 0x01, 0x20, 0x00, 0x20,
                0xbd, 0x46,
            ],
        ),
    ] {
        let plan = thumb::plan(entry, 0x1c27_0001, 0x1c28_0000, code).unwrap();
        assert_eq!(plan.patch_len, 8);
        assert_eq!(&plan.trampoline[..8], &code[..8]);
        assert_eq!(&plan.trampoline[8..12], &[0xdf, 0xf8, 0x00, 0xf0]);
        assert_eq!(&plan.trampoline[12..16], &(entry + 8).to_le_bytes());
    }
}

#[test]
fn object_clear_flag_entry_relocates_its_prologue() {
    let code = [
        0xf0, 0xb5, 0x89, 0xb0, 0x0d, 0x46, 0x00, 0xaf, 0x04, 0x46, 0x01, 0xf0, 0xf9, 0xfb, 0xea,
        0x06,
    ];
    let plan = thumb::plan(0x1c02_8c85, 0x1c27_0001, 0x1c28_0000, code).unwrap();
    assert_eq!(plan.patch_len, 8);
    assert_eq!(&plan.trampoline[..8], &code[..8]);
}

#[test]
fn event_target_and_parameter_getters_relocate_complete_prologues() {
    for (entry, load) in [
        (0x002b_fd45, 0x00),
        (0x002b_fd55, 0x40),
        (0x002b_fd79, 0x00),
    ] {
        let load_high = if entry == 0x002b_fd79 { 0x69 } else { 0x68 };
        let code = [
            0x80, 0xb4, load, load_high, 0x00, 0xaf, 0xbd, 0x46, 0x5d, 0xf8, 0x04, 0x7b, 0x70,
            0x47, 0x00, 0xbf,
        ];
        let plan = thumb::plan(entry, 0x1c27_0001, 0x1c28_0000, code).unwrap();
        assert_eq!(plan.patch_len, 8);
        assert_eq!(&plan.trampoline[..8], &code[..8]);
        assert_eq!(&plan.trampoline[12..16], &(entry + 8).to_le_bytes());
    }
}

#[test]
fn event_code_entry_relocates_mask_and_resumes_after_full_instruction() {
    let code = [
        0x80, 0xb4, 0x00, 0x89, 0x00, 0xaf, 0xc0, 0xf3, 0x0e, 0x00, 0xbd, 0x46, 0x5d, 0xf8, 0x04,
        0x7b,
    ];
    let plan = thumb::plan(0x002b_fd65, 0x1c27_0001, 0x1c28_0000, code).unwrap();
    assert_eq!(plan.patch_len, 10);
    assert_eq!(&plan.trampoline[..10], &code[..10]);
    assert_eq!(&plan.trampoline[10..12], &[0x00, 0xbf]);
    assert_eq!(&plan.trampoline[16..20], &0x002b_fd6fu32.to_le_bytes());
    let mut unsupported = code;
    unsupported[8] = 0x0f;
    assert!(thumb::plan(0x002b_fd65, 0x1c27_0001, 0x1c28_0000, unsupported).is_err());
}

#[test]
fn event_user_data_entry_supports_the_actual_thumb_prologue() {
    let code = [
        0x80, 0xb4, 0xc0, 0x68, 0x00, 0xaf, 0xbd, 0x46, 0x5d, 0xf8, 0x04, 0x7b, 0x70, 0x47, 0x00,
        0xbf,
    ];
    let plan = thumb::plan(0x002b_fd89, 0x1c27_0001, 0x1c28_0000, code).unwrap();
    assert_eq!(plan.patch_len, 8);
    assert_eq!(&plan.trampoline[..8], &code[..8]);
    assert_eq!(&plan.trampoline[12..16], &0x002b_fd91u32.to_le_bytes());
}

#[test]
fn image_source_entry_supports_the_actual_thumb_prologue() {
    let code = [
        0x2d, 0xe9, 0xf0, 0x43, 0x0d, 0x46, 0x8f, 0xb0, 0x04, 0xaf, 0x04, 0x46, 0xbe, 0xf7, 0x20,
        0xfa,
    ];
    let plan = thumb::plan(0x1c06_ceb5, 0x1c27_0001, 0x1c28_0000, code).unwrap();
    assert_eq!(plan.patch_len, 8);
    assert_eq!(&plan.trampoline[..8], &code[..8]);
}

#[test]
fn add_flag_entry_supports_the_actual_thumb_prologue() {
    let code = [
        0x2d, 0xe9, 0xf0, 0x41, 0x88, 0xb0, 0x0d, 0x46, 0x00, 0xaf, 0x04, 0x46, 0x01, 0xf0, 0x4e,
        0xfc,
    ];
    let plan = thumb::plan(0x1c02_8bd9, 0x1c27_0001, 0x1c28_0000, code).unwrap();
    assert_eq!(plan.patch_len, 8);
    assert_eq!(&plan.trampoline[..8], &code[..8]);
}

#[test]
fn set_size_entry_supports_the_actual_thumb_prologue() {
    let code = [
        0xf0, 0xb5, 0x14, 0x46, 0x83, 0xb0, 0x00, 0xaf, 0x0e, 0x46, 0x00, 0x23, 0x01, 0x21, 0x3a,
        0x1d,
    ];
    let plan = thumb::plan(0x1c02_a2d1, 0x1c27_0001, 0x1c28_0000, code).unwrap();
    assert_eq!(plan.patch_len, 8);
    assert_eq!(&plan.trampoline[..8], &code[..8]);
}

struct Ram {
    bytes: [u8; 0x4000],
    publishes: usize,
    fail_at: Vec<usize>,
}
impl Ram {
    fn new() -> Self {
        Self {
            bytes: [0; 0x4000],
            publishes: 0,
            fail_at: vec![],
        }
    }
    fn pointer(&mut self, address: usize, value: usize) {
        self.write(address, &value.to_le_bytes()).unwrap();
    }
    fn word(&self, address: usize) -> usize {
        usize::from_le_bytes(
            self.bytes[address..address + size_of::<usize>()]
                .try_into()
                .unwrap(),
        )
    }
}
impl Memory for Ram {
    fn read(&self, address: usize, output: &mut [u8]) -> Result<()> {
        output.copy_from_slice(
            self.bytes
                .get(address..address + output.len())
                .ok_or(Error::Memory)?,
        );
        Ok(())
    }
    fn write(&mut self, address: usize, bytes: &[u8]) -> Result<()> {
        self.bytes
            .get_mut(address..address + bytes.len())
            .ok_or(Error::Memory)?
            .copy_from_slice(bytes);
        Ok(())
    }
    fn code(&self, execute: usize, _: usize) -> Result<CodeMemory> {
        Ok(CodeMemory {
            execute,
            write: execute,
        })
    }
    fn trampoline(&self, index: usize) -> Result<CodeMemory> {
        self.code(0x3000 + index * 32, 32)
    }
    fn publish(&mut self, _: usize, _: usize) -> Result<()> {
        self.publishes += 1;
        if self.fail_at.contains(&self.publishes) {
            Err(Error::Memory)
        } else {
            Ok(())
        }
    }
}

unsafe extern "C" fn before(context: *mut CallContext, data: *mut c_void) {
    let trace = unsafe { &mut *(data as *mut Vec<usize>) };
    let call = unsafe { &mut *context };
    trace.push(call.args[0]);
    call.args[0] += 10;
}
unsafe extern "C" fn after(context: *mut CallContext, data: *mut c_void) {
    let trace = unsafe { &mut *(data as *mut Vec<usize>) };
    let call = unsafe { &mut *context };
    trace.push(call.result);
    call.result *= 2;
}
unsafe extern "C" fn early(context: *mut CallContext, _: *mut c_void) {
    let call = unsafe { &mut *context };
    call.result = 7;
    call.return_early = 1;
}

fn callbacks(trace: &mut Vec<usize>, priority: i32) -> Callbacks {
    Callbacks {
        before: Some(before),
        after: Some(after),
        user_data: trace as *mut _ as _,
        priority,
    }
}

#[test]
fn multiple_modules_order_disable_early_return_and_restore() {
    let mut memory = Ram::new();
    memory.pointer(0x1000, 0x101);
    let mut engine = Engine::new(memory);
    let low = engine.register(b"low").unwrap();
    let high = engine.register(b"high").unwrap();
    let mut low_trace = vec![];
    let mut high_trace = vec![];
    let target = Target::Pointer {
        slot: 0x1000,
        expected: 0x101,
    };
    let low_hook = engine
        .attach(
            low,
            target,
            callbacks(&mut low_trace, 1),
            &[0x999; MAX_SITES],
        )
        .unwrap();
    engine
        .attach(
            high,
            target,
            callbacks(&mut high_trace, 10),
            &[0x999; MAX_SITES],
        )
        .unwrap();
    let call = engine.snapshot(0).unwrap();
    assert_eq!(
        unsafe { call.invoke([1, 2, 3, 4], |a| a.iter().sum()) },
        120
    );
    assert_eq!(high_trace, [1, 60]);
    assert_eq!(low_trace, [11, 30]);
    engine.set_enabled(high, false).unwrap();
    assert_eq!(
        unsafe {
            engine
                .snapshot(0)
                .unwrap()
                .invoke([1, 2, 3, 4], |a| a.iter().sum())
        },
        40
    );
    engine.set_enabled(high, true).unwrap();
    engine.unregister(high).unwrap();
    let stop = engine.register(b"stop").unwrap();
    engine
        .attach(
            stop,
            target,
            Callbacks {
                before: Some(early),
                after: Some(after),
                user_data: &mut high_trace as *mut _ as _,
                priority: 99,
            },
            &[0x999; MAX_SITES],
        )
        .unwrap();
    assert_eq!(
        unsafe {
            engine
                .snapshot(0)
                .unwrap()
                .invoke([0; 4], |_| panic!("original called"))
        },
        14
    );
    engine.unregister(stop).unwrap();
    assert_eq!(engine.memory_mut().word(0x1000), 0x999);
    assert_eq!(engine.detach(high, low_hook), Err(Error::NotFound));
    engine.detach(low, low_hook).unwrap();
    assert_eq!(engine.memory_mut().word(0x1000), 0x101);
    assert_eq!(engine.detach(low, low_hook), Err(Error::NotFound));
}

#[test]
fn typed_replacement_ownership_and_external_writer_conflict() {
    let mut ram = Ram::new();
    ram.pointer(0x1000, 0x123);
    let mut engine = Engine::new(ram);
    let owner = engine.register(b"typed").unwrap();
    let stranger = engine.register(b"stranger").unwrap();
    let target = Target::Pointer {
        slot: 0x1000,
        expected: 0x123,
    };
    let (hook, original) = engine.replace(owner, target, 0x456).unwrap();
    assert_eq!(original, 0x123);
    assert_eq!(
        engine.replace(stranger, target, 0x888),
        Err(Error::Conflict)
    );
    assert_eq!(engine.detach(stranger, hook), Err(Error::NotFound));
    engine.memory_mut().pointer(0x1000, 0x999);
    assert_eq!(engine.unregister(owner), Err(Error::Conflict));
    assert_eq!(engine.memory_mut().word(0x1000), 0x999);
    engine.memory_mut().pointer(0x1000, 0x456);
    engine.unregister(owner).unwrap();
    assert_eq!(engine.memory_mut().word(0x1000), 0x123);
}

fn prologue() -> [u8; 16] {
    [
        0x98, 0xb5, 0x03, 0x46, 0x0c, 0x46, 0x00, 0xaf, 0x19, 0x46, 0x04, 0x48, 0xbc, 0xf7, 0x58,
        0xfa,
    ]
}

#[test]
fn thumb_alignment_and_unsafe_instruction_rejection() {
    for function in [0x2001, 0x2003] {
        let mut code = [0; 16];
        for instruction in code.chunks_exact_mut(2) {
            instruction.copy_from_slice(&[0x00, 0xbf]);
        }
        let plan = thumb::plan(function, 0x4567, 0x3000, code).unwrap();
        let padding = ((function & !1) & 2) as usize;
        assert_eq!(&plan.patch[padding..padding + 4], [0xdf, 0xf8, 0x00, 0xf0]);
        assert_eq!(
            &plan.patch[padding + 4..padding + 8],
            0x4567_u32.to_le_bytes()
        );
        let resume = ((function & !1) + plan.patch_len as u32) | 1;
        assert_eq!(
            &plan.trampoline[plan.trampoline_len - 4..plan.trampoline_len],
            resume.to_le_bytes()
        );
    }
    assert_eq!(
        thumb::plan(0x2001, 0x4567, 0x3000, prologue())
            .unwrap()
            .patch_len,
        8
    );
    for instruction in [
        0x4800u16, 0xa000, 0xe000, 0xd000, 0xbf08, 0x4770, 0xbd10, 0xb100, 0x4678,
    ] {
        let mut code = prologue();
        code[..2].copy_from_slice(&instruction.to_le_bytes());
        assert_eq!(
            thumb::plan(0x2001, 0x4567, 0x3000, code).unwrap_err(),
            Error::Unsupported
        );
    }
    let mut wide = prologue();
    wide[..4].copy_from_slice(&[0x2d, 0xe9, 0xf0, 0x41]);
    assert!(thumb::plan(0x2001, 0x4567, 0x3000, wide).is_ok());
}

#[test]
fn inline_signature_failure_and_publish_rollback_are_recoverable() {
    for failures in [vec![2], vec![2, 3]] {
        let mut ram = Ram::new();
        ram.write(0x2000, &prologue()).unwrap();
        ram.fail_at = failures;
        let mut engine = Engine::new(ram);
        let owner = engine.register(b"inline").unwrap();
        let mut wrong = prologue();
        wrong[0] = 0;
        assert_eq!(
            engine.replace(
                owner,
                Target::Inline {
                    function: 0x2001,
                    expected: wrong
                },
                0x4001
            ),
            Err(Error::Signature)
        );
        let target = Target::Inline {
            function: 0x2001,
            expected: prologue(),
        };
        assert_eq!(engine.replace(owner, target, 0x4001), Err(Error::Memory));
        engine.unregister(owner).unwrap();
        assert_eq!(&engine.memory_mut().bytes[0x2000..0x2010], prologue());
        let owner = engine.register(b"retry").unwrap();
        let (handle, original) = engine.replace(owner, target, 0x4001).unwrap();
        assert_eq!(original, 0x3001);
        assert_eq!(
            engine.replace(
                owner,
                Target::Inline {
                    function: 0x2003,
                    expected: prologue()
                },
                0x5001
            ),
            Err(Error::Conflict)
        );
        engine.detach(owner, handle).unwrap();
        assert_eq!(&engine.memory_mut().bytes[0x2000..0x2010], prologue());
    }
}

#[test]
fn failed_callback_publication_keeps_a_safe_retired_dispatcher() {
    for failures in [vec![2], vec![2, 3]] {
        let mut ram = Ram::new();
        ram.write(0x2000, &prologue()).unwrap();
        ram.fail_at = failures;
        let mut engine = Engine::new(ram);
        let owner = engine.register(b"failed-callback").unwrap();
        let target = Target::Inline {
            function: 0x2001,
            expected: prologue(),
        };
        let mut trace = vec![];
        assert_eq!(
            engine.attach(
                owner,
                target,
                callbacks(&mut trace, 0),
                &[0x4001; MAX_SITES]
            ),
            Err(Error::Memory)
        );
        let orphan = engine.snapshot(0).unwrap();
        assert_eq!(orphan.original, 0x3001);
        assert_eq!(
            unsafe { orphan.invoke([1, 2, 3, 4], |args| args.iter().sum()) },
            10
        );
        assert!(trace.is_empty());
        engine.rollback_all().unwrap();
        assert_eq!(engine.site_count(), 0);
        assert_eq!(engine.vacant_site(), Some(1));
        assert_eq!(&engine.memory_mut().bytes[0x2000..0x2010], prologue());
        assert_eq!(
            unsafe {
                engine
                    .snapshot(0)
                    .unwrap()
                    .invoke([1, 2, 3, 4], |args| args.iter().sum())
            },
            10
        );
    }
}

#[test]
fn emergency_rollback_continues_after_one_site_fails_and_bypasses_callbacks() {
    let mut ram = Ram::new();
    ram.pointer(0x1000, 0x101);
    ram.pointer(0x1010, 0x201);
    let mut engine = Engine::new(ram);
    let owner = engine.register(b"emergency").unwrap();
    let mut trace = vec![];
    engine
        .attach(
            owner,
            Target::Pointer {
                slot: 0x1000,
                expected: 0x101,
            },
            callbacks(&mut trace, 0),
            &[0x999; MAX_SITES],
        )
        .unwrap();
    engine
        .replace(
            owner,
            Target::Pointer {
                slot: 0x1010,
                expected: 0x201,
            },
            0x777,
        )
        .unwrap();
    engine.memory_mut().pointer(0x1000, 0x555); // external writer prevents this restore
    assert_eq!(engine.rollback_all(), Err(Error::Conflict));
    assert_eq!(engine.memory_mut().word(0x1010), 0x201);
    assert_eq!(engine.site_count(), 1);
    assert_eq!(
        unsafe {
            engine
                .snapshot(0)
                .unwrap()
                .invoke([1, 2, 3, 4], |args| args.iter().sum())
        },
        10
    );
    assert!(trace.is_empty());
    engine.memory_mut().pointer(0x1000, 0x999);
    engine.rollback_all().unwrap();
    assert_eq!(engine.site_count(), 0);
}

#[test]
fn raw_module_switch_retains_registration_and_checks_original_on_reenable() {
    let mut ram = Ram::new();
    ram.pointer(0x1000, 0x101);
    let mut engine = Engine::new(ram);
    let owner = engine.register(b"switchable").unwrap();
    engine
        .replace(
            owner,
            Target::Pointer {
                slot: 0x1000,
                expected: 0x101,
            },
            0x999,
        )
        .unwrap();
    engine.set_enabled(owner, false).unwrap();
    assert_eq!(engine.memory_mut().word(0x1000), 0x101);
    assert_eq!(engine.site_count(), 0);
    let mut modules = [veposed_core::ModuleInfo::EMPTY; 16];
    assert_eq!(engine.list_modules(&mut modules), 1);
    assert_eq!(modules[0].hook_count, 1);
    assert_eq!(modules[0].enabled, 0);
    engine.set_enabled(owner, true).unwrap();
    assert_eq!(engine.memory_mut().word(0x1000), 0x999);
    engine.set_enabled(owner, false).unwrap();
    engine.memory_mut().pointer(0x1000, 0x555);
    assert_eq!(engine.set_enabled(owner, true), Err(Error::Conflict));
    assert_eq!(engine.memory_mut().word(0x1000), 0x555);
}
