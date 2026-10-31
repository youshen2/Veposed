#![no_std]
//! Allocation-free native hook ownership and Xposed-style callback dispatch.

pub mod recovery;
pub mod thumb;

use core::ffi::c_void;

pub const MAX_MODULES: usize = 16;
pub const MAX_SITES: usize = 32;
pub const MAX_CALLBACKS: usize = 32;
pub type Result<T> = core::result::Result<T, Error>;

#[repr(i32)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    Argument = -1,
    Capacity = -2,
    NotFound = -3,
    Conflict = -4,
    Unsupported = -5,
    Signature = -6,
    Memory = -7,
    Busy = -8,
    Firmware = -9,
    Abi = -10,
    SafeMode = -11,
    Storage = -12,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Target {
    Pointer { slot: usize, expected: usize },
    Inline { function: usize, expected: [u8; 16] },
}

impl Target {
    fn key(self) -> (u8, usize) {
        match self {
            Self::Pointer { slot, .. } => (0, slot),
            Self::Inline { function, .. } => (1, function & !1),
        }
    }
}

#[derive(Clone, Copy)]
pub struct CodeMemory {
    pub execute: usize,
    pub write: usize,
}

/// Platform operations are serialized by the caller. A failed write must leave
/// memory unchanged. A failed publish may have written bytes; the engine rolls
/// them back and retains their ownership until restoration succeeds.
pub trait Memory {
    fn read(&self, address: usize, output: &mut [u8]) -> Result<()>;
    fn write(&mut self, address: usize, bytes: &[u8]) -> Result<()>;
    fn code(&self, execute: usize, length: usize) -> Result<CodeMemory>;
    fn trampoline(&self, index: usize) -> Result<CodeMemory>;
    fn publish(&mut self, execute: usize, length: usize) -> Result<()>;
}

#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct CallContext {
    pub args: [usize; 4],
    pub result: usize,
    /// A before callback sets this to one to skip the original and remaining before callbacks.
    pub return_early: u32,
    /// Read-only original entry and calling contract supplied by the runtime.
    pub original: usize,
    pub contract: u32,
}

pub type Callback = unsafe extern "C" fn(*mut CallContext, *mut c_void);

#[repr(C)]
#[derive(Clone, Copy)]
pub struct Callbacks {
    pub before: Option<Callback>,
    pub after: Option<Callback>,
    pub user_data: *mut c_void,
    pub priority: i32,
}

#[derive(Clone, Copy)]
struct Listener {
    token: u32,
    owner: u32,
    enabled: bool,
    callbacks: Callbacks,
}

#[derive(Clone, Copy)]
struct Module {
    token: u32,
    name: [u8; 48],
    name_len: usize,
    enabled: bool,
}

#[derive(Clone, Copy)]
enum Patch {
    Pointer {
        slot: usize,
        original: usize,
        installed: usize,
    },
    Inline {
        memory: CodeMemory,
        plan: thumb::Plan,
    },
}

#[derive(Clone, Copy)]
struct Site {
    target: Target,
    original: usize,
    patch: Patch,
    listeners: [Option<Listener>; MAX_CALLBACKS],
    raw_owner: Option<u32>,
    token: u32,
    installed: bool,
    // A suspended caller may still hold the dispatcher address. Never reuse it
    // until the runtime itself is restarted with all old callers gone.
    retired: bool,
}

impl Site {
    fn retire(mut self) -> Self {
        self.installed = false;
        self.retired = true;
        self.listeners = [None; MAX_CALLBACKS];
        self
    }
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct ModuleInfo {
    pub id: u32,
    pub name: [u8; 48],
    pub name_len: u32,
    pub enabled: u32,
    pub hook_count: u32,
}

impl ModuleInfo {
    pub const EMPTY: Self = Self {
        id: 0,
        name: [0; 48],
        name_len: 0,
        enabled: 0,
        hook_count: 0,
    };
}

#[derive(Clone, Copy)]
pub struct Invocation {
    pub original: usize,
    listeners: [Option<Listener>; MAX_CALLBACKS],
}

impl Invocation {
    pub fn bypass_callbacks(mut self) -> Self {
        self.listeners = [None; MAX_CALLBACKS];
        self
    }
    /// Invoke a four-word integer/pointer ABI hook. Floating-point, variadic,
    /// aggregate-return and stack-argument functions require a typed raw hook.
    ///
    /// # Safety
    /// Registered callback pointers and user data must remain valid for this call.
    pub unsafe fn invoke(
        &self,
        args: [usize; 4],
        original: impl FnOnce([usize; 4]) -> usize,
    ) -> usize {
        unsafe { self.invoke_scoped(args, 3, |_, _| true, original) }
    }

