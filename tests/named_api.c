#include "veposed.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static uint8_t journal[32];
static int32_t read_guard(uint8_t *p) { (void)p; return 1; }
static int32_t write_guard(const uint8_t *p) { memcpy(journal,p,32); return 0; }
static char rendered[96];
static uintptr_t subject = 0x1234, subject2 = 0x5678, busy, busy2, active, active2, os_active = 1;
static unsigned originals, entered;
static void set_text(uintptr_t label, uintptr_t text) {
    (void)label; snprintf(rendered,sizeof(rendered),"%s",(const char *)text);
}
static uintptr_t pair(uintptr_t a, uintptr_t b) { originals++; return a+b; }
static uintptr_t sum(uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d) { return a+b+c+d; }
static uintptr_t text_slot, pair_slot, sum_slot;
static size_t text_site;
static void skip(vep_call *c, void *p) { (void)p; c->return_early=1; c->result=77; }
static void double_result(vep_call *c, void *p) { (void)p; c->result*=2; }
static void lower(vep_call *c, void *p) { (void)c; (void)p; entered++; }
static void edit(vep_call *c, void *p) { (void)p; c->args[0]+=10; }
static void replace_with_original(vep_call *c, void *p) {
    (void)p;
    c->args[0]+=10;
    uintptr_t original=veposed_get_api()->call_original(c);
    assert(original==20);
    c->result=original*3;
}
static void call_other(vep_call *c, void *p) {
    (void)p;
    uintptr_t args[4]={2,3,0,0}, value;
    assert(veposed_get_api()->call_named((const uint8_t *)"test.pair",args,&value)==0);
    c->result=value; c->return_early=1;
}
/* Called only to supply an exact synthetic LR in host scope checks. */
extern uintptr_t veposed_named_dispatch(uintptr_t,uintptr_t,uintptr_t,uintptr_t,uintptr_t,size_t);
static void render(uintptr_t label, uintptr_t caller) {
    veposed_named_dispatch(label,(uintptr_t)"stock",0,0,caller,text_site);
}
int main(void) {
    text_slot=(uintptr_t)set_text; pair_slot=(uintptr_t)pair; sum_slot=(uintptr_t)sum;
    vep_named_point points[] = {
        {.name="settings.about.os_version",.contract=VEP_VOID2,
         .target={.kind=VEP_POINTER,.address=(uintptr_t)&text_slot,.expected_pointer=(uintptr_t)set_text},
         .caller=0x400,.subject_slot=(uintptr_t)&subject,.quiescent_slot=(uintptr_t)&busy,.active_slot=(uintptr_t)&os_active,.text_arg1=1},
        {.name="test.pair",.contract=VEP_WORD2,
         .target={.kind=VEP_POINTER,.address=(uintptr_t)&pair_slot,.expected_pointer=(uintptr_t)pair}},
        {.name="test.sum",.contract=VEP_WORD4,
         .target={.kind=VEP_POINTER,.address=(uintptr_t)&sum_slot,.expected_pointer=(uintptr_t)sum}},
        {.name="settings.about.system_version",.contract=VEP_VOID2,
         .target={.kind=VEP_POINTER,.address=(uintptr_t)&text_slot,.expected_pointer=(uintptr_t)set_text},
         .caller=0x500,.caller2=0x600,.subject_slot=(uintptr_t)&subject2,.quiescent_slot=(uintptr_t)&busy,.active_slot=(uintptr_t)&active,.quiescent_slot2=(uintptr_t)&busy2,.active_slot2=(uintptr_t)&active2,.text_arg1=1},
    };
    static vep_named_point catalog[2048];
    memcpy(catalog,points,sizeof(points));
    for (unsigned i=4; i<2048; i++) {
        catalog[i]=points[0];
        memset(catalog[i].name,0,sizeof(catalog[i].name));
        snprintf((char *)catalog[i].name,sizeof(catalog[i].name),"test.catalog.%u",i);
        if (i >= 5) catalog[i].caller=0x700+4*i;
    }
    catalog[4].text_arg1=0;
    /* Global and caller-scoped aliases share the same underlying entry. */
    catalog[2046].caller=0; catalog[2046].caller2=0;
    catalog[2046].subject_slot=0; catalog[2046].active_slot=0;
    catalog[2046].quiescent_slot=0; catalog[2046].text_arg1=0;
    vep_platform platform={VEP_ABI_VERSION,sizeof(platform),0,read_guard,write_guard,catalog,2048,sizeof(vep_named_point)};
    platform.point_size -= sizeof(uintptr_t);
    assert(veposed_init(&platform)==VEP_ABI);
    platform.point_size = sizeof(vep_named_point);
    vep_named_point saved = catalog[2047];
    catalog[2047].quiescent_slot = 1;
    assert(veposed_init(&platform)==VEP_ARGUMENT);
    catalog[2047] = saved;
    catalog[2047].caller = 0; catalog[2047].caller2 = 0x800;
    assert(veposed_init(&platform)==VEP_ARGUMENT);
    catalog[2047] = saved;
    catalog[2047].name[strlen((const char *)catalog[2047].name)+1] = 'x';
    assert(veposed_init(&platform)==VEP_ARGUMENT);
    catalog[2047] = saved;
    assert(veposed_init(&platform)==0);
    const vep_api *api=veposed_get_api();
    static vep_hook_point_info info[2048]; uint32_t count,owner,other,handle,second,third;
    assert(api->list_hook_points(info,2048,&count)==0 && count==2048);
    assert(!strcmp((char *)info[0].name,"settings.about.os_version"));
    assert(api->register_module((const uint8_t *)"named",5,&owner)==0);
    assert(api->register_module((const uint8_t *)"other",5,&other)==0);
    assert(api->hook_text(owner,catalog[4].name,(const uint8_t *)"x",&handle)==VEP_ARGUMENT);
    vep_callbacks suppress={.before=skip};
    assert(api->attach_named(owner,catalog[4].name,&suppress,&handle)==0);
    void (*stale_text)(uintptr_t,uintptr_t)=(void *)text_slot;
    strcpy(rendered,"untouched"); render(subject,0x401); assert(!strcmp(rendered,"untouched"));
    render(subject,0x405); assert(!strcmp(rendered,"stock"));
    assert(api->detach(owner,handle)==0 && text_slot==(uintptr_t)set_text);
    text_site++;
    uint32_t shared[32];
    assert(api->hook_text(owner,points[0].name,(const uint8_t *)"SHARED",&shared[0])==0);
    stale_text(subject,(uintptr_t)"retired"); assert(!strcmp(rendered,"retired"));
    for (unsigned i=1; i<32; i++)
        assert(api->hook_text(owner,catalog[i+4].name,(const uint8_t *)"SHARED",&shared[i])==0);
    render(subject,0x700+4*35+1); assert(!strcmp(rendered,"SHARED"));
    render(subject,0x405); assert(!strcmp(rendered,"stock"));
    assert(api->hook_text(owner,points[3].name,(const uint8_t *)"EXTRA",&second)==VEP_CAPACITY);
    assert(api->detach(owner,shared[31])==0);
    assert(api->hook_text(owner,points[3].name,(const uint8_t *)"EXTRA",&second)==0);
    assert(api->detach(owner,second)==0);
    for (unsigned i=0; i<31; i++) assert(api->detach(owner,shared[i])==0);
    assert(text_slot==(uintptr_t)set_text);
    text_site++;
    assert(api->hook_text(owner,(const uint8_t *)"unknown",(const uint8_t *)"x",&handle)==VEP_NOT_FOUND);
    busy=1;
    assert(api->hook_text(owner,points[0].name,(const uint8_t *)"MOYE.114514",&handle)==VEP_BUSY);
    assert(text_slot==(uintptr_t)set_text); busy=0;
    vep_recovery_status status; assert(api->recovery_status(&status)==0 && status.mode==VEP_RECOVERY_CLEAN);
    char replacement[]="MOYE.114514";
    assert(api->hook_text(owner,points[0].name,(const uint8_t *)replacement,&handle)==0);
    os_active=0; render(subject,0x401); assert(!strcmp(rendered,"stock")); os_active=1;
    replacement[0]='X'; render(subject,0x401); assert(!strcmp(rendered,"MOYE.114514"));
    render(subject,0x405); assert(!strcmp(rendered,"stock"));
    render(subject+4,0x401); assert(!strcmp(rendered,"stock"));
    busy2=1;
    assert(api->hook_text(other,points[3].name,(const uint8_t *)"SYS.TEST",&second)==VEP_BUSY);
    busy2=0;
    assert(api->hook_text(other,points[3].name,(const uint8_t *)"SYS.TEST",&second)==0);
    render(subject2,0x501); assert(!strcmp(rendered,"stock"));
    active2=1;
    render(subject2,0x501); assert(!strcmp(rendered,"SYS.TEST"));
    active2=0;
    active=1;
    render(subject2,0x501); assert(!strcmp(rendered,"SYS.TEST"));
    render(subject2,0x601); assert(!strcmp(rendered,"SYS.TEST"));
    render(subject2,0x401); assert(!strcmp(rendered,"stock"));
    active=0; render(subject2,0x501); assert(!strcmp(rendered,"stock"));
    active=1;
    render(subject,0x501); assert(!strcmp(rendered,"stock"));
    render(subject,0x401); assert(!strcmp(rendered,"MOYE.114514"));
    assert(api->set_enabled(other,0)==0); render(subject2,0x501); assert(!strcmp(rendered,"stock"));
    busy2=1;
    assert(api->detach(other,second)==VEP_BUSY);
    assert(api->unregister_module(other)==VEP_BUSY);
    assert(text_slot!=(uintptr_t)set_text);
    busy2=0;
    assert(api->detach(other,second)==0);
    active=0;
    assert(api->set_enabled(other,1)==0);
    assert(api->set_enabled(owner,0)==0); render(subject,0x401); assert(!strcmp(rendered,"stock"));
    assert(api->set_enabled(owner,1)==0); render(subject,0x401); assert(!strcmp(rendered,"MOYE.114514"));
    vep_callbacks global={.before=lower};
    entered=0;
    assert(api->attach_named(other,catalog[2046].name,&global,&second)==0);
    render(subject,0x401); assert(entered==1 && !strcmp(rendered,"MOYE.114514"));
    render(subject,0x405); assert(entered==2 && !strcmp(rendered,"stock"));
    render(subject+4,0x401); assert(entered==3 && !strcmp(rendered,"stock"));
    assert(api->detach(other,second)==0);
    entered=0;
    assert(api->detach(owner,handle)==0 && text_slot==(uintptr_t)set_text);
    text_site++;
    assert(api->hook_text(owner,catalog[2047].name,(const uint8_t *)"LARGE.TABLE",&handle)==0);
    render(subject,0x700+4*2047+1); assert(!strcmp(rendered,"LARGE.TABLE"));
    assert(api->detach(owner,handle)==0 && text_slot==(uintptr_t)set_text);
    vep_callbacks high={skip,double_result,0,10}, low={lower,lower,0,0};
    assert(api->attach_named(owner,points[1].name,&high,&handle)==0);
    assert(api->attach_named(other,points[1].name,&low,&second)==0);
    uintptr_t (*call2)(uintptr_t,uintptr_t)=(void *)pair_slot;
    assert(call2(2,3)==154 && originals==0 && entered==0);
    assert(api->set_enabled(owner,0)==0);
    assert(call2(2,3)==5 && originals==1 && entered==2);
    assert(api->detach(other,second)==0);
    assert(api->detach(owner,handle)==0 && pair_slot==(uintptr_t)pair);
    assert(api->set_enabled(owner,1)==0);
    vep_callbacks change={edit,double_result,0,0};
    assert(api->attach_named(owner,points[2].name,&change,&handle)==0);
    uintptr_t (*call4)(uintptr_t,uintptr_t,uintptr_t,uintptr_t)=(void *)sum_slot;
    assert(call4(1,2,3,4)==40);
    assert(api->detach(owner,handle)==0);
    change.before=replace_with_original; change.after=0;
    assert(api->attach_named(owner,points[2].name,&change,&handle)==0);
    call4=(void *)sum_slot;
    assert(call4(1,2,3,4)==60);
    assert(api->detach(owner,handle)==0);
    assert(api->attach_named(owner,points[1].name,&high,&second)==0);
    change.before=call_other;
    assert(api->attach_named(owner,points[2].name,&change,&handle)==0);
    call4=(void *)sum_slot;
    assert(call4(1,2,3,4)==5);
    assert(api->hook_text(owner,points[0].name,(const uint8_t *)"PENDING",&third)==0);
    busy=1;
    assert(api->enter_safe_mode()==VEP_BUSY);
    assert(sum_slot==(uintptr_t)sum && pair_slot==(uintptr_t)pair);
    assert(call4(1,2,3,4)==10);
    assert(text_slot!=(uintptr_t)set_text);
    void (*call_text)(uintptr_t,uintptr_t)=(void *)text_slot;
    call_text(subject,(uintptr_t)"stock"); assert(!strcmp(rendered,"stock"));
    assert(api->recovery_status(&status)==0 && status.active_sites==1 && status.rollback_error==VEP_BUSY);
    assert(api->recovery_reset()==VEP_BUSY);
    assert(api->detach(owner,third)==VEP_BUSY);
    busy=0;
    assert(api->enter_safe_mode()==0 && text_slot==(uintptr_t)set_text);
    assert(api->unregister_module(owner)==0 && api->unregister_module(other)==0);
    assert(api->recovery_reset()==0);
    puts("named API: exact scope, owned text, switches, skip, return edits, priority, original/other function calls and rollback PASS");
}
