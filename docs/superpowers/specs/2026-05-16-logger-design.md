# Logger Design Spec

**Date:** 2026-05-16
**Status:** Draft (awaiting review)
**Module:** `toolkitsy.logger`

---

## 1. Goal

Provide a shared, batteries-included logger for `toolkitsy` and any downstream repo that depends on it. Carry over useful concepts from prior in-house loggers (correlation_id, caller info, hourly file rotation, console + file output, DEBUG level), redesign the implementation to be production-grade (no Singleton, no per-call file-handler swap, no import-time side effects, testable).

## 2. Non-Goals

- Distributed tracing / OpenTelemetry integration (future)
- Log shipping (Loki / Datadog / CloudWatch) — out of scope; users emit JSON to stdout and let infra handle shipping
- Async logging (`QueueHandler`) — not needed at current scale
- Backwards-compat shim for the reference Singleton API

## 3. Public API

Everything is imported from `toolkitsy.logger`.

```python
# 99% use case — single line in every file
from toolkitsy.logger import logger
logger.info("hello")
logger.debug("payload=%s", payload)
logger.exception("db failed")     # auto-includes traceback
```

```python
# Per-module logger (optional escape hatch for fine-grained level control)
from toolkitsy.logger import get_logger
log = get_logger(__name__)
```

```python
# App-level configuration — called ONCE in entry point (main.py / FastAPI startup / conftest.py)
from toolkitsy.logger import configure
configure(
    level="INFO",          # default INFO; env var LOG_LEVEL overrides
    file_dir=None,         # None = console only; "logs" = also write to ./logs/YYYY-MM-DD/HH00.log
    json=False,            # True = JSON formatter (for containers/log aggregators)
)
```

```python
# Runtime level change
from toolkitsy.logger import set_level
set_level("DEBUG")                          # global
set_level("DEBUG", name="toolkitsy.db")     # only this module's logger
```

```python
# Correlation id (FastAPI middleware, Kafka consumer, etc.)
from toolkitsy.logger import set_correlation_id, get_correlation_id
set_correlation_id()                # auto-generate uuid4
set_correlation_id("req-abc-123")   # explicit
cid = get_correlation_id()
```

### Exported names (final)

`logger`, `get_logger`, `configure`, `set_level`, `set_correlation_id`, `get_correlation_id`.

## 4. Behavior

### 4.1 Level resolution (priority high → low)

1. `set_level(...)` runtime call
2. `LOG_LEVEL` environment variable
3. `configure(level=...)` argument
4. Built-in default: `INFO`

### 4.2 Output format

**Text (default):**
```
2026-05-16 10:26:40,671 | INFO | c9b524fc-a9a4-4523-909f-387da78cb21c | user.py:42 | user login
```
Fields: `asctime | levelname | correlation_id | filename:lineno | message`.

**JSON (when `json=True`):**
```json
{"ts":"2026-05-16T10:26:40.671Z","level":"INFO","correlation_id":"c9b524fc-...","caller":"user.py:42","msg":"user login"}
```
Extra kwargs passed via `logger.info("...", extra={"user_id": 123})` are merged into the JSON object as top-level fields. In text mode, extras are appended as `key=value` pairs.

### 4.3 Correlation ID

- Stored in `contextvars.ContextVar` (same as reference) — propagates correctly across `asyncio` tasks
- If unset when a log fires, auto-generated as `uuid.uuid4()` and stored for the rest of the context
- Always present in output (never `NO_CORRELATION_ID` placeholder)

### 4.4 Caller info (`filename:lineno`)

Use `logging.Formatter`'s built-in `%(filename)s:%(lineno)d`. **No frame-inspection decorator.** This is correct by construction and zero overhead.

### 4.5 File output

- **Default: disabled.** No `logs/` directory created on import.
- Enabled via `configure(file_dir="logs")`. Directory created at `configure()` time, not at import.
- Uses `logging.handlers.TimedRotatingFileHandler` with `when="H"`, `interval=1` — hourly rotation, stdlib-managed (no race conditions, no per-call handler swap).
- File path: `{file_dir}/YYYY-MM-DD/HH00.log` — same naming as reference (handler customised to produce this layout).
- Encoding: UTF-8.

