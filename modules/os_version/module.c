#define VEP_MODULE_ID "org.veposed.os_version"
#define VEP_MODULE_STATUS_PATH "/data/veposed-moye-status.txt"
#include "veposed_module.h"

static int32_t vep_module_setup(void) {
    uint32_t handle;
    return vep->hook_text(vep_owner, (const uint8_t *)"settings.about.os_version",
                          (const uint8_t *)"MOYE.114514", &handle);
}
