from gcgen.api import Emitter, Scope, Json, snippet, get_snippet
from typing import List


@snippet("hello")
def __hello(e: Emitter, s: Scope, val: Json):
    if val is None:
        e.emitln("hello stranger...")
    else:
        e.emitln(f"hello {val}!")


@snippet("print_files")
def s_bar(e: Emitter, s: Scope, val: Json):
    if not isinstance(val, list):
        raise RuntimeError("not a list")
    for f in val:
        e.emitln(f"printing file '{f}'...")


def gcgen_parse_files() -> List[str]:
    return ["example.txt"]
