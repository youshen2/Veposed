/* p67cn native application/page ABI, independently implemented using Canopus'
 * recovered layout. The resident runtime owns descriptors until reboot.
 */
#include "veposed.h"
#include "veposed_target.h"

#define APP_ID 0xceu
#define MAX_MODULES 16u
typedef struct page page;
struct page {
    void *parent;
    uint8_t pad04[12];
    const char *name;
    uint16_t page_id, app_id, flags;
    uint8_t pad1a[2];
    int32_t deadline, priority;
    uint32_t destroy_state;
    uint8_t lifecycle, layer, kind, pad2b;
    void *context, *root;
    int (*signal)(page *, uint32_t, void *);
    void *default56;
    uint8_t pad3c[4];
    void *previous, *next, *runtime_parent;
    int (*create)(page *, void *, void *);
    int (*resume)(page *);
    void *foreground;
    int (*pause)(page *);
    int (*destroy)(page *);
    void *ui_destroy, *extra100, *system_back, *extra108, *scroll;
};
typedef struct {
    uint32_t previous, next;
    const char *package, *icon;
    uint16_t app_id;
    uint8_t flags, pad13;
    const char *owned20, *owned24;
    const char *(*metadata)(void);
    uint8_t pad20[16];
    void *pages;
    uint8_t pad34[8];
    uint8_t hidden, tail[3];
} application;
_Static_assert(sizeof(page) == 116 && offsetof(page, create) == 76 && offsetof(page, destroy) == 92, "p67cn page ABI");
_Static_assert(sizeof(application) == 64 && offsetof(application, package) == 8, "p67cn application ABI");

typedef void (*event_callback)(void *);
typedef struct { uint32_t action, module; } action;
static page descriptor;
static void *container, *status_card, *modules_heading, *empty_card;
static void *module_cards[MAX_MODULES], *recovery_heading, *stop_card, *reset_card;
static void *diagnostics_heading, *diagnostics_card;
static action module_actions[MAX_MODULES];
static vep_module_info modules[MAX_MODULES];
static uint32_t module_count;
static char module_titles[MAX_MODULES][49], module_details[MAX_MODULES][80];
static char status_text[96], diagnostics_title[64], diagnostics_text[64];
static int32_t last_action;
static int restart_ready;
volatile int32_t veposed_manager_status = VEP_ABI;
static int registered, launcher_added;
int32_t vep_recovery_rearm(void);

static const char *display_name(void) { return "Veposed 管理器"; }
static application app = {
    .package = "org.veposed.manager", .icon = "/data/veposed/manager_icon.bin",
    .app_id = APP_ID, .metadata = display_name,
};

static char *text(char *out, const char *s) { while (*s) *out++ = *s++; *out = 0; return out; }
static char *number(char *out, uint32_t n) {
    char digits[10]; uint32_t count = 0;
    do { digits[count++] = (char)('0' + n % 10); n /= 10; } while (n);
    while (count) *out++ = digits[--count]; *out = 0; return out;
}
static char *signed_number(char *out, int32_t n) {
    if (n < 0) *out++ = '-';
    return number(out, n < 0 ? 0u - (uint32_t)n : (uint32_t)n);
}
static int same_name(const vep_module_info *m, const char *name) {
    uint32_t i = 0;
    while (name[i] && i < m->name_len && name[i] == (char)m->name[i]) i++;
    return i == m->name_len && !name[i];
}
static void set_text(void *label, const char *value) {
    ((void (*)(void *, const char *))VEP_FW_LABEL_SET_TEXT)(label, value);
}
static void place(void *object, int y, int width, int height) {
    ((void (*)(void *, int32_t, int32_t))VEP_FW_OBJECT_SET_SIZE)(object, width, height);
    ((void (*)(void *, uint32_t, int32_t, int32_t))VEP_FW_OBJECT_ALIGN)(object, 2, 0, y);
}
static void click(void *event);

static void flag(void *object, uint32_t value, int enabled) {
    if (!object) return;
    if (enabled) ((void (*)(void *, uint32_t))VEP_FW_OBJECT_ADD_FLAG)(object, value);
    else ((void (*)(void *, uint32_t))VEP_FW_OBJECT_CLEAR_FLAG)(object, value);
}