    /// Apply a per-listener scope once, before callbacks change the arguments.
    /// Only callbacks entered in this invocation receive an after callback.
    ///
    /// # Safety
    /// The callback and user-data lifetime requirements are identical to `invoke`.
    pub unsafe fn invoke_scoped(
        &self,
        args: [usize; 4],
        contract: u32,
        mut matches: impl FnMut(u32, u32) -> bool,
        original: impl FnOnce([usize; 4]) -> usize,
    ) -> usize {
        let mut context = CallContext {
            args,
            result: 0,
            return_early: 0,
            original: self.original,
            contract,
        };
        let mut entered = [0; MAX_CALLBACKS];
        let mut count = 0;
        for (index, listener) in self.listeners.iter().enumerate() {
            let Some(listener) = listener.as_ref().filter(|l| l.enabled) else {
                continue;
            };
            if !matches(listener.owner, listener.token) {
                continue;
            }
            entered[count] = index;
            count += 1;
            if let Some(callback) = listener.callbacks.before {
                unsafe { callback(&mut context, listener.callbacks.user_data) };
            }
            if context.return_early != 0 {
                break;
            }
        }
        if context.return_early == 0 {
            context.result = original(context.args);
        }
        for index in entered[..count].iter().rev() {
            let listener = self.listeners[*index].as_ref().unwrap();
            if let Some(callback) = listener.callbacks.after {
                unsafe { callback(&mut context, listener.callbacks.user_data) };
            }
        }
        context.result
    }
}

pub struct Engine<M> {
    memory: M,
    modules: [Option<Module>; MAX_MODULES],
    sites: [Option<Site>; MAX_SITES],
    next_token: u32,
}

impl<M: Memory> Engine<M> {
    pub const fn new(memory: M) -> Self {
        Self {
            memory,
            modules: [None; MAX_MODULES],
            sites: [None; MAX_SITES],
            next_token: 1,
        }
    }

    pub fn memory_mut(&mut self) -> &mut M {
        &mut self.memory
    }

    pub fn site_count(&self) -> usize {
        self.sites.iter().flatten().filter(|s| s.installed).count()
    }

    pub fn vacant_site(&self) -> Option<usize> {
        self.sites.iter().position(Option::is_none)
    }

    pub fn target_site(&self, target: Target) -> Option<usize> {
        self.sites
            .iter()
            .position(|s| s.is_some_and(|s| !s.retired && s.target.key() == target.key()))
    }

    pub fn original_for(&self, target: Target) -> Option<usize> {
        self.target_site(target)
            .and_then(|i| self.sites[i].map(|s| s.original))
    }

    pub fn hook_site(&self, owner: u32, token: u32) -> Option<usize> {
        self.sites.iter().position(|s| {
            s.is_some_and(|s| {
                (s.raw_owner == Some(owner) && s.token == token)
                    || s.listeners
                        .iter()
                        .flatten()
                        .any(|l| l.owner == owner && l.token == token)
            })
        })
    }

    pub fn list_modules(&self, output: &mut [ModuleInfo]) -> usize {
        let mut count = 0;
        for (module, info) in self.modules.iter().flatten().zip(output.iter_mut()) {
            *info = ModuleInfo {
                id: module.token,
                name: module.name,
                name_len: module.name_len as u32,
                enabled: module.enabled as u32,
                hook_count: self
                    .sites
                    .iter()
                    .flatten()
                    .map(|site| {
                        if site.raw_owner == Some(module.token) {
                            1
                        } else {
                            site.listeners
                                .iter()
                                .flatten()
                                .filter(|l| l.owner == module.token)
                                .count()
                        }
                    })
                    .sum::<usize>() as u32,
            };
            count += 1;
        }
        count
    }

    /// Quarantine callbacks before restoring every physical site. Continue past
    /// individual failures and retain those records for a subsequent retry.
    pub fn rollback_all(&mut self) -> Result<()> {
        self.rollback_where(|_| true)
    }

