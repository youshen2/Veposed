from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sdk"))
sys.path.insert(0, str(ROOT / "tools"))
from veposed import Module, arg, field, result
from face import pack, unpack

POINTS = {
    "text": {"contract": "void2", "text_arg1": True},
    "image": {"contract": "void2"},
    "pair": {"contract": "word2"},
    "sum": {"contract": "word4"},
}


class SDKTests(unittest.TestCase):
    def test_profile_fields_filter_navigation_actions_and_null_is_ignored(self):
        points = {"navigate": {"contract": "word1", "fields": {
            "page_id": {"arg": 0, "offset": 4, "width": 2, "size": 44},
            "app_id": {"arg": 0, "offset": 6, "width": 2, "size": 44},
            "source": {"arg": 0, "offset": 8, "width": 1, "size": 44},
        }}}
        module = Module("org.test.fields", "Fields")
        module.before("navigate").when(
            (field("page_id") == 0x1234) & (field("app_id") == 0xabcd) & (field("source") == 9)
        ).return_(77)
        source = module.emit_c(points)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "fields.c"
            target.write_text('''#include "veposed.h"
#define VEPOSED_MODULE_H
static vep_callbacks cb;
static int32_t capture(uint32_t owner, const uint8_t *name, const vep_callbacks *value, uint32_t *handle) {
 (void)owner; (void)name; cb=*value; *handle=1; return 0;
}
static const vep_api api={.attach_named=capture};
static const vep_api *vep=&api;
static uint32_t vep_owner=1;
''' + source + '''
#include <assert.h>
int main(void) {
 uint8_t action[44]={0}; action[4]=0x34; action[5]=0x12; action[6]=0xcd; action[7]=0xab; action[8]=9;
 assert(vep_module_setup()==0);
 vep_call c={.args={(uintptr_t)action}};
 cb.before(&c,0); assert(c.return_early && c.result==77);
 c.return_early=0; action[6]=0; cb.before(&c,0); assert(!c.return_early);
 c.args[0]=0; cb.before(&c,0); assert(!c.return_early);
 return 0;
}
''')
            binary = Path(folder) / "fields"
            subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I",
                            str(ROOT / "include"), str(target), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
        bad = Module("org.test.badfield", "Bad")
        bad.before("navigate").when(field("unknown") == 1).return_(0)
        with self.assertRaisesRegex(ValueError, "unknown field"):
            bad.emit_c(points)
        bad = Module("org.test.afterfield", "Bad")
        bad.after("navigate").when(field("page_id") == 1).set_result(0)
        with self.assertRaisesRegex(ValueError, "only before"):
            bad.emit_c(points)
        bad = Module("org.test.changedarg", "Bad")
        bad.before("navigate").when(field("page_id") == 1).set_arg(0, 0)
        with self.assertRaisesRegex(ValueError, "cannot replace an argument"):
            bad.emit_c(points)
        bad = Module("org.test.aftercall", "Bad")
        bad.before("navigate").call_original().set_result(field("page_id"))
        with self.assertRaisesRegex(ValueError, "before calling"):
            bad.emit_c(points)

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
            lambda m: m.replace_text("image", "x"),
            lambda m: m.before("missing").skip(),
        ):
            module = Module("org.test.bad", "Bad")
            configure(module)
            with self.assertRaises(ValueError):
                module.emit_c(POINTS)
        module = Module("org.test.image", "Image")
        module.before("image").set_arg(1, "/data/test.bin")
        self.assertIn("call->args[1]", module.emit_c(POINTS))

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

    def test_all_word_and_void_contracts_validate_argument_counts(self):
        for kind in ("void", "word"):
            for count in range(5):
                points = {"point": {"contract": f"{kind}{count}"}}
                module = Module("org.test.contract", "Contract")
                module.replace("point").call("point", *range(count))
                module.emit_c(points)
                invalid = Module("org.test.badarg", "Bad")
                invalid.replace("point").call("point", *range(count + 1))
                with self.assertRaisesRegex(ValueError, "wrong argument count"):
                    invalid.emit_c(points)
                if kind == "void":
                    invalid = Module("org.test.badreturn", "Bad")
                    invalid.before("point").return_(1)
                    with self.assertRaisesRegex(ValueError, "has no return value"):
                        invalid.emit_c(points)
