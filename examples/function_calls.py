"""A replacement can invoke the original trampoline or a verified named entry.
Both branches preserve image creation; choose the desired call style at build time.
"""

from veposed import Module, arg

module = Module("org.veposed.function_calls", "函数替换与调用")
USE_NAMED_CALL = False
replacement = module.replace("ui.image.create")
if USE_NAMED_CALL:
    replacement.call("ui.image.create", arg(0), arg(1))
else:
    replacement.call_original()
