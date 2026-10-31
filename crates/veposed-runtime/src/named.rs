//! Named, typed recipes owned by the board adapter, not by third-party modules.
use super::*;
use veposed_core::MAX_CALLBACKS;

pub const VOID2: u32 = 1;
pub const WORD2: u32 = 2;
pub const WORD4: u32 = 3;
pub const VOID0: u32 = 4;
pub const WORD0: u32 = 5;
pub const VOID1: u32 = 6;
pub const WORD1: u32 = 7;
pub const VOID3: u32 = 8;
pub const WORD3: u32 = 9;
pub const VOID4: u32 = 10;
const MAX_TEXT: usize = 96;
const MAX_NAMED_POINTS: usize = 2048;
const NAME_BUCKETS: usize = MAX_NAMED_POINTS * 2;
const MAX_BINDINGS: usize = 256;

#[repr(C)]
#[derive(Clone, Copy)]
pub struct NamedPoint {
    pub name: [u8; 48],
    pub contract: u32,
    pub target: HookTarget,
    pub caller: usize,
    pub caller2: usize,
    pub subject_slot: usize,
    pub quiescent_slot: usize,
    pub active_slot: usize,
    pub quiescent_slot2: usize,
    pub active_slot2: usize,
    pub text_arg1: u32,
}
#[repr(C)]
#[derive(Clone, Copy)]
pub struct HookPointInfo {
    pub name: [u8; 48],
    pub contract: u32,
}
#[derive(Clone, Copy)]
struct Binding {
    owner: u32,
    token: u32,
    point: usize,
    site: usize,
}
#[derive(Clone, Copy)]
struct Text {
    owner: u32,
    token: u32,
    bytes: [u8; MAX_TEXT],
}

pub(super) struct Registry {
    points: [Option<NamedPoint>; MAX_NAMED_POINTS],
    names: [u16; NAME_BUCKETS],
    kinds: [Option<u32>; MAX_SITES],
    pending: [Option<usize>; MAX_SITES],
    bindings: [Option<Binding>; MAX_BINDINGS],
    texts: [Option<Text>; MAX_BINDINGS],
}
impl Registry {
    pub const fn new() -> Self {
        Self {
            points: [None; MAX_NAMED_POINTS],
            names: [0; NAME_BUCKETS],
            kinds: [None; MAX_SITES],
            pending: [None; MAX_SITES],
            bindings: [None; MAX_BINDINGS],
            texts: [None; MAX_BINDINGS],
        }
    }
    pub unsafe fn configure(&mut self, points: *const NamedPoint, count: u32) -> Result<()> {
        if count as usize > MAX_NAMED_POINTS || (count != 0 && points.is_null()) {
            return Err(Error::Argument);
        }
        for i in 0..count as usize {
            let point = unsafe { points.add(i).read() };
            let name_end = point.name.iter().position(|byte| *byte == 0);
            if !matches!(
                point.contract,
                VOID0 | VOID1 | VOID2 | VOID3 | VOID4 | WORD0 | WORD1 | WORD2 | WORD3 | WORD4
            ) || name_end
                .is_none_or(|end| end == 0 || point.name[end..].iter().any(|byte| *byte != 0))
                || point.text_arg1 > 1
                || (point.text_arg1 == 1 && point.contract != VOID2)
                || (point.active_slot2 != 0 && point.active_slot == 0)
                || (point.caller2 != 0 && point.caller == 0)
                || [
                    point.subject_slot,
                    point.quiescent_slot,
                    point.active_slot,
                    point.quiescent_slot2,
                    point.active_slot2,
                ]
                .into_iter()
                .any(|slot| {
                    slot != 0
                        && (!slot.is_multiple_of(core::mem::align_of::<usize>())
                            || !writable(slot, core::mem::size_of::<usize>()))
                })
            {
                return Err(Error::Argument);
            }
            point.target.decode()?;
        }
        // Store index + 1 so zero is the empty marker. At most half of the
        // buckets are occupied, so probing always reaches an empty bucket.
        for i in 0..count as usize {
            let name = unsafe { (*points.add(i)).name };
            let mut bucket = name_hash(&name);
            while self.names[bucket] != 0 {
                let previous = usize::from(self.names[bucket] - 1);
                if unsafe { (*points.add(previous)).name } == name {
                    self.names.fill(0);
                    return Err(Error::Conflict);
                }
                bucket = (bucket + 1) & (NAME_BUCKETS - 1);
            }
            self.names[bucket] = (i + 1) as u16;
        }
        for i in 0..count as usize {
            self.points[i] = Some(unsafe { points.add(i).read() });
        }
        Ok(())
    }
    pub fn site_kind(&self, site: usize) -> Option<u32> {
        self.kinds[site]
    }
    pub fn owner_busy(&self, owner: u32, token: Option<u32>) -> bool {
        self.bindings
            .iter()
            .flatten()
            .filter(|binding| {
                binding.owner == owner && token.is_none_or(|token| binding.token == token)
            })
            .any(|binding| self.points[binding.point].is_some_and(busy))
    }
    pub fn site_busy(&self, site: usize) -> bool {
        self.pending[site].is_some_and(|point| self.points[point].is_some_and(busy))
            || self
                .bindings
                .iter()
                .flatten()
                .filter(|binding| binding.site == site)
                .any(|binding| self.points[binding.point].is_some_and(busy))
    }
    pub fn prune(&mut self, engine: &Engine<NativeMemory>) {
        for binding in &mut self.bindings {
            if binding.is_some_and(|b| engine.hook_site(b.owner, b.token).is_none()) {
                *binding = None;
            }
        }
        for text in &mut self.texts {
            if text.is_some_and(|t| engine.hook_site(t.owner, t.token).is_none()) {
                *text = None;
            }
        }
        for (i, kind) in self.kinds.iter_mut().enumerate() {
            if engine.snapshot(i).is_err() {
                *kind = None;
                self.pending[i] = None;
            }
        }
    }
    fn find(&self, name: &[u8; 48]) -> Result<usize> {
        let mut bucket = name_hash(name);
        while self.names[bucket] != 0 {
            let index = usize::from(self.names[bucket] - 1);
            if self.points[index].is_some_and(|point| point.name == *name) {
                return Ok(index);
            }
            bucket = (bucket + 1) & (NAME_BUCKETS - 1);
        }
        Err(Error::NotFound)
    }
}

