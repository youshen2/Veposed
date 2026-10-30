/* Native loadable module: a pointer-hook self-test and an optional typed UI hook. */
#include "veposed.h"
#include "veposed_target.h"

typedef uintptr_t (*four_words)(uintptr_t, uintptr_t, uintptr_t, uintptr_t);
static uint32_t owner;
static const char *startup_stage = "init";
static int driver_registered;
int32_t vep_guard_read(uint8_t *record);
int32_t vep_guard_write(const uint8_t *record);
int32_t vep_clear_load_marker(void);
int32_t vep_clear_disable_marker(void);
static void write_status(int32_t status);
#ifdef VEP_NATIVE_MANAGER
int32_t veposed_manager_register(void);
int32_t veposed_manager_launcher(void);
#endif
volatile int32_t veposed_device_status = VEP_ABI;
volatile uint32_t veposed_image_calls;
#ifdef VEP_IMAGE_PROBE
static vep_hook_result image_hook;
#endif

/* The exact .043 file_operations layout is twelve 32-bit words. */
typedef struct {
    int (*open)(void *);
    int (*close)(void *);
    int32_t (*read)(void *, void *, uint32_t);
    int32_t (*write)(void *, const void *, uint32_t);
    uintptr_t remaining[8];
} file_operations;
_Static_assert(sizeof(file_operations) == 48, "p67cn file_operations ABI");

static int control_open(void *file) { (void)file; return 0; }
static int control_close(void *file) { (void)file; return 0; }
static int32_t control_read(void *file, void *buffer, uint32_t size) {
    (void)file;
    if (size < sizeof(vep_discovery)) return -22;
    vep_discovery discovery = {
        .magic = VEP_DISCOVERY_MAGIC, .abi_version = VEP_ABI_VERSION,
        .struct_size = sizeof(vep_discovery), .api = veposed_get_api()
    };
    (void)veposed_recovery_status(&discovery.recovery);
    const uint8_t *source = (const uint8_t *)&discovery;
    uint8_t *destination = buffer;
    for (size_t i = 0; i < sizeof(discovery); ++i) destination[i] = source[i];
    return sizeof(discovery);
}

static int command_is(const void *buffer, uint32_t size, const char *command, uint32_t length) {
    const uint8_t *bytes = buffer;
    if (size != length && !(size == length + 1 && bytes[length] == '\n')) return 0;
    for (uint32_t i = 0; i < length; ++i) if (bytes[i] != (uint8_t)command[i]) return 0;
    return 1;
}

int32_t vep_recovery_rearm(void) {
    int32_t rc = veposed_recovery_reset();
    if (!rc) rc = vep_clear_load_marker();
    if (!rc) rc = vep_clear_disable_marker();
    return rc;
}

static int32_t control_write(void *file, const void *buffer, uint32_t size) {
    (void)file;
    int32_t rc;
    if (command_is(buffer, size, "disable", 7)) {
        rc = veposed_enter_safe_mode();
    } else if (command_is(buffer, size, "reset", 5)) {
        rc = vep_recovery_rearm();
    }
#ifdef VEP_NATIVE_MANAGER
    else if (command_is(buffer, size, "manager-register", 16)) rc = veposed_manager_register();
    else if (command_is(buffer, size, "manager-launcher", 16)) rc = veposed_manager_launcher();
#endif
    else { return -22; }
    write_status(rc);
    return rc == VEP_OK ? (int32_t)size : rc;
}

static const file_operations operations = {
    .open = control_open, .close = control_close, .read = control_read, .write = control_write
};

static int install_discovery(void) {
    typedef int (*register_fn)(const char *, const void *, uint32_t, void *);
    typedef int (*open_fn)(const char *, int, ...);
    typedef int (*close_fn)(int);
    int fd = ((open_fn)VEP_FW_OPEN)(VEP_DEVICE_PATH, 1);
    if (fd >= 0) { (void)((close_fn)VEP_FW_CLOSE)(fd); return VEP_CONFLICT; }
    int rc = ((register_fn)VEP_FW_REGISTER_DRIVER)(VEP_DEVICE_PATH, &operations, 0600, 0);
    if (rc != 0) return rc;
    fd = ((open_fn)VEP_FW_OPEN)(VEP_DEVICE_PATH, 1);
    if (fd < 0) return VEP_MEMORY;
    (void)((close_fn)VEP_FW_CLOSE)(fd);
    driver_registered = 1;
    return VEP_OK;
}

static uintptr_t sum(uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d) {
    return a + b + c + d;
}
static four_words volatile sum_slot = sum;

static void before(vep_call *call, void *data) {
    (void)data;
    call->args[0] += 10;
}
static void after(vep_call *call, void *data) {
    (void)data;
    call->result *= 2;
}

/* Only used by the pointer-hook self-test. The PSRAM probe requires a board-
 * specific cache publisher supplied with --publisher; DSB/ISB alone are not
 * evidence of coherence between cached PSRAM data/instruction views. */
#ifdef VEP_BOARD_PUBLISHER
extern int32_t vep_board_publish(uintptr_t execute, size_t length);
#define publish vep_board_publish
#else
static int32_t publish(uintptr_t execute, size_t length) {
    (void)execute; (void)length;
    return VEP_UNSUPPORTED;
}
#endif

