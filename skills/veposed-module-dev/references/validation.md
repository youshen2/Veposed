# 模块验证、安装与恢复

## 有针对性的主机验证

优先复用项目已有检查：

```sh
cd "$REPO"
python3 -m unittest discover -s tools/tests
python3 scripts/test-host.py
python3 scripts/test-module.py
```

涉及加载、状态文件或恢复时再运行：

```sh
python3 scripts/test-bootstrap.py --lua "$LUA"
python3 scripts/test-installer.py --lua "$LUA"
python3 scripts/test-recovery.py
```

需要测试新回调时，将生成的 C 与 host stub/真实 Rust 静态库链接，验证条件命中和未命中、原函数调用次数、before/after 顺序、停用后恢复。不要用仅匹配源码字符串的测试代替执行语义。已有主机用例见 `tools/tests/test_sdk.py` 和 `tests/named_api.c`。

## 设备流程

1. 核对型号、profile 与设备固件一致。安装框架 `.face`，完成后应用列表出现 Veposed 管理器。
2. 使用独立模块 `.face` 安装。初始化报告应为成功，管理器列出该包名并默认停用。
3. 先启用一个模块，在约定页面/操作中验证目标行为，同时检查同名的其他字段/页面是否保持原行为。
4. 停用模块后重新触发页面渲染，确认原行为恢复。测试多模块时检查顺序与范围冲突。
5. 更新已驻留模块时，先停用并确认恢复状态，重启后加载新二进制；失败会话不能靠连续点击安装来重试。

## 故障信息

| 信息 | 含义和下一步 |
| --- | --- |
| `E_ALREADY_LOADED` | runtime 已驻留；去应用列表，更新代码需结束会话并重启 |
| `E_ATTEMPTED` | 该表盘已尝试加载；保留原错误，不重复注入 |
| `E_ISOLATED` / `E_BOOT_BLOCKED` | 加载标记阻止重复失败；进入 SAFE RECOVERY，读取原因 |
| `reason=1` | 上次 Hook 会话未干净结束 |
| `reason=2`, `last=-7` | Hook 失败且返回内存错误；检查执行/写入别名、动态堆范围，不能只改目标地址 |
| `last=-6` | 签名不一致；核对固件与预期字节 |
| `last=-8` | 当前忙；保持现场，等待已确认的静止时机 |
| `reason=4/5` | 恢复存储或日志校验出错；先处理持久化 |
| `rollback!=0` / `hooks!=0` | 仍有恢复工作；不得重置隔离或卸载代码 |

SAFE RECOVERY 会建立安全模式中的恢复管理器。原因修复、原入口恢复完成、无活动执行后，用户可手动“重置隔离”，随后重启。重置只放行下一次启动，不在当前会话自动重新启用。Lua 安装器使用内建 ASCII 字体显示故障；不要为了中文标签把报错变成方块。

交付时记录测试设备、固件哈希、模块哈希、安装前后状态与复现步骤。主机测试、静态逆向和模拟器验证分别标注；没有实际设备证据就保留 `device_validation: pending`。
