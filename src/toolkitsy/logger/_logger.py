"""Configuration entry point and public logger helpers."""

from __future__ import annotations

import contextlib
import logging
import os
from typing import IO

from toolkitsy.logger._handlers import build_console_handler, build_file_handler

_NAMESPACE = "toolkitsy"
_VALID_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


def _resolve_level(explicit: str | None) -> int:
    """Priority: env var > configure() arg > INFO."""
    raw = os.environ.get("LOG_LEVEL") or explicit or "INFO"
    raw = raw.upper()
    if raw not in _VALID_LEVELS:
        raise ValueError(f"Invalid log level {raw!r}; expected one of {sorted(_VALID_LEVELS)}")
    return getattr(logging, raw)


def _get_root() -> logging.Logger:
    return logging.getLogger(_NAMESPACE)


def configure(
    *,
    level: str | None = None,
    file_dir: str | None = None,
    json: bool = False,
    stream: IO[str] | None = None,
) -> None:
    """Configure the toolkitsy logger.

    Called once from an application entry point. Replaces any handlers
    previously attached by ``configure`` so repeated calls are idempotent.
    """
    log = _get_root()
    for h in list(log.handlers):
        log.removeHandler(h)
        with contextlib.suppress(Exception):
            h.close()

    log.setLevel(_resolve_level(level))
    log.propagate = False
    log.addHandler(build_console_handler(stream=stream, use_json=json))
    if file_dir is not None:
        log.addHandler(build_file_handler(file_dir=file_dir, use_json=json))


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger under the ``toolkitsy`` namespace."""
    if name in (None, "", _NAMESPACE):
        return _get_root()
    if name.startswith(_NAMESPACE + "."):
        return logging.getLogger(name)
    return logging.getLogger(f"{_NAMESPACE}.{name}")


def set_level(level: str, *, name: str | None = None) -> None:
    """Change the level of the root or a named logger at runtime."""
    raw = level.upper()
    if raw not in _VALID_LEVELS:
        raise ValueError(f"Invalid log level {raw!r}; expected one of {sorted(_VALID_LEVELS)}")
    resolved = getattr(logging, raw)
    target = get_logger(name) if name else _get_root()
    target.setLevel(resolved)


# Module-level logger: registered at import with NO handlers and no I/O.
logger = _get_root()
