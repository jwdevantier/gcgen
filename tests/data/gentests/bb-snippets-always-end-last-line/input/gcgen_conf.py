from gcgen.api import snippet, Section, Scope, Json


@snippet("foo")
def s_foo(s: Section, scope: Scope, val: Json):
    s.emit("i end in the middle of a line...")


@snippet("bar")
def s_bar(s: Section, scope: Scope, val: Json):
    s.emitln("I end on a fresh (new) line..")


def gcgen_parse_files():
    return ["testfile.txt"]
