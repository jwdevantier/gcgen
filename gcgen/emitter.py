from typing import List, Union, NewType, Iterator


EmitterBuf = NewType("EmitterBuf", List[Union[str, "Emitter"]])


class EmitterError(Exception):
    pass


class EmitterDedentError(Exception):
    msg = "dedent called too many times - trying to dedent out of minimum indentation"


class Emitter:
    """Helper to emit text and control indentation.

    Args:
        prefix: base prefix of each line, this will correspond to the level
            of indentation of the snippet start line or the parent emitter.
        indent_by: the sequence of characters to use for each level of
            indentation. E.g. could be 4 spaces for Python files or one
            tab character for Go files.
    """

    def __init__(self, prefix: str, indent_by: str = " "):
        self._buf: EmitterBuf = EmitterBuf([])
        self._beginning_of_line = True
        self._indent_by = indent_by
        self._indent_level = 0
        self._prefix = prefix
        pass

    def __indent_if_necessary(self) -> None:
        """indent line iff. currently at the beginning of a new line"""
        if not self._beginning_of_line:
            return
        self._buf.append(self._prefix)
        self._buf.append(self._indent_by * self._indent_level)
        self._beginning_of_line = False

    def newline(self) -> None:
        """add a newline"""
        self._buf.append("\n")
        self._beginning_of_line = True

    def freshline(self) -> None:
        """emit newline iff not currently at the beginning of a new line"""
        if self._beginning_of_line:
            return
        self.newline()

    def add_section(self) -> "Emitter":
        """Add section to be filled in later.

        Returns a new emitter object, whose contents will form the part
        of the final output between the prior line of this emitter
        (if any) and any subsequently added lines.

        Note: this function will cause a newline if the current line has any
        contents already written to it (using `emit`).

        Returns:
            A new emitter object whose contents will be injected into the
            final output at this point
        """
        """add section to be filled in later"""
        self.freshline()
        child = Emitter(
            indent_by=self._indent_by,
            prefix=f"""{self._prefix}{self._indent_by * self._indent_level}""",
        )
        self._buf.append(child)
        return child

    def indent(self) -> None:
        """Indent subsequent lines.

        Causes all future lines to be indented one level more.

        Note: this function will cause a newline if the current line has any
        contents already written to it (using `emit`).
        """
        self.freshline()
        self._indent_level += 1

    def dedent(self) -> None:
        """Dedent lines by one.

        Causes all future lines to be indented one level less.

        Note: this function will cause a newline if the current line has any
        contents already written to it (using `emit`).
        """
        self.freshline()
        self._indent_level -= 1
        if self._indent_level < 0:
            raise EmitterDedentError

    def emit(self, *s: str) -> None:
        """emit one or more strings to the output.

        Emit one or more strings. If multiple strings are provided, they
        will be concatenated without any space or separation.

        *Note*: in most cases, using `emitln` with an f-string is a better
        idea.

        Args:
            *s: one or more strings, which will be concatenated.
        """
        self.__indent_if_necessary()
        res = "".join(s).replace("\n", "\\n")
        if res == "":
            return
        self._buf.append(res)

    def emitln_r(self, *s: str) -> None:
        """Emit line, then indent."""
        self.emitln(*s)
        self.indent()

    def emitln_l(self, *s: str) -> None:
        """Emit line, then dedent."""
        self.emitln(*s)
        self.dedent()

    def emitln(self, *s: str) -> None:
        """Emit a new line to the output.

        Writes a full line of output, taking care to properly indent the line
        as defined by the `indent_by` attribute and current level of
        indentation.

        Args:
            *s: one or more strings, each becoming a separate line of output.
        """
        self.__indent_if_necessary()
        buf_append = self._buf.append
        buf_append(s[0].replace("\n", "\\n"))
        for s in s[1:]:
            self.newline()
            self.__indent_if_necessary()
            buf_append(s.replace("\n", "\\n"))
        self.newline()

    def __str__(self) -> str:
        """Compile buffer of lines into a string."""
        return "".join(str(elem) for elem in self._buf)

    def lines(self) -> Iterator[str]:
        """Return iterator of each element in buffer."""
        for elem in self._buf:
            yield str(elem)

    def ensure_newlines(self, n: int):
        """Ensure (at least) `n` empty lines."""
        # if empty, n newlines suffice
        # if some line BEFORE, then n+1 newlines needed
        buf_end = self._buf[-(n + 1):]
        buf_end.reverse()
        num_newlines = 0
        for e in buf_end:
            if e != "\n":
                n += 1
                break
            num_newlines += 1
        self._buf.extend("\n" for _ in range(0, n - num_newlines))
