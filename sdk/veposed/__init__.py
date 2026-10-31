"""Host-side Python DSL that compiles named hook rules into native C callbacks."""

from dataclasses import dataclass, field as dataclass_field
import json
import re


def literal(value):
    if isinstance(value, Expr):
        return value.code
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        if not -(2**31) <= value <= 0xFFFFFFFF:
            raise ValueError("word literal is outside 32-bit range")
        return f"((uintptr_t)(int32_t){value})" if value < 0 else str(value) + "u"
    if isinstance(value, str):
        return "(uintptr_t)" + json.dumps(value, ensure_ascii=False)
    raise TypeError("expected integer, string, arg() or result() expression")


@dataclass(eq=False)
class Expr:
    code: str
    arguments: frozenset = frozenset()
    uses_result: bool = False
    fields: frozenset = frozenset()

    def _binary(self, other, op):
        rhs = other if isinstance(other, Expr) else Expr(literal(other))
        return Expr(
            f"({self.code} {op} {rhs.code})",
            self.arguments | rhs.arguments,
            self.uses_result or rhs.uses_result,
            self.fields | rhs.fields,
        )

    def __add__(self, other):
        return self._binary(other, "+")

    def __sub__(self, other):
        return self._binary(other, "-")

    def __mul__(self, other):
        return self._binary(other, "*")

    def __and__(self, other):
        return self._binary(other, "&")

    def __or__(self, other):
        return self._binary(other, "|")

    def __xor__(self, other):
        return self._binary(other, "^")

    def __eq__(self, other):
        return self._binary(other, "==")

    def __ne__(self, other):
        return self._binary(other, "!=")

    def __lt__(self, other):
        return self._binary(other, "<")

    def __le__(self, other):
        return self._binary(other, "<=")

    def __gt__(self, other):
        return self._binary(other, ">")

    def __ge__(self, other):
        return self._binary(other, ">=")

    def __bool__(self):
        raise TypeError("hook expressions run on the device; use .when(expr)")


def arg(index):
    if not isinstance(index, int) or not 0 <= index < 4:
        raise ValueError("argument index must be 0..3")
    return Expr(f"call->args[{index}]", frozenset({index}))


def result():
    return Expr("call->result", uses_result=True)


def field(name):
    """Read a named field of a Hook argument, as defined by its target profile."""
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError("invalid field name")
    return Expr(f"VEP_FIELD_{name}__", fields=frozenset({name}))


@dataclass
class Rule:
    point: str
    phase: str
    priority: int = 0
    condition: Expr | None = None
    actions: list = dataclass_field(default_factory=list)

    def when(self, expression):
        if not isinstance(expression, Expr):
            raise TypeError("when requires a hook expression")
        self.condition = expression
        return self

    def set_arg(self, index, value):
        arg(index)
        if self.phase == "after":
            raise ValueError("set_arg is a before/replace action")
        self.actions.append(("arg", index, value))
        return self

    def set_result(self, value):
        self.actions.append(("result", None, value))
        return self

    def return_(self, value):
        if self.phase == "after":
            raise ValueError("return_ is a before/replace action")
        self.actions.append(("return", None, value))
        return self

    def skip(self):
        if self.phase == "after":
            raise ValueError("skip is a before/replace action")
        self.actions.append(("skip", None, 0))
        return self

    def call_original(self):
        self.actions.append(("original", None, 0))
        return self

    def call(self, point, *arguments):
        self.actions.append(("call", point, arguments))
        return self


