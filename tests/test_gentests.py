from pathlib import Path
from dataclasses import dataclass
from contextlib import contextmanager
import tempfile
import hashlib
from setuptools._distutils.dir_util import copy_tree
from typing import Dict, List
from gcgen import generate
from gcgen.snippetparser import UnclosedSnippetError, NestedSnippetsError, SnippetJsonValueError
import pytest
import logging


logging.getLogger().setLevel(logging.DEBUG)


GENTESTS_ROOT = Path(__file__).parent / "data" / "gentests"


@dataclass(frozen=True)
class GenTestCase:
    input_path: Path
    expected_path: Path


@contextmanager
def load_gentest(testcase: str):
    """load a test case, copying it into a temporary directory ahead of use."""
    if not (GENTESTS_ROOT / testcase):
        raise RuntimeError(
            f"gentest case: {testcase!r} - testcase directory does not exist"
        )
    src = GENTESTS_ROOT / testcase / "input"
    if not src.is_dir():
        raise RuntimeError(
            f"gentest case: {testcase!r} - `input` directory does not exist"
        )

    expected = GENTESTS_ROOT / testcase / "expected"
    if not expected.is_dir():
        raise RuntimeError(
            f"gentest case: {testcase!r} - `expected` directory does not exist"
        )

    with tempfile.TemporaryDirectory() as tmp_dir_strpath:
        copy_tree(str(src), tmp_dir_strpath)
        yield GenTestCase(input_path=Path(tmp_dir_strpath), expected_path=expected)


def md5sum(fname: Path, blk_size=4096) -> str:
    h = hashlib.md5()
    with open(fname, "rb") as fh:
        for blk in iter(lambda: fh.read(blk_size), b""):
            h.update(blk)
        return h.hexdigest()


def dir_checksums(root: Path) -> Dict[str, str]:
    checksums = {}
    for fpath in root.rglob("*"):
        checksums[str(fpath.relative_to(root))] = md5sum(fpath.resolve())
    return checksums


def gentest_test_eql(testcase: str, files: List[str]):
    "test equality between specific files"
    with load_gentest(testcase) as gtc:
        generate.compile(gtc.input_path)
        errs_expected = {}
        errs_actual = {}
        for file in files:
            src = gtc.input_path / file
            expected = gtc.expected_path / file
            with open(src, "r") as fh:
                src_lines = fh.readlines()
            with open(expected, "r") as fh:
                expected_lines = fh.readlines()

            if src_lines != expected_lines:
                errs_expected[file] = expected_lines
                errs_actual[file] = src_lines
        if errs_expected != errs_actual:
            for file in errs_actual.keys():
                actual_lines = errs_actual[file]
                expected_lines = errs_expected[file]
                print(f"   ------------file: {file!s} (expected)------------")
                for line in expected_lines:
                    print(line, end="")
                print(f"   ------------file: {file!s} (actual)------------")
                for line in actual_lines:
                    print(line, end="")
        # breakpoint()
        assert errs_expected == errs_actual


def test_aa_empty_conf_ok():
    with load_gentest("aa-empty-conf-ok") as gentestcase:
        """an empty config should be OK, no required sections"""
        generate.compile(gentestcase.input_path)


def test_aa_conf_is_imported():
    """if successful, this proves that the top-level cgen file is imported"""
    with load_gentest("aa-conf-is-imported") as gtc:
        with pytest.raises(RuntimeError, match="conf module was imported"):
            generate.compile(gtc.input_path)


def test_aa_cgen_scope_extend_hook_run():
    """ensure that the scope extend function in the cgen module is run (if present)."""
    with load_gentest("aa-ensure-conf-scope-extend-hook-fn-called") as gtc:
        with pytest.raises(generate.CompileScopeExtendError):
            generate.compile(gtc.input_path)


def test_aa_generators_called():
    """ensure that a generator functions in the cgen module are run"""
    with load_gentest("aa-generators-called") as gtc:
        with pytest.raises(generate.CompileGeneratorFunctionError):
            generate.compile(gtc.input_path)


def test_aa_exclude_dirs_respected():
    "ensure 'exclude_dirs' entry in conf causes recursive traversal to skip those subtrees."
    with load_gentest("aa-exclude-dirs-respected") as gtc:
        generate.compile(gtc.input_path)


def test_bb_snippets():
    gentest_test_eql("bb-snippets", ["filea.py"])


def test_bb_snippets_nested():
    """Tests input with nested directory overriding snippet and scope variable."""
    gentest_test_eql("bb-snippets-nested", ["outerfile.txt", "inner/innerfile.txt"])


def test_bb_snippets_nested_deep():
    """Tests input with nested directory overriding snippet and scope variable
    now inside intermediate dir w/o gcgen.py file of its own"""
    gentest_test_eql(
        "bb-snippets-nested-deep", ["outerfile.txt", "inner/innermost/innerfile.txt"]
    )


def test_bb_snippets_mod_file_scope():
    """Modifying the scope in one snippet should affect snippets in the rest of the file."""
    gentest_test_eql("bb-snippets-mod-file-scope", ["greetings.txt"])


def test_bb_snippets_calling_snippets():
    gentest_test_eql(
        "bb-snippets-calling-snippets", ["outerfile.txt", "inner/innerfile.txt"]
    )


def test_bb_snippets_json_args():
    gentest_test_eql(
        "bb-snippets-json-args", ["example.txt"]
    )


def test_bb_snippets_json_args_err():
    with load_gentest("bb-snippets-json-args-err") as gtc:
        with pytest.raises(SnippetJsonValueError):
            generate.compile(gtc.input_path)


def test_bb_snippets_err_nested_snippets():
    with load_gentest("bb-snippets-err-nested-snippets") as gtc:
        with pytest.raises(NestedSnippetsError):
            generate.compile(gtc.input_path)


def test_bb_snippets_err_unclosed_snippet():
    with load_gentest("bb-snippets-err-unclosed-snippet") as gtc:
        with pytest.raises(UnclosedSnippetError):
            generate.compile(gtc.input_path)


def test_cc_generators_write_test():
    "write two files using a generator"
    gentest_test_eql("cc-generators-write-test", ["foo.txt", "bar.txt"])
