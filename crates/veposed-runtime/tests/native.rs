use std::ffi::c_void;
use std::sync::Mutex;
use veposed_core::{CallContext, Callbacks, Error};
use veposed_runtime::*;

static JOURNAL: Mutex<Option<[u8; 32]>> = Mutex::new(None);
unsafe extern "C" fn guard_read(output: *mut u8) -> i32 {
    if let Some(bytes) = *JOURNAL.lock().unwrap() {
        unsafe {
            std::ptr::copy_nonoverlapping(bytes.as_ptr(), output, 32);
        }
        0
    } else {
        1
    }
}
unsafe extern "C" fn guard_write(input: *const u8) -> i32 {
    let mut bytes = [0; 32];
    unsafe {
        std::ptr::copy_nonoverlapping(input, bytes.as_mut_ptr(), 32);
    }
    *JOURNAL.lock().unwrap() = Some(bytes);
    0
}

extern "C" fn sum(a: usize, b: usize, c: usize, d: usize) -> usize {
    a + b + c + d
}
unsafe extern "C" fn before(context: *mut CallContext, data: *mut c_void) {
    assert_eq!(
        veposed_set_enabled(unsafe { *(data as *const u32) }, 0),
        Error::Busy as i32
    );
    unsafe {
        (*context).args[0] += 10;
    }
}
unsafe extern "C" fn after(context: *mut CallContext, _: *mut c_void) {
    unsafe {
        (*context).result *= 2;
    }
}

#[test]
fn exported_api_redirects_real_function_pointer_and_restores_it() {
    let old_prefix = [1u32, 8u32];
    assert_eq!(
        unsafe { veposed_init(old_prefix.as_ptr().cast()) },
        Error::Abi as i32
    );
    let platform = Platform {
        abi_version: ABI_VERSION,
        struct_size: size_of::<Platform>() as u32,
        publish: None,
        guard_read: Some(guard_read),
        guard_write: Some(guard_write),
        points: core::ptr::null(),
        point_count: 0,
        point_size: size_of::<NamedPoint>(),
    };
    assert_eq!(unsafe { veposed_init(&platform) }, 0);
    let mut owner = 0;
    assert_eq!(
        unsafe { veposed_register(b"integration".as_ptr(), 11, &mut owner) },
        0
    );
    let mut slot = sum as *const () as usize;
    let target = HookTarget {
        kind: 1,
        address: &mut slot as *mut _ as usize,
        expected_pointer: slot,
        expected_code: [0; 16],
    };
    let callbacks = Callbacks {
        before: Some(before),
        after: Some(after),
        user_data: &owner as *const _ as *mut _,
        priority: 1,
    };
    let mut handle = 0;
    assert_eq!(
        unsafe { veposed_attach(owner, &target, &callbacks, &mut handle) },
        0
    );
    let hooked: extern "C" fn(usize, usize, usize, usize) -> usize =
        unsafe { std::mem::transmute(slot) };
    assert_eq!(hooked(1, 2, 3, 4), 40);
    assert_eq!(veposed_set_enabled(owner, 0), 0);
    assert_eq!(hooked(1, 2, 3, 4), 10);
    assert_eq!(veposed_set_enabled(owner, 1), 0);
    assert_eq!(veposed_unregister(owner), 0);
    assert_eq!(slot, sum as *const () as usize);
    assert_eq!(unsafe { veposed_init(&platform) }, Error::Conflict as i32);
}