static void heading(void **slot, const char *value, int y) {
    if (*slot) { place(*slot, y, 296, 32); return; }
    void *object = ((void *(*)(void *))VEP_FW_LABEL_CREATE)(container);
    if (!object) return;
    ((int (*)(void *, const void *, int32_t, uint32_t))VEP_FW_STYLE_APPLY)(object, (const void *)VEP_FW_STYLE_24, 255, 0);
    set_text(object, value); place(object, y, 296, 32);
    *slot = object;
}

/* Use the same stock LVX item as Settings and Canopus. The item owns its
 * labels and trailing widget; all of them are freed with the page root. */
static void card(void **slot, const char *title, const char *detail, int y,
                 uint8_t trailing, uint8_t selected, action *cookie) {
    if (!*slot) {
        *slot = ((void *(*)(void *, const char *, const char *, uint8_t))VEP_FW_LIST_ROW_CREATE)(container, title, detail, trailing);
        if (!*slot) return;
        flag(*slot, 2, cookie != 0);
        if (cookie) {
            ((void (*)(void *, event_callback, uint32_t, void *))VEP_FW_EVENT_ADD)(*slot, click, 7, cookie);
        }
        /* The whole card is the sole hit target. A tap on the switch must not
         * toggle once in LVGL and a second time in the framework callback. */
        void *end = ((void *(*)(void *))VEP_FW_LIST_ROW_TRAILING)(*slot);
        flag(end, 2, 0);
    }
    ((void (*)(void *, const void *, const char *, const char *, int32_t, uint8_t))VEP_FW_LIST_ROW_UPDATE)(*slot, 0, title, detail, 0, selected);
    place(*slot, y, 328, 104);
    flag(*slot, 1, 0);
}

static action stop_action = { 1, 0 }, reset_action = { 2, 0 };

static void render(void) {
    if (!container) return;
    vep_recovery_status state;
    if (veposed_recovery_status(&state)) return;
    if (veposed_list_modules(modules, MAX_MODULES, &module_count)) return;
    uint32_t visible = 0;
    for (uint32_t i = 0; i < module_count; i++) {
        if (same_name(&modules[i], "veposed.example")) continue;
        vep_module_info *m = &modules[i];
        char *out = module_titles[visible];
        if (same_name(m, "org.veposed.os_version")) out = text(out, "OS 版本替换");
        else { for (uint32_t j = 0; j < m->name_len; j++) *out++ = (char)m->name[j]; *out = 0; }
        out = text(module_details[visible], m->enabled ? "已启用 · " : "已停用 · ");
        out = number(out, m->hook_count); text(out, " 处 Hook");
        module_actions[visible] = (action){ 0, m->id };
        card(&module_cards[visible], module_titles[visible], module_details[visible],
             152 + (int)visible * 116, 1, m->enabled != 0, &module_actions[visible]);
        visible++;
    }
    for (uint32_t i = visible; i < MAX_MODULES; i++) {
        flag(module_cards[i], 1, 1);
    }
    char *out = number(status_text, visible);
    out = text(out, " 个模块 · "); out = number(out, state.active_sites); text(out, " 处 Hook");
    const char *title = restart_ready ? "隔离已重置 · 请重启" : state.mode == VEP_RECOVERY_SAFE ? "安全模式" : "Veposed 已加载";
    card(&status_card, title, status_text, 0, 0, 0, 0);
    heading(&modules_heading, "模块", 116);
    if (!visible) card(&empty_card, "暂无模块", "安装模块后在这里管理", 152, 0, 0, 0);
    else flag(empty_card, 1, 1);

    int y = 152 + (int)(visible ? visible : 1) * 116;
    heading(&recovery_heading, "恢复", y);
    card(&stop_card, "停用全部 Hook", "进入安全模式，保留管理器", y + 36, 3, 1, &stop_action);
    card(&reset_card, "重置隔离", restart_ready ? "重启设备后再加载框架" : "允许下次启动，随后手动重启", y + 152, 3, 1, &reset_action);

    out = text(diagnostics_title, "r="); out = number(out, state.reason);
    out = text(out, " n="); out = number(out, state.failed_sessions);
    out = text(out, " last="); out = signed_number(out, state.last_error);
    out = text(diagnostics_text, "rollback="); out = signed_number(out, state.rollback_error);
    out = text(out, " op="); signed_number(out, last_action);
    heading(&diagnostics_heading, "诊断", y + 268);
    card(&diagnostics_card, diagnostics_title, diagnostics_text, y + 304, 0, 0, 0);
}

