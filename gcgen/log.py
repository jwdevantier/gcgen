import logging
from typing import Optional
from enum import Enum

format = logging.Formatter("%(levelname)s - %(name)s: %(message)s")


class LogLevel(Enum):
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


_loggers = []
_default_loglevel = LogLevel.CRITICAL


def get_logger(name: str, level: Optional[LogLevel] = None) -> logging.Logger:
    """get a logger, use `__name__` by convention."""
    global _loggers
    l = logging.getLogger(name)
    if level:
        l.setLevel(level.value)
    else:
        l.setLevel(_default_loglevel.value)
    return l


def loggers_set_log_level(level: LogLevel):
    global _default_loglevel
    for logger in _loggers:
        logger.setLevel(level.value)
    _default_loglevel = level


if __name__ != "__main__":
    # configure root logger to log to console
    # (wait with adding a file-handler until we know the project root)
    root_logger = logging.getLogger()
    sh = logging.StreamHandler()
    sh.setFormatter(format)
    root_logger.addHandler(sh)
