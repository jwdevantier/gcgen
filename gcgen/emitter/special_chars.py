from enum import Enum

class CtrlChr(Enum):
    Newline = "<NL>"
    Freshline = "<FL>"
    Indent = "<INDENT>"
    Dedent = "<DEDENT>"


class Padding:
    __slots__ = "numlines"

    def __init__(self, numlines: int):
        self.numlines: int = numlines

    def __str__(self):
        return f"<PADDING({self.numlines})>"

    def __repr__(self):
        return f"<PADDING({self.numlines})>"

    def __eq__(self, other):
        return isinstance(other, Padding) and other.numlines == self.numlines


__all__ = [
    "Padding",
    "CtrlChr",
]
