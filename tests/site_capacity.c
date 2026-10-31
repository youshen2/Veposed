#include "veposed.h"
#include <assert.h>
#include <stdio.h>

enum { SITES = 32 };
typedef uintptr_t (*four_words)(uintptr_t, uintptr_t, uintptr_t, uintptr_t);

static uintptr_t sum(uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d) {
    return a + b + c + d;
}
static void before(vep_call *call, void *data) {
    (void)data;
    call->args[0] += 10;
}
static void after(vep_call *call, void *data) {
    (void)data;
    call->result *= 2;
}
static int32_t read_guard(uint8_t *record) { (void)record; return 1; }
static int32_t write_guard(const uint8_t *record) { (void)record; return 0; }

int main(int argc, char **argv) {
    (void)argv;
    uintptr_t slots[SITES + 1];
    vep_named_point points[SITES + 1] = {0};
    uint32_t handles[SITES], owner, ignored;
    vep_callbacks callbacks = { .before = before, .after = after };
    for (unsigned i = 0; i <= SITES; ++i) {
        slots[i] = (uintptr_t)sum;
        snprintf((char *)points[i].name, sizeof(points[i].name), "capacity.%u", i);
        points[i].contract = VEP_WORD4;
        points[i].target = (vep_target){ .kind = VEP_POINTER,
            .address = (uintptr_t)&slots[i], .expected_pointer = slots[i] };
    }
    vep_platform platform = { VEP_ABI_VERSION, sizeof(platform), 0, read_guard,
        write_guard, points, SITES + 1, sizeof(vep_named_point) };
    assert(veposed_init(&platform) == VEP_OK);
    const vep_api *api = veposed_get_api();
    assert(api->register_module((const uint8_t *)"capacity", 8, &owner) == VEP_OK);
    vep_target invalid = { .kind = 3 };
    vep_recovery_status recovery;
    assert(api->attach(owner, &invalid, &callbacks, &ignored) == VEP_ARGUMENT);
    assert(api->recovery_status(&recovery) == VEP_OK && recovery.mode == VEP_RECOVERY_CLEAN);
    if (argc == 1) {
        for (unsigned i = 0; i < SITES; ++i)
            assert(api->attach_named(owner, points[i].name, &callbacks, &handles[i]) == VEP_OK);
        assert(api->attach_named(owner, points[SITES].name, &callbacks, &ignored) == VEP_CAPACITY);
        assert(((four_words)slots[0])(1, 2, 3, 4) == 40);
        assert(((four_words)slots[SITES - 1])(1, 2, 3, 4) == 40);
        four_words stale = (four_words)slots[0];
        assert(api->unregister_module(owner) == VEP_OK);
        for (unsigned i = 0; i <= SITES; ++i) assert(slots[i] == (uintptr_t)sum);
        assert(stale(1, 2, 3, 4) == 10);
        assert(api->register_module((const uint8_t *)"capacity-again", 14, &owner) == VEP_OK);
        assert(api->attach_named(owner, points[0].name, &callbacks, &ignored) == VEP_CAPACITY);
        puts("32 named sites: restore, stale dispatch and retired capacity PASS");
        return 0;
    }
    for (unsigned i = 0; i < SITES; ++i)
        assert(api->attach(owner, &points[i].target, &callbacks, &handles[i]) == VEP_OK);
    assert(api->attach(owner, &points[SITES].target, &callbacks, &ignored) == VEP_CAPACITY);
    assert(api->recovery_status(&recovery) == VEP_OK && recovery.mode == VEP_RECOVERY_ARMED);
    assert(((four_words)slots[SITES - 1])(1, 2, 3, 4) == 40);
    assert(api->unregister_module(owner) == VEP_OK);
    for (unsigned i = 0; i <= SITES; ++i) assert(slots[i] == (uintptr_t)sum);
    puts("32 raw callback sites: dispatch, capacity and restore PASS");
}