static void click(void *event) {
    action *a = ((void *(*)(void *))VEP_FW_EVENT_USER_DATA)(event);
    if (!a) return;
    restart_ready = 0;
    if (a->action == 1) last_action = veposed_enter_safe_mode();
    else if (a->action == 2) {
        last_action = veposed_enter_safe_mode();
        if (!last_action) last_action = vep_recovery_rearm();
        if (!last_action) restart_ready = 1;
    } else {
        uint32_t count;
        last_action = veposed_list_modules(modules, MAX_MODULES, &count);
        if (!last_action) {
            last_action = VEP_NOT_FOUND;
            for (uint32_t i = 0; i < count; i++) {
                if (modules[i].id == a->module) {
                    last_action = veposed_set_enabled(a->module, !modules[i].enabled);
                    break;
                }
            }
        }
    }
    render();
}

static void back(void *unused) { (void)unused; ((int (*)(page *))VEP_FW_PAGE_FINISH)(&descriptor); }
static int signal_page(page *p, uint32_t e, void *d) { (void)p; (void)e; (void)d; return 0; }
static int create_page(page *p, void *root, void *data) {
    (void)data;
    p->root = root;
    ((void *(*)(void *, const char *, uint32_t, event_callback, void *))VEP_FW_PAGE_TITLE_CREATE)(root, display_name(), 1, back, 0);
    container = ((void *(*)(void *))VEP_FW_CONTENT_CREATE)(root);
    if (!container) return VEP_MEMORY;
    ((void (*)(void *, int32_t, int32_t))VEP_FW_OBJECT_SET_SIZE)(container, 336, 424);
    ((void (*)(void *, uint32_t, int32_t, int32_t))VEP_FW_OBJECT_ALIGN)(container, 2, 0, 56);
    ((void (*)(void *, int32_t, uint32_t))VEP_FW_CONTENT_PAD_BOTTOM)(container, 32, 0);
    render();
    return 0;
}
static int resume_page(page *p) { (void)p; render(); return 0; }
static int pause_page(page *p) { (void)p; return 0; }
static int destroy_page(page *p) {
    (void)p; container = 0; status_card = 0; modules_heading = 0; empty_card = 0;
    recovery_heading = 0; stop_card = 0; reset_card = 0;
    diagnostics_heading = 0; diagnostics_card = 0;
    for (uint32_t i = 0; i < MAX_MODULES; i++) module_cards[i] = 0;
    return 0;
}

int32_t veposed_manager_register(void) {
    if (!vep_target_matches()) return VEP_FIRMWARE;
    typedef void *(*lookup_fn)(uint16_t);
    if (registered) return 0;
    if (((lookup_fn)VEP_FW_APP_LOOKUP)(APP_ID)) return VEP_CONFLICT;
    descriptor.name = "main"; descriptor.app_id = APP_ID;
    descriptor.signal = signal_page; descriptor.create = create_page;
    descriptor.resume = resume_page; descriptor.pause = pause_page; descriptor.destroy = destroy_page;
    page *pages[] = { &descriptor };
    (void)((int (*)(const application *, page *const *, uint32_t))VEP_FW_APP_INSTALL)(&app, pages, 1);
    int rc = ((lookup_fn)VEP_FW_APP_LOOKUP)(APP_ID) ? 0 : VEP_NOT_FOUND;
    veposed_manager_status = rc;
    if (!rc) registered = 1;
    return rc;
}

int32_t veposed_manager_launcher(void) {
    if (launcher_added) return 0;
    if (veposed_manager_status) return veposed_manager_status;
    // The stock function returns its final log call's value, not an error code.
    ((void (*)(uint16_t))VEP_FW_LAUNCHER_ADD)(APP_ID);
    veposed_manager_status = 0;
    launcher_added = 1;
    return veposed_manager_status;
}
