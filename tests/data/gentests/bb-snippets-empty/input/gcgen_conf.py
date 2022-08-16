from typing import List
from gcgen.api import snippet, Section, Scope, Json


@snippet("foo")
def _foo(_: Section, __: Scope, ___: Json):
    pass


def gcgen_parse_files() -> List[str]:
    return ["test.txt"]