#![cfg_attr(target_os = "none", no_std)]
//! Native C ABI. All pointer arguments must be live, aligned and valid for the
//! documented extent. Patching/unloading requires quiescent target threads.
#![allow(clippy::missing_safety_doc)]

use core::{
    cell::UnsafeCell,
    ffi::c_void,
    sync::atomic::{AtomicBool, AtomicUsize, Ordering},
};
use veposed_core::recovery::{self, Guard as BootGuard, RECORD_SIZE};
use veposed_core::{Callbacks, CodeMemory, Engine, Error, MAX_SITES, Memory, Result, Target};

pub use veposed_core::CallContext;
pub const ABI_VERSION: u32 = 4;
#[cfg(any(target_arch = "arm", test))]
mod memory_map;
mod named;
pub use named::{
    HookPointInfo, NamedPoint, veposed_attach_named, veposed_call_named, veposed_call_original,
    veposed_hook_text, veposed_list_hook_points,
};

#[repr(C)]
#[derive(Clone, Copy)]
pub struct Platform {
    pub abi_version: u32,
    pub struct_size: u32,
    /// Clean the data view and invalidate instruction caches for this code range.
    pub publish: Option<unsafe extern "C" fn(usize, usize) -> i32>,
    /// Read exactly 32 bytes: 0=record, 1=missing, 2=external disable, negative=I/O failure.
    pub guard_read: Option<unsafe extern "C" fn(*mut u8) -> i32>,
    /// Persist exactly 32 bytes and synchronize stable storage before returning 0.
    pub guard_write: Option<unsafe extern "C" fn(*const u8) -> i32>,
    pub points: *const NamedPoint,
    pub point_count: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct HookTarget {
    /// 1 = RAM function-pointer slot; 2 = Thumb executable address.
    pub kind: u32,
    pub address: usize,
    pub expected_pointer: usize,
    pub expected_code: [u8; 16],
}

impl HookTarget {
    fn decode(self) -> Result<Target> {
        match self.kind {
            1 => Ok(Target::Pointer {
                slot: self.address,
                expected: self.expected_pointer,
            }),
            2 => Ok(Target::Inline {
                function: self.address,
                expected: self.expected_code,
            }),
            _ => Err(Error::Argument),
        }
    }
}

#[repr(C)]
pub struct HookResult {
    pub handle: u32,
    pub original: usize,
}

/// Stable service table for modules loaded into the same address space.
#[repr(C)]
pub struct Api {
    pub abi_version: u32,
    pub struct_size: u32,
    pub register: unsafe extern "C" fn(*const u8, usize, *mut u32) -> i32,
    pub replace: unsafe extern "C" fn(u32, *const HookTarget, usize, *mut HookResult) -> i32,
    pub attach: unsafe extern "C" fn(u32, *const HookTarget, *const Callbacks, *mut u32) -> i32,
    pub detach: extern "C" fn(u32, u32) -> i32,
    pub set_enabled: extern "C" fn(u32, u32) -> i32,
    pub unregister: extern "C" fn(u32) -> i32,
    pub recovery_status: unsafe extern "C" fn(*mut RecoveryStatus) -> i32,
    pub enter_safe_mode: extern "C" fn() -> i32,
    pub recovery_reset: extern "C" fn() -> i32,
    pub list_modules: unsafe extern "C" fn(*mut veposed_core::ModuleInfo, usize, *mut u32) -> i32,
    pub attach_named: unsafe extern "C" fn(u32, *const u8, *const Callbacks, *mut u32) -> i32,
    pub hook_text: unsafe extern "C" fn(u32, *const u8, *const u8, *mut u32) -> i32,
    pub list_hook_points: unsafe extern "C" fn(*mut HookPointInfo, usize, *mut u32) -> i32,
    pub call_original: unsafe extern "C" fn(*mut CallContext) -> usize,
    pub call_named: unsafe extern "C" fn(*const u8, *const usize, *mut usize) -> i32,
}

#[repr(C)]
pub struct RecoveryStatus {
    pub mode: u32,
    pub reason: u32,
    pub failed_sessions: u32,
    pub active_sites: u32,
    pub last_error: i32,
    pub rollback_error: i32,
}

static API: Api = Api {
    abi_version: ABI_VERSION,
    struct_size: core::mem::size_of::<Api>() as u32,
    register: veposed_register,
    replace: veposed_replace,
    attach: veposed_attach,
    detach: veposed_detach,
    set_enabled: veposed_set_enabled,
    unregister: veposed_unregister,
    recovery_status: veposed_recovery_status,
    enter_safe_mode: veposed_enter_safe_mode,
    recovery_reset: veposed_recovery_reset,
    list_modules: veposed_list_modules,
    attach_named: veposed_attach_named,
    hook_text: veposed_hook_text,
    list_hook_points: veposed_list_hook_points,
    call_original: veposed_call_original,
    call_named: veposed_call_named,
};

#[unsafe(no_mangle)]
pub extern "C" fn veposed_get_api() -> *const Api {
    &API
}

struct NativeMemory {
    publish: Option<unsafe extern "C" fn(usize, usize) -> i32>,
}

#[cfg(target_arch = "arm")]
core::arch::global_asm!(
    ".section .text.veposed_trampolines,\"ax\",%progbits",
    ".balign 4",
    ".global veposed_trampolines",
    "veposed_trampolines:",
    ".space 512",
    ".previous",
);

#[cfg(target_arch = "arm")]
unsafe extern "C" {
    static veposed_trampolines: u8;
}

fn writable(address: usize, size: usize) -> bool {
    #[cfg(target_arch = "arm")]
    {
        memory_map::writable(address, size)
    }
    #[cfg(not(target_arch = "arm"))]
    {
        address != 0 && address.checked_add(size).is_some()
    }
}

impl Memory for NativeMemory {
    fn read(&self, address: usize, output: &mut [u8]) -> Result<()> {
        if !writable(address, output.len()) {
            return Err(Error::Memory);
        }
        for (i, byte) in output.iter_mut().enumerate() {
            *byte = unsafe { (address as *const u8).add(i).read_volatile() };
        }
        Ok(())
    }

