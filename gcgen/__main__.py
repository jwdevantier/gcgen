import argparse
import functools
from pathlib import Path
import sys
import configparser
import traceback
import gcgen.generate as gen
from gcgen.log import loggers_set_log_level, LogLevel, get_logger
from gcgen.excbase import GcgenError


logger = get_logger(__name__, LogLevel.DEBUG)

cliparse = argparse.ArgumentParser(
    description="generate output into snippets embedded in files or create files from scratch with generators"
)

cliparse.add_argument(
    "-p",
    "--project",
    action="store",
    dest="project_root",
    help="designate the root of the project, otherwise inferred from searching up parent directories until encountering gcgen_project.ini or, failing that, a .git folder",
)

cliparse.add_argument(
    "-l",
    "--log-level",
    action="store",
    dest="log_level",
    help="set log level (debug|info|warning|error|critical)",
)

cliparse.add_argument(
    "--log-file",
    action="store",
    dest="log_file",
    help="output log to file",
)

cliparse.add_argument(
    "--tag-start", action="store", dest="tag_start", help="set start tag (`[[start`)"
)
cliparse.add_argument(
    "--tag-end", action="store", dest="tag_end", help="set end tag (`end]]`)"
)


def pp_error(f):
    """catch and pretty-print GcgenError's which have a pretty-print function."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except GcgenError as exc:
            print("\nError Traceback:")
            print(traceback.format_exc())
            exc.printerr()
            sys.exit(1)

    return wrapper


@pp_error
def main():
    print("gcgen running...")
    print("See documentation at: https://jwdevantier.github.io/gcgen")
    args = cliparse.parse_args()
    if args.project_root is None:
        project_root = gen.find_project_root(Path.cwd())
    else:
        project_root = Path(args.project_root)
        if not project_root.exists():
            print(f"Invalid project root: {project_root!s} does not exist")
            sys.exit(1)
        if not project_root.is_dir():
            print(f"Invalid project root: {project_root!s} not a directory")
            sys.exit(1)

    # read config
    conf_file = project_root / "gcgen_project.ini"
    config = configparser.ConfigParser()
    config.read_dict(
        {
            "parse": {"tag_start": "[[start", "tag_end": "end]]"},
            "log": {"level": "warning"},
        }
    )
    if conf_file.exists():
        config.read(conf_file)

    if args.log_level:
        if not config.has_section("log"):
            config.add_section("log")
        config.set("log", "level", args.log_level)

    level = config.get("log", "level", fallback="warning")
    try:
        loggers_set_log_level(LogLevel[level.upper()])
    except KeyError:
        print(
            f"Invalid log-level {level!r}, valid are: debug/info/warning/error/critical"
        )
        sys.exit(1)
    tag_start = config.get("parse", "tag_start")
    tag_end = config.get("parse", "tag_end")
    if level == "debug":
        logger.debug(f"Tag start: `{tag_start}`")
        logger.debug(f"Tag end: `{tag_end}`")

    # ensure python code in the top-level directory of the project can be imported for use in snippets & generators
    mod_root = project_root / "gcgen_modules"
    if mod_root.exists() and mod_root.is_dir():
        sys.path.insert(1, str(mod_root.resolve()))
    else:
        logger.info(
            f"`gcgen_modules` missing, Python modules placed in this directory can be included from snippets and configuration files"
        )

    gen.compile(project_root, tag_start=tag_start, tag_end=tag_end)


if __name__ == "__main__":
    main()
