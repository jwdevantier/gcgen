from gcgen.api import Emitter, Scope, snippet, Json
from typing import List


gcgen_indent_by = {
    "py": "    ",
}


def gcgen_scope_extend(s: Scope):
    s["some-var"] = "<<some-inner-val>>"


@snippet("bar")
def name_does_not_matter(e: Emitter, s: Scope, val: Json):
    e.emitln("bar from inner ctx!")
    e.emitln(f"""scope["other-val"]: {s["other-val"]}""")


def gcgen_parse_files() -> List[str]:
    return ["innerfile.txt"]
