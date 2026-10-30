# C 模块与编译

当 Python DSL 无法表达业务时使用 C。先读 `include/veposed_module.h`：它负责匹配固件、读取 `/dev/veposed`、检查 ABI、注册模块、失败清理和默认停用。模块应使用 `vep_api`，不要链接第二份 runtime。

最小源码示例：

```c
#define VEP_MODULE_ID "org.example.native"
#define VEP_MODULE_STATUS_PATH "/data/veposed/org.example.native.status"
#include "veposed_module.h"

static void replace_image(vep_call *call, void *unused) {
    (void)unused;
    if (!call->args[0]) {
        call->result = 0;
        call->return_early = 1;
        return;
    }
    (void)vep->call_original(call);
}

static int32_t vep_module_setup(void) {
    uint32_t handle;
    const vep_callbacks callbacks = { .before = replace_image };
    return vep->attach_named(vep_owner, (const uint8_t *)"ui.image.create",
                             &callbacks, &handle);
}
```

这里省略独立 GUI，交给原生管理器控制模块。若涉及复杂 ABI，可用 `vep->replace()` 及严格匹配原型的 trampoline；必须另外证明地址、覆盖字节、缓存发布和并发静止条件，不能靠强转函数指针规避 ABI 限制。

## 从当前工具生成 C 构建环境

以下示例对应 Cortex-M33 的 p67cn 适配。其他 CPU 使用所选 profile 的参数及相应 Rust/LLVM target。

```sh
mkdir -p "$REPO/build/native-module"
python3 "$REPO/tools/firmware.py" header "$FIRMWARE" --profile "$PROFILE" \
  --output "$REPO/build/native-module/veposed_target.h"
clang --target=arm-none-eabi -mcpu=cortex-m33 -mthumb -mfloat-abi=soft \
  -ffreestanding -fno-builtin -fno-stack-protector -fno-unwind-tables \
  -fno-asynchronous-unwind-tables -Os -Wall -Wextra -Werror \
  -I "$REPO/include" -I "$REPO/build/native-module" \
  -c module.c -o "$REPO/build/native-module/module.o"
ld.lld -r --gc-sections -u vep_module_status -T "$REPO/scripts/module.ld" \
  -o "$REPO/build/native-module/module.elf" "$REPO/build/native-module/module.o"
llvm-objcopy --strip-debug --strip-unneeded "$REPO/build/native-module/module.elf"
```

用 `tools/elf.py` 的 `inspect(blob, required_exports=("vep_module_status",))` 检查产物；该模块是 Python 工具 API，先核对本地签名。发布为 `.face` 时复用 `tools/face.py` 的 `pack/unpack/preview/module_face_id`，及 `installer/module.lua`，遵循 `tools/module_builder.py` 当前生成的三项资源与配置结构：

- `lua/main.lua`：通用模块安装器。
- `lua/module.bin`：检查通过的 ELF。
- `lua/module_config.lua`：name、size、destination、loader_name、status；这些值与 C 中状态路径一致。

包名生成稳定 12 位 face ID；name 使用可显示的 ASCII 安装器名称；destination / loader_name 使用只含安全字符的明确值。先 `unpack` 比较实际嵌入字节，再安装。CLI `vep.py build` 当前编译 Python 模块，不能将 `.c` 当作 Python 源输入。

## 生命周期与并发

- 回调中的 `vep_call *`、原函数上下文不能保存给定时器或别的线程稍后使用。
- 回调中不执行文件 I/O、阻塞等待、堆栈不明的日志或注册/注销自身。
- `VEP_BUSY` 表示仍有执行或页面未静止，保留模块和原代码，待安全时机再人工重试。
- 注销成功前不得释放回调、userdata、自定义 trampoline。注册进系统应用表的描述符和代码须保持驻留到重启。
- 失败若不能回滚全部现场，保持隔离并交付准确的诊断，不能返回成功或自动卸载仍被引用的 ELF。
