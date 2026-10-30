/* Host behavior model: the ARM build checks the real page/descriptor layout. */
#include "veposed.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct widget widget;
struct widget {
    widget *parent, *trailing;
    void (*click)(void *);
    void *cookie;
    uint32_t flags;
    int x, y, width, height, selected;
    char title[160], detail[160];
};
static widget widgets[160];
static unsigned allocated, toggles, disables, resets;
static int toggle_error, reset_error;
static vep_recovery_status recovery;
static vep_module_info registry[3];
static unsigned registry_count;

static widget *new_widget(void *parent) {
    assert(allocated < sizeof(widgets) / sizeof(widgets[0]));
    widget *w = &widgets[allocated++];
    memset(w, 0, sizeof(*w)); w->parent = parent; return w;
}
static void *row_create(void *parent, const char *title, const char *detail, uint8_t end) {
    widget *w = new_widget(parent);
    snprintf(w->title, sizeof(w->title), "%s", title);
    snprintf(w->detail, sizeof(w->detail), "%s", detail);
    if (end) { w->trailing = new_widget(w); w->trailing->flags = 2; }
    return w;
}
static void row_update(void *object, const void *icon, const char *title, const char *detail, int32_t value, uint8_t selected) {
    (void)icon; (void)value;
    widget *w = object;
    snprintf(w->title, sizeof(w->title), "%s", title);
    snprintf(w->detail, sizeof(w->detail), "%s", detail);
    w->selected = selected;
}
static void *row_trailing(void *object) { return ((widget *)object)->trailing; }
static void label_text(void *object, const char *value) { snprintf(((widget *)object)->title, 160, "%s", value); }
static void object_size(void *object, int32_t width, int32_t height) { widget *w = object; w->width = width; w->height = height; }
static void object_align(void *object, uint32_t align, int32_t x, int32_t y) { assert(align == 2); widget *w = object; w->x = x; w->y = y; }
static void flag_add(void *object, uint32_t flags) { ((widget *)object)->flags |= flags; }
static void flag_clear(void *object, uint32_t flags) { ((widget *)object)->flags &= ~flags; }
static int style_apply(void *object, const void *style, int32_t opacity, uint32_t selector) {
    (void)object; (void)style; assert(opacity == 255 && selector == 0); return 0;
}
static void event_add(void *object, void (*callback)(void *), uint32_t code, void *cookie) {
    widget *w = object; assert(code == 7 && !w->click); w->click = callback; w->cookie = cookie;
}
static void *event_data(void *event) { return event; }
static void *page_title(void *root, const char *title, uint32_t mode, void (*back)(void *), void *cookie) {
    (void)root; (void)title; (void)mode; (void)back; (void)cookie; return root;
}
static void pad_bottom(void *object, int32_t pad, uint32_t selector) { (void)object; assert(pad == 32 && selector == 0); }
static int finish(void *page) { (void)page; return 0; }
static void *lookup(uint16_t id) { (void)id; return NULL; }
static int install(const void *app, void *const *pages, uint32_t count) { (void)app; (void)pages; (void)count; return 0; }
static void launcher(uint16_t id) { (void)id; }
static int vep_target_matches(void) { return 1; }

#define VEP_FW_LIST_ROW_CREATE row_create
#define VEP_FW_LIST_ROW_UPDATE row_update
#define VEP_FW_LIST_ROW_TRAILING row_trailing
#define VEP_FW_LABEL_CREATE new_widget
#define VEP_FW_LABEL_SET_TEXT label_text
#define VEP_FW_OBJECT_SET_SIZE object_size
#define VEP_FW_OBJECT_ALIGN object_align
#define VEP_FW_OBJECT_ADD_FLAG flag_add
#define VEP_FW_OBJECT_CLEAR_FLAG flag_clear
#define VEP_FW_STYLE_APPLY style_apply
#define VEP_FW_STYLE_24 0
#define VEP_FW_EVENT_ADD event_add
#define VEP_FW_EVENT_USER_DATA event_data
#define VEP_FW_PAGE_TITLE_CREATE page_title
#define VEP_FW_CONTENT_CREATE new_widget
#define VEP_FW_CONTENT_PAD_BOTTOM pad_bottom
#define VEP_FW_PAGE_FINISH finish
#define VEP_FW_APP_LOOKUP lookup
#define VEP_FW_APP_INSTALL install
#define VEP_FW_LAUNCHER_ADD launcher
#define _Static_assert(condition, message)
#include "../manager/native.c"
#undef _Static_assert

