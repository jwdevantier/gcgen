"""
Discover files with code to generate.
"""

# should look for a common filename, e.g. `gcgen_<>.py`
# should consider all parent directories up to a `gcgen.[yml|toml]` or .git
#  keep going up, looking for gcgen conf, if none, restart, looking for .git, if none, abort.

from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, Union
import importlib.util
import sys
import os
from io import TextIOWrapper
from gcgen.scope import Scope
from gcgen import decorators
from gcgen.snippetparser import ParserBase
from gcgen.emitter import Emitter
from gcgen.log import get_logger, LogLevel
from gcgen.api.snippets_helpers import SnippetFn


logger = get_logger(__name__, LogLevel.DEBUG)


class SnippetException(Exception):
    def __init__(
        self,
        snippet_name: str,
        snippet: SnippetFn,
        fpath: Path,
        emitter: Emitter,
        scope: Scope,
    ):
        self.snippet_name = snippet_name
        self.snippet = snippet
        self.emitter = emitter
        self.scope = scope
        self.fpath = fpath
        super().__init__(f"exception in snippet {snippet_name!r} called from {fpath!s}")


class Parser(ParserBase):
    def __init__(
        self,
        snippet_start: str,
        snippet_end: str,
        scope: Scope,
        snippets_scope: Scope,
        indent_by: Scope,
        project_root: Path,
    ):
        super().__init__(snippet_start, snippet_end)
        self._scope = scope
        self._snippets_scope = snippets_scope
        self._indent_by = indent_by
        self._project_root = project_root

    @property
    def scope(self) -> Scope:
        return self._scope

    @scope.setter
    def scope(self, scope: Scope) -> None:
        self._scope = scope

    def on_snippet(
        self, snippet_name: str, snippet_prefix: str, src_path: Path, fh: TextIOWrapper
    ):
        logger.debug(f"on_snippet {snippet_name!r} called")
        snippet_fn: Union[SnippetFn, None] = self._snippets_scope.get(
            snippet_name, None
        )
        fpath = src_path.relative_to(self._project_root)
        if snippet_fn is None:
            logger.critical(f"undefined snippet {snippet_name!r} called from {fpath!s}")
            # TODO: custom error here, perhaps.
            raise RuntimeError(f"snippet {snippet_name!r} not defined")
        indent_by = self._indent_by.get(src_path.suffix[1:]) or self._indent_by[""]
        emitter = Emitter(indent_by=indent_by, prefix=snippet_prefix)
        scope = self._scope  # do not derive, share
        scope["$snippet"] = snippet_name
        scope["$file"] = fpath
        scope["$snippets"] = self._snippets_scope.derive()
        try:
            snippet_fn(emitter, scope)
        except Exception as e:
            logger.error(
                f"error executing snippet {snippet_name!r} in {fpath!s}", exc_info=True
            )
            raise SnippetException(
                snippet_name, snippet_fn, src_path, emitter, scope
            ) from e
        logger.debug(list(emitter.lines()))
        for line in emitter.lines():
            fh.write(line)


class ProjectRootNotFoundError(Exception):
    def __init__(self, start: Path):
        self.start = start
        super().__init__(f"Failed to find project root relative to {start!s}")


class CompileError(Exception):
    pass


class CompileScopeExtendError(CompileError):
    def __init__(self, conf_path: Path):
        self.conf_path = conf_path
        super().__init__(
            f"error during execution of `gcgen_scope_extend` in {conf_path!s}"
        )


class CompileParseFilesError(CompileError):
    def __init__(self, conf_path: Path):
        self.conf_path = conf_path
        super().__init__(
            f"error during execution of `gcgen_parse_files` in {conf_path!s}"
        )


class CompileExcludeFilesError(CompileError):
    def __init__(self, conf_path: Path):
        self.conf_path = conf_path
        super().__init__(f"error during execution of `exclude_dirs` in {conf_path!s}")


class CompileGeneratorFunctionError(CompileError):
    def __init__(self, generator_fn_name: str, conf_path: Path):
        self.conf_path = conf_path
        self.generator_fn_name = generator_fn_name
        super().__init__(
            f"error during execution of generator function {generator_fn_name!s} in {conf_path!s}"
        )


def find_project_root(start: Path) -> Path:
    """Find directory closest to `start` which is determined to be a project root."""
    search_path = [start, *start.parents]
    for directory in search_path:
        for elem in ["gcgen_project.ini", ".git"]:
            p = directory / elem
            if p.exists():
                return directory
    raise ProjectRootNotFoundError(start)


def import_from_path(root: Path, modpath: Path):
    modname = modpath.relative_to(root)
    modname = modname.parent / modname.name[: -len(modname.suffix)]
    modname = ".".join(e.replace(" ", "_") for e in modname.parts)
    spec = importlib.util.spec_from_file_location(modname, modpath)
    if spec is None:
        raise RuntimeError("spec not loaded, should be impossible")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


