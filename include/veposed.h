#ifndef VEPOSED_H
#define VEPOSED_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define VEP_ABI_VERSION 4u
#define VEP_POINTER 1u
#define VEP_INLINE 2u

enum vep_error {
    VEP_OK = 0, VEP_ARGUMENT = -1, VEP_CAPACITY = -2, VEP_NOT_FOUND = -3,
    VEP_CONFLICT = -4, VEP_UNSUPPORTED = -5, VEP_SIGNATURE = -6,
    VEP_MEMORY = -7, VEP_BUSY = -8, VEP_FIRMWARE = -9, VEP_ABI = -10,
    VEP_SAFE_MODE = -11, VEP_STORAGE = -12
};

typedef struct {
    uint32_t kind;
    uintptr_t address;
    uintptr_t expected_pointer;
    uint8_t expected_code[16];
} vep_target;

/* Named-point calling contracts: arguments are integer/pointer words. */
#define VEP_VOID2 1u
#define VEP_WORD2 2u
#define VEP_WORD4 3u
#define VEP_VOID0 4u
#define VEP_WORD0 5u
#define VEP_VOID1 6u
#define VEP_WORD1 7u
#define VEP_VOID3 8u
#define VEP_WORD3 9u
#define VEP_VOID4 10u
/* Board-only recipe; modules use names through attach_named/hook_text. */
typedef struct {
    uint8_t name[48];
    uint32_t contract;
    vep_target target;
    uintptr_t caller;          /* 0 = any callsite */
    uintptr_t caller2;         /* optional second normalized return PC */
    uintptr_t subject_slot;    /* 0 = any object; otherwise args[0] must match *slot */
    uintptr_t quiescent_slot;  /* *slot must be zero while installing */
    uintptr_t active_slot;     /* *slot must be nonzero when dispatching */
    uintptr_t quiescent_slot2; /* optional additional slot that must be zero */
    uintptr_t active_slot2;    /* optional alternative active slot (OR) */
    uint32_t text_arg1;        /* 1 if argument 1 is a NUL-terminated text string */
} vep_named_point;
typedef struct {
    uint8_t name[48];
    uint32_t contract;
} vep_hook_point_info;

typedef struct {
    uint32_t abi_version;
    uint32_t struct_size;
    int32_t (*publish)(uintptr_t execute, size_t length);
    int32_t (*guard_read)(uint8_t *record);       /* 32 bytes; 0=present, 1=absent, 2=disabled */
    int32_t (*guard_write)(const uint8_t *record); /* fsync before returning success */
    const vep_named_point *points;
    uint32_t point_count;
    size_t point_size; /* sizeof(vep_named_point); identifies the board recipe layout */
} vep_platform;

typedef struct {
    uint32_t handle;
    uintptr_t original;
} vep_hook_result;

typedef struct {
    uintptr_t args[4];
    uintptr_t result;
    uint32_t return_early;
    uintptr_t original; /* read-only; valid only for this callback invocation */
    uint32_t contract;  /* read-only VEP_VOID0..4 / VEP_WORD0..4 */
} vep_call;

typedef void (*vep_callback)(vep_call *call, void *user_data);
typedef struct {
    vep_callback before;
    vep_callback after;
    void *user_data;
    int32_t priority;
} vep_callbacks;

/* Call from thread context. Storage and callback code remain live until detached.
 * Quiesce affected targets before install/removal, especially for inline hooks.
 * publish synchronizes writable aliases with instruction fetches before returning.
 */
int32_t veposed_init(const vep_platform *platform);
int32_t veposed_register(const uint8_t *name, size_t length, uint32_t *owner);
/* A typed replacement preserves the target's complete AAPCS signature. */
int32_t veposed_replace(uint32_t owner, const vep_target *target,
                       uintptr_t replacement, vep_hook_result *result);
/* Callback dispatch is limited to uintptr_t f(uintptr_t,uintptr_t,uintptr_t,uintptr_t). */
int32_t veposed_attach(uint32_t owner, const vep_target *target,
                      const vep_callbacks *callbacks, uint32_t *handle);
