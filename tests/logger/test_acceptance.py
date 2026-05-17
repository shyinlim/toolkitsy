"""End-to-end acceptance tests matching spec §9 checkboxes."""

import contextlib
import io
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _reset_logger_state(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    yield
    for name in ("toolkitsy", "toolkitsy.foo.bar", "toolkitsy.db", "toolkitsy.baz"):
        lg = logging.getLogger(name)
        for h in list(lg.handlers):
            lg.removeHandler(h)
            with contextlib.suppress(Exception):
                h.close()
        lg.setLevel(logging.NOTSET)


def test_acceptance_basic_import_and_emit():
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    configure(stream=stream)
    logger.info("x")
    assert "x" in stream.getvalue()


def test_acceptance_env_var_overrides_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    configure(stream=stream)
    logger.debug("debug-via-env")
    assert "debug-via-env" in stream.getvalue()


def test_acceptance_file_dir_produces_dated_hourly_path(tmp_path):
    from toolkitsy.logger import configure, logger

    file_dir = tmp_path / "logs"
    configure(stream=io.StringIO(), file_dir=str(file_dir))
    logger.info("on-disk")

    now = datetime.now()
    expected = file_dir / now.strftime("%Y-%m-%d") / (now.strftime("%H") + "00.log")
    assert expected.exists(), f"expected file {expected} was not created"
    assert "on-disk" in expected.read_text(encoding="utf-8")


def test_acceptance_import_creates_no_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = set(os.listdir("."))
    import importlib

    import toolkitsy.logger

    importlib.reload(toolkitsy.logger)
    after = set(os.listdir("."))
    assert before == after


def test_acceptance_correlation_id_always_present():
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    configure(stream=stream)
    logger.info("line-1")
    logger.info("line-2")
    lines = [ln for ln in stream.getvalue().splitlines() if ln.strip()]
    assert len(lines) >= 2
    for ln in lines:
        parts = [p.strip() for p in ln.split("|")]
        cid = parts[2]
        assert cid and cid != "NO_CORRELATION_ID"


def test_acceptance_json_mode_parseable():
    from toolkitsy.logger import configure, logger

    stream = io.StringIO()
    configure(stream=stream, json=True)
    logger.info("j1")
    logger.warning("j2")
    for ln in stream.getvalue().splitlines():
        if ln.strip():
            json.loads(ln)


def test_acceptance_set_level_scoped_to_named_logger():
    from toolkitsy.logger import configure, get_logger, set_level

    stream = io.StringIO()
    configure(level="WARNING", stream=stream)
    foo = get_logger("foo.bar")
    other = get_logger("baz")
    set_level("DEBUG", name="toolkitsy.foo.bar")

    foo.debug("foo-msg")
    other.debug("baz-msg")

    out = stream.getvalue()
    assert "foo-msg" in out
    assert "baz-msg" not in out


def test_acceptance_no_third_party_runtime_deps():
    import tomllib

    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    deps = data["project"].get("dependencies", [])
    assert deps == [], f"toolkitsy must have zero runtime deps, got: {deps}"
