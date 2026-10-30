//! Named, typed recipes owned by the board adapter, not by third-party modules.
use super::*;
use veposed_core::MAX_CALLBACKS;

pub const VOID2: u32 = 1;
pub const WORD2: u32 = 2;
pub const WORD4: u32 = 3;
const MAX_TEXT: usize = 96;
const MAX_BINDINGS: usize = MAX_SITES * MAX_CALLBACKS;

#[repr(C)]
#[derive(Clone, Copy)]
pub struct NamedPoint {
    pub name: [u8; 48],
    pub contract: u32,
    pub target: HookTarget,
    pub caller: usize,
    pub subject_slot: usize,
    pub quiescent_slot: usize,
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
    points: [Option<NamedPoint>; MAX_SITES],
    kinds: [Option<u32>; MAX_SITES],
    bindings: [Option<Binding>; MAX_BINDINGS],
    texts: [Option<Text>; MAX_SITES],
}
impl Registry {
    pub const fn new() -> Self {
        Self {
            points: [None; MAX_SITES],
            kinds: [None; MAX_SITES],
            bindings: [None; MAX_BINDINGS],
            texts: [None; MAX_SITES],
        }
    }
    pub unsafe fn configure(&mut self, points: *const NamedPoint, count: u32) -> Result<()> {
        if count as usize > MAX_SITES || (count != 0 && points.is_null()) {
            return Err(Error::Argument);
        }
        for i in 0..count as usize {
            let point = unsafe { points.add(i).read() };
            if !matches!(point.contract, VOID2 | WORD2 | WORD4)
                || point.name[0] == 0
                || !point.name.contains(&0)
            {
                return Err(Error::Argument);
            }
            point.target.decode()?;
            if self.points[..i]
                .iter()
                .flatten()
                .any(|p| p.name == point.name)
            {
                return Err(Error::Conflict);
            }
            self.points[i] = Some(point);
        }
        Ok(())
    }
    pub fn site_kind(&self, site: usize) -> Option<u32> {
        self.kinds[site]
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
            }
        }
    }
    fn find(&self, name: &[u8; 48]) -> Result<usize> {
        self.points
            .iter()
            .position(|p| p.is_some_and(|p| p.name == *name))
            .ok_or(Error::NotFound)
    }
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
    if text_only && point.contract != VOID2 {
        return Err(Error::Argument);
    }
    if point.quiescent_slot != 0
        && unsafe { (point.quiescent_slot as *const usize).read_volatile() } != 0
    {
        return Err(Error::Busy);
    }
    Ok(index)
}

fn install(state: &mut State, owner: u32, point_index: usize, callbacks: Callbacks) -> Result<u32> {
    let point = state.named.points[point_index].ok_or(Error::NotFound)?;
    if point.quiescent_slot != 0
        && unsafe { (point.quiescent_slot as *const usize).read_volatile() } != 0
    {
        return Err(Error::Busy);
    }
    let target = point.target.decode()?;
    if let Some(site) = state.engine.target_site(target)
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
    let attached = state.engine.attach(owner, target, callbacks, &thunks());
    // A failed cache publication can leave an owned site pending rollback.
    // Keep its ABI so an in-flight call can still reach the original function.
    if let Some(site) = state.engine.target_site(target) {
        state.named.kinds[site] = Some(point.contract);
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
    if output.is_null() || count.is_null() || capacity == 0 || capacity > MAX_SITES {
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
                if (point.caller == 0 || point.caller & !1 == caller & !1)
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
entries!(n0=>0,n1=>1,n2=>2,n3=>3,n4=>4,n5=>5,n6=>6,n7=>7,n8=>8,n9=>9,n10=>10,n11=>11,n12=>12,n13=>13,n14=>14,n15=>15);

unsafe fn call_address(kind: u32, address: usize, args: [usize; 4]) -> usize {
    unsafe {
        match kind {
            VOID2 => {
                let f: unsafe extern "C" fn(usize, usize) = core::mem::transmute(address);
                f(args[0], args[1]);
                0
            }
            WORD2 => {
                let f: unsafe extern "C" fn(usize, usize) -> usize = core::mem::transmute(address);
                f(args[0], args[1])
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
