import pytest
import tempfile
from pathlib import Path


# REWRITE - possibly use functions
# But basically load input, output, gen temp-dir, allow user to call gen and see if results pan out


@pytest.fixture(scope="function")
def _tmp_outdir():
    with tempfile.TemporaryDirectory() as tmp_dir_strpath:
        yield Path(tmp_dir_strpath)


## TODO: need a fn to traverse dir, computing file hashes, output
##  {<file relpath>: <hash>} dict.

## TODO: need fn to then compare two dicts, finding differences, possibly writing patch diffs.

# Can use this to
# 1) compare/ensure that input dir's contents (aside from generated files) don't change between
#    run (2) and (3)
# 2) compare that actual result matches expected results dir.
