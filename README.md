# Veposed

面向小米 Vela 穿戴设备的原生 Hook 框架。

实现参考自 [Canopus](https://github.com/AstralSightStudios/Canopus/tree/4928f1eb70594263292c32ffc531a7cad3aea555)。

Veposed 提供面向 Hook 的独立 API、模块所有权和 before/after 调度。

## 已支持固件

**小米手环 10 Pro（p67cn），固件 3.101.043**

## 生成式AI使用声明

该项目本质也是AI Slop，我不建议你化身肉编器直接阅读项目代码，以免你不小心吃到屎。

区别于某些装货，我们负责任地披露项目的主要代码使用以下模型生成：

gpt-6.1-sol

你可以自行携带你的SI加入这个项目，但如果你使用纯AI无人工干预来发布Issue或Pull Request，那我会操死你的妈。

[开发与固件适配](docs/development.md)

## 安装套件与原生管理器

```sh
python3 vep.py suite --firmware /path/to/[.bin的固件包路径]
```

运行后将会输出 `dist/Veposed-[机型]-[版本号].face`，安装此表盘后点击“Install Veposed“来安装通用框架和「Veposed 管理器」。

## Python 模块与命名接口

Veposed 支持使用`Python`编写模块。

### 替换系统版本号示例

#### 代码
```python
from veposed import Module, arg

module = Module("org.example.logic", "逻辑修改")
module.replace_text("settings.about.os_version", "MOYE.114514")
module.before("ui.image.create").when(arg(0) == 0).return_(0)
```

#### 编译方法

```sh
python3 vep.py hooks
python3 vep.py build modules/os_version/module.py --firmware /path/to/firmware.bin --out build/os-version
```

#### 使用

安装上面的 `build` 命令生成的 `build/os-version/module.face` 表盘后，在管理器启用后，“设置 → 我的设备 → 关于本机”的 OS 版本显示为 `MOYE.114514`。

注意：
> `before` / `after` 支持修改参数、跳过原逻辑及修改返回值；`replace`、`call_original`、`call` 可替换函数处理过程并主动调用原实现或其他命名入口。
> 完整规则与限制见 [Python SDK](docs/python-sdk.md)。

## AI 开发

Veposed 已提供从固件中逆向hook点和编写模块的Skill。

- [veposed-module-dev](skills/veposed-module-dev/SKILL.md)：Python/C 模块、逻辑修改、编译、安装与恢复验证。
- [veposed-firmware-port](skills/veposed-firmware-port/SKILL.md)：固件提取、地址映射、ABI/Hook 恢复、适配表与证据校验。

技能含模块脚手架、AP 提取、分析 ELF 生成及适配表校验脚本。安装方式、目录职责、格式化命令和新固件选择见 [开发说明](docs/development.md)。

## 构建与验证

依赖 Rust、Python 3.11+ 和 LLVM（`clang`、`ld.lld`、`llvm-objcopy`）。
Lua 不在 PATH 时可运行 `make check LUA=/path/to/lua`。

```sh
rustup target add thumbv8m.main-none-eabi
make check

python3 tools/firmware.py verify /path/to/[.bin的固件包路径]
python3 scripts/build-device.py /path/to/[.bin的固件包路径]
```

构建产物位于 `build/[固件包名称]/self-test/`：

- `veposed.elf`：resident runtime、模块注册、服务发现和函数指针自测。
- `client.elf`：独立加载的模块，经服务表运行自己的回调自测。
- `report.json`：固件身份、产物 hash、ELF 类型、重定位、导入和内存节大小。
- `veposed_target.h`：从核验过的目标配置生成的地址和字节签名。
- `bootstrap.lua`：在加载原生 ELF 前检查禁用文件和上次加载标记。

构建会检查 ELF32 little-endian、ARM ET_REL、soft-float、构造/析构数组、零未解析导入，以及目标 loader 的重定位类型。`resident_section_bytes` 是可分配节大小之和，实际占用还包括 loader 的对齐、符号/重定位元数据及运行栈。

查看一个执行地址对应的 AP 字节：

```sh
python3 tools/firmware.py address /path/to/firmware.bin --address 0x1c06cac1
```

## 故障回退与恢复

保护分为加载前和注入前两层：

1. **加载前**：将设备现有的自动启动入口接到 `bootstrap.lua`。脚本先检查 `/data/veposed.disable` 和 `/data/veposed-load.pending`，创建并 flush/close 本次加载标记后才执行 `insmod`。加载失败、构造函数崩溃，以及成功加载后的普通重启，都会保留这个标记；下一次自动启动直接跳过原生 ELF。该入口采用手动重新启用策略。
2. **注入前**：runtime 将带 CRC32 的 32 字节记录写入 `/data/veposed-guard.bin`，成功 `fsync` 后才修改目标。最后一个 Hook 成功恢复后才写 CLEAN。正常重启时若仍有 Hook 在运行，也按未干净结束处理。

安装失败会隔离本次会话，尝试恢复全部已安装 Hook。恢复某一项失败时仍继续恢复其他项，并保留失败项的原始字节、句柄和所有权。

日志损坏、截断、读取失败、写入失败或同步失败都会阻止继续注入。

主动停止 Hook：

```sh
printf disable > /dev/veposed
cat /data/veposed-status.txt
```

若上次加载已在早期崩溃，先创建外部禁用文件，然后手动加载 runtime，取得安全模式中的恢复服务：

```sh
printf 1 > /data/veposed.disable
insmod /data/veposed/veposed.elf veposed
cat /data/veposed-status.txt
```

确认故障模块已经修复，且状态中的 `sites=0`、`rollback=0` 后，手动为下一次启动解除隔离：

```sh
printf disable > /dev/veposed
printf reset > /dev/veposed
rm /data/veposed.disable
```

## 编写模块

完整的 C 示例见 [examples/host/main.c](examples/host/main.c)、[examples/device/client.c](examples/device/client.c)，公共接口见 [include/veposed.h](include/veposed.h)。

```c
vep_target target = {
    .kind = VEP_POINTER,
    .address = (uintptr_t)&callback_slot,
    .expected_pointer = (uintptr_t)original_callback,
};
vep_callbacks callbacks = {
    .before = before_callback,
    .after = after_callback,
    .priority = 100,
};
uint32_t handle;
int32_t rc = api->attach(owner, &target, &callbacks, &handle);
```

`expected_pointer` 或 16 字节 `expected_code` 必须与当前目标一致。多个模块共同 Hook 同一目标时使用同一份原始描述；框架复用物理跳转，分别管理回调句柄。相同优先级按注册顺序执行。回调中只能修改本次 `vep_call`；安装、卸载或启停应在回调返回后的线程上下文进行。

## 开源与许可

工程按 [AGPL-3.0-only](LICENSE) 发布。