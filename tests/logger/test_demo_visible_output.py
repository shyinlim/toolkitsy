"""Demo tests that print real logger output so a human can eyeball the format.

Run with ``pytest -s tests/logger/test_demo_visible_output.py`` to see the
emitted lines on the console; the assertions still keep these honest tests.
"""

import io
import json
import logging

import pytest

from toolkitsy.logger import (
    configure,
    get_logger,
    logger,
    set_correlation_id,
    set_level,
)


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    yield
    for name in ("toolkitsy", "toolkitsy.api", "toolkitsy.db"):
        lg = logging.getLogger(name)
        for h in list(lg.handlers):
            lg.removeHandler(h)
        lg.setLevel(logging.NOTSET)


def _show(capsys, title, stream):
    """Print captured stream under a banner via the *real* stdout."""
    output = stream.getvalue()
    with capsys.disabled():
        print(f"\n────── {title} ──────")
        print(output, end="" if output.endswith("\n") else "\n")
        print("─" * (len(title) + 14))
    return output


def test_demo_text_format_every_level(capsys):
    stream = io.StringIO()
    configure(level="DEBUG", stream=stream)
    set_correlation_id("demo-text-cid")

    logger.debug("debug line")
    logger.info("info line")
    logger.warning("warning line")
    logger.error("error line")
    logger.critical("critical line")

    out = _show(capsys, "TEXT format — all levels", stream)
    for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        assert level in out
    assert out.count("demo-text-cid") == 5


def test_demo_text_format_with_extras(capsys):
    stream = io.StringIO()
    configure(level="INFO", stream=stream)
    set_correlation_id("demo-extras-cid")

    logger.info("user signed in", extra={"user_id": 42, "ip": "10.0.0.1"})
    logger.warning("rate limit", extra={"endpoint": "/api/x", "remaining": 0})

    out = _show(capsys, "TEXT format — extras (user_id, ip, ...)", stream)
    assert "user_id=42" in out
    assert "ip=10.0.0.1" in out
    assert "endpoint=/api/x" in out


def test_demo_text_format_with_exception(capsys):
    stream = io.StringIO()
    configure(level="INFO", stream=stream)
    set_correlation_id("demo-exc-cid")

    try:
        {}["missing"]
    except KeyError:
        logger.exception("lookup failed")

    out = _show(capsys, "TEXT format — exception traceback", stream)
    assert "lookup failed" in out
    assert "KeyError" in out


def test_demo_json_format(capsys):
    stream = io.StringIO()
    configure(level="INFO", stream=stream, json=True)
    set_correlation_id("demo-json-cid")

    logger.info("login ok", extra={"user_id": 7})
    logger.error("db down", extra={"shard": "us-west-2"})

    out = _show(capsys, "JSON format — one object per line", stream)
    for ln in out.splitlines():
        if ln.strip():
            payload = json.loads(ln)
            assert payload["correlation_id"] == "demo-json-cid"
            assert "ts" in payload and "level" in payload


def test_demo_named_logger_and_set_level(capsys):
    stream = io.StringIO()
    configure(level="WARNING", stream=stream)
    set_correlation_id("demo-named-cid")

    api = get_logger("toolkitsy.api")
    db = get_logger("toolkitsy.db")

    # Below threshold → suppressed
    api.debug("api debug (hidden)")
    db.info("db info (hidden)")

    # Raise just toolkitsy.db
    set_level("DEBUG", name="toolkitsy.db")
    api.debug("api debug (still hidden)")
    db.debug("db debug (now visible)")
    api.warning("api warning (visible)")

    out = _show(capsys, "Named loggers + per-logger set_level", stream)
    assert "db debug (now visible)" in out
    assert "api warning (visible)" in out
    assert "hidden" not in out
