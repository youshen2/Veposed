local lvgl = require("lvgl")
local controller
local text_font = lvgl.BUILTIN_FONT.MONTSERRAT_14
local root = lvgl.Object(nil, {
    w = lvgl.HOR_RES(), h = lvgl.VER_RES(), bg_color = 0x10141C,
    bg_opa = lvgl.OPA(100), border_width = 0,
})
root:clear_flag(lvgl.FLAG.SCROLLABLE)
local panel = lvgl.Object(root, {
    w = 336, h = 480, bg_color = 0x10141C, bg_opa = lvgl.OPA(100),
    border_width = 0, pad_all = 0, align = lvgl.ALIGN.CENTER,
})
panel:clear_flag(lvgl.FLAG.SCROLLABLE)
lvgl.Label(panel, { text = "Veposed", text_font = text_font, text_color = 0xFFFFFF,
    align = {type = lvgl.ALIGN.CENTER, x_ofs = 0, y_ofs = -185} })
lvgl.Label(panel, { text = "10 Pro / 3.101.043", text_font = text_font, text_color = 0xA2AAB8,
    align = {type = lvgl.ALIGN.CENTER, x_ofs = 0, y_ofs = -145} })
local status = lvgl.Label(panel, { text_font = text_font, text = "Native Manager + OS version module\nModules start disabled", text_color = 0xCFD4DF,
    width = 294, height = 168,
    align = {type = lvgl.ALIGN.CENTER, x_ofs = 0, y_ofs = 136} })
local busy, attempted = false, false
local active_timer
local function set_status(message, failed)
    local readable = tostring(message):gsub("[^\n -~]", "?")
    status:set { text = readable, text_color = failed and 0xFFB0A8 or 0xCFD4DF }
    print("[Veposed] " .. tostring(message))
end
local function run_steps(steps, completion, operation)
    if busy then return end
    busy = true
    local index = 1
    local timer = lvgl.Timer { period = 800, repeat_count = -1, paused = true,
        cb = function(t)
            local step = steps[index]
            if not step then
                t:pause(); active_timer = nil; busy = false
                set_status(type(completion) == "function" and completion() or completion)
                return
            end
            set_status(operation .. " STEP " .. index .. "/" .. #steps .. "\n" .. step[1])
            local called, ok, message = pcall(step[2])
            if not called or not ok then
                t:pause(); active_timer = nil; busy = false
                set_status("FAIL S" .. index .. " [" .. operation .. "]\n" .. tostring(called and message or ok), true)
                return
            end
            index = index + 1
        end,
    }
    if not timer then busy = false; set_status("E_TIMER: cannot create install task", true); return end
    active_timer = timer
    timer:resume()
    timer:ready()
end
local function button(text, y, color, action)
    local object = lvgl.Object(panel, {
        w = 278, h = 58, bg_color = color, bg_opa = lvgl.OPA(100), radius = 16,
        align = {type = lvgl.ALIGN.CENTER, x_ofs = 0, y_ofs = y},
    })
    object:clear_flag(lvgl.FLAG.SCROLLABLE)
    object:add_flag(lvgl.FLAG.CLICKABLE)
    lvgl.Label(object, {text = text, text_font = text_font, text_color = 0xFFFFFF, align = lvgl.ALIGN.CENTER})
    object:onClicked(action)
    return object
end
-- Draw the status label before touching script resources, so loading failures
-- are visible on the watch instead of aborting before the first frame.
local loaded, result = pcall(function()
    local root_path = assert(SCRIPT_PATH, "SCRIPT_PATH is required")
    if root_path:sub(-1) ~= "/" then root_path = root_path .. "/" end
    return dofile(root_path .. "loader.lua")(root_path)
end)
if not loaded then
    set_status("E_INIT: script load failed\n" .. tostring(result), true)
    return
end
controller = result

local install_button
install_button = button("INSTALL VEPOSED", -60, 0x6557D9, function()
    -- A second click (or a repeated event) must not hide the first result or
    -- re-enter a partially completed native installation.
    if busy or attempted then return end
    attempted = true
    install_button:clear_flag(lvgl.FLAG.CLICKABLE)
    run_steps(controller.install_steps(), controller.install_result, "INSTALL")
end)
button("SAFE RECOVERY", 18, 0x334158, function()
    run_steps(controller.recovery_steps(), controller.recovery_result, "RECOVERY")
end)
if VEP_RECOVERY_ON_OPEN then
    run_steps(controller.recovery_steps(), controller.recovery_result, "RECOVERY")
end
