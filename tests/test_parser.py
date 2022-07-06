from gcgen import snippetparser
from pathlib import Path
from io import TextIOWrapper
from tempfile import NamedTemporaryFile
from dataclasses import dataclass
from typing import Optional
from contextlib import contextmanager

# one way to test
# inherit from parser base, impl `on_snippet`
# seed w contents from file/string/similar
# compare to get expected outputs.


@contextmanager
def tmpfile_of_str(s):
    tf = NamedTemporaryFile(mode="w+t", delete=False)
    fpath = Path(tf.name)
    try:
        tf.write(s)
        tf.close()
        yield fpath
    finally:
        if fpath.exists():
            fpath.unlink()


@dataclass
class SnippetResult:
    name: str
    prefix: str
    args: snippetparser.Json


class CapturingParser(snippetparser.ParserBase):
    def __init__(self, snippet_start: str, snippet_end: str):
        super().__init__(snippet_start, snippet_end)
        self._results = []

    def parse(self, fpath: Path, dpath: Path):
        self._results = []
        super().parse(fpath, dpath)

    def on_snippet(
        self, snippet_prefix: str, snippet_name: str, snippet_arg: snippetparser.Json, src_path: Path, fh: TextIOWrapper
    ):
        self._results.append(SnippetResult(
            name=snippet_name,
            prefix=snippet_prefix,
            args=snippet_arg
        ))
        # pass


prog_w_noarg_snippets = """\
print("hello, world")
# [[start hello
# end]]

def foo():
    print("inside foo")
    # [[start smth
    # end]]
"""


def test_prog_w_noarg_snippets():
    with tmpfile_of_str(prog_w_noarg_snippets) as fpath:
        parser = CapturingParser("[[start", "end]]")
        parser.parse(fpath, fpath)
        assert parser._results == [
            SnippetResult(name="hello", prefix="", args=None),
            SnippetResult(name="smth", prefix="    ", args=None)
        ]


prog_w_json_args = """\
print("hello, world")
# [[start hello
# end]]
# [[start hello null
# end]]
# [[start hello  
# end]]
# [[start hello "Jacque"
# end]]

def foo():
    print("inside foo")
    # [[start print_files ["file1", "file2"]
    # end]]
    print("...")
    # [[start mk_user {"username": "jane", "groups": ["wheel", "docker"]}
    # end]]
"""


def test_prog_w_json_args():
    with tmpfile_of_str(prog_w_json_args) as fpath:
        parser = CapturingParser("[[start", "end]]")
        parser.parse(fpath, fpath)
        assert parser._results == [
            SnippetResult(name="hello", prefix="", args=None),
            SnippetResult(name="hello", prefix="", args=None),
            SnippetResult(name="hello", prefix="", args=None),
            SnippetResult(name="hello", prefix="", args="Jacque"),
            SnippetResult(name="print_files", prefix="    ", args=["file1", "file2"]),
            SnippetResult(name="mk_user", prefix="    ", args={"username": "jane", "groups": ["wheel", "docker"]}),
        ]
