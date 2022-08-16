from pathlib import Path
from typing import List
from gcgen.api import snippet, Section, Scope, Json


gcgen_indent_by = {
    "py": "    ",
}


@snippet("sumfn")
def gen_sumfn(s: Section, scope: Scope, val: Json):
    s.emitln_r("def sum(a, b):")
    s.emitln("return a + b")


@snippet("something_else_middle")
def smth_else_middle(s: Section, scope: Scope, val: Json):
    s.emitln("a += 100")
    s.emitln("a += 1000")


def gcgen_parse_files() -> List[str]:
    return ["filea.py"]
