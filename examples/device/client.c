/* Independent ELF module. All runtime services are obtained through /dev/veposed. */
#include "veposed.h"
#include "veposed_target.h"

static const vep_api *api;
static uint32_t owner;
volatile int32_t veposed_client_status = VEP_ABI;
static uintptr_t sum(uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d) { return a + b + c + d; }
static uintptr_t (*volatile slot)(uintptr_t, uintptr_t, uintptr_t, uintptr_t) = sum;
static vep_target target;

static void add_ten(vep_call *call, void *unused) { (void)unused; call->args[0] += 10; }
static const vep_callbacks callbacks = { .before = add_ten, .priority = 100 };

__attribute__((constructor))
static void client_init(void) {
    if (!vep_target_matches()) { veposed_client_status = VEP_FIRMWARE; return; }
    typedef int (*open_fn)(const char *, int, ...);
    typedef int32_t (*read_fn)(int, void *, uint32_t);
    typedef int (*close_fn)(int);
    int fd = ((open_fn)VEP_FW_OPEN)(VEP_DEVICE_PATH, 1);
    if (fd < 0) return;
    vep_discovery discovery;
    int32_t got = ((read_fn)VEP_FW_READ)(fd, &discovery, sizeof(discovery));
    (void)((close_fn)VEP_FW_CLOSE)(fd);
    if (got != sizeof(discovery) || discovery.magic != VEP_DISCOVERY_MAGIC
        || discovery.abi_version != VEP_ABI_VERSION || discovery.struct_size != sizeof(discovery)) return;
    api = discovery.api;
    if (!api || api->abi_version != VEP_ABI_VERSION || api->struct_size != sizeof(*api)) return;
    const uint8_t name[] = "veposed.client";
    int32_t rc = api->register_module(name, sizeof(name) - 1, &owner);
    if (rc != VEP_OK) { veposed_client_status = rc; return; }
    target.kind = VEP_POINTER;
    target.address = (uintptr_t)&slot;
    target.expected_pointer = (uintptr_t)sum;
    uint32_t handle;
    rc = api->attach(owner, &target, &callbacks, &handle);
    if (rc == VEP_OK) {
        uintptr_t result = slot(1, 2, 3, 4);
        rc = api->detach(owner, handle);
        if (rc == VEP_OK && result != 20) rc = VEP_CONFLICT;
    }
    veposed_client_status = rc;
}

__attribute__((destructor))
static void client_fini(void) {
    if (api && owner) veposed_client_status = api->unregister_module(owner);
}
