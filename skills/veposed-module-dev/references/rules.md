# Python 规则选择与真实执行语义

以工程 `sdk/veposed/__init__.py`、`docs/python-sdk.md`、`crates/veposed-runtime/src/named.rs` 为当前实现；调用接口前核对这些文件。

## 函数契约

| 契约 | 参数 | 返回 |
| --- | --- | --- |
| `void2` | 两个整数/指针字 | 无 |
| `word2` | 两个整数/指针字 | 一个整数/指针字 |
| `word4` | 四个整数/指针字 | 一个整数/指针字 |

ABI 4 的命名调用限于整数/指针寄存器，不把浮点、结构体传值或变参函数强转进此契约。参数数字是 32 位字，负数会转换成对应位模式，比较通常按无符号执行。指针不能由电脑地址、Python 对象地址或任意数字伪造。

## 按需求选择最小规则

```python
from veposed import Module, arg, result

module = Module("org.example.logic", "逻辑修改", "1.0.0")
```

下面示例应按需求分别选择，不默认全部组合：

```python
# 作用域由适配表约束的字符串替换。最多 95 个 UTF-8 字节，无 NUL。
module.replace_text("settings.about.os_version", "CUSTOM.OS")

# void 函数删掉本次逻辑，不编造返回值。
module.before("settings.about.os_version").skip()

# 调整入参，继续执行原函数。
module.before("settings.about.os_version").set_arg(1, "CUSTOM.OS")

# 有返回值函数：只在无父对象时提前返回空指针。
module.before("ui.image.create", priority=50).when(arg(0) == 0).return_(0)

# 替换函数但显式执行原实现，原函数只调用一次。
module.replace("ui.image.create").call_original()

# 调用已确认的命名原始入口；已有 Hook 时绕过分发，避免自递归。
module.replace("ui.image.create").call("ui.image.create", arg(0), arg(1))

# after 按目标返回值语义处理结果；这里原样保留空指针。
module.after("ui.image.create").when(result() == 0).set_result(0)
```

- `replace()` 在条件成立后设置提前返回；条件不成立仍走原流程。
- `skip()` / `return_()` 终止当前 before 链及原函数；已经进入的 after 仍会执行。
- before 按优先级降序，after 按本次进入顺序的逆序。
- `call_original()` 使用当前参数，存入 `result()` 并阻止分发器再次调用原实现。after 中调用会明确再执行一次原函数。
- `call()` 的参数数量按被调用点校验；只在活动回调内调用，不能用它在安装构造函数中任意执行系统 API。
- `when()` 作用于整条链式规则。不要写 Python `if arg(0)` 或 Python `and/or`；表达式需使用 `.when(...)` 及带括号的 `&` / `|`。
- Python 普通函数、循环在构建时运行；设备侧动态逻辑由 DSL 表达式或 C 回调实现。
- `ui.image.create` 是底层广域接口，改写会影响多个应用。确认对象和调用作用域后再启用，不能把“编译通过”等同于“功能范围正确”。

字符串常量必须在整个回调生命周期内有效。`replace_text` 由框架保存副本；C 手写字符串和自定义对象由模块维护。模块停用时分发入口可能仍驻留，原始行为应恢复；只有成功注销并等待执行结束才可卸载代码。
