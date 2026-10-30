#include "veposed.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static uint8_t journal[32];
static int journal_present;
static int32_t guard_read(uint8_t *record) {
    if (!journal_present) return 1;
    memcpy(record, journal, sizeof(journal)); return 0;
}
static int32_t guard_write(const uint8_t *record) {
    memcpy(journal, record, sizeof(journal)); journal_present = 1; return 0;
}

static uintptr_t sum(uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d) { return a + b + c + d; }
static void before(vep_call *call, void *unused) { (void)unused; call->args[0] += 10; }
static void after(vep_call *call, void *unused) { (void)unused; call->result *= 2; }
static uintptr_t (*volatile slot)(uintptr_t, uintptr_t, uintptr_t, uintptr_t) = sum;

int main(void) {
    vep_platform platform = { VEP_ABI_VERSION, sizeof(vep_platform), 0, guard_read, guard_write, 0, 0 };
    assert(veposed_init(&platform) == 0);
    const vep_api *api = veposed_get_api();
    assert(api->abi_version == VEP_ABI_VERSION && api->struct_size == sizeof(*api));
    uint32_t owner, handle;
    assert(api->register_module((const uint8_t *)"host-demo", 9, &owner) == 0);
    vep_module_info modules[16]; uint32_t count;
    assert(api->list_modules(modules, 16, &count) == 0 && count == 1);
    assert(modules[0].id == owner && modules[0].enabled == 1 && modules[0].name_len == 9);
    vep_target target = { .kind = VEP_POINTER, .address = (uintptr_t)&slot, .expected_pointer = (uintptr_t)sum };
    vep_callbacks callbacks = { .before = before, .after = after, .priority = 100 };
    assert(api->attach(owner, &target, &callbacks, &handle) == 0);
    printf("original=10, hooked=%lu\n", (unsigned long)slot(1, 2, 3, 4));
    assert(slot(1, 2, 3, 4) == 40);
    assert(api->set_enabled(owner, 0) == 0);
    assert(slot(1, 2, 3, 4) == 10);
    assert(api->set_enabled(owner, 1) == 0);
    assert(slot(1, 2, 3, 4) == 40);
    assert(api->unregister_module(owner) == 0);
    assert(slot == sum);
    puts("C ABI / service table / pointer hook / restore: PASS");
    return 0;
}
