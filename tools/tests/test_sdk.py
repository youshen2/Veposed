from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sdk"))
sys.path.insert(0, str(ROOT / "tools"))
from veposed import Module, arg, result
from face import pack, unpack

POINTS = {
    "text": {"contract": "void2"},
    "pair": {"contract": "word2"},
    "sum": {"contract": "word4"},
}


class SDKTests(unittest.TestCase):
    def test_generated_callbacks_execute_conditions_skip_and_rewrite(self):
        module = Module("org.test.rules", "Rules")
        module.before("pair", priority=80).when(arg(0) == 0).return_(77)
        module.before("sum").set_arg(1, arg(1) + 10)
        module.after("sum").set_result(result() * 2)
        module.replace("pair").call_original().set_result(result() + 1)
        module.replace("sum").call("pair", arg(0), arg(1)).set_result(result() * 2)
        source = module.emit_c(POINTS)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "rules.c"
            target.write_text(
                """#include "veposed.h"
#define VEPOSED_MODULE_H
static vep_callbacks callbacks[5];
static unsigned used;
static int32_t capture(uint32_t owner, const uint8_t *name, const vep_callbacks *cb, uint32_t *handle) {
 (void)owner; (void)name; *handle=used+1; callbacks[used++]=*cb; return 0;
}
static uintptr_t original(vep_call *call) { call->return_early=1; call->result=call->args[0]+call->args[1]; return call->result; }
static int32_t named(const uint8_t *name, const uintptr_t *args, uintptr_t *result) { (void)name; *result=args[0]+args[1]; return 0; }
static const vep_api api={.attach_named=capture,.call_original=original,.call_named=named};
static const vep_api *vep=&api;
static uint32_t vep_owner=1;
"""
                + source
                + """
#include <assert.h>
int main(void) {
 assert(vep_module_setup()==0 && used==5);
 vep_call c={.args={1,2,3,4}};
 callbacks[0].before(&c,0); assert(!c.return_early);
 c.args[0]=0; callbacks[0].before(&c,0); assert(c.return_early && c.result==77);
 callbacks[1].before(&c,0); assert(c.args[1]==12);
 c.result=20; callbacks[2].after(&c,0); assert(c.result==40);
 c.args[0]=2; c.args[1]=3; c.return_early=0;
 callbacks[3].before(&c,0); assert(c.return_early && c.result==6);
 c.return_early=0; callbacks[4].before(&c,0); assert(c.return_early && c.result==10);
 return 0;
}
"""
            )
            binary = Path(folder) / "rules"
            subprocess.run(
                [
                    "cc",
                    "-std=c11",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-I",
                    str(ROOT / "include"),
                    str(target),
                    "-o",
                    str(binary),
                ],
                check=True,
            )
            subprocess.run([str(binary)], check=True)

    def test_invalid_signature_and_unknown_point_are_build_errors(self):
        for configure in (
            lambda m: m.before("text").return_(1),
            lambda m: m.before("pair").set_arg(3, 1),
            lambda m: m.replace_text("pair", "x"),
            lambda m: m.before("missing").skip(),
        ):
            module = Module("org.test.bad", "Bad")
            configure(module)
            with self.assertRaises(ValueError):
                module.emit_c(POINTS)

    def test_face_roundtrip_and_truncation(self):
        files = {"lua/main.lua": b'print("ok")'}
        for i in range(4):
            files[f"lua/test{i}.bin"] = bytes(i + 5)
        packed = pack(files, bytes(336 * 480 * 4), "Veposed", "190067000101")
        parsed = unpack(packed)
        self.assertEqual(parsed["files"], files)
        self.assertEqual((parsed["width"], parsed["height"]), (336, 480))
        self.assertEqual(packed[:4], bytes.fromhex("5aa53412"))
        with self.assertRaises(ValueError):
            unpack(packed[:-1])
