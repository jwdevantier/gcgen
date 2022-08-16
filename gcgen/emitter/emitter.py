from typing import Protocol, TYPE_CHECKING
from gcgen.emitter.special_chars import Padding, FreshLine, Newline, Indent, Dedent

if TYPE_CHECKING:
    from gcgen.emitter.section import Section


class Writer(Protocol):
    def write(self, e: str):
        ...


class Emitter:
    def __init__(self, *, prefix: str, indent_by: str = " "):
        self._prefix = prefix
        self._indent_by = indent_by

    def emit(self, s: "Section", w: Writer) -> None:
        fresh = True
        padding = 0
        nls = 0
        indent_by = self._indent_by
        prefix = self._prefix
        level = 0

        for ndx, elem in enumerate(s.iterator()):
            if isinstance(elem, Padding):
                if ndx == 0 or elem.numlines < padding:
                    continue
                fresh = True
                padding = elem.numlines
                continue
            elif isinstance(elem, Newline):
                nls += 1
                fresh = True
                continue
            elif isinstance(elem, FreshLine):
                if not fresh:
                    nls += 1
                continue
            elif isinstance(elem, Indent):
                level += 1
                if not fresh:
                    nls = 1
                continue
            elif isinstance(elem, Dedent):
                level -= 1
                if not fresh:
                    nls = 1
                continue
            elif isinstance(elem, str):
                if padding:
                    w.write("\n" * max(nls, padding + 1))
                    padding = nls = 0
                    fresh = True
                elif nls:
                    w.write("\n" * nls)
                    padding = nls = 0
                    fresh = True

                if fresh:
                    fresh = False
                    w.write(prefix)
                    w.write(indent_by * level)
                w.write(elem)

        if nls:
            w.write("\n" * nls)
