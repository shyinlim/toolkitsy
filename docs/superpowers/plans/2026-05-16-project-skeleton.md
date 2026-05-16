# Project Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the minimal `toolkitsy` Python package skeleton (src layout, pyproject.toml, version module, namespace `__init__.py`) so the project is pip-installable and exposes `toolkitsy.__version__`.

**Architecture:** PEP 621 `pyproject.toml` (no `setup.py`), `src/` layout to prevent accidental imports from repo root, namespace package `toolkitsy` so future submodules (`logger`, `http`, `database`) share one PyPI distribution. Build backend: `hatchling` (zero-config, fast, well-supported).

**Tech Stack:** Python 3.12+, hatchling build backend.

---

## File Structure

```
toolkitsy/
├── pyproject.toml             # Project metadata, build config, dependencies, extras
├── src/
│   └── toolkitsy/
│       ├── __init__.py        # Re-exports __version__
│       └── _version.py        # Single source of truth for version string
└── tests/
    └── test_package.py        # Smoke test: importable + has __version__
```

---

### Task 1: Create directory layout

**Files:**
- Create: `src/toolkitsy/__init__.py`
- Create: `src/toolkitsy/_version.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create directories**

Run:
```bash
mkdir -p src/toolkitsy tests
```

- [ ] **Step 2: Create `src/toolkitsy/_version.py`**

```python
__version__ = "0.0.1"
```

- [ ] **Step 3: Create `src/toolkitsy/__init__.py`**

```python
from toolkitsy._version import __version__

__all__ = ["__version__"]
```

- [ ] **Step 4: Create empty `tests/__init__.py`**

Run:
```bash
touch tests/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git add src tests
git commit -m "chore: scaffold src/toolkitsy package layout"
```

---

### Task 2: Write `pyproject.toml`

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling>=1.24"]
build-backend = "hatchling.build"

[project]
name = "toolkitsy"
dynamic = ["version"]
description = "Personal Python toolkit: logger, http client, database helpers, etc."
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.12"
authors = [{ name = "shyinlim" }]
keywords = ["toolkit", "logger", "utility"]
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.6",
]

[project.urls]
Homepage = "https://github.com/shyinlim/toolkitsy"
Repository = "https://github.com/shyinlim/toolkitsy"
Issues = "https://github.com/shyinlim/toolkitsy/issues"

[tool.hatch.version]
path = "src/toolkitsy/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/toolkitsy"]
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pyproject.toml with hatchling backend"
```

---

### Task 3: Smoke test — package is importable and exposes `__version__`

**Files:**
- Test: `tests/test_package.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_package.py
import re

import toolkitsy


def test_package_exposes_version():
    assert hasattr(toolkitsy, "__version__")


def test_version_is_semver_like():
    assert re.match(r"^\d+\.\d+\.\d+", toolkitsy.__version__)
```

- [ ] **Step 2: Verify it fails (package not yet installed)**

Run: `python -m pytest tests/test_package.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'toolkitsy'` (because we haven't installed it yet — that happens in the `dev-environment` plan).

- [ ] **Step 3: Commit**

```bash
git add tests/test_package.py
git commit -m "test: add smoke tests for package import and version"
```

---

## Self-Review Notes

- Spec coverage: skeleton ✓, version exposed ✓, pip-installable shape ✓.
- Tests will pass only after the `dev-environment` plan installs the package in editable mode.
- No placeholders, no TBDs.
