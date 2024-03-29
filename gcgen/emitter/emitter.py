from typing import Protocol, TYPE_CHECKING
from gcgen.emitter.special_chars import Padding, CtrlChr

if TYPE_CHECKING:
    from gcgen.emitter.section import Section


class Writer(Protocol):
    def write(self, e: str):
        ...


class Emitter:
    __slots__ = "_prefix", "_indent_by"

    def __init__(self, *, prefix: str, indent_by: str = " "):
        self._prefix = prefix
        self._indent_by = indent_by

    def emit(self, s: "Section", w: Writer) -> None:
        fresh: bool = True
        padding: int = 0
        nls: int = 0
        indent_by: str = self._indent_by
        prefix: str = self._prefix
        level: int = 0

        for ndx, elem in enumerate(s.iterator()):
            if isinstance(elem, Padding):
                if ndx == 0 or elem.numlines < padding:
                    continue
                fresh = True
                padding = elem.numlines
                continue
            elif elem == CtrlChr.Newline:
                nls += 1
                fresh = True
                continue
            elif elem == CtrlChr.Freshline:
                if not fresh:
                    nls += 1
                    fresh = True
                continue
            elif elem == CtrlChr.Indent:
                level += 1
                if not fresh:
                    nls = 1
                    fresh = True
                continue
            elif elem == CtrlChr.Dedent:
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