    /// Retain sites whose restore condition is not yet met, while restoring
    /// other sites and keeping every callback disabled for a later retry.
    pub fn rollback_where(&mut self, mut can_restore: impl FnMut(usize) -> bool) -> Result<()> {
        for module in self.modules.iter_mut().flatten() {
            module.enabled = false;
        }
        for site in self.sites.iter_mut().flatten() {
            for listener in site.listeners.iter_mut().flatten() {
                listener.enabled = false;
            }
        }
        let mut failure = None;
        for index in (0..MAX_SITES).rev() {
            if let Some(site) = self.sites[index] {
                if site.retired {
                    continue;
                }
                if !site.installed {
                    self.sites[index] = None;
                    continue;
                }
                if !can_restore(index) {
                    failure.get_or_insert(Error::Busy);
                    continue;
                }
                match self.restore(site.patch) {
                    Ok(()) => {
                        self.sites[index] = if site.raw_owner.is_some() {
                            None
                        } else {
                            Some(site.retire())
                        }
                    }
                    Err(error) => {
                        failure.get_or_insert(error);
                    }
                }
            }
        }
        failure.map_or(Ok(()), Err)
    }

    fn token(&mut self) -> Result<u32> {
        let token = self.next_token;
        self.next_token = token.checked_add(1).ok_or(Error::Capacity)?;
        Ok(token)
    }

    pub fn register(&mut self, name: &[u8]) -> Result<u32> {
        if name.is_empty()
            || name.len() > 48
            || !name
                .iter()
                .all(|b| b.is_ascii_alphanumeric() || b"._-".contains(b))
        {
            return Err(Error::Argument);
        }
        if self
            .modules
            .iter()
            .flatten()
            .any(|m| &m.name[..m.name_len] == name)
        {
            return Err(Error::Conflict);
        }
        let index = self
            .modules
            .iter()
            .position(Option::is_none)
            .ok_or(Error::Capacity)?;
        let token = self.token()?;
        let mut module = Module {
            token,
            name: [0; 48],
            name_len: name.len(),
            enabled: true,
        };
        module.name[..name.len()].copy_from_slice(name);
        self.modules[index] = Some(module);
        Ok(token)
    }

    fn module(&self, token: u32) -> Result<&Module> {
        self.modules
            .iter()
            .flatten()
            .find(|m| m.token == token)
            .ok_or(Error::NotFound)
    }

    fn overlaps(&self, target: Target) -> Result<bool> {
        let (start, size) = match target {
            Target::Pointer { slot, .. } => (slot, core::mem::size_of::<usize>()),
            Target::Inline { function, .. } => (self.memory.code(function & !1, 16)?.write, 16),
        };
        let end = start.checked_add(size).ok_or(Error::Argument)?;
        Ok(self
            .sites
            .iter()
            .flatten()
            .filter(|site| !site.retired)
            .any(|site| {
                let (other, size) = match site.patch {
                    Patch::Pointer { slot, .. } => (slot, core::mem::size_of::<usize>()),
                    Patch::Inline { memory, .. } => (memory.write, 16),
                };
                start < other.saturating_add(size) && other < end
            }))
    }

    fn prepare(
        &mut self,
        index: usize,
        target: Target,
        replacement: usize,
    ) -> Result<(Patch, usize)> {
        if replacement == 0 {
            return Err(Error::Argument);
        }
        match target {
            Target::Pointer { slot, expected } => {
                if slot == 0 || slot % core::mem::size_of::<usize>() != 0 || expected == 0 {
                    return Err(Error::Argument);
                }
                let mut bytes = [0; core::mem::size_of::<usize>()];
                self.memory.read(slot, &mut bytes)?;
                let original = usize::from_le_bytes(bytes);
                if original != expected {
                    return Err(Error::Signature);
                }
                Ok((
                    Patch::Pointer {
                        slot,
                        original,
                        installed: replacement,
                    },
                    original,
                ))
            }
            Target::Inline { function, expected } => {
                let entry = function & !1;
                let memory = self.memory.code(entry, 16)?;
                let mut actual = [0; 16];
                self.memory.read(memory.write, &mut actual)?;
                if actual != expected {
                    return Err(Error::Signature);
                }
                let trampoline = self.memory.trampoline(index)?;
                let plan = thumb::plan(
                    u32::try_from(function).map_err(|_| Error::Argument)?,
                    u32::try_from(replacement).map_err(|_| Error::Argument)?,
                    u32::try_from(trampoline.execute).map_err(|_| Error::Argument)?,
                    actual,
                )?;
                self.memory
                    .write(trampoline.write, &plan.trampoline[..plan.trampoline_len])?;
                self.memory
                    .publish(trampoline.execute, plan.trampoline_len)?;
                Ok((Patch::Inline { memory, plan }, trampoline.execute | 1))
            }
        }
    }

