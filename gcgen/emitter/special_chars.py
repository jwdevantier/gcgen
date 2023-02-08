class SpecialChar:
    ...

class Newline(SpecialChar):
    def __init__(self):
        ...

    def __str__(self):
        return "<NL>"

    def __repr__(self):
        return "<NL>"

    def __eq__(self, other):
        return isinstance(other, Newline)


class FreshLine(SpecialChar):
    def __init__(self):
        ...

    def __str__(self):
        return "<FL>"

    def __repr__(self):
        return "<FL>"

    def __eq__(self, other):
        return isinstance(other, FreshLine)


class Indent(SpecialChar):
    def __init__(self):
        ...

    def __str__(self):
        return "<INDENT>"

    def __repr__(self):
        return "<INDENT>"

    def __eq__(self, other):
        return isinstance(other, Indent)


class Dedent(SpecialChar):
    def __init__(self):
        ...

    def __str__(self):
        return "<DEDENT>"

    def __repr__(self):
        return "<DEDENT>"

    def __eq__(self, other):
        return isinstance(other, Dedent)


class Padding(SpecialChar):
    def __init__(self, numlines: int):
        self.__numlines = numlines

    @property
    def numlines(self):
        return self.__numlines

    def __str__(self):
        return f"<PADDING({self.__numlines})>"

    def __repr__(self):
        return f"<PADDING({self.__numlines})>"

    def __eq__(self, other):
        return isinstance(other, Padding) and other.__numlines == self.__numlines


NL = Newline()
FL = FreshLine()
I = Indent()
D = Dedent()

__all__ = [
    "SpecialChar",
    "Newline",
    "FreshLine",
    "Indent",
    "Dedent",
    "Padding",
    "NL",
    "FL",
    "I",
    "D",
]