fn name_hash(name: &[u8; 48]) -> usize {
    let hash = name.iter().fold(0x811c_9dc5u32, |hash, byte| {
        (hash ^ u32::from(*byte)).wrapping_mul(0x0100_0193)
    });
    (hash as usize) & (NAME_BUCKETS - 1)
}

unsafe fn c_string<const N: usize>(input: *const u8) -> Result<[u8; N]> {
    if input.is_null() {
        return Err(Error::Argument);
    }
    let mut bytes = [0; N];
    for (i, byte) in bytes.iter_mut().enumerate() {
        *byte = unsafe { input.add(i).read() };
        if *byte == 0 {
            return Ok(bytes);
        }
    }
    Err(Error::Argument)
}

fn busy(point: NamedPoint) -> bool {
    [point.quiescent_slot, point.quiescent_slot2]
        .into_iter()
        .any(|slot| slot != 0 && unsafe { (slot as *const usize).read_volatile() } != 0)
}

fn active(point: NamedPoint) -> bool {
    point.active_slot == 0
        || [point.active_slot, point.active_slot2]
            .into_iter()
            .any(|slot| slot != 0 && unsafe { (slot as *const usize).read_volatile() } != 0)
}

fn resolve(name: &[u8; 48], text_only: bool) -> Result<usize> {
    let _gate = Gate::acquire();
    let state = unsafe { &*STATE.0.get() };
    if !state.ready {
        return Err(Error::Abi);
    }
    if state.guard.safe {
        return Err(Error::SafeMode);
    }
    let index = state.named.find(name)?;
    let point = state.named.points[index].ok_or(Error::NotFound)?;
    if text_only && (point.contract != VOID2 || point.text_arg1 != 1) {
        return Err(Error::Argument);
    }
    if busy(point) {
        return Err(Error::Busy);
    }
    Ok(index)
}

