from gcgen.api import Section, Scope, snippet, Json
from typing import List


gcgen_indent_by = {
    "py": "    ",
}


def gcgen_scope_extend(s: Scope):
    s["some-var"] = "<<some-inner-val>>"


@snippet("bar")
def name_does_not_matter(s: Section, scope: Scope, _: Json):
    s.emitln("bar from inner ctx!")
    s.emitln(f"""scope["other-val"]: {scope["other-val"]}""")


def gcgen_parse_files() -> List[str]:
    return ["innerfile.txt"]
