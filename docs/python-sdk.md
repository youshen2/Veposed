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

CLI 会先验证提供固件的 AP SHA-256、版本、build、函数字节和内联入口的可写映射，并用 `rustc` 运行框架实际的 Thumb 跳板规划器和内存策略；不支持的入口、范围外状态槽或同一入口的冲突调用约定会在编译前报错。编译器还检查输出为 ARM ELF32 ET_REL、soft-float、零未解析导入和受支持的重定位。未知 Hook 名称、越界参数和错误的返回值类型在编译前报错；这些检查不能代替真机验证。

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

例如，将指南针北方向图标的显示角度增加 90 度：

```python
from veposed import Module, arg

module = Module("org.example.compass_rotation", "指南针图标旋转")
module.before("apps.compass.north_angle").set_arg(1, arg(1) + 900)
```

该点只作用于指南针中北方向图标的指定调用，角度单位为十分之一度。`ui.image.set_angle` 则匹配同一底层入口的所有调用；两个名称同时启用时，对符合限定条件的调用都会执行回调。图标旋转不会改变传感器数据，且设备验证仍待完成。

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

`call(name, *args)` 依据该名称的原型调用底层原始入口，将返回值存入 `result()`。名称既可以是当前函数，也可以是另一个已确认的函数；入口已有 Hook 时直接使用其原实现，避免递归进入同一替换过程。参数数量在编译时校验。对于 `void` 约定，结果记为 0。

`set_arg`、`call_original`、`call`、`set_result` 和 `return_` 可以按顺序链式组合；`when` 控制整条规则。例如先调整参数，再调用原逻辑，再根据目标函数的返回值含义执行修改。替换指针返回值时仍须提供目标系统中的有效对象。

## 根据固件结构字段筛选

适配表为导航动作记录了字段后，Python 模块可以读取字段作为条件。例如下面按示例编号筛选页面导航，命中时跳过这次请求并返回 0：

```python
from veposed import Module, field

module = Module("org.example.navigation_filter", "导航过滤")
module.before("system.navigation.page").when(
    (field("app_id") == 0x16) & (field("page_id") == 0x18)
).return_(0)
```

在 `system.navigation.page`、`app`、`back`、`finish_page` 和 `background_page` 中，`field("page_id")`、`field("app_id")` 和 `field("source")` 对应导航动作中偏移 `4`、`6`、`8` 的无符号字段，大小分别为 2、2、1 字节；`source` 是固件归一化前的来源值。示例中的 `0x16 / 0x18` 是关于本机页面的描述符初始编号；其他已确认的初始编号见[导航页面 ID 对照表](navigation-page-ids-xiaomi-band-10-pro-3.101.043.md)。名称导航不一定填写这些数字，运行时映射尚未真机验证。

各页面的 `ui_create`、`ui_destroy` 入口也支持 `field("page_id")` 和 `field("app_id")`，但它们读取的是 `arg(0)` 所指向的页面描述符，偏移分别为 `20` 和 `22`。创建回调的参数为页面、根对象和导航数据；销毁回调的参数为页面。跳过这些回调可能破坏页面初始化或资源清理。

字段只可在 `before` 或 `replace` 中读取，不能在一次规则里先调用原生函数再读取，也不能在同一规则中替换字段所属的参数。生成的代码对空指针直接跳过该规则；这不会改变原函数对空指针的处理。非空指针仍必须由固件调用方提供有效的动作结构。字段读取不会修改结构；需要改结构或字符串内容时使用 C SDK，并核对对象所有权和生命周期。

C SDK 对应 `vep_api.call_original(call)` 和 `call_named(name, args, &result)`。`call_original` 只接受当前回调的活动上下文；`call_named` 在已建立恢复日志的回调内使用。参数改写、原函数调用与嵌套调用都受当前执行计数保护，运行时不会在途中卸载 Hook。

完整示例见 `examples/function_calls.py`；其中 Python 分支在构建时选择使用 trampoline 还是命名入口。

## 当前固件的命名表

