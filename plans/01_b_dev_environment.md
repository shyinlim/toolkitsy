# 01_b — Dev Environment (uv + editable install) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up a reproducible local development environment using `uv`, install `toolkitsy` in editable mode with dev dependencies, and add a `.gitignore` that excludes `.venv/`, build artifacts, and editor noise.

**Architecture:** `uv` manages the virtualenv (`.venv/`) and resolves dependencies from `pyproject.toml`. `uv.lock` is committed for reproducible installs. The package is installed editable so source edits take effect without reinstall.

**Tech Stack:** uv (Rust-based Python package manager), pip-compatible editable installs.

---

## File Structure

```
toolkitsy/
├── .gitignore                 # NEW: ignore .venv, dist, caches
├── .python-version            # NEW: pin Python interpreter version
└── uv.lock                    # NEW: generated lock file (committed)
```

---

### Task 1: Add `.gitignore`

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Create `.gitignore`**

```gitignore
# Virtualenv
.venv/
venv/

# Python bytecode
__pycache__/
*.py[cod]
*$py.class

# Build artifacts
build/
dist/
*.egg-info/
*.egg

# Test / coverage
.pytest_cache/
.coverage
htmlcov/
.coverage.*
coverage.xml

# Type / lint caches
.mypy_cache/
.ruff_cache/

# Editors
.vscode/
.idea/
*.swp
.DS_Store

# Env files
.env
.env.local
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore"
```

---

### Task 2: Verify `uv` is installed

- [ ] **Step 1: Check uv presence**

Run: `uv --version`
Expected: prints a version (e.g. `uv 0.4.x` or newer). If not installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart shell or: source ~/.zshrc
```

- [ ] **Step 2: Pin Python version for the project**

Run: `uv python pin 3.12`
Expected: creates `.python-version` file containing `3.12`.

- [ ] **Step 3: Commit Python pin**

```bash
git add .python-version
git commit -m "chore: pin Python 3.12 via uv"
```

---

### Task 3: Create venv and install package in editable mode

- [ ] **Step 1: Create the virtualenv**

Run: `uv venv`
Expected: creates `.venv/` using Python 3.12 (per `.python-version`). Prints activation hint.

- [ ] **Step 2: Install package with dev extras (editable)**

Run: `uv pip install -e ".[dev]"`
Expected: installs `toolkitsy` in editable mode plus `pytest`, `pytest-cov`, `ruff`.

- [ ] **Step 3: Activate the venv (for interactive use)**

Run: `source .venv/bin/activate`
Expected: shell prompt shows venv prefix; `which python` points inside `.venv/`.

- [ ] **Step 4: Verify smoke tests from 01_a now pass**

Run: `pytest tests/test_package.py -v`
Expected: PASS — both `test_package_exposes_version` and `test_version_is_semver_like`.

---

### Task 4: Generate and commit `uv.lock`

- [ ] **Step 1: Generate lock file**

Run: `uv lock`
Expected: writes `uv.lock` to repo root.

- [ ] **Step 2: Commit lock file**

```bash
git add uv.lock
git commit -m "chore: add uv.lock for reproducible dev installs"
```

---

## Self-Review Notes

- `uv.lock` committed → solves Req #5 (dependency version determinism for dev).
- `.gitignore` excludes `.venv/` but `uv.lock` is intentionally tracked.
- Package is installed editable: source edits in `src/toolkitsy/` are immediately importable.
- No placeholders.

## Notes for downstream consumers

When other repos want to install `toolkitsy` (after the repo is pushed to GitHub):

```bash
# Pip:
pip install "toolkitsy @ git+https://github.com/shyinlim/toolkitsy.git"
# Pinned to a tag:
pip install "toolkitsy @ git+https://github.com/shyinlim/toolkitsy.git@v0.1.0"
# uv:
uv pip install "toolkitsy @ git+https://github.com/shyinlim/toolkitsy.git"
```

This works without any access token because the repo is public.
