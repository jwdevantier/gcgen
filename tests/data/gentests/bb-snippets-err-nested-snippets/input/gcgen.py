from gcgen.api import snippet, Emitter, Scope


@snippet("baz")
def s_baz(e: Emitter, scope: Scope):
    pass


def gcgen_parse_files():
    return ["testfile.txt"]
