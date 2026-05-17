import io
import logging
from datetime import datetime, timedelta
from pathlib import Path

from toolkitsy.logger._handlers import (
    HourlyDirRotatingHandler,
    build_console_handler,
    build_file_handler,
)


def test_build_console_handler_writes_to_stream():
    stream = io.StringIO()
    handler = build_console_handler(stream=stream, use_json=False)
    logger = logging.getLogger("toolkitsy.test.console")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("hello console")

    assert "hello console" in stream.getvalue()


def test_build_console_handler_json_mode_emits_json():
    import json as _json

    stream = io.StringIO()
    handler = build_console_handler(stream=stream, use_json=True)
    logger = logging.getLogger("toolkitsy.test.console.json")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("hello json")

    line = stream.getvalue().strip().splitlines()[-1]
    payload = _json.loads(line)
    assert payload["msg"] == "hello json"


def test_build_file_handler_creates_directory_at_call_time(tmp_path):
    file_dir = tmp_path / "logs"
    assert not file_dir.exists()

    handler = build_file_handler(file_dir=str(file_dir), use_json=False)
    handler.close()

    assert file_dir.exists()
    base = Path(handler.baseFilename)
    assert base.parent.parent == file_dir
    assert base.name.endswith(".log")
    assert len(base.parent.name) == 10


def test_file_handler_writes_to_expected_path(tmp_path):
    file_dir = tmp_path / "logs"
    handler = build_file_handler(file_dir=str(file_dir), use_json=False)

    logger = logging.getLogger("toolkitsy.test.file")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("hello file")
    handler.flush()
    handler.close()

    base = Path(handler.baseFilename)
    assert base.exists(), f"log file {base} was not created"
    content = base.read_text(encoding="utf-8")
    assert "hello file" in content


def test_hourly_dir_handler_target_path_layout(tmp_path):
    handler = HourlyDirRotatingHandler(file_dir=str(tmp_path / "logs"))
    try:
        base = Path(handler.baseFilename)
        now = datetime.now()
        assert base.parent.name == now.strftime("%Y-%m-%d")
        assert base.name == now.strftime("%H") + "00.log"
    finally:
        handler.close()


def test_hourly_dir_handler_rotation_computes_new_path(tmp_path):
    handler = HourlyDirRotatingHandler(file_dir=str(tmp_path / "logs"))
    try:
        original = Path(handler.baseFilename)
        handler.rolloverAt = handler.rolloverAt - 3600
        future = datetime.now() + timedelta(hours=1)
        handler._now_for_test = future  # noqa: SLF001
        handler.doRollover()
        new_path = Path(handler.baseFilename)
        assert new_path != original
        assert new_path.parent.name == future.strftime("%Y-%m-%d")
        assert new_path.name == future.strftime("%H") + "00.log"
    finally:
        handler.close()


def test_file_handler_uses_utf8(tmp_path):
    handler = build_file_handler(file_dir=str(tmp_path / "logs"), use_json=False)
    logger = logging.getLogger("toolkitsy.test.utf8")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("中文 émoji ✓")
    handler.flush()
    handler.close()

    content = Path(handler.baseFilename).read_text(encoding="utf-8")
    assert "中文" in content
    assert "✓" in content
