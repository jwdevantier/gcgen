from pathlib import Path
from typing import List
from gcgen.api import snippet, Emitter, Scope


gcgen_indent_by = {
    "py": "    ",
}


@snippet("sumfn")
def gen_sumfn(e: Emitter, s: Scope):
    e.emitln_r("def sum(a, b):")
    e.emitln("return a + b")


@snippet("something_else_middle")
def smth_else_middle(e: Emitter, s: Scope):
    e.emitln("a += 100")
    e.emitln("a += 1000")


def gcgen_parse_files() -> List[str]:
    return ["filea.py"]