### 4.6 No import-time side effects

- Importing `toolkitsy.logger` does NOT create directories, files, or handlers beyond a stdout console handler.
- Module-level `logger` is constructed lazily on first use, OR constructed at import with only a stdout handler attached (decision: at import, with stdout only — keeps API simple, costs nothing).

### 4.7 Thread / async safety

- `logging` module is thread-safe by design (already locks internally).
- `correlation_id` uses `ContextVar` → safe across `asyncio` and threads.
- File handler from stdlib → safe.

## 5. File Structure

```
src/toolkitsy/logger/
├── __init__.py              # Re-exports public API: logger, get_logger, configure,
│                            # set_level, set_correlation_id, get_correlation_id
├── _correlation_id.py       # ContextVar + get/set helpers
├── _formatters.py           # TextFormatter, JsonFormatter (both add correlation_id)
├── _handlers.py             # build_console_handler(), build_file_handler()
└── _logger.py               # configure(), get_logger(), set_level(),
                             # module-level `logger` instance
```

Private modules prefixed with `_` — only `__init__.py` re-exports form the public surface.

### Tests

```
tests/logger/
├── __init__.py
├── test_basic.py            # info/debug/warning/error/exception emit correctly
├── test_levels.py           # env var, configure, set_level priority
├── test_correlation_id.py   # auto-gen, manual set, contextvar isolation
├── test_formatters.py       # text format, json format, extras handling
├── test_file_handler.py     # file written to correct path, rotates, no side effects on import
└── test_no_side_effects.py  # importing toolkitsy.logger does not create logs/ dir
```

## 6. Dependencies

- **Stdlib only.** No `python-json-logger`, no `structlog`, no `loguru`.
- Rationale: zero supply-chain risk, no version conflicts in downstream repos, easy to reason about.
- JSON formatter is ~20 lines of code — not worth a dependency.

## 7. Cross-Repo Usage (different log levels)

Each consuming repo is a separate process; loggers are isolated by process. Each repo controls its own level via:

1. **Env var (recommended):** `LOG_LEVEL=DEBUG` in `.env` / docker-compose / k8s manifest
2. **Code:** `configure(level="DEBUG")` in entry point
3. **Runtime:** `set_level("DEBUG")`

No coordination needed between repos.

## 8. Design Decisions

Choices made to keep the module simple, testable, and side-effect-free:

| Aspect | Decision | Rationale |
|---|---|---|
| Import | `from toolkitsy.logger import logger` | One-line boilerplate; covers 99% of uses |
| File output | Opt-in via `configure(file_dir=...)` | No directories created on import |
| Logger identity | Module-level `logger` + optional `get_logger(__name__)` | Simple default, escape hatch for per-module level control |
| Caller info | Formatter's built-in `%(filename)s:%(lineno)d` | Zero-overhead, always correct |
| File rotation | Stdlib `TimedRotatingFileHandler` | Battle-tested, no per-call handler churn |
| Output format | Text default, JSON opt-in | Text for humans, JSON for log aggregators |

Method signatures (`logger.info(msg, ...)`, `.debug`, `.warning`, `.error`, `.exception`) match stdlib `Logger` exactly.

## 9. Acceptance Criteria

- [ ] `from toolkitsy.logger import logger; logger.info("x")` works after `pip install -e .`
- [ ] `LOG_LEVEL=DEBUG` env var switches level without code change
- [ ] `configure(file_dir="logs")` produces `logs/YYYY-MM-DD/HH00.log`
- [ ] Importing `toolkitsy.logger` does NOT create any directory
- [ ] correlation_id appears in every log line, auto-generated when not set
- [ ] `configure(json=True)` emits valid JSON per line, parseable by `json.loads`
- [ ] `set_level("DEBUG", name="foo.bar")` only affects that logger
- [ ] All tests pass with `pytest tests/logger/`
- [ ] No third-party runtime dependencies added to `pyproject.toml`

## 10. Execution Order Note

Logger should be implemented **after** `quality-and-ci` (so CI guards the first
feature) and **before** `repo-meta` (so README examples can quote the real
API) and `pypi-release` (so v0.1.0 ships with usable content).
