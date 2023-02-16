from typing import List, Union, NewType, Iterator
from gcgen.emitter.special_chars import CtrlChr, Padding


class SectionError(Exception):
    pass


class SectionDedentError(SectionError):
    msg = "dedent called too many times - trying to dedent out of minimum indentation"


SectionElem = Union[str, "Section", CtrlChr, Padding]
SectionBuf = NewType("SectionBuf", List[SectionElem])


class Section:
    """A class for storing (buffered) text/code output.

    A section is an abstraction of text writing which provides 2 capabilities:
    1. It provides a way to control indentation
    2. It provides a way to nest Section(s) within a Section

    (1) The indentation abstraction facilitates composition and reuse of
    generator code, because each helper function only needs to call `indent()`/
    `dedent()` to adjust line indentation, rather than embedding a fixed,
    absolute amount of indentation into the strings of each line written out.

    (2) By allowing a section to contain other sections, it becomes possible to
    define 'placeholders' which can be filled out at a later time. Effectively
    making it possible to define the final output out of order, e.g. adding
    more variable definitions to the start of a function as it becomes
    necessary.
    """
    __slots__ = "_buf", "_indent_level"

    def __init__(self) -> None:
        self._buf: SectionBuf = SectionBuf([])
        # to ensure indent/dedent is balanced within a section
        self._indent_level = 0

    def newline(self) -> "Section":
        """add a newline."""
        self._buf.append(CtrlChr.Newline)
        return self

    def nl(self) -> "Section":
        return self.newline()

    def freshline(self) -> "Section":
        """emit newline iff. not currently at the beginning of a line."""
        if self._buf and self._buf[-1] in (CtrlChr.Freshline, CtrlChr.Newline):
            return self
        self._buf.append(CtrlChr.Freshline)
        return self

    def fl(self) -> "Section":
        """emit newline iff. not currently at the beginning of a line."""
        return self.freshline()

    def add_section(self, s: "Section") -> "Section":
        """Add section to be filled in when desired.

        Adds provided section object such that its contents will be preceded by
        the current contents of this section and superceded by any subsequently
        added contents to this section.
        """
        self.freshline()
        self._buf.append(s)
        return self

    def indent(self) -> "Section":
        """Indent subsequent lines.

        Causes all future lines to be indented one level more.

        Note: this function will cause a newline if the current line has any
        contents already written to it (using `emit`).
        """
        self._buf.append(CtrlChr.Indent)
        self._indent_level += 1
        return self

    def dedent(self) -> "Section":
        """Dedent lines by one.

        Causes all future lines to be indented one level less.

        Note: this function will cause a newline if the current line has any
        contents already written to it (using `emit`).
        """
        self._buf.append(CtrlChr.Dedent)
        self._indent_level -= 1
        if self._indent_level < 0:
            raise SectionDedentError
        return self

    def ensure_padding_lines(self, nlines: int) -> "Section":
        """Ensure (at least) `n` empty lines of padding between two sections

        NOTE: if this is the top-level buffer and it is empty, this becomes a NO-OP
        """
        self._buf.append(Padding(nlines))
        return self

    def emit(self, *elems: str) -> "Section":
        """Emit one or more string elements."""
        bappend = self._buf.append
        for elem in elems:
            if not isinstance(elem, str):
                raise TypeError(f"got {type(elem)}, expected str (val: {repr(elem)})")
            bappend(elem.replace("\n", "\\n"))
        return self

    def emitln(self, *elems: str) -> "Section":
        """Emit one or more string elements followed by a newline."""
        self.emit(*elems)
        self._buf.append(CtrlChr.Newline)
        return self

    def emitln_r(self, *elems: str) -> "Section":
        """Write line, then indent.

        NOTE: deprecated, use `sec.emitln(...).indent()` instead
        """
        self.emitln(*elems)
        self.indent()
        return self

    def emitln_l(self, *elems: str) -> "Section":
        """Emit line, then dedent.

        NOTE: deprecated, use `sec.emitln(...).dedent()` instead.
        """
        self.emitln(*elems)
        self.dedent()
        return self

    def iterator(self) -> Iterator[SectionElem]:
        for elem in self._buf:
            if isinstance(elem, Section):
                yield from elem.iterator()
            else:
                yield elem

    def __repr__(self) -> str:
        return "SECTION(" + ", ".join(repr(elem) for elem in self._buf) + ")"

    def __str__(self) -> str:
        return "".join(str(elem) for elem in self._buf)
