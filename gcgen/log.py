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


_current_log_level: Optional[LogLevel] = None
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
        v = default_loglevel or LogLevel.WARNING
        assert isinstance(v, LogLevel)
        _fallback_loglevels[name] = v.value
        l = logging.getLogger(name)
        if _current_log_level is not None:
            l.setLevel(_current_log_level.value)
        else:
            l.setLevel(_fallback_loglevels[name])
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