int32_t veposed_recovery_status(vep_recovery_status *out) { *out = recovery; return 0; }
int32_t veposed_list_modules(vep_module_info *out, size_t capacity, uint32_t *count) {
    assert(capacity >= registry_count);
    memcpy(out, registry, registry_count * sizeof(*out)); *count = registry_count; return 0;
}
int32_t veposed_set_enabled(uint32_t id, uint32_t enabled) {
    toggles++;
    if (toggle_error) return toggle_error;
    for (unsigned i = 0; i < registry_count; i++) if (registry[i].id == id) { registry[i].enabled = enabled; return 0; }
    return VEP_NOT_FOUND;
}
int32_t veposed_enter_safe_mode(void) {
    disables++; recovery.mode = VEP_RECOVERY_SAFE; recovery.active_sites = 0;
    for (unsigned i = 0; i < registry_count; i++) registry[i].enabled = 0;
    return 0;
}
int32_t vep_recovery_rearm(void) { resets++; return reset_error; }

static void tap(widget *w) {
    /* LVGL resolves a non-clickable trailing widget to its clickable parent. */
    while (w && !(w->flags & 2)) w = w->parent;
    assert(w && w->click); w->click(w->cookie);
}
static void set_module(unsigned i, unsigned id, const char *name, int enabled) {
    registry[i] = (vep_module_info){ .id = id, .enabled = enabled, .hook_count = 1 };
    registry[i].name_len = (uint32_t)strlen(name);
    memcpy(registry[i].name, name, registry[i].name_len);
}
int main(void) {
    set_module(0, 7, "veposed.example", 1);
    set_module(1, 42, "org.veposed.os_version", 0);
    registry_count = 2; recovery.active_sites = 1;
    assert(create_page(&descriptor, new_widget(NULL), NULL) == 0);
    widget *module = module_cards[0];
    assert(module && module->trailing && !module_cards[1]);
    assert(!strcmp(module->title, "OS 版本替换") && !module->selected);
    assert(module->y >= ((widget *)status_card)->y + ((widget *)status_card)->height);
    assert(((widget *)stop_card)->y >= module->y + module->height);
    tap(module->trailing);
    assert(toggles == 1 && registry[1].enabled && module->selected);
    toggle_error = VEP_BUSY;
    tap(module);
    assert(toggles == 2 && registry[1].enabled && module->selected);
    assert(strstr(((widget *)diagnostics_card)->detail, "op=-") != NULL);
    toggle_error = 0;
    tap(stop_card);
    assert(disables == 1 && !module->selected && recovery.mode == VEP_RECOVERY_SAFE);
    reset_error = VEP_BUSY;
    tap(reset_card);
    assert(resets == 1 && !restart_ready && recovery.mode == VEP_RECOVERY_SAFE);
    reset_error = 0;
    tap(reset_card);
    assert(resets == 2 && restart_ready && recovery.mode == VEP_RECOVERY_SAFE);
    assert(strstr(((widget *)status_card)->title, "请重启") != NULL);
    unsigned before = allocated;
    resume_page(&descriptor); assert(allocated == before);
    registry_count = 1; render();
    assert(module->flags & 1); assert(empty_card && !(((widget *)empty_card)->flags & 1));
    registry_count = 2; render();
    assert(!(module->flags & 1)); assert(((widget *)empty_card)->flags & 1);
    destroy_page(&descriptor);
    assert(!container && !status_card && !module_cards[0] && !diagnostics_card);
    allocated = 0;
    assert(create_page(&descriptor, new_widget(NULL), NULL) == 0);
    assert(module_cards[0] && ((widget *)module_cards[0])->trailing);
    puts("manager UI: native cards, one tap/one toggle, failed action state, recovery, empty list and reopen PASS");
}
