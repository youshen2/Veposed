"""Run with the CLI to compile; intended only to demonstrate logic-hook syntax.
Enabling this module suppresses image creation whose parent is NULL.
"""

from veposed import Module, arg, result

module = Module("org.veposed.logic_rules", "逻辑 Hook 示例")
module.before("ui.image.create", priority=100).when(arg(0) == 0).return_(0)
# An identity rewrite illustrates after-result syntax without inventing pointers.
module.after("ui.image.create").set_result(result())
