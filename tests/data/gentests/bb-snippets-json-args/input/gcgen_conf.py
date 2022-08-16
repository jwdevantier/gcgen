from gcgen.api import Section, Scope, Json, snippet
from typing import List


@snippet("hello")
def __hello(s: Section, _: Scope, val: Json):
    if val is None:
        s.emitln("hello stranger...")
    else:
        s.emitln(f"hello {val}!")


@snippet("print_files")
def s_bar(s: Section, _: Scope, val: Json):
    if not isinstance(val, list):
        raise RuntimeError("not a list")
    for f in val:
        s.emitln(f"printing file '{f}'...")


def gcgen_parse_files() -> List[str]:
    return ["example.txt"]
