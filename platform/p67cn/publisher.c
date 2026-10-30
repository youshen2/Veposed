/* .043 HAL: id 1 is the D-cache (0x07ffc000), id 0 the I-cache (0x07ffa000).
 * Exact instruction and literal evidence is recorded in evidence/runtime-memory.json.
 */
#include "veposed.h"
#include "veposed_target.h"

typedef int (*cache_operation)(uint32_t, void *, uint32_t);

#ifdef VEP_PUBLISH_TEST
int vep_test_cache_clean(uint32_t, void *, uint32_t);
int vep_test_cache_invalidate(uint32_t, void *, uint32_t);
void vep_test_barrier(void);
#define CLEAN vep_test_cache_clean
#define INVALIDATE vep_test_cache_invalidate
static void barrier(void) { vep_test_barrier(); }
#else
#define CLEAN ((cache_operation)VEP_FW_CACHE_CLEAN)
#define INVALIDATE ((cache_operation)VEP_FW_CACHE_INVALIDATE)
static void barrier(void) { __asm__ volatile("dsb\n\tisb" ::: "memory"); }
#endif

int32_t vep_board_publish(uintptr_t execute, size_t length) {
    barrier();
    uintptr_t write;
    if ((execute >= 0x1c000000u && execute < 0x1c080500u)
        || (execute >= VEP_UMEM_START - 0x20000000u && execute < VEP_UMEM_END - 0x20000000u)) {
        uintptr_t end = execute < 0x1c080500u ? 0x1c080500u : VEP_UMEM_END - 0x20000000u;
        if (length > end - execute) return VEP_ARGUMENT;
        write = execute + 0x20000000u;
    } else if (execute >= VEP_UMEM_START && execute < VEP_UMEM_END) {
        if (length > VEP_UMEM_END - execute) return VEP_ARGUMENT;
        write = execute;
    } else if ((execute >= 0x00200000u && execute < 0x00400000u)
               || (execute >= 0x20000000u && execute < 0x20400000u)) {
        return VEP_OK;
    } else {
        return VEP_UNSUPPORTED;
    }
    int rc = CLEAN(1, (void *)write, (uint32_t)length);
    if (rc) return VEP_MEMORY;
    barrier();
    rc = INVALIDATE(0, (void *)execute, (uint32_t)length);
    if (rc) return VEP_MEMORY;
    barrier();
    return VEP_OK;
}
