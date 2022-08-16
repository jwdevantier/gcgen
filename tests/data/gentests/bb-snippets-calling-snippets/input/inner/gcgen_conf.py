from gcgen.api import Section, Scope, snippet, Json
from typing import List


@snippet("foo")
def s_foo(s: Section, _: Scope, __: Json):
    s.emitln("inner foo!")


def gcgen_parse_files() -> List[str]:
    return ["innerfile.txt"]
