from gcgen.api import Emitter, Scope, snippet


# Snippets are annotated `@snippet("<name>")`
@snippet("common_math_funcs")
def gen_arithmetic_ops(e: Emitter, s: Scope):
    ops = {
        "add": "+",
        "sub": "-",
        "div": "/",
        "mul": "*",
    }
    first = True
    for name, op in ops.items():
        if not first:
            e.newline()
            e.newline()
        else:
            first = False
        e.emitln(f"def {name}(x, y):")
        e.indent()
        e.emitln(f"return x {op} y")
        e.dedent()


def gcgen_parse_files():
    # tell gcgen which files to process for snippets
    # inside of this directory.
    return ["my_mathlib.py"]
