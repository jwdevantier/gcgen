from gcgen.api import Section, Scope, Json, snippet


# Snippets are annotated `@snippet("<name>")`
@snippet("common_math_funcs")
def gen_arithmetic_ops(sec: Section, s: Scope, val: Json):
    first = True
    for lbl, op in val:
        if not first:
            sec.newline()
            sec.newline()
        else:
            first = False
        sec.emitln(f"def {lbl}(x, y):")
        sec.indent()
        sec.emitln(f"return x {op} y")
        sec.dedent()


def gcgen_parse_files():
    # tell gcgen which files to process for snippets
    # inside of this directory.
    return ["my_mathlib.py"]
