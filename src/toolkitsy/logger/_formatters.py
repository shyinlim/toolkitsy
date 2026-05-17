"""Formatters that inject correlation_id and merge ``extra`` kwargs."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from toolkitsy.logger._correlation_id import get_correlation_id

_RESERVED_RECORD_ATTRS = frozenset({
    "args", "asctime", "created", "exc_info", "exc_text", "filename",
    "funcName", "levelname", "levelno", "lineno", "message", "module",
    "msecs", "msg", "name", "pathname", "process", "processName",
    "relativeCreated", "stack_info", "taskName", "thread", "threadName",
})


def _collect_extras(record: logging.LogRecord) -> dict[str, object]:
    return {
        k: v
        for k, v in record.__dict__.items()
        if k not in _RESERVED_RECORD_ATTRS and not k.startswith("_")
    }


class TextFormatter(logging.Formatter):
    """Human-readable single-line format.

    ``asctime | LEVEL | correlation_id | filename:lineno | message [k=v ...]``
    """

    default_msec_format = "%s,%03d"

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s,%(msecs)03d | %(levelname)s | %(correlation_id)s | "
                "%(filename)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        record.correlation_id = get_correlation_id()
        base = super().format(record)
        extras = _collect_extras(record)
        # Drop the synthetic correlation_id we set above
        extras.pop("correlation_id", None)
        if extras:
            base = base + " " + " ".join(f"{k}={v}" for k, v in extras.items())
        return base


class JsonFormatter(logging.Formatter):
    """Machine-readable JSON-per-line format suitable for log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=UTC)
        payload: dict[str, object] = {
            "ts": ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z",
            "level": record.levelname,
            "correlation_id": get_correlation_id(),
            "caller": f"{record.filename}:{record.lineno}",
            "msg": record.getMessage(),
        }
        payload.update(_collect_extras(record))
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)
        return json.dumps(payload, default=str)
