from gcgen.api import Section, Scope, snippet, Json
from typing import List


gcgen_indent_by = {
    "py": "    ",
}


def gcgen_scope_extend(s: Scope):
    s["some-var"] = "<<some-outer-val>>"
    s["other-val"] = "<<other-outer-val>>"


@snippet("foo")
def s_foo(s: Section, scope: Scope, _: Json):
    s.emitln("foo from outer ctx!")
    s.emitln(f"""scope["some-var"]: {scope["some-var"]}""")
    s.emitln("/outer foo end")


@snippet("bar")
def name_does_not_matter(s: Section, _: Scope, __: Json):
    s.emitln("bar from outer ctx!")


def gcgen_parse_files() -> List[str]:
    return ["outerfile.txt"]
