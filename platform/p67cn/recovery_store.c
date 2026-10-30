/* Exact p67cn persistent guard. A torn record is rejected by the Rust CRC. */
#include "veposed.h"
#include "veposed_target.h"

#define GUARD_PATH "/data/veposed-guard.bin"
#define DISABLE_PATH "/data/veposed.disable"
#define LOAD_MARKER "/data/veposed-load.pending"
#define RECORD_SIZE 32u

typedef int (*open_fn)(const char *, int, ...);
typedef int32_t (*read_fn)(int, void *, uint32_t);
typedef int32_t (*write_fn)(int, const void *, uint32_t);
typedef int (*fd_fn)(int);
typedef int *(*errno_fn)(void);

static int missing(void) { return *((errno_fn)VEP_FW_ERRNO_LOCATION)() == 2; }

int32_t vep_guard_read(uint8_t *record) {
    int fd = ((open_fn)VEP_FW_OPEN)(DISABLE_PATH, 1);
    if (fd >= 0) {
        (void)((fd_fn)VEP_FW_CLOSE)(fd);
        return 2;
    }
    if (!missing()) return -1;
    fd = ((open_fn)VEP_FW_OPEN)(GUARD_PATH, 1);
    if (fd < 0) return missing() ? 1 : -1;
    uint32_t used = 0;
    while (used < RECORD_SIZE) {
        int32_t got = ((read_fn)VEP_FW_READ)(fd, record + used, RECORD_SIZE - used);
        if (got <= 0) { (void)((fd_fn)VEP_FW_CLOSE)(fd); return -1; }
        used += (uint32_t)got;
    }
    uint8_t extra;
    int32_t trailing = ((read_fn)VEP_FW_READ)(fd, &extra, 1);
    int closed = ((fd_fn)VEP_FW_CLOSE)(fd);
    return trailing == 0 && closed == 0 ? 0 : -1;
}

int32_t vep_guard_write(const uint8_t *record) {
    /* O_TRUNC keeps an interrupted write detectable and repairs oversized records. */
    int fd = ((open_fn)VEP_FW_OPEN)(GUARD_PATH, 2 | 4 | 32, 0600);
    if (fd < 0) return -1;
    uint32_t used = 0;
    while (used < RECORD_SIZE) {
        int32_t written = ((write_fn)VEP_FW_WRITE)(fd, record + used, RECORD_SIZE - used);
        if (written <= 0) { (void)((fd_fn)VEP_FW_CLOSE)(fd); return -1; }
        used += (uint32_t)written;
    }
    int synced = ((fd_fn)VEP_FW_FSYNC)(fd);
    int closed = ((fd_fn)VEP_FW_CLOSE)(fd);
    return synced == 0 && closed == 0 ? 0 : -1;
}

int32_t vep_clear_load_marker(void) {
    typedef int (*unlink_fn)(const char *);
    int result = ((unlink_fn)VEP_FW_UNLINK)(LOAD_MARKER);
    return result == 0 || missing() ? 0 : VEP_STORAGE;
}

int32_t vep_clear_disable_marker(void) {
    typedef int (*unlink_fn)(const char *);
    int result = ((unlink_fn)VEP_FW_UNLINK)(DISABLE_PATH);
    return result == 0 || missing() ? 0 : VEP_STORAGE;
}
