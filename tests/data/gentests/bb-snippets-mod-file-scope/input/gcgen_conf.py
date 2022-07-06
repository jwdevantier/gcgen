from pathlib import Path
from typing import List
from gcgen.api import snippet, Emitter, Scope


def gcgen_scope_extend(scope: Scope):
    scope["name"] = "John Doe"


@snippet("modify-scope")
def _env(e: Emitter, s: Scope):
    s["name"] = "Jane Doe"


@snippet("greet")
def _greet(e: Emitter, s: Scope):
    e.emitln(f"""Hello, {s["name"]}!""")


def gcgen_parse_files() -> List[str]:
    return ["greetings.txt"]
