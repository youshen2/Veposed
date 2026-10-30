# OS 版本替换模块

为小米手环 10 Pro / 3.101.043 编写的独立 Veposed 模块。在 **设置 → 我的设备 → 关于本机** 中将 OS 版本显示为 `MOYE.114514`。

先安装 Veposed 框架与管理器表盘，再安装本模块生成的 `.face`，打开表盘并点击「INSTALL MODULE」。然后在应用列表中的「Veposed 管理器」启用“OS 版本替换”。

模块默认停用。停用后重新打开“关于本机”，显示恢复原值。框架只对指定调用位置和 OS 标签对象分发回调，原始固件版本字符串保持不变。

## Python 源码

```python
from veposed import Module

module = Module(
    "org.veposed.os_version", "OS 版本替换", status_path="/data/veposed-moye-status.txt"
)
module.replace_text("settings.about.os_version", "MOYE.114514")
```

在完整套件的 `source/` 目录编译：

```sh
python3 vep.py build modules/os_version/module.py --firmware /path/to/firmware.bin --out build/os-version
```

输出 `module.elf`、`module.face`、生成的 C 代码及构建报告。`module.c` 同时提供等价 C SDK 示例；完整的参数、返回值和逻辑修改接口见 `docs/python-sdk.md`。

加载失败后通过 Veposed 安装表盘的「SAFE RECOVERY」处理，再到管理器检查状态。设备实际验证状态以构建报告为准。
