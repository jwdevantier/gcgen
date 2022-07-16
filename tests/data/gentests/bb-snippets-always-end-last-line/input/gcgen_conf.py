from gcgen.api import snippet, Emitter, Scope, Json


@snippet("foo")
def s_foo(e: Emitter, scope: Scope, val: Json):
    e.emit("i end in the middle of a line...")


@snippet("bar")
def s_bar(e: Emitter, scope: Scope, val: Json):
    e.emitln("I end on a fresh (new) line..")


def gcgen_parse_files():
    return ["testfile.txt"]
