import argparse
from gcgen.emitter import Emitter
import gcgen.generate as gen
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from gcgen.log import loggers_set_log_level, LogLevel, get_logger
import sys
import configparser


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


def main():
    args = cliparse.parse_args()
    if args.project_root is None:
        try:
            project_root = gen.find_project_root(Path.cwd())
        except gen.ProjectRootNotFoundError:
            print("Failed to find project root directory!")
            print("")
            print(
                "Project root directory was not explicitly provided (i.e `-p /path/to/project`)."
            )
            print(
                "Instead, we try to determine the project root by looking at the current directory"
            )
            print(
                "and each of the parent directories, first looking for a `gcgen_project.ini` configuration"
            )
            print(
                "file which would mark the top-level directory of the project, secondarily for a "
            )
            print("`.git` folder.")
            print("")
            print(
                "We failed to find either before searching the root directory of the file system."
            )
            print("TIP: create a `gcgen_project.ini` file in the root of your project.")
            sys.exit(1)
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


# TODO: save until later, measure speed with (some) generation
#       reuse mp trick somewhere in compiler.. I think..
# @app.command()
# def parse5(proj: Path):
#     from gcgen import snippetparser
#
#     if not proj.is_dir():
#         raise RuntimeError("must be a directory")
#     import time
#
#     parse5 = snippetparser.parse5
#     start = time.time()
#     from multiprocessing import cpu_count
#
#     with ProcessPoolExecutor(cpu_count()) as pool:
#         for path in proj.rglob("*.c"):
#             dpath = path.parent / f"{path.name}.gcgen"
#             pool.submit(parse5, path, dpath, "[[start", "end]]")
#     end = time.time()
#     print(f"elapsed: {end - start}s")
#     nfiles = 0
#     for _ in proj.rglob("*.c"):
#         nfiles += 1
#
#     print(f"processed {nfiles}")
#     print(f"{nfiles / (end - start)} files/second")
#

if __name__ == "__main__":
    main()
