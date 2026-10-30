# Python 模块 SDK 与 CLI

模块作者可用 Python 来描述 Hook，通过 CLI 在电脑上执行描述文件，生成 C 回调并交叉编译为 ARM ELF，再封装为可安装的 `.face`。

## 编译与安装

```sh
python3 vep.py hooks
python3 vep.py build modules/os_version/module.py --firmware /path/to/firmware.bin --out build/os-version
python3 vep.py inspect-face build/os-version/module.face
python3 vep.py suite --firmware /path/to/firmware.bin
```

`build` 将会输出 `module.elf`、`module.face`、`module.json`、生成的 `module.c`、目标头文件和 `build-report.json`。

`suite` 输出 `dist/` 下的框架与管理器安装表盘、源码 ZIP 和技能 ZIP。通过现有表盘安装工具（如AstroBox）安装 `.face`，在手环上打开安装表盘并点击安装。

`hooks`、`build`、`suite` 均接受 `--profile targets/目标.json`，默认选择 `xiaomi-band-10-pro-3.101.043.json`。新固件还需同步平台 ABI 和内存范围，具体流程见 `skills/veposed-firmware-port/SKILL.md`。

CLI 会先验证提供固件的 AP SHA-256、版本、build 和函数字节。编译器检查输出为 ARM ELF32 ET_REL、soft-float、零未解析导入和受支持的重定位。未知 Hook 名称、越界参数和错误的返回值类型在编译前报错。

生成模块表盘时，CLI 根据模块包名稳定生成 12 位数字 ID；框架安装表盘使用独立 ID。打包与检查工具均遵循 AstroBox 的 9/12 位 ASCII 字母数字规则，具体解析依据记录在 `evidence/astrobox-face-id.json`。

## 文字替换

```python
from veposed import Module

module = Module("org.example.os_version", "OS 版本替换")
module.replace_text("settings.about.os_version", "MOYE.114514")
```

框架拥有替换字符串副本，在固件适配表指定的调用位置和标签对象都匹配时调用回调。框架恢复和模块注销也会清理这项注册。

## 跳过、替换和修改逻辑

```python
from veposed import Module, arg, result

module = Module("org.example.logic", "逻辑修改")

# 条件成立时，整个原始函数不再执行，直接返回 NULL。
module.before("ui.image.create", priority=100).when(arg(0) == 0).return_(0)

# 对 void 函数，跳过这次调用。例如停止更新设置页面上的 OS 值。
module.before("settings.about.os_version").skip()

# 在调用原始函数前，把第二个参数换成一个模块生命周期内有效的字符串。
module.before("settings.about.os_version", priority=10).set_arg(1, "CUSTOM.OS")

# after 可读取原函数返回值，并有条件地替换。这里展示返回值接口，保留 NULL。
module.after("ui.image.create").when(result() == 0).set_result(0)
```

以上各条是可独立选择的规则；同时注册 `skip()` 与字段修改时，高优先级或先注册的 `skip()` 会阻止后续 before 和原函数，因而应按实际目的组合。

- `before(point, priority=0)`：原逻辑之前；`after(point, priority=0)`：原逻辑或提前返回之后。
- `set_arg(index, value)`：修改参数；索引从 0 开始。
- `skip()`：跳过原函数与后续 before。返回值保持当前 `result`，初始为 0。
- `return_(value)`：设置结果并跳过原函数与后续 before，用于有返回值的目标。
- `set_result(value)`：修改结果；通常用于 after。
- `when(expression)`：条件成立才执行该规则；没有条件则每次执行。
- `arg(i)`、`result()`：设备运行时读取的表达式，支持 `+ - * & | ^ == != < <= > >=`；用 `&` / `|` 组合条件并显式加括号。
- 数值为 32 位无符号字；字符串编译为模块常量。与指针有关的参数和返回值须遵守目标函数约定。
- Python 的循环、函数等可以组织并生成规则；回调执行的是上述表达式和动作。需要任意 C 函数体、复杂内存访问或其他原生 ABI 时使用 C SDK。

before 按 priority 降序执行，after 按本次实际进入的回调逆序执行。停用模块会绕过其回调；命名 Hook 的物理调度入口可能继续驻留，直到最后一个监听者注销或执行安全恢复。

## 替换函数与主动调用

`replace()` 注册函数替代逻辑。命中规则后默认跳过原实现，可显式调用原函数，再继续处理结果：

```python
from veposed import Module, arg, result

module = Module("org.example.calls", "函数调用")
module.replace("ui.image.create").call_original()
```

`call_original()` 使用此刻的参数，调用原始 trampoline，把结果存入 `result()` 并标记本次原逻辑已执行。框架不会在回调返回后再自动执行一次。它也可以用于 before 或 after；after 中使用它意味着明确再次调用原实现。

主动调用指定函数的另一种写法：

```python
module = Module("org.example.direct_call", "主动调用")
module.replace("ui.image.create").call("ui.image.create", arg(0), arg(1))
```

`call(name, *args)` 依据该名称的原型调用底层原始入口，将返回值存入 `result()`。名称既可以是当前函数，也可以是另一个已确认的函数；入口已有 Hook 时直接使用其原实现，避免递归进入同一替换过程。参数数量在编译时校验。对于 `void2`，结果记为 0。

`set_arg`、`call_original`、`call`、`set_result` 和 `return_` 可以按顺序链式组合；`when` 控制整条规则。例如先调整参数，再调用原逻辑，再根据目标函数的返回值含义执行修改。替换指针返回值时仍须提供目标系统中的有效对象。

C SDK 对应 `vep_api.call_original(call)` 和 `call_named(name, args, &result)`。`call_original` 只接受当前回调的活动上下文；`call_named` 在已建立恢复日志的回调内使用。参数改写、原函数调用与嵌套调用都受当前执行计数保护，运行时不会在途中卸载 Hook。

完整示例见 `examples/function_calls.py`；其中 Python 分支在构建时选择使用 trampoline 还是命名入口。

## 当前固件的命名表

| 名称 | 约定 | 参数 / 返回 | 范围 |
| --- | --- | --- | --- |
| `settings.about.os_version` | `void2` | `arg(0)` 标签对象、`arg(1)` C 字符串；无返回值 | 设置 → 我的设备 → 关于本机中的 OS 值行 |
| `ui.image.create` | `word2` | `arg(0)` 父对象、`arg(1)` options 指针；返回新图像对象指针 | 此固件的 LVGL 图像创建入口 |

框架也支持 `word4`：四个字参数、一个字返回值。名称通过 `targets/xiaomi-band-10-pro-3.101.043.json` 的 `named_hooks` 注册；新功能的固件语义、原型、调用位置与签名应在适配层确认一次，模块作者随后通过名字使用它。CLI 的 `hooks` 列表反映实际可用点，不会自动猜测任意系统功能的位置。

C 接口为 `vep_api.attach_named`、`hook_text`、`list_hook_points`、`call_original`、`call_named`，详见 `include/veposed.h`。`attach_named` 的 `vep_call` 与 Python 接口使用相同调度机制。当前公共 ABI 为 4。