int32_t veposed_detach(uint32_t owner, uint32_t handle);
/* Disabling a raw module restores its sites while preserving registration. */
int32_t veposed_set_enabled(uint32_t owner, uint32_t enabled);
int32_t veposed_unregister(uint32_t owner);

#define VEP_RECOVERY_CLEAN 0u
#define VEP_RECOVERY_ARMED 1u
#define VEP_RECOVERY_SAFE 2u
typedef struct {
    uint32_t mode;
    uint32_t reason;
    uint32_t failed_sessions;
    uint32_t active_sites;
    int32_t last_error;
    int32_t rollback_error;
} vep_recovery_status;
int32_t veposed_recovery_status(vep_recovery_status *status);
int32_t veposed_enter_safe_mode(void);
/* All sites must have been restored. Current session stays in safe mode. */
int32_t veposed_recovery_reset(void);

typedef struct {
    uint32_t id;
    uint8_t name[48];
    uint32_t name_len;
    uint32_t enabled;
    uint32_t hook_count;
} vep_module_info;
int32_t veposed_list_modules(vep_module_info *output, size_t capacity, uint32_t *count);

/* Names are NUL terminated (max 47 bytes). Text is copied (max 95 bytes).
 * hook_text requires a point marked text_arg1 by the board recipe.
 * attach_named supports before/after, argument/result edits and return_early.
 * Only the declared argument words are meaningful. VOID contracts have no result.
 * Normal priority, module switches, detach and recovery apply to named hooks.
 */
int32_t veposed_attach_named(uint32_t owner, const uint8_t *name,
                            const vep_callbacks *callbacks, uint32_t *handle);
int32_t veposed_hook_text(uint32_t owner, const uint8_t *name,
                         const uint8_t *text, uint32_t *handle);
int32_t veposed_list_hook_points(vep_hook_point_info *output, size_t capacity, uint32_t *count);
/* Invoke the original using current args; sets result and return_early, so the
 * dispatcher will not invoke it again. May only be called with a live context. */
uintptr_t veposed_call_original(vep_call *call);
/* Callback-only direct call of a verified named entry, bypassing its hooks.
 * args always points to four words; only the declared argument count is read. */
int32_t veposed_call_named(const uint8_t *name, const uintptr_t *args, uintptr_t *result);

typedef struct {
    uint32_t abi_version;
    uint32_t struct_size;
    int32_t (*register_module)(const uint8_t *, size_t, uint32_t *);
    int32_t (*replace)(uint32_t, const vep_target *, uintptr_t, vep_hook_result *);
    int32_t (*attach)(uint32_t, const vep_target *, const vep_callbacks *, uint32_t *);
    int32_t (*detach)(uint32_t, uint32_t);
    int32_t (*set_enabled)(uint32_t, uint32_t);
    int32_t (*unregister_module)(uint32_t);
    int32_t (*recovery_status)(vep_recovery_status *);
    int32_t (*enter_safe_mode)(void);
    int32_t (*recovery_reset)(void);
    int32_t (*list_modules)(vep_module_info *, size_t, uint32_t *);
    int32_t (*attach_named)(uint32_t, const uint8_t *, const vep_callbacks *, uint32_t *);
    int32_t (*hook_text)(uint32_t, const uint8_t *, const uint8_t *, uint32_t *);
    int32_t (*list_hook_points)(vep_hook_point_info *, size_t, uint32_t *);
    uintptr_t (*call_original)(vep_call *);
    int32_t (*call_named)(const uint8_t *, const uintptr_t *, uintptr_t *);
} vep_api;
const vep_api *veposed_get_api(void);

#define VEP_DISCOVERY_MAGIC 0x56504531u
#define VEP_DEVICE_PATH "/dev/veposed"
typedef struct {
    uint32_t magic;
    uint32_t abi_version;
    uint32_t struct_size;
    const vep_api *api;
    vep_recovery_status recovery;
} vep_discovery;

#ifdef __cplusplus
}
#endif
#endif