fn install(state: &mut State, owner: u32, point_index: usize, callbacks: Callbacks) -> Result<u32> {
    let point = state.named.points[point_index].ok_or(Error::NotFound)?;
    if busy(point) {
        return Err(Error::Busy);
    }
    let target = point.target.decode()?;
    let existing = state.engine.target_site(target);
    if let Some(site) = existing
        && state.named.kinds[site] != Some(point.contract)
    {
        return Err(Error::Conflict);
    }
    let free = state
        .named
        .bindings
        .iter()
        .position(Option::is_none)
        .ok_or(Error::Capacity)?;
    let candidate = existing.or_else(|| state.engine.vacant_site());
    let attached = state.engine.attach(owner, target, callbacks, &thunks());
    // A failed cache publication can leave an owned site pending rollback.
    // Keep its ABI so an in-flight call can still reach the original function.
    if let Some(site) = candidate.filter(|site| state.engine.snapshot(*site).is_ok()) {
        state.named.kinds[site] = Some(point.contract);
        if attached.is_err() && existing.is_none() && state.engine.target_site(target) == Some(site)
        {
            state.named.pending[site] = Some(point_index);
        }
    }
    let token = attached?;
    let site = state
        .engine
        .hook_site(owner, token)
        .ok_or(Error::NotFound)?;
    state.named.bindings[free] = Some(Binding {
        owner,
        token,
        point: point_index,
        site,
    });
    Ok(token)
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_attach_named(
    owner: u32,
    name: *const u8,
    callbacks: *const Callbacks,
    output: *mut u32,
) -> i32 {
    if callbacks.is_null() || output.is_null() {
        return Error::Argument as i32;
    }
    let name = match unsafe { c_string::<48>(name) } {
        Ok(n) => n,
        Err(e) => return e as i32,
    };
    let callbacks = unsafe { *callbacks };
    if callbacks.before.is_none() && callbacks.after.is_none() {
        return Error::Argument as i32;
    }
    let point = match resolve(&name, false) {
        Ok(p) => p,
        Err(e) => return e as i32,
    };
    mutate_state(Operation::NamedInstall, |state| {
        let token = install(state, owner, point, callbacks)?;
        unsafe { output.write(token) };
        Ok(())
    })
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_hook_text(
    owner: u32,
    name: *const u8,
    text: *const u8,
    output: *mut u32,
) -> i32 {
    if output.is_null() {
        return Error::Argument as i32;
    }
    let name = match unsafe { c_string::<48>(name) } {
        Ok(n) => n,
        Err(e) => return e as i32,
    };
    let bytes = match unsafe { c_string::<MAX_TEXT>(text) } {
        Ok(n) => n,
        Err(e) => return e as i32,
    };
    let point = match resolve(&name, true) {
        Ok(p) => p,
        Err(e) => return e as i32,
    };
    mutate_state(Operation::NamedInstall, |state| {
        let index = state
            .named
            .texts
            .iter()
            .position(Option::is_none)
            .ok_or(Error::Capacity)?;
        let callbacks = Callbacks {
            before: Some(replace_text),
            after: None,
            user_data: (index + 1) as *mut c_void,
            priority: 0,
        };
        let token = install(state, owner, point, callbacks)?;
        state.named.texts[index] = Some(Text {
            owner,
            token,
            bytes,
        });
        unsafe { output.write(token) };
        Ok(())
    })
}

unsafe extern "C" fn replace_text(context: *mut CallContext, data: *mut c_void) {
    // All mutation is excluded for the complete invocation. The copied string
    // lives until detach/unregister and the setter copies it into the label.
    let state = unsafe { &*STATE.0.get() };
    if let Some(text) = &state.named.texts[data as usize - 1] {
        unsafe {
            (*context).args[1] = text.bytes.as_ptr() as usize;
        }
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_list_hook_points(
    output: *mut HookPointInfo,
    capacity: usize,
    count: *mut u32,
) -> i32 {
    if output.is_null() || count.is_null() || capacity == 0 {
        return Error::Argument as i32;
    }
    let _gate = Gate::acquire();
    let state = unsafe { &*STATE.0.get() };
    if !state.ready {
        return Error::Abi as i32;
    }
    let mut used = 0;
    for point in state.named.points.iter().flatten().take(capacity) {
        unsafe {
            output.add(used).write(HookPointInfo {
                name: point.name,
                contract: point.contract,
            });
        }
        used += 1;
    }
    unsafe {
        count.write(used as u32);
    }
    0
}

// This entry is public for host conformance tests; modules call only the API table.
#[unsafe(no_mangle)]
pub extern "C" fn veposed_named_dispatch(
    a: usize,
    b: usize,
    c: usize,
    d: usize,
    caller: usize,
    index: usize,
) -> usize {
    let args = [a, b, c, d];
    let (invocation, kind, matched) = {
        let _gate = Gate::acquire();
        let state = unsafe { &*STATE.0.get() };
        let Ok(invocation) = state.engine.snapshot(index) else {
            return 0;
        };
        let Some(kind) = state.named.kinds[index] else {
            return 0;
        };
        let mut matched = [(0, 0); MAX_CALLBACKS];
        if !state.guard.safe {
            let mut next = 0;
            for binding in state
                .named
                .bindings
                .iter()
                .flatten()
                .filter(|b| b.site == index)
            {
                let point = state.named.points[binding.point].unwrap();
                if (point.caller == 0
                    || point.caller & !1 == caller & !1
                    || (point.caller2 != 0 && point.caller2 & !1 == caller & !1))
                    && active(point)
                    && (point.subject_slot == 0
                        || (a != 0
                            && unsafe { (point.subject_slot as *const usize).read_volatile() }
                                == a))
                {
                    matched[next] = (binding.owner, binding.token);
                    next += 1;
                }
            }
        }
        IN_FLIGHT.fetch_add(1, Ordering::Release);
        (invocation, kind, matched)
    };
    let value = unsafe {
        invocation.invoke_scoped(
            args,
            kind,
            |owner, token| matched.contains(&(owner, token)),
            |args| call_address(kind, invocation.original, args),
        )
    };
    IN_FLIGHT.fetch_sub(1, Ordering::Release);
    value
}

macro_rules! entries {
    ($($name:ident => $index:expr),* $(,)?) => {
        $(
            #[cfg(target_arch = "arm")]
            #[unsafe(naked)]
            unsafe extern "C" fn $name(_: usize, _: usize, _: usize, _: usize) -> usize {
                core::arch::naked_asm!(
                    "push {{r4, lr}}", "sub sp, sp, #8", "str lr, [sp, #0]",
                    "movs r4, #{index}", "str r4, [sp, #4]", "bl veposed_named_dispatch",
                    "add sp, sp, #8", "pop {{r4, pc}}", index = const $index,
                );
            }
            #[cfg(not(target_arch = "arm"))]
            extern "C" fn $name(a: usize, b: usize, c: usize, d: usize) -> usize {
                veposed_named_dispatch(a,b,c,d,0,$index)
            }
        )*
        fn thunks() -> [usize; MAX_SITES] { [$($name as *const () as usize),*] }
    }
}
entries!(n0=>0,n1=>1,n2=>2,n3=>3,n4=>4,n5=>5,n6=>6,n7=>7,n8=>8,n9=>9,n10=>10,n11=>11,n12=>12,n13=>13,n14=>14,n15=>15,
    n16=>16,n17=>17,n18=>18,n19=>19,n20=>20,n21=>21,n22=>22,n23=>23,n24=>24,n25=>25,n26=>26,n27=>27,n28=>28,n29=>29,n30=>30,n31=>31);

unsafe fn call_address(kind: u32, address: usize, args: [usize; 4]) -> usize {
    unsafe {
        match kind {
            VOID0 => {
                let f: unsafe extern "C" fn() = core::mem::transmute(address);
                f();
                0
            }
            WORD0 => {
                let f: unsafe extern "C" fn() -> usize = core::mem::transmute(address);
                f()
            }
            VOID1 => {
                let f: unsafe extern "C" fn(usize) = core::mem::transmute(address);
                f(args[0]);
                0
            }
            WORD1 => {
                let f: unsafe extern "C" fn(usize) -> usize = core::mem::transmute(address);
                f(args[0])
            }
            VOID2 => {
                let f: unsafe extern "C" fn(usize, usize) = core::mem::transmute(address);
                f(args[0], args[1]);
                0
            }
            WORD2 => {
                let f: unsafe extern "C" fn(usize, usize) -> usize = core::mem::transmute(address);
                f(args[0], args[1])
            }
            VOID3 => {
                let f: unsafe extern "C" fn(usize, usize, usize) = core::mem::transmute(address);
                f(args[0], args[1], args[2]);
                0
            }
            WORD3 => {
                let f: unsafe extern "C" fn(usize, usize, usize) -> usize =
                    core::mem::transmute(address);
                f(args[0], args[1], args[2])
            }
            VOID4 => {
                let f: unsafe extern "C" fn(usize, usize, usize, usize) =
                    core::mem::transmute(address);
                f(args[0], args[1], args[2], args[3]);
                0
            }
            WORD4 => {
                let f: unsafe extern "C" fn(usize, usize, usize, usize) -> usize =
                    core::mem::transmute(address);
                f(args[0], args[1], args[2], args[3])
            }
            _ => 0,
        }
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_call_original(context: *mut CallContext) -> usize {
    let call = unsafe { &mut *context };
    let value = unsafe { call_address(call.contract, call.original, call.args) };
    call.result = value;
    call.return_early = 1;
    value
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn veposed_call_named(
    name: *const u8,
    args: *const usize,
    output: *mut usize,
) -> i32 {
    if args.is_null() || output.is_null() {
        return Error::Argument as i32;
    }
    let name = match unsafe { c_string::<48>(name) } {
        Ok(n) => n,
        Err(e) => return e as i32,
    };
    let (kind, address) = {
        let _gate = Gate::acquire();
        let state = unsafe { &*STATE.0.get() };
        if !state.ready {
            return Error::Abi as i32;
        }
        if state.guard.safe {
            return Error::SafeMode as i32;
        }
        // Direct calls are issued within a callback's already-journaled lease.
        if IN_FLIGHT.load(Ordering::Acquire) == 0 {
            return Error::Busy as i32;
        }
        let index = match state.named.find(&name) {
            Ok(i) => i,
            Err(e) => return e as i32,
        };
        let point = state.named.points[index].unwrap();
        let target = match point.target.decode() {
            Ok(t) => t,
            Err(e) => return e as i32,
        };
        let address = state.engine.original_for(target).unwrap_or(match target {
            Target::Pointer { expected, .. } => expected,
            Target::Inline { function, .. } => function,
        });
        IN_FLIGHT.fetch_add(1, Ordering::Release);
        (point.contract, address)
    };
    let arguments = unsafe {
        [
            args.read(),
            args.add(1).read(),
            args.add(2).read(),
            args.add(3).read(),
        ]
    };
    let value = unsafe { call_address(kind, address, arguments) };
    unsafe {
        output.write(value);
    }
    IN_FLIGHT.fetch_sub(1, Ordering::Release);
    0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejected_configuration_does_not_leave_partial_catalog() {
        let mut name = [0; 48];
        name[..5].copy_from_slice(b"first");
        let point = NamedPoint {
            name,
            contract: WORD1,
            target: HookTarget {
                kind: 1,
                address: 8,
                expected_pointer: 1,
                expected_code: [0; 16],
            },
            caller: 0,
            caller2: 0,
            subject_slot: 0,
            quiescent_slot: 0,
            active_slot: 0,
            quiescent_slot2: 0,
            active_slot2: 0,
            text_arg1: 0,
        };
        let mut invalid = point;
        invalid.name[0] = b'x';
        invalid.quiescent_slot = 1;
        let mut registry = Registry::new();
        assert!(matches!(
            unsafe { registry.configure([point, invalid].as_ptr(), 2) },
            Err(Error::Argument)
        ));
        assert!(registry.points.iter().all(Option::is_none));
        assert!(unsafe { registry.configure(&point, 1) }.is_ok());
        assert_eq!(registry.find(&point.name), Ok(0));
        assert!(registry.points[1..].iter().all(Option::is_none));
    }

    #[test]
    fn full_catalog_handles_collisions_and_duplicate_retry() {
        let point = NamedPoint {
            name: [0; 48],
            contract: WORD1,
            target: HookTarget {
                kind: 1,
                address: 8,
                expected_pointer: 1,
                expected_code: [0; 16],
            },
            caller: 0,
            caller2: 0,
            subject_slot: 0,
            quiescent_slot: 0,
            active_slot: 0,
            quiescent_slot2: 0,
            active_slot2: 0,
            text_arg1: 0,
        };
        let mut points = vec![point; MAX_NAMED_POINTS];
        for (i, item) in points.iter_mut().enumerate() {
            let name = format!("test.catalog.{i}");
            item.name[..name.len()].copy_from_slice(name.as_bytes());
        }
        let mut hashes = [false; NAME_BUCKETS];
        let mut collision = false;
        for item in &points {
            let bucket = name_hash(&item.name);
            collision |= hashes[bucket];
            hashes[bucket] = true;
        }
        assert!(collision);
        let mut registry = Registry::new();
        let saved = points[MAX_NAMED_POINTS - 1];
        points[MAX_NAMED_POINTS - 1] = points[0];
        assert!(matches!(
            unsafe { registry.configure(points.as_ptr(), MAX_NAMED_POINTS as u32) },
            Err(Error::Conflict)
        ));
        assert!(registry.points.iter().all(Option::is_none));
        assert!(registry.names.iter().all(|item| *item == 0));
        points[MAX_NAMED_POINTS - 1] = saved;
        assert!(unsafe { registry.configure(points.as_ptr(), MAX_NAMED_POINTS as u32) }.is_ok());
        for (i, point) in points.iter().enumerate() {
            assert_eq!(registry.find(&point.name), Ok(i));
        }
        assert!(matches!(
            unsafe { Registry::new().configure(points.as_ptr(), (MAX_NAMED_POINTS + 1) as u32) },
            Err(Error::Argument)
        ));
    }
}
