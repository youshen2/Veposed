# 开发与固件适配

## 目录职责

| 目录 | 职责 |
| --- | --- |
| `crates/veposed-core` | Hook 引擎、Thumb 指令检查与恢复状态机 |
| `crates/veposed-runtime` | C ABI、命名 Hook 分发与内存访问 |
| `platform/p67cn` | 设备 runtime、NuttX 恢复存储与 cache publisher |
| `platform/aeabi.c` | 独立模块所需的 ARM ABI 辅助实现 |
| `manager` | 系统应用列表中的原生卡片管理器 |
| `installer` | 框架安装、启动保护、模块安装与安全恢复 Lua 入口 |
| `modules` | 独立功能模块；`os_version` 提供版本展示实例 |
| `sdk` / `include` | Python 描述语言与 C ABI 头文件 |
| `tools` / `scripts` | 编译、固件校验、封装和验证入口 |
| `targets` / `evidence` | 固件适配表和可追溯的字节/调用链证据 |
| `skills` | 模块开发和固件逆向技能及配套脚本 |
| `examples` / `tests` | 调用示例与主机行为验证 |

## 安装和使用技能

两套技能位于 `skills/veposed-module-dev` 与 `skills/veposed-firmware-port`。可以将这两个目录复制或链接到 `~/.codex/skills/`；也可将 `dist/Veposed-Development-Skills.zip` 解压到该目录。已有同名目录时先检查内容，避免覆盖个人修改。新的 Codex 会话可自动发现，或按名称显式调用：

```text
$veposed-module-dev 为指定命名 Hook 编写模块，编译并验证独立 face。
$veposed-firmware-port 分析给定固件，恢复地址映射、ABI 和适配表。
```

技能中的工具接受 `--repo`，可在解压后的源码工程或其他检出目录运行。技能不携带原始固件；`FIRMWARE` 指向自己提供的精确 OTA/AP。

## 构建

```sh
rustup target add thumbv8m.main-none-eabi
python3 vep.py suite --firmware /path/to/firmware.bin
python3 vep.py build modules/os_version/module.py \
  --firmware /path/to/firmware.bin --out build/os-version
```

框架表盘、开发源码 ZIP 和技能 ZIP 位于 `dist/`；独立模块产物位于 `build/os-version/`。源码 ZIP 的 `source/` 包含完整构建文件，重建时进入该目录并使用外部固件路径。

选择其他已完成适配的固件表：

```sh
python3 vep.py hooks --profile targets/目标.json
python3 vep.py suite --firmware /path/to/firmware.bin --profile targets/目标.json
python3 vep.py build /path/to/module.py --firmware /path/to/firmware.bin \
  --profile targets/目标.json --out build/custom-module
```

新增设备时，JSON 选择与平台代码移植需要共同完成。尤其检查动态堆地址、cache 别名、app/page ABI、屏幕尺寸和 Lua 接口。

## 格式与检查

构建工具使用 Python 标准库。开发时安装格式化器和技能校验依赖：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/ruff format .
.venv/bin/ruff check .
make check LUA=/path/to/lua
```