| 名称 | 约定 | 参数 / 返回 | 范围 |
| --- | --- | --- | --- |
| `settings.about.os_version` | `void2` | `arg(0)` 标签对象、`arg(1)` C 字符串；无返回值 | 设置 → 我的设备 → 关于本机中的 OS 值行 |
| `settings.about.os_version_size` | `void3` | `arg(0)` 标签对象、`arg(1)` 宽、`arg(2)` 高；无返回值 | 关于本机中的 OS 值标签尺寸设置 |
| `settings.about.device_type` | `void2` | 标签对象、C 字符串；无返回值 | 关于本机中的设备型号值行 |
| `settings.about.system_version` | `void2` | 标签对象、C 字符串；无返回值 | 关于本机中的系统版本值行 |
| `settings.about.mac_address` | `void2` | 标签对象、C 字符串；无返回值 | 关于本机中的 MAC 值行 |
| `settings.about.serial_number` | `void2` | 标签对象、C 字符串；无返回值 | 关于本机中的序列号值行 |
| `settings.about.system_version_clickable` | `void2` | `arg(0)` 标签对象、`arg(1)` 标志位；无返回值 | 关于本机中为系统版本标签添加可点击标志的调用 |
| `settings.display.auto_brightness_hint` | `void2` | 标签对象、C 字符串；无返回值 | 亮度设置中的自动亮度说明标签，覆盖创建和语言刷新 |
| `settings.display.brightness.auto_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 自动亮度控件事件注册 |
| `settings.display.brightness.sunshine_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 阳光模式控件事件注册 |
| `settings.display.brightness.manual_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 手动亮度入口事件注册 |
| `settings.display.brightness.action_data` | `word1` | 事件对象；返回操作编号 | 亮度设置共用回调；编号 0、1、2 对应自动、阳光、手动入口 |
| `settings.dnd.info` | `void2` | 标签对象、C 字符串；无返回值 | 勿扰与睡眠设置中的勿扰说明 |
| `settings.sleep_mode.info` | `void2` | 标签对象、C 字符串；无返回值 | 勿扰与睡眠设置中的睡眠模式说明 |
| `settings.dnd.schedule_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 注册勿扰时间设置行回调 |
| `settings.sleep_mode.toggle_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 注册睡眠模式开关回调 |
| `settings.dnd.schedule_click_data` | `word1` | 事件对象；返回用户数据 | 勿扰时间设置行点击处理 |
| `settings.return_to_dial.selected_description` | `void2` | 标签对象、C 字符串；无返回值 | 返回表盘设置中当前选中选项的说明文字 |
| `settings.return_to_dial.selected_option` | `word1` | 事件对象；返回选项编号 | 返回表盘设置点击处理，修改返回值可改变实际保存的选项；有效编号为 0、1、2 |
| `settings.return_to_dial.event_code` | `word1` | 事件对象；返回事件代码 | 返回表盘设置回调；代码 7 进入选项保存分支 |
| `settings.return_to_dial.option_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 返回表盘选项行注册；用户数据为行编号 |
| `settings.connectivity.nfc.event_code` | `word1` | 事件对象；返回事件代码 | 更多连接设置的 NFC 开关回调；代码 7 进入点击处理 |
| `settings.connectivity.nfc.click_data` | `word1` | 事件对象；返回点击数据 | NFC 点击处理；低字节为 0 时进入开关处理 |
| `settings.connectivity.nfc.click_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 更多连接设置的 NFC 开关注册 |
| `settings.battery.estimate` | `void2` | 标签对象、C 字符串；无返回值 | 电池页面预计续航说明，覆盖创建和电池事件更新 |
| `settings.battery.long_mode_estimate` | `void2` | 标签对象、C 字符串；无返回值 | 电池页面长续航开关下方的预计续航说明 |
| `settings.battery.charge_indicator_source` | `void2` | 图像对象、资源指针；无返回值 | 电池页面充电指示图标的资源设置调用 |
| `settings.battery.long_mode_click_data` | `word1` | 事件对象；返回该回调的用户数据 | 电池页面长续航开关的点击处理，原值为 1 |
| `settings.battery.long_mode_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 电池页面长续航开关注册 |
| `watchface.selection.preview_name` | `void2` | 标签对象、C 字符串；无返回值 | 表盘选择预览卡片的名称 |
| `watchface.selection.hint` | `void2` | 标签对象、C 字符串；无返回值 | 表盘选择提示卡片文字 |
| `watchface.selection.tile_event_code` | `word1` | 事件对象；返回事件代码 | 表盘选择列表回调 |
| `watchface.selection.drag_start_event_code` | `word1` | 事件对象；返回事件代码 | 表盘选择拖动起始回调 |
| `watchface.selection.drag_motion_event_code` | `word1` | 事件对象；返回事件代码 | 表盘选择拖动过程回调 |
| `watchface.selection.drag_position_text` | `void2` | 标签对象、C 字符串；无返回值 | 进入拖动时的位置／总数文字 |
| `watchface.dual_time.selected_index` | `word1` | 事件对象；返回固件时区列表索引 | 表盘双时区选择，可改变保存并发布的选项；索引为 0 至 42 |
| `watchface.dual_time.option_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 双时区选项创建和更新时注册，用户数据为列表编号 |
| `watchface.sport_selection.item_data` | `word1` | 事件对象；返回条目指针 | 表盘运动分类和运动选择的点击处理；返回 0 可跳过该回调 |
| `watchface.sport_selection.item_register` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 表盘运动或分类条目创建和更新时注册，用户数据为条目指针 |
| `apps.mijia.scene.selected_index` | `word1` | 事件对象；返回场景列表索引 | 米家场景点击处理；替代值必须是当前列表的有效非负索引，会改变实际执行的场景 |
| `apps.mijia.scene.register_create` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 米家场景行创建时注册，覆盖两个分支 |
| `apps.mijia.scene.register_update` | `word4` | 对象、回调、事件代码、用户数据；返回事件描述符 | 米家场景行更新时注册，覆盖两个分支 |
| `apps.sports.list_edit.event_code` | `word1` | 事件对象；返回事件代码 | 运动列表编辑回调；代码 4 进入操作分支 |
| `apps.sports.list_edit.action_data` | `word1` | 事件对象；返回操作编号 | 运动列表编辑回调；0、1、2 分别对应完成、删除、标记 |
| `apps.sports.list_edit.flag_register` | `word4` | 对象、回调、事件过滤值、用户数据；返回事件描述符 | 运动列表编辑的标记按钮注册 |
| `apps.sports.list_edit.delete_register` | `word4` | 对象、回调、事件过滤值、用户数据；返回事件描述符 | 运动列表编辑的删除按钮注册 |
| `apps.sports.list_edit.done_register` | `word4` | 对象、回调、事件过滤值、用户数据；返回事件描述符 | 运动列表编辑的完成按钮注册 |
| `health.heart_rate.current_caption` | `void2` | 标签对象、C 字符串；无返回值 | 心率主页面已有读数时的当前状态文字 |
| `health.heart_rate.measuring_caption` | `void2` | 标签对象、C 字符串；无返回值 | 心率主页面测量中状态文字 |
| `health.heart_rate.timeout_caption` | `void2` | 标签对象、C 字符串；无返回值 | 心率主页面超时状态文字 |
| `health.heart_rate.retry_caption` | `void2` | 标签对象、C 字符串；无返回值 | 心率主页面超时界面的重试文字 |
| `health.heart_rate.action_id` | `word1` | 事件对象；返回导航编号 | 心率应用多个视图共用的操作回调，按调用点过滤 |
| `health.heart_rate.setting.option_search_limit` | `word1` | 事件对象；返回选项搜索上界 | 心率设置选项回调，修改可能导致越界或错误选择 |
| `health.heart_rate.reminder.ignore_register` | `word4` | 对象、回调、事件过滤值、用户数据；返回事件描述符 | 心率提醒“忽略”按钮的注册 |
| `health.heart_rate.reminder.dismiss_register` | `word4` | 对象、回调、事件过滤值、用户数据；返回事件描述符 | 心率提醒“今日不再提醒”按钮的注册 |
| `health.heart_rate.reminder.dismiss_type` | `word1` | 事件对象；返回提醒类型 | “今日不再提醒”命令中的提醒类型 |
| `settings.about.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 设置：关于本机：UI 创建回调 |
| `settings.about.ui_destroy` | `void1` | 页面；无返回值 | 设置：关于本机：UI 销毁回调 |
| `settings.display.brightness.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 设置：亮度：UI 创建回调 |
| `settings.display.brightness.ui_destroy` | `void1` | 页面；无返回值 | 设置：亮度：UI 销毁回调 |
| `settings.dnd.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 设置：勿扰与睡眠：UI 创建回调 |
| `settings.dnd.ui_destroy` | `void1` | 页面；无返回值 | 设置：勿扰与睡眠：UI 销毁回调 |
| `settings.battery.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 设置：电池：UI 创建回调 |
| `settings.battery.ui_destroy` | `void1` | 页面；无返回值 | 设置：电池：UI 销毁回调 |
| `settings.connectivity.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 设置：更多连接：UI 创建回调 |
| `settings.connectivity.ui_destroy` | `void1` | 页面；无返回值 | 设置：更多连接：UI 销毁回调 |
| `health.heart_rate.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 心率主页面：UI 创建回调 |
| `health.heart_rate.ui_destroy` | `void1` | 页面；无返回值 | 心率主页面：UI 销毁回调 |
| `watchface.dual_time.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 表盘双时区：UI 创建回调 |
| `watchface.dual_time.ui_destroy` | `void1` | 页面；无返回值 | 表盘双时区：UI 销毁回调 |
| `apps.mijia.scene.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 米家场景：UI 创建回调 |
| `apps.mijia.scene.ui_destroy` | `void1` | 页面；无返回值 | 米家场景：UI 销毁回调 |
| `apps.timer.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 计时器主页面：UI 创建回调 |
| `apps.timer.ui_destroy` | `void1` | 页面；无返回值 | 计时器主页面：UI 销毁回调 |
| `apps.alarm.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 闹钟主页面：UI 创建回调 |
| `apps.alarm.ui_destroy` | `void1` | 页面；无返回值 | 闹钟主页面：UI 销毁回调 |
| `apps.weather.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 天气主页面：UI 创建回调 |
| `apps.weather.ui_destroy` | `void1` | 页面；无返回值 | 天气主页面：UI 销毁回调 |
| `health.sleep.ui_create` | `word3` | 页面、根对象、导航数据；返回原函数的机器字 | 睡眠主页面：UI 创建回调 |
| `health.sleep.ui_destroy` | `void1` | 页面；无返回值 | 睡眠主页面：UI 销毁回调 |
| `health.oxygen.ui_create` | `void3` | 页面、根对象、导航数据；无返回值 | 血氧主页面：UI 创建回调 |
| `health.oxygen.ui_destroy` | `void1` | 页面；无返回值 | 血氧主页面：UI 销毁回调 |
| `ui.image.create` | `word2` | `arg(0)` 父对象、`arg(1)` options 指针；返回新图像对象指针 | 此固件的 LVGL 图像创建入口 |
| `ui.image.set_angle` | `void2` | `arg(0)` 图像对象、`arg(1)` 有符号旋转角（十分之一度）；无返回值 | 此固件的 LVGL 图像旋转设置入口，全局作用域 |
| `ui.image.set_source` | `void2` | `arg(0)` 图像对象、`arg(1)` 资源指针；无返回值 | 此固件的 LVGL 图像资源设置入口，全局作用域 |
| `ui.event.user_data` | `word1` | 事件对象；返回用户数据指针字 | LVGL 事件用户数据读取入口，全局作用域 |
| `ui.event.code` | `word1` | 事件对象；返回事件代码 | LVGL 事件代码读取入口，全局作用域 |
| `ui.event.current_target` | `word1` | 事件对象；返回当前处理目标指针 | 事件冒泡时可随当前对象改变，全局作用域 |
| `ui.event.original_target` | `word1` | 事件对象；返回原始目标指针 | 事件的初始对象，全局作用域 |
| `ui.event.parameter` | `word1` | 事件对象；返回参数指针 | 参数含义由事件类型决定，全局作用域 |
| `ui.label.set_text` | `void2` | 标签对象、C 字符串；无返回值 | 标签文字设置，全局作用域 |
| `ui.object.set_size` | `void3` | 控件对象、宽、高；无返回值 | 控件宽高设置，全局作用域 |
| `ui.object.add_flag` | `void2` | 控件对象、标志位；无返回值 | 添加控件标志，全局作用域 |
| `ui.object.clear_flag` | `void2` | 控件对象、标志位；无返回值 | 清除控件标志，全局作用域 |
| `ui.object.has_flag` | `word2` | 控件对象、标志位；全部包含则返回 1 | 标志查询，全局作用域 |
| `ui.object.has_state` | `word2` | 控件对象、状态位；任一包含则返回 1 | 状态查询，全局作用域 |
| `ui.object.clean` | `void1` | 控件对象；无返回值 | 清除子控件，全局作用域 |
| `ui.object.create` | `word2` | 父对象、可空 options 指针；返回基础控件指针 | 基础控件创建入口，全局作用域 |
| `ui.object.delete` | `void1` | 控件对象；无返回值 | 删除对象，全局作用域；原函数执行后对象可能已释放 |
| `ui.object.class_allocate` | `word2` | 类描述符、父对象；返回待初始化对象 | 按类分配控件，全局作用域 |
| `ui.object.event_add` | `word4` | 对象、回调指针、事件过滤值、用户数据；返回事件描述符 | 注册控件事件回调，全局作用域 |
| `ui.object.event_remove` | `word2` | 对象、回调指针；返回是否移除 | 按函数移除第一个匹配回调，全局作用域 |
| `ui.object.send_event` | `word3` | 对象、事件代码、参数；返回状态 | 向对象发送事件，全局作用域；事件代码使用低 16 位 |
| `system.navigation.page` | `word1` | 导航动作指针；返回状态 | 经共享函数表发起页面导航 |
| `system.navigation.app` | `word1` | 导航动作指针；返回状态 | 经共享函数表发起应用导航 |
| `system.navigation.back` | `word1` | 导航动作指针；返回状态 | 经共享函数表发起返回导航 |
| `system.navigation.finish_page` | `word1` | 可为空的导航动作指针；返回固件结果 | 结束指定页面或当前栈顶页面 |
| `system.navigation.home` | `word1` | 模式整数；返回固件结果 | 返回主界面，非零值选择另一组转场回调 |
| `system.navigation.background_page` | `word1` | 导航动作指针；返回固件结果 | 后台页面导航路径 |
| `system.apps.kill_background` | `word2` | 调用方字符串、原因；返回固件结果 | 请求终止后台应用；返回值不一定是布尔值 |
| `system.apps.kill` | `word3` | 调用方字符串、原因、应用包名；返回固件结果 | 请求终止指定应用 |

关于本机的值行共用文本函数，但各按调用位置及对应标签对象过滤；安装前需要关闭该页面。它们经过固件静态分析和主机分发测试，设备验证状态为 pending。修改 MAC 或序列号的值行只影响该页面的显示。

自动亮度说明标签按对象及页面存活状态过滤；安装前关闭亮度设置页面。页面销毁后，即使固件保留旧标签指针，框架也不会继续对它分发回调。该点经过静态分析和主机测试，设备验证状态为 pending。

框架支持 `void0`～`void4` 和 `word0`～`word4`：名称末尾表示整数或指针字参数的个数，`void` 没有返回值，`word` 返回一个字。名称通过 `targets/xiaomi-band-10-pro-3.101.043.json` 的 `named_hooks` 注册；新功能的固件语义、原型、调用位置与签名应在适配层确认一次，模块作者随后通过名字使用它。CLI 的 `hooks` 列表反映实际可用点，不会自动猜测任意系统功能的位置。

C 接口为 `vep_api.attach_named`、`hook_text`、`list_hook_points`、`call_original`、`call_named`，详见 `include/veposed.h`。`attach_named` 的 `vep_call` 与 Python 接口使用相同调度机制。当前公共 ABI 为 4。
