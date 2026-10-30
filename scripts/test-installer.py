#!/usr/bin/env python3
"""Exercise Lua install/recovery sequencing with the real loader/bootstrap."""

import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--lua", default="lua")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
harness = r"""
local root, scenario = arg[1], arg[2]
local factory = dofile(root .. "/installer/loader.lua")
local original_dofile = dofile
local files, calls = {}, {}
local device, mode, reason, failures, last, rollback, sites = false, 0, 0, 0, 0, 0, 0
local blob = "\127ELF\1\1\1" .. string.rep("\0",9) .. "\1\0\40\0"
files["/resources/runtime"] = blob
local resources = {
 {source="runtime",destination="/data/veposed/veposed.elf",size=#blob,elf=true}
}
local bundle = {abi=4,firmware="3.101.043",resources=resources}
dofile = function(path)
 if path == "/resources/bundle.lua" then return bundle end
 if path == "/resources/bootstrap.lua" then return original_dofile(root .. "/installer/bootstrap.lua") end
 error(path)
end
io.open = function(path, access)
 if scenario == "read-error" and path == "/dev/veposed" then return nil,"denied",13 end
 if path == "/dev/veposed" and not device then return nil,"missing",2 end
 if access == "rb" and path ~= "/dev/veposed" and not files[path] then return nil,"missing",2 end
 local pending = ""
 return {
  read=function(_, size)
   if path == "/dev/veposed" then return string.pack("<I4I4I4I4I4I4I4I4I4I4",0x56504531,4,40,1,mode,reason,failures,sites,last % 0x100000000,rollback % 0x100000000) end
   return type(size)=="number" and files[path]:sub(1,size) or files[path]
  end,
  write=function(self, data)
   if path == "/dev/veposed" then
    local cmd = data:match("^%s*(.-)%s*$"); calls[#calls+1]=cmd
    if scenario == "manager-fail" and cmd == "manager-register" then return nil end
    if cmd == "disable" then
     if scenario=="rollback-fail" then return nil,"rollback failed" end
     mode=2; reason=3; last=0
    end
   else pending=pending .. data end
   return self
  end,
  flush=function() if scenario=="io-no-return" then return end; return true end,
  close=function()
   if access=="wb" then files[path]=pending end
   if scenario=="close-error" then return nil,"I/O error",5 end
   if scenario=="io-no-return" then return end
   return true
  end
 }
end
os.remove=function(path) files[path]=nil; return true end
os.execute=function(command)
 if command:match("^getprop") then files["/data/veposed-version.tmp"]="3.101.043\n"
 elseif command:match("^mkdir") then return true
 elseif command:match("^insmod") then
  calls[#calls+1]="runtime"; device=true; mode=files["/data/veposed.disable"] and 2 or 0
  if mode==2 then reason=3 end
  if scenario=="safe-on-load" then mode=2; reason=4; last=-12 end
 else error(command) end
 return true
end
local controller=factory("/resources/")
local failed=false
local steps
if scenario=="existing-safe" or scenario=="recovery-existing" or scenario=="rollback-fail" then
 device=true; mode=2; reason=1; failures=2; files["/data/veposed-load.pending"]="pending"
end
if scenario=="rollback-fail" then sites=1; rollback=-7 end
if scenario=="recovery" or scenario=="recovery-existing" or scenario=="rollback-fail" then
 files["/data/veposed-load.pending"]="pending"; steps=controller.recovery_steps()
else steps=controller.install_steps() end
for _,step in ipairs(steps) do local ok=step[2](); if not ok then failed=true; break end end
if scenario=="ok" or scenario=="io-no-return" then
 assert(not failed); assert(#steps==4); assert(table.concat(calls,",")=="runtime,manager-register,manager-launcher")
 assert(controller.install_result():find("Install modules from their own faces",1,true))
 assert(controller.install_steps()[1][2]()==false)
elseif scenario=="close-error" then assert(failed and #calls==0)
elseif scenario=="manager-fail" then assert(failed and calls[#calls]=="manager-register")
elseif scenario=="read-error" then assert(failed and #calls==0)
elseif scenario=="recovery" then
 assert(not failed and mode==2); assert(table.concat(calls,",")=="runtime,manager-register,manager-launcher")
 assert(files["/data/veposed-load.pending"]=="pending" and files["/data/veposed.disable"])
elseif scenario=="safe-on-load" then
 assert(not failed and mode==2)
 assert(table.concat(calls,",")=="runtime,manager-register,manager-launcher")
 assert(controller.install_result():find("reason=4 STORAGE ERROR",1,true))
 assert(controller.install_result():find("last=-12 rollback=0",1,true))
 assert(files["/data/veposed-load.pending"]=="pending\n")
elseif scenario=="existing-safe" or scenario=="recovery-existing" then
 assert(not failed and mode==2 and reason==1)
 assert(table.concat(calls,",")=="manager-register,manager-launcher")
 local result=scenario=="existing-safe" and controller.install_result() or controller.recovery_result()
 assert(result:find("reason=1 UNCLOSED SESSION",1,true))
 assert(result:find("failures=2",1,true))
 assert(files["/data/veposed-load.pending"]=="pending")
elseif scenario=="rollback-fail" then
 assert(failed and table.concat(calls,",")=="disable")
 assert(reason==1 and sites==1 and rollback==-7)
end
print(scenario .. ": PASS")
"""
with tempfile.TemporaryDirectory() as directory:
    script = Path(directory) / "harness.lua"
    script.write_text(harness)
    for scenario in (
        "ok",
        "io-no-return",
        "close-error",
        "manager-fail",
        "read-error",
        "recovery",
        "safe-on-load",
        "existing-safe",
        "recovery-existing",
        "rollback-fail",
    ):
        subprocess.run([args.lua, str(script), str(root), scenario], check=True, timeout=10)

