from gcgen.api import Emitter, Scope, snippet
from typing import List


gcgen_indent_by = {
    "py": "    ",
}


def gcgen_scope_extend(s: Scope):
    s["some-var"] = "<<some-outer-val>>"
    s["other-val"] = "<<other-outer-val>>"


@snippet("foo")
def s_foo(e: Emitter, s: Scope):
    e.emitln("foo from outer ctx!")
    e.emitln(f"""scope["some-var"]: {s["some-var"]}""")
    e.emitln("/outer foo end")


@snippet("bar")
def name_does_not_matter(e: Emitter, s: Scope):
    e.emitln("bar from outer ctx!")


def gcgen_parse_files() -> List[str]:
    return ["outerfile.txt"]
