from gcgen.emitter import Emitter, EmitterDedentError
from pathlib import Path
from contextlib import contextmanager
from io import StringIO
import pytest


RESULTS_ROOT = Path(__file__).parent / "data" / "emitter-results"


@contextmanager
def write_file(expected, prefix="", indent_by=" "):
    expected_contents = (RESULTS_ROOT / expected).read_text()
    e = Emitter(prefix=prefix, indent_by=indent_by)
    yield e
    buf = StringIO()
    for elem in e.lines():
        buf.write(elem)
    assert expected_contents == buf.getvalue()


def test_emit_emitln():
    with write_file("aa-emit-emitln-emit-emit.txt") as e:
        e.emit("one")
        e.emitln("two")
        e.emit("three")
        e.emit("four")


def test_emitln_emitln_emitln():
    with write_file("aa-emitln-emitln-emitln.txt") as e:
        e.emitln("one")
        e.emitln("two")
        e.emitln("three")


def test_emitln_indent_emitln_dedent_emitln():
    with write_file("aa-emitln-indent-emitln-dedent-emitln.txt", indent_by="   ") as e:
        e.emitln("one")
        e.indent()
        e.emitln("two")
        e.dedent()
        e.emitln("three")


def test_emitln_indent_emitln_dedent_emitln_2():
    with write_file("aa-emitln-indent-emitln-dedent-emitln.txt", indent_by="   ") as e:
        e.emitln_r("one")
        e.emitln_l("two")
        e.emitln("three")


def test_add_section_empty():
    # NOTE: if a section has no content, it won't generate an empty line
    # (if is essentially not affecting the output).
    with write_file("bb-sections-empty.txt") as e:
        e.emitln("one")
        e.indent()
        s1 = e.add_section()
        e.dedent()
        e.emitln("two")
        e.indent()
        s2 = e.add_section()
        e.dedent()
        e.emitln("three")


def test_add_section_contents_flat():
    with write_file("bb-sections-contents-flat.txt") as e:
        e.emitln("one")
        s1 = e.add_section()
        e.emitln("two")
        s2 = e.add_section()
        e.emitln("three")

        s2.emitln("s2 one")
        s1.emitln("s1 one")
        s1.emitln("s1 two")


def test_add_section_contents_indented():
    with write_file("bb-sections-contents-indented.txt") as e:
        e.emitln("one")
        e.indent()
        s1 = e.add_section()
        e.dedent()
        e.emitln("two")
        e.indent()
        s2 = e.add_section()
        e.dedent()
        e.emitln("three")

        s2.emitln("s2 one")
        s1.emitln("s1 one")
        s1.emitln("s1 two")


def test_dedent_guard():
    e = Emitter(prefix="   ", indent_by="   ")
    e.indent()
    e.dedent()
    e.indent()
    e.indent()
    e.dedent()
    e.dedent()
    with pytest.raises(EmitterDedentError):
        e.dedent()
