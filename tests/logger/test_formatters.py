import json
import logging
import re

from toolkitsy.logger._correlation_id import set_correlation_id
from toolkitsy.logger._formatters import JsonFormatter, TextFormatter


def _make_record(msg="hello", level=logging.INFO, args=None, extra=None):
    record = logging.LogRecord(
        name="toolkitsy.test",
        level=level,
        pathname="/abs/path/to/user.py",
        lineno=42,
        msg=msg,
        args=args,
        exc_info=None,
    )
    if extra:
        for k, v in extra.items():
            setattr(record, k, v)
            record.__dict__.setdefault("_toolkitsy_extras", []).append(k)
    return record


def test_text_format_basic_fields_present():
    set_correlation_id("cid-text-1")
    record = _make_record("user login")
    out = TextFormatter().format(record)
    assert " | INFO | cid-text-1 | user.py:42 | user login" in out
    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \| ", out)


def test_text_format_includes_extras_as_key_value():
    set_correlation_id("cid-text-2")
    record = _make_record("login", extra={"user_id": 123, "ip": "1.2.3.4"})
    out = TextFormatter().format(record)
    assert "user_id=123" in out
    assert "ip=1.2.3.4" in out


def test_text_format_handles_args_substitution():
    set_correlation_id("cid-text-3")
    record = _make_record("payload=%s", args=("blob",))
    out = TextFormatter().format(record)
    assert "payload=blob" in out


def test_json_format_is_valid_json_per_line():
    set_correlation_id("cid-json-1")
    record = _make_record("hello json")
    out = JsonFormatter().format(record)
    payload = json.loads(out)
    assert payload["level"] == "INFO"
    assert payload["correlation_id"] == "cid-json-1"
    assert payload["caller"] == "user.py:42"
    assert payload["msg"] == "hello json"
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$", payload["ts"])


def test_json_format_includes_extras_as_top_level_fields():
    set_correlation_id("cid-json-2")
    record = _make_record("login", extra={"user_id": 123, "ip": "1.2.3.4"})
    payload = json.loads(JsonFormatter().format(record))
    assert payload["user_id"] == 123
    assert payload["ip"] == "1.2.3.4"


def test_json_format_handles_exception_traceback():
    set_correlation_id("cid-json-3")
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = logging.LogRecord(
            name="x",
            level=logging.ERROR,
            pathname="user.py",
            lineno=1,
            msg="db failed",
            args=None,
            exc_info=sys.exc_info(),
        )
    payload = json.loads(JsonFormatter().format(record))
    assert "ValueError: boom" in payload["exc_info"]