    fn write(&mut self, address: usize, bytes: &[u8]) -> Result<()> {
        if !writable(address, bytes.len()) {
            return Err(Error::Memory);
        }
        // A pointer slot is updated by one naturally aligned native-word store.
        if bytes.len() == core::mem::size_of::<usize>()
            && address.is_multiple_of(core::mem::align_of::<usize>())
        {
            let mut word = [0; core::mem::size_of::<usize>()];
            word.copy_from_slice(bytes);
            unsafe { (address as *mut usize).write_volatile(usize::from_le_bytes(word)) };
        } else {
            for (i, byte) in bytes.iter().enumerate() {
                unsafe { (address as *mut u8).add(i).write_volatile(*byte) };
            }
        }
        Ok(())
    }

    fn code(&self, execute: usize, length: usize) -> Result<CodeMemory> {
        #[cfg(target_arch = "arm")]
        {
            memory_map::code(execute, length).ok_or(Error::Unsupported)
        }
        #[cfg(not(target_arch = "arm"))]
        {
            let _ = (execute, length);
            Err(Error::Unsupported)
        }
    }

    fn trampoline(&self, index: usize) -> Result<CodeMemory> {
        #[cfg(target_arch = "arm")]
        {
            self.code(
                core::ptr::addr_of!(veposed_trampolines) as usize + index * 32,
                32,
            )
        }
        #[cfg(not(target_arch = "arm"))]
        {
            let _ = index;
            Err(Error::Unsupported)
        }
    }

