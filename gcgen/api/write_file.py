import tempfile
from os import rename as os_rename
from pathlib import Path
from gcgen.emitter import Emitter
from typing import Union


class write_file(object):
    """Context manager to safely write a file using an Emitter.

    If the context manager finishes successfully, then the file identified by
    `fpath` is replaced atomically by the temporary file which contains the
    new contents.
    If the context manager is exiting due to an exception, the temporary file
    is removed and the file at `fpath` (if any) is untouched.

    Args:
        fpath: path to the file to write.
            (recommended to only write files in the same directory)
        indent_by: what to write for each level of indentation
            defaults to a single space (' ').
    """

    def __init__(self, fpath: Union[Path, str], indent_by: str = " "):
        if not isinstance(fpath, (str, Path)):
            raise RuntimeError("path supplied must be a pathlib.Path or str")
        self._fpath = fpath if isinstance(fpath, Path) else Path(fpath)
        self._indent_by = indent_by

    def __enter__(self) -> Emitter:
        self._fh = tempfile.NamedTemporaryFile("w", dir=self._fpath.parent, delete=False)
        self._emitter = Emitter(prefix="", indent_by=self._indent_by)
        return self._emitter

    def __exit__(self, exc_type, _, __):
        if exc_type:
            self._fh.close()
            self._fh.unlink()
            return

        try:
            for line in self._emitter.lines():
                self._fh.write(line)
            self._fh.close()
            os_rename(src=self._fh.name, dst=self._fpath)
        except Exception as e:
            self._fh.close()
            p = Path(self._fh.name)
            if p.exists():
                p.unlink()
            raise e
