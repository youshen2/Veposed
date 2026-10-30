#ifndef VEPOSED_MODULE_H
#define VEPOSED_MODULE_H
/* Define VEP_MODULE_ID, VEP_MODULE_STATUS_PATH and vep_module_setup().
 * This adapter is linked into the module; authored hooks use only vep_api.
 */
#include "veposed.h"
#include "veposed_target.h"
static const vep_api *vep;
static uint32_t vep_owner;
volatile int32_t vep_module_status = VEP_ABI;
static int32_t vep_module_setup(void);

static void vep_write_status(int32_t status) {
    typedef int (*open_fn)(const char *, int, ...);
    typedef int32_t (*write_fn)(int, const void *, uint32_t);
    typedef int (*close_fn)(int);
    char record[64];
    const char prefix[] = "Veposed module status=";
    uint32_t i;
    for (i = 0; i < sizeof(record); i++) record[i] = ' ';
    for (i = 0; i < sizeof(prefix) - 1; i++) record[i] = prefix[i];
    record[i++] = status < 0 ? '-' : '+';
    uint32_t value = status < 0 ? 0u - (uint32_t)status : (uint32_t)status;
    record[i++] = (char)('0' + value / 10);
    record[i] = (char)('0' + value % 10);
    record[63] = '\n';
    int fd = ((open_fn)VEP_FW_OPEN)(VEP_MODULE_STATUS_PATH, 2 | 4 | 32, 0600);
    if (fd < 0) return;
    uint32_t used = 0;
    while (used < sizeof(record)) {
        int32_t written = ((write_fn)VEP_FW_WRITE)(fd, record + used, sizeof(record) - used);
        if (written <= 0) break;
        used += (uint32_t)written;
    }
    (void)((close_fn)VEP_FW_CLOSE)(fd);
}
static int32_t vep_module_start(void) {
    typedef int (*open_fn)(const char *, int, ...);
    typedef int32_t (*read_fn)(int, void *, uint32_t);
    typedef int (*close_fn)(int);
    int fd = ((open_fn)VEP_FW_OPEN)(VEP_DEVICE_PATH, 1);
    if (fd < 0) return VEP_NOT_FOUND;
    vep_discovery discovery;
    int32_t got = ((read_fn)VEP_FW_READ)(fd, &discovery, sizeof(discovery));
    (void)((close_fn)VEP_FW_CLOSE)(fd);
    if (got != sizeof(discovery) || discovery.magic != VEP_DISCOVERY_MAGIC
        || discovery.abi_version != VEP_ABI_VERSION || discovery.struct_size != sizeof(discovery)) return VEP_ABI;
    vep = discovery.api;
    if (!vep || vep->abi_version != VEP_ABI_VERSION || vep->struct_size != sizeof(*vep)) return VEP_ABI;
    if (discovery.recovery.mode == VEP_RECOVERY_SAFE) return VEP_SAFE_MODE;
    static const uint8_t name[] = VEP_MODULE_ID;
    int32_t rc = vep->register_module(name, sizeof(name) - 1, &vep_owner);
    if (rc) return rc;
    rc = vep_module_setup();
    if (!rc) rc = vep->set_enabled(vep_owner, 0);
    if (rc) (void)vep->unregister_module(vep_owner);
    return rc;
}
__attribute__((constructor)) static void vep_module_init(void) {
    if (!vep_target_matches()) { vep_module_status = VEP_FIRMWARE; return; }
    vep_module_status = vep_module_start();
    vep_write_status(vep_module_status);
}
__attribute__((destructor)) static void vep_module_fini(void) {
    if (vep && vep_owner) vep_module_status = vep->unregister_module(vep_owner);
}
#endif
