# 适配表及证据契约

以工程 `tools/firmware.py`、`targets/xiaomi-band-10-pro-3.101.043.json`、`include/veposed.h`、`crates/veposed-runtime/src/named.rs` 为可执行契约。JSON 不支持注释，不发布有占位地址的表。

| 字段 | 含义及证据 |
| --- | --- |
| `schema`, `target`, `device`, `version`, `build` | schema 当前为 1，target 唯一，型号/build 与实际包对应 |
| `cpu`, `rust_target` | 编译架构，如 cortex-m33 / thumbv8m.main-none-eabi |
| `package_sha256`, `ap_sha256`, `ap_size` | 原包/AP 的独立身份；当前 verify 按 AP 严格校验 |
| `identity.version/build` | 各自的 AP `file_offset` 和设备可读 `address`，包含 NUL |
| `mappings[]` | name、execute、file_offset、length、writable；可写段另有 write 别名 |
| `symbols` | 当前平台代码读取的 `VEP_FW_*` 符号，函数用 Thumb 可调用地址，数据用真实地址 |
| `hooks` | address、file_offset、16 字节 expected、prototype、状态；原始 Hook 入口 |
| `named_hooks` | 面向模块的语义名称、contract、target 和作用范围约束 |
| `verification_windows[]` | name、file_offset、expected；从关键调用/初始化取得独立证据窗口 |
| `runtime_memory.umem` | data_start/data_end、execute_start/execute_end；动态模块 text/data 的合法区域 |
| `reference`, `device_validation` | 可追溯来源及本项目实际验证状态 |

## 命名点的特殊字段

当前生成器把 `os_setter_return` 转为 `caller`，把 `os_label_slot` 转为 `subject_slot`，把 `about_root` 转为 `quiescent_slot`。这些是现有 JSON 字段名称，迁移其他页面仍需按生成器实际支持填写或同时修改生成器与测试。

- `caller` 采用归一化返回 PC：通常调用指令后的偶地址，运行时将 LR 最低位清除后比较。记录调用指令宽度，不一律假设 `+4`。
- `subject_slot` 指向持有目标 label/对象指针的存储槽，命中时 `args[0] == *slot`；不是 label 本身的当前动态地址。
- `quiescent_slot` 指向页面根指针槽，安装期间要求槽中为零，避免页面活跃时修改入口。
- 0 表示无该过滤。广域入口不应为了绕过 `VEP_BUSY` 随意删去静止/对象过滤。

## 数值与映射约束

地址可按现有表写为十六进制字符串，长度为正数。签名对应实际运行入口的 AP 源字节；若 Hook 指向 SRAM/PSRAM 执行别名，file_offset 必须沿启动映射反算。BSS、设备 MMIO 和堆当前内容没有可读取的 AP 原字节，要用初始化/分配器证据证明。

当前 `generate_header` 还读取名为 `lv_image_create`、`lvx_label_set_text` 的 Hook，以及 `runtime_memory.umem`。新增固件应提供真实对应入口；新增平台若改变这些需求，应先重构平台/生成器并通过检查，不能填虚拟地址凑齐字段。

## 每个新增入口的 evidence

在 `evidence/<target>-<topic>.json` 记录：固件 hash、符号/命名点、函数原型、文件/执行/可写位置、预期字节、关键调用者与参数证据、调用上下文、对象生命周期、参考来源、当前验证层级、仍需确认的条件。

保留推理与事实的界线。例如“字符串 xref 指向此函数”是事实；“它应该是设置页面”是候选解释，需控件创建和更新链证实。只保存与任务有关的短反编译片段和元数据，原始固件及数据库留在被忽略的分析目录。

## 哪些内容不能只改 JSON

- `crates/veposed-runtime/src/memory_map.rs` 的合法区间和写入别名。
- `platform/p67cn/publisher.c` 的 I/D cache 操作与动态堆执行视图。
- `platform/p67cn/runtime.c` 和 `recovery_store.c` 的 NuttX 布局/调用 ABI。
- `manager/native.c` 的 app/page/widget ABI、分辨率、生命周期和字体。
- `tools/face.py` 的目标画布/封装规则、`installer/*.lua` 的实际 Lua binding。

`--profile` 将所选表传入验证、头文件生成、模块和框架构建；它不会自动推断这些平台差异。
