from gcgen.api import Emitter, Scope, Json, snippet


# Snippets are annotated `@snippet("<name>")`
@snippet("common_math_funcs")
def gen_arithmetic_ops(e: Emitter, s: Scope, val: Json):
    first = True
    for lbl, op in val:
        if not first:
            e.newline()
            e.newline()
        else:
            first = False
        e.emitln(f"def {lbl}(x, y):")
        e.indent()
        e.emitln(f"return x {op} y")
        e.dedent()


def gcgen_parse_files():
    # tell gcgen which files to process for snippets
    # inside of this directory.
    return ["my_mathlib.py"]