    fn apply(&mut self, patch: Patch) -> Result<()> {
        match patch {
            Patch::Pointer {
                slot, installed, ..
            } => self.memory.write(slot, &installed.to_le_bytes()),
            Patch::Inline { memory, plan } => {
                self.memory
                    .write(memory.write, &plan.patch[..plan.patch_len])?;
                self.memory.publish(memory.execute, plan.patch_len)
            }
        }
    }

    fn restore(&mut self, patch: Patch) -> Result<()> {
        match patch {
            Patch::Pointer {
                slot,
                original,
                installed,
            } => {
                let mut bytes = [0; core::mem::size_of::<usize>()];
                self.memory.read(slot, &mut bytes)?;
                // Do not overwrite another patcher's later change.
                let current = usize::from_le_bytes(bytes);
                if current != installed && current != original {
                    return Err(Error::Conflict);
                }
                self.memory.write(slot, &original.to_le_bytes())
            }
            Patch::Inline { memory, plan } => {
                let mut bytes = [0; 16];
                self.memory
                    .read(memory.write, &mut bytes[..plan.patch_len])?;
                if bytes[..plan.patch_len] != plan.patch[..plan.patch_len]
                    && bytes[..plan.patch_len] != plan.saved[..plan.patch_len]
                {
                    return Err(Error::Conflict);
                }
                self.memory
                    .write(memory.write, &plan.saved[..plan.patch_len])?;
                self.memory.publish(memory.execute, plan.patch_len)
            }
        }
    }

    fn install(&mut self, index: usize, site: Site) -> Result<()> {
        // Retain ownership if both publication and rollback fail, allowing a retry.
        self.sites[index] = Some(site);
        if let Err(error) = self.apply(site.patch) {
            // A failed publication may already have exposed the dispatcher.
            // Disable callbacks even if restoration itself also fails.
            let mut abandoned = site;
            abandoned.listeners = [None; MAX_CALLBACKS];
            self.sites[index] = Some(abandoned);
            if self.restore(site.patch).is_ok() {
                self.sites[index] = if site.raw_owner.is_some() {
                    None
                } else {
                    Some(abandoned.retire())
                };
            }
            return Err(error);
        }
        Ok(())
    }

    pub fn replace(
        &mut self,
        owner: u32,
        target: Target,
        replacement: usize,
    ) -> Result<(u32, usize)> {
        if !self.module(owner)?.enabled {
            return Err(Error::Busy);
        }
        if self.overlaps(target)? {
            return Err(Error::Conflict);
        }
        let index = self
            .sites
            .iter()
            .position(Option::is_none)
            .ok_or(Error::Capacity)?;
        let token = self.token()?;
        let (patch, original) = self.prepare(index, target, replacement)?;
        self.install(
            index,
            Site {
                target,
                original,
                patch,
                listeners: [None; MAX_CALLBACKS],
                raw_owner: Some(owner),
                token,
                installed: true,
                retired: false,
            },
        )?;
        Ok((token, original))
    }

    pub fn attach(
        &mut self,
        owner: u32,
        target: Target,
        callbacks: Callbacks,
        thunks: &[usize; MAX_SITES],
    ) -> Result<u32> {
        let enabled = self.module(owner)?.enabled;
        if callbacks.before.is_none() && callbacks.after.is_none() {
            return Err(Error::Argument);
        }
        let existing = self
            .sites
            .iter()
            .position(|s| s.is_some_and(|s| !s.retired && s.target.key() == target.key()));
        if existing.is_none() && self.overlaps(target)? {
            return Err(Error::Conflict);
        }
        let index = existing
            .or_else(|| self.sites.iter().position(Option::is_none))
            .ok_or(Error::Capacity)?;
        if let Some(site) = self.sites[index] {
            if site.raw_owner.is_some() {
                return Err(Error::Conflict);
            }
            if site.target != target {
                return Err(Error::Signature);
            }
            if site.listeners.iter().all(Option::is_some) {
                return Err(Error::Capacity);
            }
        }
        let token = self.token()?;
        let listener = Listener {
            token,
            owner,
            enabled,
            callbacks,
        };
        if existing.is_none() {
            let (patch, original) = self.prepare(index, target, thunks[index])?;
            let mut listeners = [None; MAX_CALLBACKS];
            listeners[0] = Some(listener);
            self.install(
                index,
                Site {
                    target,
                    original,
                    patch,
                    listeners,
                    raw_owner: None,
                    token,
                    installed: true,
                    retired: false,
                },
            )?;
        } else {
            let site = self.sites[index].as_mut().ok_or(Error::NotFound)?;
            let insertion = site
                .listeners
                .iter()
                .position(Option::is_none)
                .ok_or(Error::Capacity)?;
            site.listeners[insertion] = Some(listener);
            // Stable descending priority; equal priority preserves registration order.
            for i in (1..=insertion).rev() {
                if site.listeners[i].unwrap().callbacks.priority
                    > site.listeners[i - 1].unwrap().callbacks.priority
                {
                    site.listeners.swap(i, i - 1);
                } else {
                    break;
                }
            }
        }
        Ok(token)
    }

