# Quality Tooling & CI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire up `pytest` configuration, `ruff` for lint+format, and a GitHub Actions workflow that runs lint and tests on every push and PR to `master`.

**Architecture:** All tool config lives in `pyproject.toml` (single source of truth). CI uses `astral-sh/setup-uv@v3` to install uv quickly, then runs `uv sync` for cached deps, `ruff check`, `ruff format --check`, and `pytest`. Matrix kept simple (Python 3.12 only for v1).

**Tech Stack:** pytest, pytest-cov, ruff, GitHub Actions.

---

## File Structure

```
toolkitsy/
├── pyproject.toml             # MODIFY: add [tool.pytest.ini_options] and [tool.ruff]
└── .github/
    └── workflows/
        └── ci.yml             # NEW: lint + test on push/PR
```

---

### Task 1: Add pytest configuration to `pyproject.toml`

**Files:**
- Modify: `pyproject.toml` (append section)

- [ ] **Step 1: Append pytest config**

Add to the end of `pyproject.toml`:

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=toolkitsy",
    "--cov-report=term-missing",
]
```

- [ ] **Step 2: Verify pytest still passes**

Run: `pytest -v`
Expected: PASS, plus a coverage summary printed.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: configure pytest with coverage and strict mode"
```

---

### Task 2: Add ruff configuration to `pyproject.toml`

**Files:**
- Modify: `pyproject.toml` (append section)

- [ ] **Step 1: Append ruff config**

Add to the end of `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "UP",     # pyupgrade
    "SIM",    # flake8-simplify
    "RUF",    # ruff-specific
]
ignore = []

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["B011"]  # allow `assert False` in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

- [ ] **Step 2: Run lint on current code**

Run: `ruff check .`
Expected: PASS (no findings) on the small skeleton.

- [ ] **Step 3: Run formatter check**

Run: `ruff format --check .`
Expected: PASS. If it complains, run `ruff format .` and re-commit.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "chore: configure ruff lint and format"
```

---

### Task 3: Add GitHub Actions CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create workflow file**

```yaml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --extra dev

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Pytest
        run: uv run pytest
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow for lint and tests"
```

- [ ] **Step 3: Push and verify on GitHub**

Run: `git push`
Expected: After push, visit `https://github.com/shyinlim/toolkitsy/actions` and confirm the `CI` workflow runs and passes.

---

## Self-Review Notes

- Req #4 (unit tests) satisfied: pytest configured, runs in CI.
- Req #5 (other package versions): `uv sync --extra dev` uses `uv.lock` for deterministic CI installs.
- Coverage report visible in CI logs; can later add Codecov if desired.
- No placeholders.
