from gcgen.emitter import Section, Emitter, SectionDedentError
from gcgen.emitter.special_chars import Padding
from pathlib import Path
from contextlib import contextmanager
from io import StringIO
import pytest


RESULTS_ROOT = Path(__file__).parent / "data" / "emitter-results"


@contextmanager
def write_file(expected, prefix="", indent_by=" "):
    expected_contents = (RESULTS_ROOT / expected).read_text()
    e = Emitter(prefix=prefix, indent_by=indent_by)
    s = Section()
    yield s
    buf = StringIO()
    e.emit(s, buf)
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


def test_emit_indent_freshline_emit():
    """found a bug where this sequence caused an unwanted additional newline"""
    with write_file("aa-emit-indent-freshline-emitln.txt", indent_by="  ") as e:
        e.emit("foo {")
        e.indent()
        e.freshline()
        e.emitln("hello();")
        print(repr(e._buf))


def test_add_section_empty():
    # NOTE: if a section has no content, it won't generate an empty line
    # (if is essentially not affecting the output).
    with write_file("bb-sections-empty.txt") as e:
        e.emitln("one")
        e.indent()
        s1 = Section()
        e.add_section(s1)
        e.dedent()
        e.emitln("two")
        e.indent()
        s2 = Section()
        e.add_section(s2)
        e.dedent()
        e.emitln("three")


def test_add_section_contents_flat():
    with write_file("bb-sections-contents-flat.txt") as e:
        e.emitln("one")
        s1 = Section()
        e.add_section(s1)
        e.emitln("two")
        s2 = Section()
        e.add_section(s2)
        e.emitln("three")

        s2.emitln("s2 one")
        s1.emitln("s1 one")
        s1.emitln("s1 two")


def test_add_section_contents_indented():
    with write_file("bb-sections-contents-indented.txt") as e:
        e.emitln("one")
        e.indent()
        s1 = Section()
        e.add_section(s1)
        e.dedent()
        e.emitln("two")
        e.indent()
        s2 = Section()
        e.add_section(s2)
        e.dedent()
        e.emitln("three")

        s2.emitln("s2 one")
        s1.emitln("s1 one")
        s1.emitln("s1 two")


def test_dedent_guard():
    s = Section()
    s.indent()
    s.dedent()
    s.indent()
    s.indent()
    s.dedent()
    s.dedent()
    with pytest.raises(SectionDedentError):
        s.dedent()


@pytest.mark.parametrize("n", [0, 1, 2, 3, 4])
def test_padding_empty_is_noop(n):
    """
    When calling with an empty buffer, do not add any newlines
    """
    s = Section()
    assert s._buf == []
    s.ensure_padding_lines(n)
    assert s._buf[-1] == Padding(n)
    h = StringIO()
    e = Emitter(prefix="", indent_by="")
    e.emit(s, h)
    assert h.getvalue() == ""


@pytest.mark.parametrize("n", [0, 1, 2, 3, 4])
def test_padding_leading(n):
    """
    When padding is leading, i.e. nothing comes before - ignore it
    """
    s = Section()
    assert s._buf == []
    s.ensure_padding_lines(n)
    s.emitln("hello, world")
    expected = "hello, world\n"
    e = Emitter(prefix="", indent_by="")
    io = StringIO()
    e.emit(s, io)
    assert io.getvalue() == expected


@pytest.mark.parametrize("n", [0, 1, 2, 3, 4])
def test_padding_trailing(n):
    """
    When padding is trailing, i.e. nothing follows after - ignore it
    """
    s = Section()
    assert s._buf == []
    s.emitln("before line")
    s.ensure_padding_lines(n)
    expected = "before line\n"
    e = Emitter(prefix="", indent_by="")
    io = StringIO()
    e.emit(s, io)
    assert io.getvalue() == expected


@pytest.mark.parametrize("n", [0, 1, 2, 3, 4])
def test_padding_between_elems(n):
    s = Section()
    assert s._buf == []
    s.emitln("before line")
    s.ensure_padding_lines(n)
    s.emitln("after line")
    expected = "before line\n"
    if n:
        expected += "\n" * n
    expected += "after line\n"
    e = Emitter(prefix="", indent_by="")
    io = StringIO()
    e.emit(s, io)
    assert io.getvalue() == expected
