from gcgen.api import Emitter, Scope, snippet
from typing import List


@snippet("foo")
def s_foo(e: Emitter, s: Scope):
    e.emitln("inner foo!")


def gcgen_parse_files() -> List[str]:
    return ["innerfile.txt"]
