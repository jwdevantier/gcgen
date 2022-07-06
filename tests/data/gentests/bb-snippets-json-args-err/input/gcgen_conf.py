from gcgen.api import Emitter, Scope, Json, snippet, get_snippet
from typing import List


@snippet("hello")
def __hello(e: Emitter, s: Scope, val: Json):
    if val is None:
        e.emitln("hello stranger...")
    else:
        e.emitln(f"hello {val}!")


def gcgen_parse_files() -> List[str]:
    return ["example.txt"]
