#include "veposed.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static unsigned seen;
static void v0(void) { seen = 100; }
static void v1(uintptr_t a) { seen = (unsigned)a; }
static void v2(uintptr_t a, uintptr_t b) { seen = (unsigned)(a+b); }
static void v3(uintptr_t a, uintptr_t b, uintptr_t c) { seen = (unsigned)(a+b+c); }
static void v4(uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d) { seen = (unsigned)(a+b+c+d); }
static uintptr_t w0(void) { return 7; }
static uintptr_t w1(uintptr_t a) { return a; }
static uintptr_t w2(uintptr_t a, uintptr_t b) { return a+b; }
static uintptr_t w3(uintptr_t a, uintptr_t b, uintptr_t c) { return a+b+c; }
static uintptr_t w4(uintptr_t a, uintptr_t b, uintptr_t c, uintptr_t d) { return a+b+c+d; }
static int32_t read_guard(uint8_t *record) { (void)record; return 1; }
static int32_t write_guard(const uint8_t *record) { (void)record; return 0; }
static const vep_api *api;
static int use_named;
static const uint8_t *current_name;

static void before(vep_call *call, void *data) {
    (void)data;
    call->args[0] += 10;
    if (use_named) {
        uintptr_t value;
        assert(api->call_named(current_name,call->args,&value)==VEP_OK);
        call->result=value;
        call->return_early=1;
    } else {
        (void)api->call_original(call);
    }
}
static void after(vep_call *call, void *data) {
    if (*(const int *)data) call->result += 10;
}
extern uintptr_t veposed_named_dispatch(uintptr_t,uintptr_t,uintptr_t,uintptr_t,uintptr_t,size_t);
int main(void) {
    const uintptr_t originals[] = {(uintptr_t)v0,(uintptr_t)w0,(uintptr_t)v1,(uintptr_t)w1,
        (uintptr_t)v2,(uintptr_t)w2,(uintptr_t)v3,(uintptr_t)w3,(uintptr_t)v4,(uintptr_t)w4};
    const uint32_t kinds[] = {VEP_VOID0,VEP_WORD0,VEP_VOID1,VEP_WORD1,VEP_VOID2,VEP_WORD2,
        VEP_VOID3,VEP_WORD3,VEP_VOID4,VEP_WORD4};
    const unsigned expected[] = {100,7,11,11,13,13,16,16,20,20};
    uintptr_t slots[10]; vep_named_point points[10] = {0};
    for (unsigned i=0; i<10; ++i) {
        slots[i]=originals[i];
        snprintf((char *)points[i].name,sizeof(points[i].name),"test.contract.%u",i);
        points[i].contract=kinds[i];
        points[i].target=(vep_target){.kind=VEP_POINTER,.address=(uintptr_t)&slots[i],.expected_pointer=slots[i]};
    }
    vep_platform platform={VEP_ABI_VERSION,sizeof(platform),0,read_guard,write_guard,points,10,sizeof(vep_named_point)};
    assert(veposed_init(&platform)==VEP_OK);
    api=veposed_get_api(); uint32_t owner, handle;
    assert(api->register_module((const uint8_t *)"contracts",9,&owner)==VEP_OK);
    for (unsigned i=0; i<10; ++i) {
        int has_result=(int)(i%2);
        vep_callbacks callbacks={.before=before,.after=after,.user_data=&has_result};
        current_name=points[i].name;
        assert(api->attach_named(owner,current_name,&callbacks,&handle)==VEP_OK);
        for (use_named=0; use_named<2; ++use_named) {
            seen=0;
            uintptr_t result=veposed_named_dispatch(1,2,3,4,0,i);
            if (has_result) assert(result==expected[i]+10 && seen==0);
            else assert(result==0 && seen==expected[i]);
        }
        assert(api->detach(owner,handle)==VEP_OK && slots[i]==originals[i]);
    }
    assert(api->unregister_module(owner)==VEP_OK);
    puts("named contracts: 0..4 arguments, void/word returns, original and named calls PASS");
}
