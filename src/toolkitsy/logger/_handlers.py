"""Console and rotating file handlers for the toolkitsy logger."""

from __future__ import annotations

import logging
import sys
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import IO

from toolkitsy.logger._formatters import JsonFormatter, TextFormatter


def _pick_formatter(use_json: bool) -> logging.Formatter:
    return JsonFormatter() if use_json else TextFormatter()


def build_console_handler(
    *,
    stream: IO[str] | None = None,
    use_json: bool = False,
) -> logging.StreamHandler:
    """Build a stdout (or supplied stream) handler with the chosen formatter."""
    handler = logging.StreamHandler(stream if stream is not None else sys.stdout)
    handler.setFormatter(_pick_formatter(use_json))
    return handler


class HourlyDirRotatingHandler(TimedRotatingFileHandler):
    """Hourly rotation that writes to ``{file_dir}/YYYY-MM-DD/HH00.log``.

    Overrides ``TimedRotatingFileHandler`` so the active file always lives at
    a path derived from the current wall clock, rather than the stdlib's
    suffix-based scheme. Creates intermediate date directories on demand.
    """

    def __init__(self, file_dir: str, *, encoding: str = "utf-8") -> None:
        self._file_dir = Path(file_dir)
        self._now_for_test: datetime | None = None
        self._file_dir.mkdir(parents=True, exist_ok=True)
        target = self._target_path(self._now())
        target.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(
            filename=str(target),
            when="H",
            interval=1,
            backupCount=0,
            encoding=encoding,
            delay=False,
            utc=False,
        )

    def _now(self) -> datetime:
        return self._now_for_test if self._now_for_test is not None else datetime.now()

    def _target_path(self, when: datetime) -> Path:
        return self._file_dir / when.strftime("%Y-%m-%d") / (when.strftime("%H") + "00.log")

    def doRollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None

        new_path = self._target_path(self._now())
        new_path.parent.mkdir(parents=True, exist_ok=True)
        self.baseFilename = str(new_path)

        if not self.delay:
            self.stream = self._open()

        current_time = int(time.time())
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at += self.interval
        self.rolloverAt = new_rollover_at


def build_file_handler(
    *,
    file_dir: str,
    use_json: bool = False,
) -> HourlyDirRotatingHandler:
    """Build the hourly-rotated file handler. Creates ``file_dir`` if missing."""
    handler = HourlyDirRotatingHandler(file_dir=file_dir)
    handler.setFormatter(_pick_formatter(use_json))
    return handler
