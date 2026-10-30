use veposed_core::{Error, recovery::*};

#[test]
fn unclosed_hook_lease_quarantines_once_and_never_auto_retries() {
    let armed = Guard::fresh().arm().unwrap();
    let (failed, checkpoint) = Guard::boot(0, &armed.record.encode());
    assert!(checkpoint && failed.safe);
    assert_eq!(failed.record.reason, PREVIOUS_SESSION);
    assert_eq!(failed.record.failures, 1);
    assert_eq!(failed.arm().unwrap_err(), Error::SafeMode);
    let (again, checkpoint) = Guard::boot(0, &failed.record.encode());
    assert!(!checkpoint && again.safe);
    assert_eq!(again.record.failures, 1);
    let reset = again.close();
    assert!(reset.safe, "reset cannot re-enable the current session");
    let (next, _) = Guard::boot(0, &reset.record.encode());
    assert!(!next.safe);
    assert_eq!(next.record.failures, 1);
}

#[test]
fn corrupt_storage_and_external_disable_fail_closed() {
    let mut bytes = Guard::fresh().arm().unwrap().record.encode();
    bytes[12] = 0; // torn write that could otherwise look like CLEAN
    let (corrupt, _) = Guard::boot(0, &bytes);
    assert!(corrupt.safe);
    assert_eq!(corrupt.record.reason, CORRUPT_RECORD);
    for status in [-1, 2, 99] {
        assert!(Guard::boot(status, &[0; 32]).0.safe);
    }
}

#[test]
fn clean_unhook_and_explicit_failures_have_distinct_boot_outcomes() {
    let armed = Guard::fresh().arm().unwrap();
    assert!(!Guard::boot(0, &armed.close().record.encode()).0.safe);
    let failed = armed.lock(HOOK_FAILURE, Error::Signature as i32);
    assert!(failed.safe);
    assert_eq!(failed.record.last_error, Error::Signature as i32);
    assert_eq!(failed.record.failures, 1);
    assert_eq!(
        Record::decode(&failed.record.encode()).unwrap(),
        failed.record
    );
}
