from gcgen.api import snippet, Section, Scope, Json


@snippet("baz")
def s_baz(_: Section, __: Scope, ___: Json):
    pass


def gcgen_parse_files():
    return ["testfile.txt"]
