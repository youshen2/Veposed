-- Put this gate in the device's existing autostart path, before any native load.
-- The pending latch is intentionally retained after success. Reset is manual.
local disabled = "/data/veposed.disable"
local pending = "/data/veposed-load.pending"
local function succeeded(value, message)
    return value ~= false and (value ~= nil or message == nil)
end

local function absent(path)
    local file, message, code = io.open(path, "rb")
    if file then file:close(); return false end
    if code == 2 then return true end
    print("Veposed blocked: cannot inspect " .. path .. ": " .. tostring(message))
    return false
end

if not absent(disabled) or not absent(pending) then
    print("Veposed recovery: native autoload skipped; manual recovery required")
    return false
end

local file, message = io.open(pending, "wb")
if not file then print("Veposed blocked: " .. tostring(message)); return false end
local written, write_error = file:write("pending\n")
local flushed, flush_error = file:flush()
local closed, close_error = file:close()
if not written or not succeeded(flushed, flush_error) or not succeeded(closed, close_error) then
    print("Veposed blocked: could not persist load latch")
    return false
end

local checkpoint = io.open(pending, "rb")
local marker = checkpoint and checkpoint:read("*a")
if checkpoint then checkpoint:close() end
if marker ~= "pending\n" then
    print("Veposed blocked: load latch readback failed")
    return false
end

-- Any loader/constructor fault leaves the latch for the following boot.
local loaded = os.execute("insmod /data/veposed/veposed.elf veposed")
if loaded ~= 0 and loaded ~= true then
    print("Veposed load failed; latch retained")
    return false
end
return true
