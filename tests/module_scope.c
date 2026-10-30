#include "veposed.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static int sequence[8], used, fail_clean;
static uintptr_t expected_write = 0x3c06f038, expected_execute = 0x1c06f038;
int vep_test_cache_clean(uint32_t id, void *address, uint32_t length) {
    assert(id == 1 && (uintptr_t)address == expected_write && length == 8);
    sequence[used++] = 2; return fail_clean ? -1 : 0;
}
int vep_test_cache_invalidate(uint32_t id, void *address, uint32_t length) {
    assert(id == 0 && (uintptr_t)address == expected_execute && length == 8);
    sequence[used++] = 3; return 0;
}
void vep_test_barrier(void) { sequence[used++] = 1; }
int32_t vep_board_publish(uintptr_t, size_t);

int main(void) {
    assert(vep_board_publish(0x1c06f038, 8) == 0);
    const int expected[] = {1,2,1,3,1};
    assert(used == 5 && !memcmp(sequence, expected, sizeof(expected)));
    used = 0; fail_clean = 1;
    assert(vep_board_publish(0x1c06f038, 8) == VEP_MEMORY);
    assert(used == 2);
    used = 0;
    assert(vep_board_publish(0x0c54d3ea, 8) == VEP_UNSUPPORTED);
    assert(used == 1);
    fail_clean = 0; expected_write = 0x3c300040;
    uintptr_t entries[] = {0x1c300040, 0x3c300040};
    for (unsigned i = 0; i < 2; ++i) {
        used = 0; expected_execute = entries[i];
        assert(vep_board_publish(expected_execute, 8) == VEP_OK);
        assert(used == 5 && !memcmp(sequence, expected, sizeof(expected)));
    }
    used = 0;
    assert(vep_board_publish(0x3dfbfffc, 8) == VEP_ARGUMENT && used == 1);
    used = 0;
    assert(vep_board_publish(0x3c100000, 8) == VEP_UNSUPPORTED && used == 1);
    puts("static/dynamic PSRAM cache ordering, bounds and failure propagation: PASS");
    return 0;
}
