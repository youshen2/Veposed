-- Standalone installation into an already running Veposed ABI 4 runtime.
local root = assert(SCRIPT_PATH, "SCRIPT_PATH is required")
if root:sub(-1) ~= "/" then root = root .. "/" end
local function read(path, count)
    local f = io.open(path, "rb")
    if not f then return nil end
    local value = f:read(count or "*a"); f:close(); return value
end
local state = read("/dev/veposed", 40)
if not state or #state ~= 40 or state:byte(5) ~= 4 or state:byte(17) == 2 then
    print("请先安装 Veposed，或在管理器中处理安全模式")
    return false
end
local path = root .. "os_version.elf"
local header = read(path, 20)
if not header or header:sub(1, 7) ~= "\127ELF\1\1\1" then
    print("缺少 os_version.elf")
    return false
end
os.remove("/data/veposed-moye-status.txt")
local quoted = "'" .. path:gsub("'", "'\\''") .. "'"
local loaded = os.execute("insmod " .. quoted .. " veposed_os_version")
local status = read("/data/veposed-moye-status.txt")
if (loaded == true or loaded == 0) and status and status:find("status=+00", 1, true) then
    print("OS 版本替换模块已安装，默认停用。请在 Veposed 管理器中启用。")
    return true
end
print("模块安装失败，请保留恢复入口并重启后处理：" .. tostring(status))
return false
