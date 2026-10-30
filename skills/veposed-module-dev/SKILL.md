---
name: veposed-module-dev
description: 开发、调试和打包 Veposed 模块，使用 Python DSL 或 C ABI 实现参数修改、跳过逻辑、返回值修改和原函数调用。适用于已有 Veposed 命名 Hook 的模块开发；需要恢复固件地址或新增适配时使用 veposed-firmware-port。
---

# Veposed 模块开发

交付可审阅源码、独立模块 `.face`、构建报告和启停/恢复验证结果。以用户指定的功能、设备和固件版本为范围；演示内容也应做成真实可安装模块。

## 定位工程和接口

1. 找到用户的 Veposed 工程，先读该目录适用的 `AGENTS.md` / `AGENT.md`。没有工程时请求路径，不猜测固件地址。将工程路径记为 `REPO`，选定 `targets/*.json` 为 `PROFILE`。
2. 读取工程当前的 `docs/python-sdk.md`、`include/veposed.h` 和相关模块源码，以它们为接口事实；本文对应 ABI 4。
3. 用 `python3 "$REPO/vep.py" hooks --profile "$PROFILE"` 检查命名点及 `void2`、`word2`、`word4` 原型。缺少所需点时转入固件适配流程，不在模块内复制或猜地址。
4. 为可用 DSL 编写 Python 模块；需要复杂内存访问、自定义函数体或更复杂 ABI 时读 [C 模块](references/native.md)。常用规则和语义见 [规则选择](references/rules.md)。

## 编写和构建

- 模块必须定义 `module = Module(id, name, version)`；包名稳定、唯一。发布安装后默认停用，用户在原生管理器中启用。
- Python 在电脑上执行并生成 C；手环运行原生代码。Python 文件具备本机执行能力，运行用户或仓库提供的源码前先阅读。
- 同一函数的跳过规则、替换规则和 before 优先级要能解释其组合结果。`void2` 没有返回值；指针返回必须满足目标对象生命周期。
- 使用辅助脚本生成起点（不会覆盖文件）：

```sh
python3 "$SKILL_DIR/scripts/new_module.py" --repo "$REPO" --profile "$PROFILE" \
  --id org.example.version --name '版本展示' \
  --point settings.about.os_version --mode text --text 'CUSTOM.OS' \
  --out "$REPO/modules/version/module.py"
python3 "$REPO/vep.py" build "$REPO/modules/version/module.py" \
  --profile "$PROFILE" --firmware "$FIRMWARE" --out "$REPO/build/version"
python3 "$REPO/vep.py" inspect-face "$REPO/build/version/module.face"
```

`SKILL_DIR` 是本技能文件所在目录。需要保留原逻辑的替换模板时使用 `--mode original`。

检查生成的 `module.c`、`module.json` 和 `build-report.json`。必须能说明目标版本、命名点、参数/返回处理和代码生命周期。ELF 应为 ARM ELF32 ET_REL、soft-float，未解析导入列表为空。不要仅凭成功编译宣称真机可用。

## 验证和交付

按 [验证与恢复](references/validation.md) 覆盖实际修改的语义：条件命中/未命中、原函数调用次数、关闭后恢复、错误路径，以及必要的安全模式行为。沿用已有测试；只为新增语义补充有价值的检查。

安装流程为框架表盘 → 原生管理器 → 独立模块表盘 → 启用模块。已驻留模块更新应先停用并按恢复流程结束会话，再重启加载新二进制；避免同包名重复 `insmod`。

交付源码、`module.face`、`module.elf`、清单和构建报告，说明实际完成的主机/设备验证及剩余限制。故障后读取原因并保留隔离，恢复成功且原因已处理时再手动重置。不要自动循环重新安装、重新启用或清除失败标记。
