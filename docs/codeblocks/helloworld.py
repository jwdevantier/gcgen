from gcgen.api import Section, Scope, Json, snippet


@snippet("test")
def gen_arithmetic_ops(sec: Section, s: Scope, val: Json):
    ops = {
        "add": "+",
        "sub": "-",
        "div": "/",
        "mul": "*",
    }
    for name, op in ops.items():
        sec.emitln(f"def {name}(x, y):")
        sec.indent()
        sec.emitln(f"return x {op} y")
        sec.dedent()
        sec.newline()
        sec.newline()


def gcgen_parse_files():
    return ["example.py"]
