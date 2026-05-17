import contextlib
import io
import json
import logging

import pytest


@pytest.fixture(autouse=True)
def _reset_logger_state(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    yield
    for name in ("toolkitsy", "toolkitsy.db", "toolkitsy.other", "toolkitsy.sub", "foo.bar"):
        lg = logging.getLogger(name)
        for h in list(lg.handlers):
            lg.removeHandler(h)
            with contextlib.suppress(Exception):
                h.close()
        lg.setLevel(logging.NOTSET)


def _read_stream(stream: io.StringIO) -> str:
    return stream.getvalue()


def test_configure_default_level_is_info():
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    configure(level=None, stream=stream)
    logger.debug("hidden")
    logger.info("visible")
    out = _read_stream(stream)
    assert "hidden" not in out
    assert "visible" in out


def test_configure_explicit_level_debug():
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    configure(level="DEBUG", stream=stream)
    logger.debug("seen")
    assert "seen" in _read_stream(stream)


def test_env_var_overrides_configure_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    configure(level="WARNING", stream=stream)
    logger.debug("env-wins")
    assert "env-wins" in _read_stream(stream)


def test_set_level_runtime_overrides_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    from toolkitsy.logger import configure, logger, set_level

    stream = io.StringIO()
    configure(stream=stream)
    logger.debug("hidden-1")
    assert "hidden-1" not in _read_stream(stream)
    set_level("DEBUG")
    logger.debug("now-visible")
    assert "now-visible" in _read_stream(stream)


def test_set_level_scoped_to_named_logger():
    from toolkitsy.logger import configure, get_logger, set_level

    stream = io.StringIO()
    configure(level="WARNING", stream=stream)
    db_log = get_logger("toolkitsy.db")
    other = get_logger("toolkitsy.other")
    set_level("DEBUG", name="toolkitsy.db")

    db_log.debug("db-msg")
    other.debug("other-msg")

    out = _read_stream(stream)
    assert "db-msg" in out
    assert "other-msg" not in out


def test_get_logger_returns_child_of_toolkitsy_namespace():
    from toolkitsy.logger import get_logger

    lg = get_logger("toolkitsy.sub")
    assert lg.name == "toolkitsy.sub"
    assert lg.parent is not None


def test_configure_file_dir_writes_to_disk(tmp_path):
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    file_dir = tmp_path / "logs"
    configure(level="INFO", stream=stream, file_dir=str(file_dir))
    logger.info("disk-test")

    matches = list(file_dir.rglob("*.log"))
    assert len(matches) == 1
    assert "disk-test" in matches[0].read_text(encoding="utf-8")
    assert "disk-test" in _read_stream(stream)


def test_configure_json_mode_emits_valid_json():
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    configure(level="INFO", stream=stream, json=True)
    logger.info("json-msg")
    last = _read_stream(stream).strip().splitlines()[-1]
    payload = json.loads(last)
    assert payload["msg"] == "json-msg"
    assert payload["level"] == "INFO"


def test_configure_is_idempotent_no_duplicate_handlers():
    from toolkitsy.logger import configure, logger

    stream1 = io.StringIO()
    stream2 = io.StringIO()
    configure(stream=stream1)
    configure(stream=stream2)
    logger.info("once")
    assert "once" in _read_stream(stream2)
    assert "once" not in _read_stream(stream1)


def test_logger_exception_includes_traceback():
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    configure(level="INFO", stream=stream)
    try:
        raise RuntimeError("nope")
    except RuntimeError:
        logger.exception("caught")
    out = _read_stream(stream)
    assert "caught" in out
    assert "RuntimeError: nope" in out


def test_invalid_level_raises():
    from toolkitsy.logger import configure

    with pytest.raises(ValueError):
        configure(level="NOTALEVEL")