module_harness = r"""
local root,scenario=arg[1],arg[2]
SCRIPT_PATH="/resources/"
local real_dofile=dofile
local run_callback,status,commands=nil,nil,{}
local blob="\127ELF\1\1\1" .. string.rep("\0",9) .. "\1\0\40\0"
local files={["/resources/module.bin"]=blob}
local config={name="Test",size=#blob,destination="/data/veposed/test.elf",loader_name="vep_test",status="/data/veposed/test.status"}
dofile=function(path) if path=="/resources/module_config.lua" then return config end; error(path) end
local function object()
 return {clear_flag=function() end,add_flag=function() end,onClicked=function(_,cb) run_callback=cb end}
end
package.preload.lvgl=function() return {
 HOR_RES=function() return 336 end,VER_RES=function() return 480 end,OPA=function(v) return v end,
 FLAG={SCROLLABLE=1,CLICKABLE=2},ALIGN={CENTER=1},BUILTIN_FONT={MONTSERRAT_14="ascii14"},Object=object,
 Label=function(_,options)
  if options.width==294 then status=options.text; return {set=function(_,values) status=values.text end} end
  return {}
 end,
 Timer=function(options)
  local timer={pause=function() end,resume=function() end}
  timer.ready=function() options.cb(timer) end
  return timer
 end,
} end
io.open=function(path,access)
 if path=="/dev/veposed" and scenario=="missing" then return nil end
 if access=="rb" and path~="/dev/veposed" and not files[path] then return nil end
 local pending=""
 return {
 read=function(_,n)
  if path=="/dev/veposed" then return string.pack("<I4I4I4I4I4I4I4I4I4I4",0x56504531,4,40,1,scenario=="safe" and 2 or 0,0,0,0,0,0) end
  return type(n)=="number" and files[path]:sub(1,n) or files[path]
 end,
 write=function(self,v) if path=="/dev/veposed" then commands[#commands+1]=v else pending=pending .. v end; return self end,
 flush=function() if scenario=="io-no-return" then return end; return true end,
 close=function() if access=="wb" then files[path]=pending end; if scenario=="io-no-return" then return end; return true end,
 }
end
os.remove=function(path) files[path]=nil end
os.execute=function(command)
 commands[#commands+1]=command
 if scenario=="fail" then return nil end
 files[config.status]="status=+00"; return true
end
real_dofile(root .. "/installer/module.lua")
assert(run_callback)
run_callback()
if scenario=="ok" or scenario=="io-no-return" then assert(status:find("DONE",1,true) and #commands==1 and files[config.destination]==blob)
elseif scenario=="fail" then assert(status:find("E_MODULE_INIT",1,true) and commands[#commands]=="disable\n")
else assert(#commands==0 and not files[config.destination]) end
local count=#commands; run_callback(); assert(#commands==count)
print("module-face " .. scenario .. ": PASS")
"""
with tempfile.TemporaryDirectory() as directory:
    script = Path(directory) / "module.lua"
    script.write_text(module_harness)
    for scenario in ("ok", "io-no-return", "fail", "missing", "safe"):
        subprocess.run([args.lua, str(script), str(root), scenario], check=True, timeout=10)

# Open the actual embedded entry selected by the element descriptor, not a
# hard-coded main.lua. Opening a watchface must render without executing native
# install commands; broken script resources must produce visible diagnostics.
import sys

sys.path.insert(0, str(root / "tools"))
from face import pack, unpack

