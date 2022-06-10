import logging
from typing import Optional, List, cast
from enum import Enum

format = logging.Formatter("%(levelname)s - %(name)s: %(message)s")


class LogLevel(Enum):
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


_default_loglevel = LogLevel.WARNING
_current_log_level = None
_fallback_loglevels = {}


def has_logger(name: str) -> bool:
    return name in logging.Logger.manager.loggerDict


def all_loggers() -> List[logging.Logger]:
    return cast(
        List[logging.Logger],
        list(
            l
            for l in logging.Logger.manager.loggerDict.values()
            if isinstance(l, logging.Logger)
        ),
    )


def get_logger(
    name: str, default_loglevel: Optional[LogLevel] = None
) -> logging.Logger:
    """get a logger, use `__name__` by convention."""
    if not has_logger(name):
        v = default_loglevel or _default_loglevel
        if isinstance(v, LogLevel):
            v = v.value
        _fallback_loglevels[name] = v
        l = logging.getLogger(name)
        l.setLevel(_current_log_level or _fallback_loglevels[name])
        return l
    else:
        return logging.getLogger()


def loggers_set_log_level(level: LogLevel):
    global _current_log_level
    _current_log_level = level
    for logger in all_loggers():
        logger.setLevel(level.value)


if __name__ != "__main__":
    # configure root logger to log to console
    # (wait with adding a file-handler until we know the project root)
    root_logger = logging.getLogger()
    sh = logging.StreamHandler()
    sh.setFormatter(format)
    root_logger.addHandler(sh)
