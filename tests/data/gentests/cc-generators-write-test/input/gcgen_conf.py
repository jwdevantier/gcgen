from gcgen.api import generator, Scope
from gcgen.api.write_file import write_file


@generator
def generate_this(s: Scope):
    with write_file("foo.txt") as e:
        e.emitln("Hello, World")
        e.emitln("Regards, Foo")

    with write_file("bar.txt") as e:
        e.emitln("Hello, World")
        e.emitln("Regards, Bar")