entry_harness = r"""
local entry,scenario,kind=arg[1],arg[2],arg[3]
SCRIPT_PATH=entry:match("^(.*[/])")
if scenario=="missing-path" then SCRIPT_PATH=nil end
local labels,buttons,roots,callbacks={},0,0,{}
local timer_count, install_disabled = 0, false
local displayed = {}
local function object(parent,options)
 if not parent then roots=roots+1 end
 local object={}
 function object:clear_flag(flag)
  if flag==2 and self.install_button then install_disabled=true end
 end
 function object:add_flag() end
 function object:onClicked(cb)
  buttons=buttons+1; callbacks[buttons]=cb
  self.install_button=buttons==1
 end
 return object
end
package.preload.lvgl=function() return {
 HOR_RES=function() return 336 end,VER_RES=function() return 480 end,OPA=function(v) return v end,
 FLAG={SCROLLABLE=1,CLICKABLE=2},ALIGN={CENTER=1},BUILTIN_FONT={MONTSERRAT_14="ascii14"},Object=object,
 Label=function(_,options)
  assert(not options.text:find("[^\n -~]"),"non-ASCII UI text")
  assert(options.text_font=="ascii14","missing built-in font")
  local item={text=options.text}; labels[#labels+1]=item
  return {set=function(_,v) assert(not v.text:find("[^\n -~]"),"non-ASCII status"); item.text=v.text; displayed[#displayed+1]=v.text end}
 end,
 Timer=function(options)
  if scenario~="install-error" and scenario~="install-success" and scenario~="install-thrown" and scenario~="recovery-success" then
   error("opening must not start native installation")
  end
  timer_count=timer_count+1
  local paused=false
  local timer={pause=function() paused=true end,resume=function() paused=false end}
  timer.ready=function()
   for _=1,3 do if paused then break end; options.cb(timer) end
  end
  return timer
 end,
} end
os.execute=function() error("opening must not run shell commands") end
local ok,err=pcall(dofile,entry)
assert(ok,err); assert(roots==1,"no visible root")
if scenario=="install-error" or scenario=="install-success" or scenario=="install-thrown" then
 callbacks[1]()
 local expected=scenario=="install-success" and "DONE" or "FAIL S1"
 local found, first=nil,nil
 for _,label in ipairs(labels) do
  if label.text:find(expected,1,true) then found=label; first=label.text end
 end
 assert(found,"missing readable first result")
 assert(install_disabled,"install button stayed clickable")
 callbacks[1](); callbacks[1]()
 assert(found.text==first,"repeated click hid the first result")
 assert(timer_count==1,"repeated click started another installation")
elseif scenario=="recovery-success" then
 callbacks[2]()
 local history=table.concat(displayed,"\n")
 assert(history:find("RECOVERY STEP 1/1",1,true))
 assert(history:find("SAFE MODE",1,true))
 assert(not history:find("INSTALL STEP",1,true))
elseif scenario=="ok" then
 assert(buttons==(kind=="suite" and 2 or 1),"missing install controls")
else
 local visible_error=false
 for _,label in ipairs(labels) do if label.text:find("E_INIT",1,true) then visible_error=true end end
 assert(visible_error,"resource error not shown on screen")
 assert(buttons==0)
end
print("watchface entry " .. kind .. " " .. scenario .. ": PASS")
"""
with tempfile.TemporaryDirectory() as directory:
    base = Path(directory)
    harness = base / "entry-test.lua"
    harness.write_text(entry_harness)
    for kind in ("suite", "module"):
        resources = {
            "lua/main.lua": (
                root / "installer" / ("main.lua" if kind == "suite" else "module.lua")
            ).read_bytes(),
            "lua/zz_native.bin": b"\x7fELF",
        }
        if kind == "suite":
            resources["lua/loader.lua"] = (root / "installer/loader.lua").read_bytes()
            resources["lua/bundle.lua"] = (
                b'return {abi=4,firmware="3.101.043",resources={},modules={}}'
            )
        else:
            resources["lua/module_config.lua"] = (
                b'return {name="Test",size=4,destination="/data/test.elf",loader_name="test",status="/data/test.status"}'
            )
        blob = pack(resources, bytes(4), "Veposed", "190067000101", 1, 1)
        contents = unpack(blob)
        scenarios = (
            (
                "ok",
                "missing-script",
                "missing-path",
                "install-error",
                "install-success",
                "install-thrown",
                "recovery-success",
            )
            if kind == "suite"
            else ("ok", "missing-script", "missing-path")
        )
        for scenario in scenarios:
            destination = base / kind / scenario
            for name, data in contents["files"].items():
                file = destination / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(data)
            if scenario in ("install-error", "install-success", "install-thrown"):
                body = {
                    "install-error": 'return false,"E_STAT: errno=13"',
                    "install-success": "return true",
                    "install-thrown": 'error("E_CALLBACK: interrupted")',
                }[scenario]
                (destination / "lua/loader.lua").write_text(
                    'return function() return {install_result=function() return "DONE" end,install_steps=function() return {{"Check files",function() '
                    + body
                    + " end}} end} end"
                )
            if scenario == "recovery-success":
                (destination / "lua/loader.lua").write_text(
                    'return function() return {recovery_result=function() return "SAFE MODE: reason=1" end,recovery_steps=function() return {{"Keep modules disabled",function() return true end}} end} end'
                )
            if scenario == "missing-script":
                (
                    destination / "lua" / ("loader.lua" if kind == "suite" else "module_config.lua")
                ).unlink()
            subprocess.run(
                [args.lua, str(harness), str(destination / contents["entrypoint"]), scenario, kind],
                check=True,
                timeout=10,
            )
