from gcgen.api import Emitter, Scope, snippet


@snippet("test")
def gen_arithmetic_ops(e: Emitter, s: Scope):
    ops = {
        "add": "+",
        "sub": "-",
        "div": "/",
        "mul": "*",
    }
    for name, op in ops.items():
        e.emitln(f"def {name}(x, y):")
        e.indent()
        e.emitln(f"return x {op} y")
        e.dedent()
        e.newline()
        e.newline()


def gcgen_parse_files():
    return ["example.py"]
