/* Each invocation is a fresh process sharing only its on-disk boot record. */
#include "veposed.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static const char *journal;
static int fail_write;
static int recover_inside_callback;

static int32_t guard_read(uint8_t *record) {
    int fd = open(journal, O_RDONLY);
    if (fd < 0) return errno == ENOENT ? 1 : -1;
    size_t used = 0;
    while (used < 32) {
        ssize_t n = read(fd, record + used, 32 - used);
        if (n <= 0) { close(fd); return -1; }
        used += (size_t)n;
    }
    uint8_t extra;
    ssize_t trailing = read(fd, &extra, 1);
    return close(fd) == 0 && trailing == 0 ? 0 : -1;
}
static int32_t guard_write(const uint8_t *record) {
    /* A status read would deadlock if the runtime held its IRQ/state gate. */
    vep_recovery_status status;
    (void)veposed_recovery_status(&status);
    if (fail_write) return -1;
    int fd = open(journal, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd < 0) return -1;
    size_t used = 0;
    while (used < 32) {
        ssize_t n = write(fd, record + used, 32 - used);
        if (n <= 0) { close(fd); return -1; }
        used += (size_t)n;
    }
    int synced = fsync(fd);
    int closed = close(fd);
    return synced == 0 && closed == 0 ? 0 : -1;
}
static uintptr_t sum(uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d) { return a + b + c + d; }
static uintptr_t (*volatile slot)(uintptr_t, uintptr_t, uintptr_t, uintptr_t) = sum;
static void before(vep_call *call, void *unused) {
    (void)unused;
    call->args[0] += 10;
    if (recover_inside_callback) assert(veposed_enter_safe_mode() == VEP_BUSY);
}

int main(int argc, char **argv) {
    assert(argc == 3);
    journal = argv[1];
    const char *mode = argv[2];
    fail_write = strcmp(mode, "storage-fail") == 0;
    vep_platform platform = { VEP_ABI_VERSION, sizeof(platform), 0, guard_read, guard_write, 0, 0 };
    assert(veposed_init(&platform) == 0);
    vep_recovery_status status;
    assert(veposed_recovery_status(&status) == 0);
    uint32_t owner = 0, handle = 0;
    if (!strcmp(mode, "safe") || !strcmp(mode, "reset")) {
        assert(status.mode == VEP_RECOVERY_SAFE);
        assert(veposed_register((const uint8_t *)"probe", 5, &owner) == VEP_SAFE_MODE);
        if (!strcmp(mode, "reset")) {
            assert(veposed_recovery_reset() == 0);
            assert(veposed_register((const uint8_t *)"probe", 5, &owner) == VEP_SAFE_MODE);
        }
    } else if (!strcmp(mode, "idle")) {
        assert(status.mode == VEP_RECOVERY_CLEAN);
    } else {
        assert(status.mode == VEP_RECOVERY_CLEAN);
        assert(veposed_register((const uint8_t *)"probe", 5, &owner) == 0);
        vep_target target = { .kind = VEP_POINTER, .address = (uintptr_t)&slot, .expected_pointer = (uintptr_t)sum };
        vep_callbacks callbacks = { .before = before };
        int32_t attached = veposed_attach(owner, &target, &callbacks, &handle);
        if (fail_write) {
            assert(attached == VEP_STORAGE && slot == sum);
            assert(veposed_recovery_status(&status) == 0 && status.mode == VEP_RECOVERY_SAFE);
        } else {
            assert(attached == 0);
            assert(slot(1, 2, 3, 4) == 20);
            if (!strcmp(mode, "arm")) {
                puts("armed; exiting without unhook");
                fflush(stdout);
                _Exit(0);
            } else if (!strcmp(mode, "hook-fail")) {
                uintptr_t other = (uintptr_t)sum;
                target.address = (uintptr_t)&other;
                target.expected_pointer++;
                assert(veposed_attach(owner, &target, &callbacks, &handle) == VEP_SIGNATURE);
                assert(slot == sum);
                assert(veposed_recovery_status(&status) == 0 && status.mode == VEP_RECOVERY_SAFE && status.active_sites == 0);
            } else if (!strcmp(mode, "busy-recovery")) {
                recover_inside_callback = 1;
                assert(slot(1, 2, 3, 4) == 20);
                assert(slot(1, 2, 3, 4) == 10); // new calls bypass the quarantined callbacks
                assert(veposed_recovery_reset() == VEP_BUSY);
                assert(veposed_enter_safe_mode() == 0 && slot == sum);
            } else {
                assert(!strcmp(mode, "clean"));
                assert(veposed_unregister(owner) == 0 && slot == sum);
            }
        }
    }
    assert(veposed_recovery_status(&status) == 0);
    printf("{\"mode\":%u,\"failures\":%u,\"reason\":%u,\"sites\":%u}\n",
           status.mode, status.failed_sessions, status.reason, status.active_sites);
    return 0;
}