def get_mod_generator_fns(mod: ModuleType) -> Dict[str, Callable]:
    return {
        name: fn for name, fn in mod.__dict__.items() if decorators.is_generator(fn)
    }


def get_mod_snippet_fns(mod: ModuleType) -> Dict[str, Callable]:
    return {name: fn for name, fn in mod.__dict__.items() if decorators.is_snippet(fn)}


def compile(root: Path, tag_start: str = "[[start", tag_end: str = "end]]"):
    # in case `root` is a relative path like '.', resolve to absolute path
    # for later use, where cwd changes.
    root = root.resolve()

    def _compile(
        path: Path, parent_scope: Scope, snippets_scope: Scope, indent_by: Scope
    ):
        gcgen_mod = None
        gcgen_conf_path = path / "gcgen.py"
        if gcgen_conf_path.exists():
            gcgen_mod = import_from_path(root, gcgen_conf_path)
        scope = parent_scope.derive()

        exclude_dirs = []
        if gcgen_mod is not None:
            if hasattr(gcgen_mod, "exclude_dirs"):
                try:
                    exclude_dirs = gcgen_mod.exclude_dirs()
                except Exception as e:
                    logger.critical(
                        f"error during execution of `exclude_dirs` in {gcgen_conf_path!s}",
                        exc_info=True,
                    )
                    raise CompileExcludeFilesError(gcgen_conf_path)

            if hasattr(gcgen_mod, "gcgen_indent_by"):
                indent_by = indent_by.derive()
                mod_indent_by = gcgen_mod.gcgen_indent_by
                if not isinstance(mod_indent_by, dict):
                    raise ValueError("`gcgen_indent_by` in conf must be a dictionary")
                indent_by.update(mod_indent_by)
            # if fn to extend local scope exists, run it
            if hasattr(gcgen_mod, "gcgen_scope_extend"):
                try:
                    gcgen_mod.gcgen_scope_extend(scope)
                except Exception as e:
                    logger.critical(
                        f"error during execution of `gcgen_scope_extend` in {gcgen_conf_path!s}",
                        exc_info=True,
                    )
                    raise CompileScopeExtendError(gcgen_conf_path) from e
            # if one or more snippets are defined, extend scope
            snippet_fns = list(get_mod_snippet_fns(gcgen_mod).values())
            if snippet_fns:
                snippets_scope = snippets_scope.derive()
                for snippet_fn in snippet_fns:
                    for name in decorators.snippet_names(snippet_fn):
                        snippets_scope[name] = snippet_fn

        # traverse and compile in depth-first order, passing initialized scope
        for p in path.iterdir():
            if p.is_dir() and p.name not in exclude_dirs:
                _compile(p, scope, snippets_scope, indent_by)

        if gcgen_mod is None:
            return

        # operate from within the path containing the gcgen.py we are currently processing
        os.chdir(path)
        # parse snippets in any files explicitly listed as having them
        if hasattr(gcgen_mod, "gcgen_parse_files"):
            try:
                files = gcgen_mod.gcgen_parse_files()
            except Exception as e:
                logger.critical(
                    f"error during execution of `gcgen_parse_files` in {gcgen_conf_path!s}",
                    exc_info=True,
                )
                raise CompileParseFilesError(gcgen_conf_path) from e
            parser = Parser(tag_start, tag_end, scope, snippets_scope, indent_by, root)
            for file in files:
                logger.info(f"Parsing {file!s}")
                file = Path(file)
                if str(file) != file.name:
                    logger.error(
                        f"{file!s} skipped - entries in ``cgen_parse_files`` must be plain filenames, not paths!",
                    )
                    raise RuntimeError("...")

                # compute absolute path to file (needed by compiler)
                file = (path / file).resolve()
                if not file.exists():
                    breakpoint()
                    logger.warning(
                        f"Could not find file!",
                        extra={"file": str(file), "gcgen file": gcgen_conf_path},
                    )
                    raise RuntimeError("...")
                elif not file.is_file():
                    logger.error(
                        f"Expected a file containing snippets, but object at {file!s} path is not a file!",
                        extra={"file": str(file), "gcgen file": gcgen_conf_path},
                    )
                    raise RuntimeError("...")
                file_scope = scope.derive()
                parser.scope = file_scope
                logger.debug(f"Input:\n{file.read_text()}")
                parser.parse(file, file)
                logger.debug(f"Output{file.read_text()}")

        # parse generators (functions which may create arbitrarily many files)
        for name, fn in get_mod_generator_fns(gcgen_mod).items():
            local_scope = scope.derive()
            try:
                fn(local_scope)
            except Exception as e:
                logger.error(
                    f"error executing generator function {name!s} in {gcgen_conf_path!s}",
                    exc_info=True,
                )
                raise CompileGeneratorFunctionError(name, gcgen_conf_path) from e

    indent_by = Scope()
    indent_by[""] = "   "
    _compile(root, Scope(), Scope(), indent_by)
