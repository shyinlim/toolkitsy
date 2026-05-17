"""Correlation-id storage and access, propagated via contextvars."""

from __future__ import annotations

import uuid
from contextvars import ContextVar

_correlation_id: ContextVar[str | None] = ContextVar("toolkitsy_correlation_id", default=None)


def set_correlation_id(value: str | None = None) -> str:
    """Set the correlation id for the current context.

    If ``value`` is ``None`` (or omitted), a new uuid4 is generated and stored.
    Returns the value that was stored.
    """
    if value is None:
        value = str(uuid.uuid4())
    _correlation_id.set(value)
    return value


def get_correlation_id() -> str:
    """Return the correlation id for the current context.

    If none has been set, generates one, stores it, and returns it so that
    every emitted log line carries a real id (never a placeholder).
    """
    cid = _correlation_id.get()
    if cid is None:
        cid = str(uuid.uuid4())
        _correlation_id.set(cid)
    return cid