    pub fn snapshot(&self, index: usize) -> Result<Invocation> {
        let site = self
            .sites
            .get(index)
            .and_then(Option::as_ref)
            .ok_or(Error::NotFound)?;
        if site.raw_owner.is_some() {
            return Err(Error::Argument);
        }
        Ok(Invocation {
            original: site.original,
            listeners: site.listeners,
        })
    }

    pub fn detach(&mut self, owner: u32, token: u32) -> Result<()> {
        self.module(owner)?;
        for index in 0..MAX_SITES {
            let Some(mut site) = self.sites[index] else {
                continue;
            };
            if site.raw_owner == Some(owner) && site.token == token {
                if site.installed {
                    self.restore(site.patch)?;
                }
                self.sites[index] = None;
                return Ok(());
            }
            let Some(position) = site
                .listeners
                .iter()
                .position(|l| l.is_some_and(|l| l.owner == owner && l.token == token))
            else {
                continue;
            };
            if site.listeners.iter().flatten().count() == 1 {
                self.restore(site.patch)?;
                self.sites[index] = Some(site.retire());
            } else {
                site.listeners[position..].rotate_left(1);
                site.listeners[MAX_CALLBACKS - 1] = None;
                self.sites[index] = Some(site);
            }
            return Ok(());
        }
        Err(Error::NotFound)
    }

    pub fn set_enabled(&mut self, owner: u32, enabled: bool) -> Result<()> {
        self.module(owner)?;
        for index in 0..MAX_SITES {
            let Some(site) = self.sites[index] else {
                continue;
            };
            if site.raw_owner != Some(owner) || site.installed == enabled {
                continue;
            }
            if enabled {
                match site.patch {
                    Patch::Pointer { slot, original, .. } => {
                        let mut bytes = [0; core::mem::size_of::<usize>()];
                        self.memory.read(slot, &mut bytes)?;
                        if usize::from_le_bytes(bytes) != original {
                            return Err(Error::Conflict);
                        }
                    }
                    Patch::Inline { memory, plan } => {
                        let mut bytes = [0; 16];
                        self.memory
                            .read(memory.write, &mut bytes[..plan.patch_len])?;
                        if bytes[..plan.patch_len] != plan.saved[..plan.patch_len] {
                            return Err(Error::Conflict);
                        }
                    }
                }
                // Keep ownership if code publication fails; the runtime's
                // quarantine path will attempt restoration of every site.
                self.sites[index].as_mut().unwrap().installed = true;
                self.apply(site.patch)?;
            } else {
                self.restore(site.patch)?;
                self.sites[index].as_mut().unwrap().installed = false;
            }
        }
        for site in self.sites.iter_mut().flatten() {
            for listener in site
                .listeners
                .iter_mut()
                .flatten()
                .filter(|l| l.owner == owner)
            {
                listener.enabled = enabled;
            }
        }
        self.modules
            .iter_mut()
            .flatten()
            .find(|m| m.token == owner)
            .unwrap()
            .enabled = enabled;
        Ok(())
    }

    pub fn unregister(&mut self, owner: u32) -> Result<()> {
        self.module(owner)?;
        for index in 0..MAX_SITES {
            if let Some(site) = self.sites[index] {
                if site.raw_owner == Some(owner) {
                    self.detach(owner, site.token)?;
                }
                for listener in site.listeners.iter().flatten().filter(|l| l.owner == owner) {
                    self.detach(owner, listener.token)?;
                }
            }
        }
        let index = self
            .modules
            .iter()
            .position(|m| m.is_some_and(|m| m.token == owner))
            .unwrap();
        self.modules[index] = None;
        Ok(())
    }
}
