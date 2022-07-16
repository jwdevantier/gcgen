from pathlib import Path
from os import replace as os_replace
from io import TextIOWrapper
from re import compile as re_compile
from gcgen.log import get_logger, LogLevel
from gcgen.excbase import GcgenError
from gcgen.api.types import Json
import json
from json.decoder import JSONDecodeError


logger = get_logger(__name__)

rgx_ws_prefix = re_compile(r"^(?P<prefix>\s*).*$")


class SnippetParseError(GcgenError):
    pass


class UnclosedSnippetError(SnippetParseError):
    def __init__(self, file: Path, snippet: str, line_start: int, line_err: int):
        self.file = file
        self.snippet = snippet
        self.line_start = line_start
        self.line_err = line_err
        super().__init__(
            f"{file!s}, error in snippet {snippet!s}, line: {line_err}: unclosed snippet"
        )

    def printerr(self) -> None:
        print("Unclosed Snippet Error:")
        print("")
        print("Reached end of file without finding a corresponding snippet close")
        print("")
        print("Details:")
        print(f"  File: {self.file}")
        print(f"  Snippet: {self.snippet!r}")
        print(f"  Snippet Start Line: {self.line_start}")


class NestedSnippetsError(SnippetParseError):
    def __init__(self, file: Path, snippet: str, line_start: int, line_err: int):
        self.file = file
        self.snippet = snippet
        self.line_start = line_start
        self.line_err = line_err

        super().__init__(
            "found start of new snippet while processing snippet",
            file,
            snippet,
            line_start,
            line_err,
        )

    def printerr(self) -> None:
        print("Nested Snippets Error:")
        print("")
        print(
            "Encountered line marking start of new snippet before current snippet end."
        )
        print("")
        print("Details:")
        print(f"  File: {self.file}")
        print(f"  Snippet: {self.snippet!r}")
        print(f"  Snippet start line: {self.line_start}")
        print(f"  Error line: {self.line_err}")


class SnippetJsonValueError(SnippetParseError):
    def __init__(
        self,
        file: Path,
        snippet: str,
        value: str,
        json_err: JSONDecodeError,
        line_start: int,
    ):
        self.file = file
        self.snippet = snippet
        self.line_start = line_start
        self.value = value
        self.json_err = json_err

        super().__init__(
            "error while parsing JSON value given to snippet",
            file,
            snippet,
            line_start,
            line_start,
        )

    def printerr(self) -> None:
        print("Snippet argument parse error:")
        print("")
        print("Error parsing argument as JSON value")
        print("")
        print("Details:")
        print(f"  File: {self.file}")
        print(f"  Snippet: {self.snippet!r}")
        print(f"  Snippet start line: {self.line_start}")
        print(f"  Raw value: {self.value!r}")
        print(f"  JSON Decode error: {str(self.json_err)}")


class ParserBase:
    def __init__(self, snippet_start: str, snippet_end: str):
        self.snippet_start = snippet_start
        self.snippet_end = snippet_end

    def on_snippet(
        self,
        snippet_prefix: str,
        snippet_name: str,
        snippet_arg: Json,
        src_path: Path,
        fh: TextIOWrapper,
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
                            parts = (
                                line[ndx + len(snippet_start) :].strip().split(" ", 1)
                            )
                            if len(parts) == 1:
                                snippet_name = parts[0]
                                snippet_arg = None
                            else:  # 2 parts, one possible JSON value
                                snippet_name = parts[0]
                                snippet_arg = parts[1].strip()
                                if snippet_arg in ("", "null"):
                                    snippet_arg = None
                                else:
                                    try:
                                        snippet_arg_raw = snippet_arg
                                        snippet_arg = json.loads(snippet_arg)
                                    except JSONDecodeError as e:
                                        raise SnippetJsonValueError(
                                            fpath,
                                            snippet_name,
                                            snippet_arg_raw,
                                            e,
                                            lineno,
                                        ) from e
                            break

                    if not cont:
                        # we exhausted the file line iterator without finding a new opening
                        # snippet, hence we stop here (no error)
                        break

                    s_end = f"{prefix}{snippet_end}"
                    prefix_match = rgx_ws_prefix.match(prefix)
                    assert (
                        prefix_match is not None
                    ), "regex failed to extract line whitespace prefix"
                    snippet_prefix = prefix_match.group(1)
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
                            self.on_snippet(
                                snippet_prefix, snippet_name, snippet_arg, fpath, dst
                            )
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