    fn publish(&mut self, execute: usize, length: usize) -> Result<()> {
        let publish = self.publish.ok_or(Error::Unsupported)?;
        if unsafe { publish(execute, length) } == 0 {
            Ok(())
        } else {
            Err(Error::Memory)
        }
    }
}

struct State {
    engine: Engine<NativeMemory>,
    ready: bool,
    guard: BootGuard,
    guard_write: Option<unsafe extern "C" fn(*const u8) -> i32>,
    rollback_error: i32,
    named: named::Registry,
}
struct Global(UnsafeCell<State>);
// Every access is protected by Gate. Snapshots own their callback table.
unsafe impl Sync for Global {}
static STATE: Global = Global(UnsafeCell::new(State {
    engine: Engine::new(NativeMemory { publish: None }),
    ready: false,
    guard: BootGuard::fresh(),
    guard_write: None,
    rollback_error: 0,
    named: named::Registry::new(),
}));
static LOCK: AtomicBool = AtomicBool::new(false);
static IN_FLIGHT: AtomicUsize = AtomicUsize::new(0);
static MUTATING: AtomicBool = AtomicBool::new(false);

struct Mutation;
impl Mutation {
    fn acquire() -> Result<Self> {
        MUTATING
            .compare_exchange(false, true, Ordering::Acquire, Ordering::Relaxed)
            .map(|_| Self)
            .map_err(|_| Error::Busy)
    }
}
impl Drop for Mutation {
    fn drop(&mut self) {
        MUTATING.store(false, Ordering::Release);
    }
}

struct Gate {
    #[cfg(target_arch = "arm")]
    primask: u32,
}

impl Gate {
    fn acquire() -> Self {
        #[cfg(target_arch = "arm")]
        let primask: u32;
        #[cfg(target_arch = "arm")]
        unsafe {
            core::arch::asm!("mrs {}, PRIMASK", "cpsid i", out(reg) primask, options(nostack));
        }
        while LOCK
            .compare_exchange_weak(false, true, Ordering::Acquire, Ordering::Relaxed)
            .is_err()
        {
            core::hint::spin_loop();
        }
        Self {
            #[cfg(target_arch = "arm")]
            primask,
        }
    }
}

impl Drop for Gate {
    fn drop(&mut self) {
        LOCK.store(false, Ordering::Release);
        #[cfg(target_arch = "arm")]
        unsafe {
            core::arch::asm!("msr PRIMASK, {}", in(reg) self.primask, options(nostack));
        }
    }
}

// Filesystem callbacks run with interrupts enabled and without holding Gate.
// Mutation keeps other management calls out while ordinary invocations can run.
fn persist_guard(mut next: BootGuard) -> Result<()> {
    let writer = {
        let _gate = Gate::acquire();
        unsafe { (*STATE.0.get()).guard_write }
    };
    let bytes = next.record.encode();
    let ok = writer.is_some_and(|write| unsafe { write(bytes.as_ptr()) == 0 });
    if !ok {
        next = next.lock(recovery::STORAGE_FAILURE, Error::Storage as i32);
    }
    {
        let _gate = Gate::acquire();
        unsafe {
            (*STATE.0.get()).guard = next;
        }
    }
    if ok { Ok(()) } else { Err(Error::Storage) }
}

fn quarantine(reason: u32, error: i32) -> Result<()> {
    let (guard, rollback) = {
        let _gate = Gate::acquire();
        let state = unsafe { &mut *STATE.0.get() };
        state.guard = state.guard.lock(reason, error);
        let rollback = if IN_FLIGHT.load(Ordering::Acquire) == 0 {
            state.engine.rollback_all()
        } else {
            Err(Error::Busy)
        };
        state.named.prune(&state.engine);
        state.rollback_error = rollback.err().map_or(0, |e| e as i32);
        (state.guard, rollback)
    };
    let persisted = persist_guard(guard);
    rollback.and(persisted)
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum Operation {
    Configure,
    Install,
    NamedInstall,
    Cleanup,
}

fn mutate(operation: Operation, f: impl FnOnce(&mut Engine<NativeMemory>) -> Result<()>) -> i32 {
    mutate_state(operation, |state| f(&mut state.engine))
}

fn mutate_state(operation: Operation, f: impl FnOnce(&mut State) -> Result<()>) -> i32 {
    let _mutation = match Mutation::acquire() {
        Ok(guard) => guard,
        Err(e) => return e as i32,
    };
    let guard = {
        let _gate = Gate::acquire();
        let state = unsafe { &*STATE.0.get() };
        if !state.ready {
            return Error::Abi as i32;
        }
        if IN_FLIGHT.load(Ordering::Acquire) != 0 {
            return Error::Busy as i32;
        }
        if state.guard.safe && operation != Operation::Cleanup {
            return Error::SafeMode as i32;
        }
        state.guard
    };
    if matches!(operation, Operation::Install | Operation::NamedInstall)
        && guard.record.phase != recovery::ARMED
    {
        let next = match guard.arm() {
            Ok(next) => next,
            Err(e) => return e as i32,
        };
        if let Err(error) = persist_guard(next) {
            return error as i32;
        }
    }
    let result = {
        let _gate = Gate::acquire();
        // An invocation can start while the journal is synchronized.
        if IN_FLIGHT.load(Ordering::Acquire) != 0 {
            return Error::Busy as i32;
        }
        let state = unsafe { &mut *STATE.0.get() };
        let result = f(state);
        state.named.prune(&state.engine);
        result
    };
    if let Err(error) = result {
        if operation == Operation::Install
            || (operation == Operation::NamedInstall
                && matches!(error, Error::Signature | Error::Memory | Error::Unsupported))
            || (operation == Operation::Cleanup && matches!(error, Error::Memory | Error::Conflict))
        {
            let _ = quarantine(recovery::HOOK_FAILURE, error as i32);
        }
        return error as i32;
    }
    let closed = {
        let _gate = Gate::acquire();
        let state = unsafe { &*STATE.0.get() };
        if state.engine.site_count() == 0
            && !state.guard.safe
            && state.guard.record.phase == recovery::ARMED
        {
            Some(state.guard.close())
        } else {
            None
        }
    };
    if let Some(closed) = closed
        && let Err(error) = persist_guard(closed)
    {
        return error as i32;
    }
    0
}

#[cfg(target_arch = "arm")]
unsafe fn firmware_matches() -> bool {
    let probes: &[(usize, &[u8])] = &[
        (0x0c0c_0810, b"3.101.043\0"),
        (0x0c0c_0850, b"CONBINE_LTALM078_T3.101.043_08041658\0"),
    ];
    probes.iter().all(|(address, expected)| {
        expected
            .iter()
            .enumerate()
            .all(|(i, b)| unsafe { ((*address as *const u8).add(i)).read_volatile() == *b })
    })
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_init(platform: *const Platform) -> i32 {
    if platform.is_null() {
        return Error::Argument as i32;
    }
    // Read the stable prefix before touching fields added by later ABI versions.
    let version = unsafe { core::ptr::addr_of!((*platform).abi_version).read() };
    let size = unsafe { core::ptr::addr_of!((*platform).struct_size).read() };
    if version != ABI_VERSION || size as usize != core::mem::size_of::<Platform>() {
        return Error::Abi as i32;
    }
    let platform = unsafe { *platform };
    #[cfg(target_arch = "arm")]
    if !unsafe { firmware_matches() } {
        return Error::Firmware as i32;
    }
    let _mutation = match Mutation::acquire() {
        Ok(guard) => guard,
        Err(e) => return e as i32,
    };
    {
        let _gate = Gate::acquire();
        let state = unsafe { &mut *STATE.0.get() };
        if state.ready {
            return Error::Conflict as i32;
        }
        if let Err(error) = unsafe { state.named.configure(platform.points, platform.point_count) }
        {
            return error as i32;
        }
        state.engine.memory_mut().publish = platform.publish;
        state.guard_write = platform.guard_write;
    }
    let mut bytes = [0; RECORD_SIZE];
    let read = if platform.guard_write.is_some() {
        platform
            .guard_read
            .map_or(-1, |read| unsafe { read(bytes.as_mut_ptr()) })
    } else {
        -1
    };
    let (guard, checkpoint) = BootGuard::boot(read, &bytes);
    {
        let _gate = Gate::acquire();
        unsafe {
            (*STATE.0.get()).guard = guard;
        }
    }
    if checkpoint {
        let _ = persist_guard(guard);
    }
    {
        let _gate = Gate::acquire();
        unsafe {
            (*STATE.0.get()).ready = true;
        }
    }
    0
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_register(name: *const u8, length: usize, owner: *mut u32) -> i32 {
    if name.is_null() || owner.is_null() || length == 0 || length > 48 {
        return Error::Argument as i32;
    }
    mutate(Operation::Configure, |engine| {
        let token = engine.register(unsafe { core::slice::from_raw_parts(name, length) })?;
        unsafe {
            owner.write(token);
        }
        Ok(())
    })
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_replace(
    owner: u32,
    target: *const HookTarget,
    replacement: usize,
    output: *mut HookResult,
) -> i32 {
    if target.is_null() || output.is_null() {
        return Error::Argument as i32;
    }
    mutate(Operation::Install, |engine| {
        let (handle, original) =
            engine.replace(owner, unsafe { *target }.decode()?, replacement)?;
        unsafe {
            output.write(HookResult { handle, original });
        }
        Ok(())
    })
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_attach(
    owner: u32,
    target: *const HookTarget,
    callbacks: *const Callbacks,
    handle: *mut u32,
) -> i32 {
    if target.is_null() || callbacks.is_null() || handle.is_null() {
        return Error::Argument as i32;
    }
    mutate_state(Operation::Install, |state| {
        let target = unsafe { *target }.decode()?;
        if state
            .engine
            .target_site(target)
            .is_some_and(|i| state.named.site_kind(i).is_some())
        {
            return Err(Error::Conflict);
        }
        let token = state
            .engine
            .attach(owner, target, unsafe { *callbacks }, &thunks())?;
        unsafe {
            handle.write(token);
        }
        Ok(())
    })
}

#[unsafe(no_mangle)]
pub extern "C" fn veposed_detach(owner: u32, handle: u32) -> i32 {
    mutate(Operation::Cleanup, |engine| engine.detach(owner, handle))
}

#[unsafe(no_mangle)]
pub extern "C" fn veposed_set_enabled(owner: u32, enabled: u32) -> i32 {
    mutate(
        if enabled == 0 {
            Operation::Cleanup
        } else {
            Operation::Install
        },
        |engine| engine.set_enabled(owner, enabled != 0),
    )
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_list_modules(
    output: *mut veposed_core::ModuleInfo,
    capacity: usize,
    count: *mut u32,
) -> i32 {
    if output.is_null() || count.is_null() || capacity == 0 || capacity > veposed_core::MAX_MODULES
    {
        return Error::Argument as i32;
    }
    let _gate = Gate::acquire();
    let state = unsafe { &*STATE.0.get() };
    if !state.ready {
        return Error::Abi as i32;
    }
    let output = unsafe { core::slice::from_raw_parts_mut(output, capacity) };
    unsafe {
        count.write(state.engine.list_modules(output) as u32);
    }
    0
}

#[unsafe(no_mangle)]
pub extern "C" fn veposed_unregister(owner: u32) -> i32 {
    mutate(Operation::Cleanup, |engine| engine.unregister(owner))
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_recovery_status(output: *mut RecoveryStatus) -> i32 {
    if output.is_null() {
        return Error::Argument as i32;
    }
    let _gate = Gate::acquire();
    let state = unsafe { &*STATE.0.get() };
    if !state.ready {
        return Error::Abi as i32;
    }
    unsafe {
        output.write(RecoveryStatus {
            mode: if state.guard.safe {
                recovery::LOCKED
            } else {
                state.guard.record.phase
            },
            reason: state.guard.record.reason,
            failed_sessions: state.guard.record.failures,
            active_sites: state.engine.site_count() as u32,
            last_error: state.guard.record.last_error,
            rollback_error: state.rollback_error,
        });
    }
    0
}

#[unsafe(no_mangle)]
pub extern "C" fn veposed_enter_safe_mode() -> i32 {
    let _mutation = match Mutation::acquire() {
        Ok(guard) => guard,
        Err(e) => return e as i32,
    };
    {
        let _gate = Gate::acquire();
        if !unsafe { (*STATE.0.get()).ready } {
            return Error::Abi as i32;
        }
    }
    quarantine(recovery::MANUAL, 0).map_or_else(|e| e as i32, |_| 0)
}

#[unsafe(no_mangle)]
pub extern "C" fn veposed_recovery_reset() -> i32 {
    let _mutation = match Mutation::acquire() {
        Ok(guard) => guard,
        Err(e) => return e as i32,
    };
    let guard = {
        let _gate = Gate::acquire();
        let state = unsafe { &*STATE.0.get() };
        if !state.ready {
            return Error::Abi as i32;
        }
        if !state.guard.safe {
            return Error::Conflict as i32;
        }
        if IN_FLIGHT.load(Ordering::Acquire) != 0 || state.engine.site_count() != 0 {
            return Error::Busy as i32;
        }
        state.guard.close()
    };
    persist_guard(guard).map_or_else(|e| e as i32, |_| 0)
}

fn dispatch(index: usize, args: [usize; 4]) -> usize {
    let invocation = {
        let _gate = Gate::acquire();
        let state = unsafe { &*STATE.0.get() };
        let Ok(snapshot) = state.engine.snapshot(index) else {
            return 0;
        };
        IN_FLIGHT.fetch_add(1, Ordering::Release);
        if state.guard.safe {
            snapshot.bypass_callbacks()
        } else {
            snapshot
        }
    };
    let original: unsafe extern "C" fn(usize, usize, usize, usize) -> usize =
        unsafe { core::mem::transmute(invocation.original) };
    let result = unsafe { invocation.invoke(args, |a| original(a[0], a[1], a[2], a[3])) };
    IN_FLIGHT.fetch_sub(1, Ordering::Release);
    result
}

macro_rules! dispatchers {
    ($($name:ident => $index:expr),* $(,)?) => {
        $(extern "C" fn $name(a: usize, b: usize, c: usize, d: usize) -> usize {
            dispatch($index, [a, b, c, d])
        })*
        fn thunks() -> [usize; MAX_SITES] { [$($name as *const () as usize),*] }
    };
}
dispatchers!(
    entry0 => 0, entry1 => 1, entry2 => 2, entry3 => 3,
    entry4 => 4, entry5 => 5, entry6 => 6, entry7 => 7,
    entry8 => 8, entry9 => 9, entry10 => 10, entry11 => 11,
    entry12 => 12, entry13 => 13, entry14 => 14, entry15 => 15,
);

/// Symbols referenced by freestanding Rust/compiler-builtins and C modules.
#[cfg(target_os = "none")]
#[unsafe(no_mangle)]
pub unsafe extern "C" fn memcpy(dst: *mut u8, src: *const u8, count: usize) -> *mut u8 {
    for i in 0..count {
        unsafe {
            dst.add(i).write_volatile(src.add(i).read_volatile());
        }
    }
    dst
}

#[cfg(target_os = "none")]
#[unsafe(no_mangle)]
pub unsafe extern "C" fn memmove(dst: *mut u8, src: *const u8, count: usize) -> *mut u8 {
    if (dst as usize) <= src as usize {
        return unsafe { memcpy(dst, src, count) };
    }
    for i in (0..count).rev() {
        unsafe {
            dst.add(i).write_volatile(src.add(i).read_volatile());
        }
    }
    dst
}

#[cfg(target_os = "none")]
#[unsafe(no_mangle)]
pub unsafe extern "C" fn memset(dst: *mut u8, value: i32, count: usize) -> *mut u8 {
    for i in 0..count {
        unsafe {
            dst.add(i).write_volatile(value as u8);
        }
    }
    dst
}

#[cfg(target_os = "none")]
#[unsafe(no_mangle)]
pub unsafe extern "C" fn memcmp(left: *const u8, right: *const u8, count: usize) -> i32 {
    for i in 0..count {
        let a = unsafe { left.add(i).read_volatile() };
        let b = unsafe { right.add(i).read_volatile() };
        if a != b {
            return a as i32 - b as i32;
        }
    }
    0
}

#[cfg(target_os = "none")]
#[panic_handler]
fn panic(_: &core::panic::PanicInfo<'_>) -> ! {
    // The durable ARMED lease remains intact. Request one Cortex-M reset;
    // the following load enters safe mode instead of repeating the hook.
    #[cfg(target_arch = "arm")]
    unsafe {
        core::arch::asm!("cpsid i", "dsb", options(nostack));
        let aircr = 0xe000_ed0c as *mut u32;
        aircr.write_volatile(0x05fa_0004 | (aircr.read_volatile() & 0x700));
        core::arch::asm!("dsb", "isb", options(nostack));
    }
    loop {
        core::hint::spin_loop();
    }
}

// Keep the C ABI callback's user-data type visible in rustdoc.
const _: Option<*mut c_void> = None;
