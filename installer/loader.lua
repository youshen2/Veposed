-- Lua installation transport. Native management stays in the application list.
return function(resource_root)
    assert(type(resource_root) == "string", "SCRIPT_PATH is required")
    if resource_root:sub(-1) ~= "/" then resource_root = resource_root .. "/" end
    local bundle = dofile(resource_root .. "bundle.lua")
    local api = {}
    local recovering = false
    -- The target binding may return no values on successful flush/close.
    -- Standard Lua reports failures as nil plus an error, or explicit false.
    local function succeeded(value, message)
        return value ~= false and (value ~= nil or message == nil)
    end

    local function read(path, count)
        local file = io.open(path, "rb")
        if not file then return nil end
        local value = file:read(count or "*a")
        file:close()
        return value
    end
    local function exists(path)
        local file, message, code = io.open(path, "rb")
        if file then file:close(); return true end
        if code == 2 then return false end
        return nil, "E_STAT: errno=" .. tostring(code) .. "\n" .. path .. "\n" .. tostring(message)
    end
    local function run(command)
        local result = os.execute(command)
        return result == true or result == 0
    end
    local function write(path, bytes)
        local file, message, errno = io.open(path, "wb")
        if not file then return false, "E_OPEN_WRITE: errno=" .. tostring(errno) .. "\n" .. path .. "\n" .. tostring(message) end
        local ok, write_error = file:write(bytes)
        local flushed, flush_error = file:flush()
        local closed, close_error = file:close()
        if not ok then return false, "E_WRITE: " .. path .. "\n" .. tostring(write_error) end
        if not succeeded(flushed, flush_error) then return false, "E_FLUSH: " .. path .. "\n" .. tostring(flush_error) end
        if not succeeded(closed, close_error) then return false, "E_CLOSE: " .. path .. "\n" .. tostring(close_error) end
        return true
    end
    local function u32(bytes, offset)
        local a,b,c,d = bytes:byte(offset, offset + 3)
        return a + b * 256 + c * 65536 + d * 16777216
    end
    local function state()
        local bytes = read("/dev/veposed", 40)
        if not bytes or #bytes ~= 40 or u32(bytes, 1) ~= 0x56504531
            or u32(bytes, 5) ~= bundle.abi or u32(bytes, 9) ~= 40 then
            return nil, "E_SERVICE: missing or wrong ABI"
        end
        local function signed(value) return value >= 0x80000000 and value - 0x100000000 or value end
        return { mode = u32(bytes, 17), reason = u32(bytes, 21), failures = u32(bytes, 25),
                 sites = u32(bytes, 29), last = signed(u32(bytes, 33)), rollback = signed(u32(bytes, 37)) }
    end
    local function command(value)
        local file = io.open("/dev/veposed", "r+b")
        if not file then return false, "E_DEVICE_OPEN: /dev/veposed" end
        local result, write_error = file:write(value .. "\n")
        local closed, close_error = file:close()
        if not result then return false, "E_COMMAND_WRITE: " .. value .. "\n" .. tostring(write_error) end
        if not succeeded(closed, close_error) then return false, "E_COMMAND_CLOSE: " .. value .. "\n" .. tostring(close_error) end
        return true
    end
    local function verify_firmware()
        if not run("getprop ro.build.version > /data/veposed-version.tmp") then
            return false, "E_VERSION_READ: getprop failed"
        end
        local version = read("/data/veposed-version.tmp")
        os.remove("/data/veposed-version.tmp")
        if not version or version:match("^%s*(.-)%s*$") ~= bundle.firmware then
            return false, "E_FIRMWARE: need " .. bundle.firmware .. "\ngot: " .. tostring(version or "unreadable")
        end
        return true
    end
    local function copy_resource(entry)
        local bytes = read(resource_root .. entry.source)
        if not bytes or #bytes ~= entry.size then return false, "E_RESOURCE_SIZE: " .. entry.source end
        if entry.elf and (bytes:sub(1, 7) ~= "\127ELF\1\1\1" or bytes:byte(17) ~= 1 or bytes:byte(19) ~= 40) then
            return false, "E_ELF: " .. entry.source
        end
        return write(entry.destination, bytes)
    end
    local function stage()
        local ok, message = verify_firmware()
        if not ok then return false, message end
        run("mkdir /data/veposed")
        for _, entry in ipairs(bundle.resources) do
            ok, message = copy_resource(entry)
            if not ok then return false, message end
        end
        return true
    end
    local function restore_hooks()
        local runtime, message = state()
        if not runtime then return false, message end
        -- Avoid overwriting an existing fault reason with MANUAL isolation.
        if runtime.mode == 2 and runtime.sites == 0 and runtime.rollback == 0 then return true end
        local ok, error_message = command("disable")
        if not ok then return false, error_message end
        runtime, message = state()
        if not runtime then return false, message end
        if runtime.mode ~= 2 or runtime.sites ~= 0 or runtime.rollback ~= 0 then
            return false, "E_ROLLBACK: hooks=" .. runtime.sites .. " code=" .. runtime.rollback
        end
        return true
    end

    function api.install_steps()
        local steps = {
            { "Check firmware / copy files", function()
                local present, error_message = exists("/dev/veposed")
                if present == nil then return false, error_message end
                if present then
                    local runtime, message = state()
                    if not runtime then return false, message end
                    if runtime.mode ~= 2 then return false, "E_ALREADY_LOADED\nOpen Veposed Manager in app list" end
                    recovering = true
                    return true
                end
                for _, path in ipairs({"/data/veposed.disable", "/data/veposed-load.pending"}) do
                    local present, message = exists(path)
                    if present == nil then return false, message end
                    if present then return false, "E_ISOLATED: use SAFE RECOVERY" end
                end
                return stage()
            end },
            { "Load Veposed runtime", function()
                if not recovering then
                    local loaded = dofile(resource_root .. "bootstrap.lua")
                    if not loaded then return false, "E_BOOT_BLOCKED: use SAFE RECOVERY" end
                end
                local runtime, message = state()
                if not runtime then return false, message end
                -- A safe runtime still provides the recovery Manager. Finish
                -- that registration, while leaving every module unloaded.
                recovering = runtime.mode == 2
                return true
            end },
            { "Prepare native Manager", function()
                if recovering then
                    local ok, message = restore_hooks()
                    if not ok then return false, message end
                end
                return command("manager-register")
            end },
            { "Add Manager to app list", function() return command("manager-launcher") end },
        }
        return steps
    end

    function api.recovery_steps()
        return {
            { "Disable module injection", function() return write("/data/veposed.disable", "disabled\n") end },
            { "Connect recovery service", function()
                local present, error_message = exists("/dev/veposed")
                if present == nil then return false, error_message end
                if present then return true end
                local ok, message = stage()
                if not ok then return false, message end
                if not run("insmod /data/veposed/veposed.elf veposed") then return false, "E_RECOVERY_LOAD: insmod failed" end
                return state() ~= nil, "E_RECOVERY_SERVICE: not ready"
            end },
            { "Restore original hooks", restore_hooks },
            { "Register recovery Manager", function() return command("manager-register") end },
            { "Show Manager in app list", function() return command("manager-launcher") end },
        }
    end
    function api.recovery_result()
        local runtime, message = state()
        if not runtime then return message end
        local reasons = {[0]="NONE",[1]="UNCLOSED SESSION",[2]="HOOK FAILURE",
                         [3]="MANUAL ISOLATION",[4]="STORAGE ERROR",[5]="BAD JOURNAL"}
        local diagnostic = read("/data/veposed-status.txt") or ""
        local phase, slot = diagnostic:match("phase=([%w%-]+)%s+slot=(%x+)")
        local detail = phase and ("\nphase=" .. phase .. " slot=" .. slot) or ""
        return "SAFE MODE - modules disabled\nreason=" .. runtime.reason .. " " .. (reasons[runtime.reason] or "UNKNOWN")
            .. "\nlast=" .. runtime.last .. " rollback=" .. runtime.rollback
            .. detail .. "\nhooks=" .. runtime.sites .. " failures=" .. runtime.failures
            .. "\nOpen Veposed Manager\nReset only after fixing the cause"
    end
    function api.install_result()
        if recovering then return api.recovery_result() end
        return "DONE\nOpen Veposed Manager in app list\nInstall modules from their own faces"
    end
    return api
end
