from __future__ import annotations

import logging
import os
import sys
from typing import Dict

_HAS_TTY = sys.stdout.isatty()
if os.name == "nt":  # Windows – enable ANSI via colorama if available
    try:
        import colorama  # type: ignore

        colorama.just_fix_windows_console()
        _HAS_TTY = True
    except ModuleNotFoundError:
        pass

_ANSI: Dict[str, str] = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m",
}


class ColorFormatter(logging.Formatter):
    """Formatter that maps each log *level* to a distinct colour."""

    LEVEL_STYLE = {
        logging.DEBUG: _ANSI["cyan"],
        logging.INFO: _ANSI["green"],
        logging.WARNING: _ANSI["yellow"],
        logging.ERROR: _ANSI["red"],
        logging.CRITICAL: "\033[1;41m" + _ANSI["white"],
    }

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        if _HAS_TTY:
            colour = self.LEVEL_STYLE.get(record.levelno, "")
            return f"{colour}{msg}{_ANSI['reset']}"
        return msg

def _create_stream_handler() -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.NOTSET)  # handler never filters, rely on logger
    # fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s" 
    fmt = "%(asctime)s | %(levelname)-8s | %(message)s"

    handler.setFormatter(ColorFormatter(fmt))
    return handler


def _to_level(level: int | str | None) -> int:
    if level is None:
        return logging.INFO
    if isinstance(level, str):
        return logging.getLevelName(level.upper())
    return level


def get_logger(name: str | None = None, *, level: int | str = "INFO") -> logging.Logger:
    """Return a colourised logger.

    Re-invoking with a **more verbose** level (e.g. DEBUG after INFO) lowers
    handlers’ thresholds so that nothing is hidden.
    """
    lvl = _to_level(level)

    logger = logging.getLogger(name)
    logger.setLevel(lvl)

    # Ensure a coloured handler exists
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(_create_stream_handler())
        logger.propagate = False

    # Always make existing handlers at least as verbose as *lvl*
    for h in logger.handlers:
        if h.level > lvl:
            h.setLevel(lvl)
    return logger

