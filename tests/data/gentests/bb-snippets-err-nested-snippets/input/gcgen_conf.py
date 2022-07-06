from gcgen.api import snippet, Emitter, Scope, Json


@snippet("baz")
def s_baz(e: Emitter, scope: Scope, val: Json):
    pass


def gcgen_parse_files():
    return ["testfile.txt"]