static int32_t self_test(void) {
    vep_target target = { .kind = VEP_POINTER, .address = (uintptr_t)&sum_slot,
                          .expected_pointer = (uintptr_t)sum };
    vep_callbacks callbacks = { .before = before, .after = after, .priority = 100 };
    uint32_t handle = 0;
    startup_stage = "selftest-attach";
    int32_t rc = veposed_attach(owner, &target, &callbacks, &handle);
    if (rc != VEP_OK) return rc;
    startup_stage = "selftest-call";
    uintptr_t hooked = sum_slot(1, 2, 3, 4);
    startup_stage = "selftest-restore";
    rc = veposed_detach(owner, handle);
    if (rc != VEP_OK) return rc;
    return hooked == 40 && sum_slot(1, 2, 3, 4) == 10 ? VEP_OK : VEP_CONFLICT;
}

#ifdef VEP_IMAGE_PROBE
static void *image_create(void *parent, const uint8_t *options) {
    typedef void *(*image_fn)(void *, const uint8_t *);
    veposed_image_calls++;
    return ((image_fn)image_hook.original)(parent, options);
}

static int32_t install_image_probe(void) {
    vep_target target = { .kind = VEP_INLINE, .address = VEP_IMAGE_CREATE,
                          .expected_code = VEP_IMAGE_SIGNATURE };
    return veposed_replace(owner, &target, (uintptr_t)image_create, &image_hook);
}
#endif

static size_t append_text(char *output, size_t used, const char *text) {
    while (*text) output[used++] = *text++;
    return used;
}
static size_t append_number(char *output, size_t used, uint32_t value) {
    char digits[10];
    size_t count = 0;
    do { digits[count++] = (char)('0' + value % 10); value /= 10; } while (value);
    while (count) output[used++] = digits[--count];
    return used;
}
static size_t append_signed(char *output, size_t used, int32_t value) {
    if (value < 0) output[used++] = '-';
    return append_number(output, used, value < 0 ? 0u - (uint32_t)value : (uint32_t)value);
}

static size_t append_hex(char *output, size_t used, uintptr_t value) {
    const char digits[] = "0123456789abcdef";
    for (int shift = 28; shift >= 0; shift -= 4) output[used++] = digits[(value >> shift) & 15u];
    return used;
}

static void write_status(int32_t status) {
    typedef int (*open_fn)(const char *, int, ...);
    typedef int32_t (*write_fn)(int, const void *, uint32_t);
    typedef int (*close_fn)(int);
    /* Fixed-size record: all runs replace the full previous record. */
    char report[224];
    size_t i;
    for (i = 0; i < sizeof(report); ++i) report[i] = ' ';
    vep_recovery_status recovery;
    if (veposed_recovery_status(&recovery) != 0) return;
    i = append_text(report, 0, "Veposed status=");
    i = append_signed(report, i, status);
    i = append_text(report, i, " mode=");
    i = append_number(report, i, recovery.mode);
    i = append_text(report, i, " reason=");
    i = append_number(report, i, recovery.reason);
    i = append_text(report, i, " failures=");
    i = append_number(report, i, recovery.failed_sessions);
    i = append_text(report, i, " sites=");
    i = append_number(report, i, recovery.active_sites);
    i = append_text(report, i, " last=");
    i = append_signed(report, i, recovery.last_error);
    i = append_text(report, i, " rollback=");
    i = append_signed(report, i, recovery.rollback_error);
    i = append_text(report, i, " phase=");
    i = append_text(report, i, startup_stage);
    i = append_text(report, i, " slot=");
    (void)append_hex(report, i, (uintptr_t)&sum_slot);
    report[sizeof(report) - 1] = '\n';
    int fd = ((open_fn)VEP_FW_OPEN)("/data/veposed-status.txt", 2 | 4, 0600);
    if (fd < 0) return;
    size_t used = 0;
    while (used < sizeof(report)) {
        int32_t wrote = ((write_fn)VEP_FW_WRITE)(fd, report + used, sizeof(report) - used);
        if (wrote <= 0) break;
        used += (size_t)wrote;
    }
    (void)((close_fn)VEP_FW_CLOSE)(fd);
}

__attribute__((constructor))
static void module_init(void) {
    vep_platform platform = { VEP_ABI_VERSION, sizeof(vep_platform), publish, vep_guard_read, vep_guard_write, VEP_NAMED_POINTS, VEP_NAMED_POINT_COUNT };
    int32_t rc = veposed_init(&platform);
    /* The identity guard precedes all firmware function calls. */
    if (rc != VEP_OK) { veposed_device_status = rc; return; }
    startup_stage = "driver";
    rc = install_discovery();
    vep_recovery_status recovery;
    (void)veposed_recovery_status(&recovery);
    if (rc == VEP_OK && recovery.mode == VEP_RECOVERY_SAFE) rc = VEP_SAFE_MODE;
    const uint8_t name[] = "veposed.example";
    if (rc == VEP_OK) { startup_stage = "register"; rc = veposed_register(name, sizeof(name) - 1, &owner); }
    if (rc == VEP_OK) rc = self_test();
#ifdef VEP_IMAGE_PROBE
    if (rc == VEP_OK) rc = install_image_probe();
#endif
    if (rc != VEP_OK && recovery.mode != VEP_RECOVERY_SAFE) {
        (void)veposed_recovery_status(&recovery);
        if (recovery.mode != VEP_RECOVERY_SAFE) (void)veposed_enter_safe_mode();
    }
    if (rc == VEP_OK) startup_stage = "ready";
    veposed_device_status = rc;
    write_status(rc);
}

__attribute__((destructor))
static void module_fini(void) {
    if (driver_registered) {
        typedef int (*unregister_fn)(const char *);
        (void)((unregister_fn)VEP_FW_UNREGISTER_DRIVER)(VEP_DEVICE_PATH);
    }
    if (owner) veposed_device_status = veposed_unregister(owner);
}
