from typing import List
from gcgen.api import snippet, Section, Scope, Json


def gcgen_scope_extend(scope: Scope):
    scope["name"] = "John Doe"


@snippet("modify-scope")
def _env(_: Section, scope: Scope, __: Json):
    scope["name"] = "Jane Doe"


@snippet("greet")
def _greet(s: Section, scope: Scope, _: Json):
    s.emitln(f"""Hello, {scope["name"]}!""")


def gcgen_parse_files() -> List[str]:
    return ["greetings.txt"]
