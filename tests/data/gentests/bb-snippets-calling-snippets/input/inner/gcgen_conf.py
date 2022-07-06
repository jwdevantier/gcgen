from gcgen.api import Emitter, Scope, snippet, Json
from typing import List


@snippet("foo")
def s_foo(e: Emitter, s: Scope, val: Json):
    e.emitln("inner foo!")


def gcgen_parse_files() -> List[str]:
    return ["innerfile.txt"]
