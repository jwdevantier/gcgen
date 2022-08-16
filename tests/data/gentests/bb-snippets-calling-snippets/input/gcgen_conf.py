from gcgen.api import Section, Scope, snippet, get_snippet, Json
from typing import List


@snippet("foo")
def s_foo(s: Section, _: Scope, __: Json):
    s.emitln("outer foo!")


@snippet("bar")
def s_bar(s: Section, scope: Scope, _: Json):
    s.emitln("outer bar!")
    # call snippet directly (so it is hard-coded and cannot be overridden)
    s_foo(s, scope, None)


@snippet("baz")
def s_baz(s: Section, scope: Scope, _: Json):
    s.emitln("outer baz!")
    # find snippet via scope (so it can be overridden)
    get_snippet(scope, "foo")(s, scope, None)


def gcgen_parse_files() -> List[str]:
    return ["outerfile.txt"]
