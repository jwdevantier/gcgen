from gcgen.api import generator, Scope


@generator
def generate_this(s: Scope):
    raise RuntimeError("generate this")