class Module:
    def __init__(self, module_id, name, version="1.0.0", *, status_path=None):
        if not re.fullmatch(r"[a-z][a-z0-9_.]{0,46}", module_id):
            raise ValueError("invalid module id")
        if not isinstance(name, str) or not name:
            raise ValueError("module name is required")
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            raise ValueError("version must be x.y.z")
        self.id, self.name, self.version = module_id, name, version
        self.status_path = status_path or "/data/veposed/" + module_id + ".status"
        self.rules = []

    def replace_text(self, point, text):
        if not isinstance(text, str) or len(text.encode()) > 95 or "\0" in text:
            raise ValueError("text must be at most 95 UTF-8 bytes, with no NUL")
        self.rules.append((point, text))
        return self

    def before(self, point, priority=0):
        return self._rule(point, "before", priority)

    def after(self, point, priority=0):
        return self._rule(point, "after", priority)

    def replace(self, point, priority=0):
        return self._rule(point, "replace", priority)

    def _rule(self, point, phase, priority):
        if not isinstance(priority, int) or not -(2**31) <= priority < 2**31:
            raise ValueError("invalid priority")
        rule = Rule(point, phase, priority)
        self.rules.append(rule)
        return rule

    def emit_c(self, points):
        if not self.rules:
            raise ValueError("module needs at least one hook")
        functions, installs = [], []
        for i, rule in enumerate(self.rules):
            point = rule[0] if isinstance(rule, tuple) else rule.point
            if point not in points:
                raise ValueError("unknown hook point: " + point)
            contract = points[point]["contract"]
            if isinstance(rule, tuple):
                if contract != "void2" or not points[point].get("text_arg1", False):
                    raise ValueError("replace_text needs a void2 text setter")
                installs.append(
                    f"rc = vep->hook_text(vep_owner, (const uint8_t *){json.dumps(point)}, (const uint8_t *){json.dumps(rule[1], ensure_ascii=False)}, &handle);"
                )
                continue
            if not rule.actions:
                raise ValueError("empty callback: " + point)
            expressions = [rule.condition] if rule.condition is not None else []
            expressions += [v for _, _, v in rule.actions if isinstance(v, Expr)]
            expressions += [
                v
                for k, _, values in rule.actions
                if k == "call"
                for v in values
                if isinstance(v, Expr)
            ]
            if contract not in {
                f"{kind}{count}" for kind in ("void", "word") for count in range(5)
            }:
                raise ValueError("unsupported contract: " + contract)
            argc = int(contract[-1])
            if any(any(n >= argc for n in e.arguments) for e in expressions):
                raise ValueError("argument exceeds " + contract)
            field_names = set().union(*(e.fields for e in expressions))
            if field_names and rule.phase == "after":
                raise ValueError("fields are available only before or during replacement")
            layouts = points[point].get("fields", {})
            field_code, field_args = {}, set()
            for name in field_names:
                if name not in layouts:
                    raise ValueError("unknown field for " + point + ": " + name)
                spec = layouts[name]
                index, offset, width, size = spec["arg"], spec["offset"], spec["width"], spec["size"]
                if not (isinstance(index, int) and 0 <= index < argc and
                        isinstance(offset, int) and offset >= 0 and width in (1, 2, 4) and
                        isinstance(size, int) and offset + width <= size):
                    raise ValueError("invalid field layout for " + point + ": " + name)
                field_args.add(index)
                parts = [
                    f"((uintptr_t)((const uint8_t *)call->args[{index}])[{offset + n}] << {n * 8})"
                    for n in range(width)
                ]
                field_code[name] = "(" + " | ".join(parts) + ")"

            called = False
            for kind, index, value in rule.actions:
                if kind == "arg" and index in field_args:
                    raise ValueError("cannot replace an argument used by field() in the same rule")
                values = value if kind == "call" else (value,)
                if called and any(isinstance(v, Expr) and v.fields for v in values):
                    raise ValueError("field() must be read before calling a native function")
                called |= kind in ("call", "original")

            def render(value):
                code = literal(value)
                if isinstance(value, Expr):
                    for name in value.fields:
                        code = code.replace(f"VEP_FIELD_{name}__", field_code[name])
                return code
            if contract.startswith("void") and (
                any(e.uses_result for e in expressions)
                or any(k in ("result", "return") for k, _, _ in rule.actions)
            ):
                raise ValueError(contract + " has no return value; use skip() to suppress it")
            statements = ["call->return_early = 1;"] if rule.phase == "replace" else []
            for kind, index, value in rule.actions:
                if kind == "arg":
                    if index >= argc:
                        raise ValueError("argument exceeds " + contract)
                    statements.append(f"call->args[{index}] = {render(value)};")
                elif kind == "original":
                    statements.append("(void)vep->call_original(call);")
                elif kind == "call":
                    if index not in points:
                        raise ValueError("unknown function: " + index)
                    called_contract = points[index]["contract"]
                    if called_contract not in {
                        f"{kind}{count}" for kind in ("void", "word") for count in range(5)
                    }:
                        raise ValueError("unsupported contract: " + called_contract)
                    count = int(called_contract[-1])
                    if len(value) != count:
                        raise ValueError("wrong argument count for " + index)
                    local = f"arguments_{len(statements)}"
                    values = [render(v) for v in value] + ["0"] * (4 - count)
                    statements.append(f"const uintptr_t {local}[4] = {{" + ", ".join(values) + "};")
                    statements.append(
                        f"if (vep->call_named((const uint8_t *){json.dumps(index)}, {local}, &call->result)) {{ call->result = 0; call->return_early = 1; return; }}"
                    )
                elif kind == "result":
                    statements.append(f"call->result = {render(value)};")
                elif kind == "return":
                    statements += [
                        f"call->result = {render(value)};",
                        "call->return_early = 1;",
                        "return;",
                    ]
                else:
                    statements += ["call->return_early = 1;", "return;"]
            body = "\n    ".join(statements)
            if rule.condition is not None:
                condition = render(rule.condition)
                if not condition.startswith("("):
                    condition = "(" + condition + ")"
                body = f"if {condition} {{\n        {body}\n    }}"
            guards = "".join(f"if (!call->args[{index}]) return;\n    " for index in sorted(field_args))
            functions.append(
                f"static void hook_{i}(vep_call *call, void *data) {{\n    (void)data;\n    {guards}{body}\n}}"
            )
            phase = "before" if rule.phase == "replace" else rule.phase
            installs += [
                f"const vep_callbacks callbacks_{i} = {{ .{phase} = hook_{i}, .priority = {rule.priority} }};",
                f"rc = vep->attach_named(vep_owner, (const uint8_t *){json.dumps(point)}, &callbacks_{i}, &handle);",
            ]
        setup = []
        for line in installs:
            setup.append(line)
            if line.startswith("rc ="):
                setup.append("if (rc) return rc;")
        return (
            f"#define VEP_MODULE_ID {json.dumps(self.id)}\n"
            f"#define VEP_MODULE_STATUS_PATH {json.dumps(self.status_path)}\n"
            '#include "veposed_module.h"\n\n'
            + "\n\n".join(functions)
            + "\n\nstatic int32_t vep_module_setup(void) {\n    uint32_t handle;\n    int32_t rc;\n    "
            + "\n    ".join(setup)
            + "\n    return 0;\n}\n"
        )
