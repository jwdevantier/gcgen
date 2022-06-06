from pathlib import Path
from os import replace as os_replace
from io import TextIOWrapper
from gcgen.log import get_logger, LogLevel


logger = get_logger(__name__)


class SnippetParseError(Exception):
    pass


class UnclosedSnippetError(SnippetParseError):
    def __init__(
        self, msg: str, file: Path, snippet: str, line_start: int, line_err: int
    ):
        self.file = file
        self.snippet = snippet
        self.line_start = line_start
        self.line_err = line_err
        self.err_msg = msg
        super().__init__(
            f"{file!s}, error in snippet {snippet!s}, line: {line_err}: unclosed snippet, {msg}"
        )


class NestedSnippetsError(UnclosedSnippetError):
    def __init__(self, file: Path, snippet: str, line_start: int, line_err: int):
        super().__init__(
            "found start of new snippet", file, snippet, line_start, line_err
        )


class ParserBase:
    def __init__(self, snippet_start: str, snippet_end: str):
        self.snippet_start = snippet_start
        self.snippet_end = snippet_end

    def on_snippet(
        self, snippet_name: str, snippet_prefix: str, src_path: Path, fh: TextIOWrapper
    ):
        pass

    def parse(self, fpath: Path, dpath: Path):
        snippet_start = self.snippet_start
        snippet_end = self.snippet_end

        if fpath == dpath:
            dst = open(Path(str(dpath) + ".gcgen.tmp"), mode="w")
        else:
            dst = open(dpath, mode="w")

        try:
            if fpath.is_symlink():
                return
            with open(fpath, "r", encoding="utf-8", errors="ignore") as src:
                prefix = snippet_name = ""  # only to satisfy type checker.
                lineno = 0
                while True:
                    cont = False
                    for line in src:
                        lineno += 1
                        dst.write(line)
                        ndx = line.find(snippet_start)
                        if ndx != -1:
                            cont = True
                            prefix = line[0:ndx]
                            snippet_name = line[ndx + len(snippet_start) :].strip()
                            break

                    if not cont:
                        # we exhausted the file line iterator without finding a new opening
                        # snippet, hence we stop here (no error)
                        break

                    s_end = f"{prefix}{snippet_end}"
                    snippet_prefix = " " * (len(prefix) - len(prefix.lstrip()))
                    logger.debug(f"snippet_name: {snippet_name}")
                    logger.debug(f"raw prefix {prefix!r} (len: {len(prefix)})")
                    logger.debug(
                        f"snippet prefix: {snippet_prefix!r} (len: {len(snippet_prefix)})"
                    )
                    snippet_line_start = lineno
                    cont = False

                    for line in src:
                        lineno += 1
                        if line.startswith(s_end):
                            # TODO: found end, now execute snippet
                            self.on_snippet(snippet_name, snippet_prefix, fpath, dst)
                            dst.write(line)  # retain the snippet end line
                            cont = True
                            break
                        elif line.find(snippet_start) != -1:
                            raise NestedSnippetsError(
                                fpath, snippet_name, snippet_line_start, lineno
                            )
                    if not cont:
                        # we exhausted the file line iterator without finding a corresponding
                        # snippet end, so we abort, this is an error
                        raise UnclosedSnippetError(
                            "reached end of file without finding snippet end",
                            fpath,
                            snippet_name,
                            snippet_line_start,
                            lineno,
                        )

            dst.close()
            os_replace(dst.name, str(fpath.absolute()))
            dst = None
        finally:
            if dst:
                Path(dst.name).unlink()
