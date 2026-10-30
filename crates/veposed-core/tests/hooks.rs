use std::ffi::c_void;
use veposed_core::{
    CallContext, Callbacks, CodeMemory, Engine, Error, MAX_SITES, Memory, Result, Target, thumb,
};

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
