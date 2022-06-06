from gcgen.api import Emitter, Scope, snippet, get_snippet
from typing import List


@snippet("foo")
def s_foo(e: Emitter, s: Scope):
    e.emitln("outer foo!")


@snippet("bar")
def s_bar(e: Emitter, s: Scope):
    e.emitln("outer bar!")
    # call snippet directly (so it is hard-coded and cannot be overridden)
    s_foo(e, s)


@snippet("baz")
def s_baz(e: Emitter, s: Scope):
    e.emitln("outer baz!")
    # find snippet via scope (so it can be overridden)
    get_snippet(s, "foo")(e, s)


def gcgen_parse_files() -> List[str]:
    return ["outerfile.txt"]
