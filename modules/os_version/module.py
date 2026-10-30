from veposed import Module

module = Module(
    "org.veposed.os_version", "OS 版本替换", status_path="/data/veposed-moye-status.txt"
)
module.replace_text("settings.about.os_version", "MOYE.114514")
