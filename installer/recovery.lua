VEP_RECOVERY_ON_OPEN = true
local root = assert(SCRIPT_PATH)
if root:sub(-1) ~= "/" then root = root .. "/" end
dofile(root .. "main.lua")
