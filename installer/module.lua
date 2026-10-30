-- Standalone module installation face; requires the matching resident runtime.
local lvgl = require("lvgl")
local base, config
local text_font = lvgl.BUILTIN_FONT.MONTSERRAT_14
local root = lvgl.Object(nil, {w=lvgl.HOR_RES(),h=lvgl.VER_RES(),bg_color=0x10141C,bg_opa=lvgl.OPA(100),border_width=0})
root:clear_flag(lvgl.FLAG.SCROLLABLE)
local loaded, result = pcall(function()
    base = assert(SCRIPT_PATH, "SCRIPT_PATH is required")
    if base:sub(-1) ~= "/" then base = base .. "/" end
    return dofile(base .. "module_config.lua")
end)
if not loaded then
    lvgl.Label(root, {text_font=text_font,text="E_INIT: script load failed\n" .. tostring(result),text_color=0xFFB0A8,width=294,align=lvgl.ALIGN.CENTER})
    print("[Veposed] " .. tostring(result))
    return
end
config = result
local title = lvgl.Label(root, {text_font=text_font,text=config.name,text_color=0xFFFFFF,align={type=lvgl.ALIGN.CENTER,x_ofs=0,y_ofs=-130}})
local status = lvgl.Label(root, {text_font=text_font,text="Requires Veposed ABI 4\nEnable in Manager after install",text_color=0xCFD4DF,width=294,height=135,align={type=lvgl.ALIGN.CENTER,x_ofs=0,y_ofs=110}})
local attempted, timer = false, nil
local function succeeded(value, message)
    return value ~= false and (value ~= nil or message == nil)
end
local function read(path, size)
    local file = io.open(path,"rb")
    if not file then return nil end
    local value=file:read(size or "*a"); file:close(); return value
end
local function word(bytes, at)
    local a,b,c,d=bytes:byte(at,at+3); return a+b*256+c*65536+d*16777216
end
local function install()
    local state=read("/dev/veposed",40)
    if not state or #state~=40 or word(state,1)~=0x56504531 or word(state,5)~=4 or word(state,9)~=40 then
        return false,"E_SERVICE: install matching Veposed first"
    end
    if word(state,17)==2 then return false,"E_SAFE_MODE: recover in Manager" end
    local bytes=read(base .. "module.bin")
    if not bytes or #bytes~=config.size or bytes:sub(1,7)~="\127ELF\1\1\1" then
        return false,"E_RESOURCE: invalid module.bin"
    end
    local file=io.open(config.destination,"wb")
    if not file then return false,"E_OPEN_WRITE: module file" end
    local ok,write_error=file:write(bytes)
    local flushed,flush_error=file:flush()
    local closed,close_error=file:close()
    if not ok then return false,"E_WRITE: module file" end
    if not succeeded(flushed,flush_error) then return false,"E_FLUSH: module file" end
    if not succeeded(closed,close_error) then return false,"E_CLOSE: module file" end
    os.remove(config.status)
    local loaded=os.execute("insmod " .. config.destination .. " " .. config.loader_name)
    local result=read(config.status)
    if (loaded==true or loaded==0) and result and result:find("status=+00",1,true) then
        return true,"DONE (module disabled)\nEnable it in Veposed Manager"
    end
    local device=io.open("/dev/veposed","r+b")
    if device then device:write("disable\n"); device:close() end
    return false,"E_MODULE_INIT\nUse Veposed SAFE RECOVERY"
end
local button=lvgl.Object(root,{w=278,h=58,bg_color=0x6557D9,bg_opa=lvgl.OPA(100),radius=16,align=lvgl.ALIGN.CENTER})
button:clear_flag(lvgl.FLAG.SCROLLABLE); button:add_flag(lvgl.FLAG.CLICKABLE)
lvgl.Label(button,{text_font=text_font,text="INSTALL MODULE",text_color=0xFFFFFF,align=lvgl.ALIGN.CENTER})
button:onClicked(function()
    if attempted then return end
    attempted=true; status:set{text="Installing..."}
    timer=lvgl.Timer{period=800,repeat_count=-1,paused=true,cb=function(t)
        t:pause()
        local called,ok,message=pcall(install)
        status:set{text=tostring(called and message or ok):gsub("[^\n -~]", "?"),text_color=called and ok and 0xCFD4DF or 0xFFB0A8}
        timer=nil
    end}
    if timer then timer:resume(); timer:ready() else status:set{text="E_TIMER: cannot create task"} end
end)
