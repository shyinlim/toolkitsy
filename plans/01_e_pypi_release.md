# 01_e — PyPI Publish (Trusted Publishing) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish `toolkitsy` to PyPI so consumers can `pip install toolkitsy`. Use PyPI **Trusted Publishing (OIDC)** — no API tokens stored anywhere — and wire a GitHub Actions workflow that builds and publishes when a `v*` tag is pushed.

**Architecture:** Two-step verification before automation. First a manual one-shot release via TestPyPI to validate the build pipeline. Then GitHub Actions `release.yml`, triggered by `v*` tags, builds `sdist + wheel` with `uv build` and publishes via `pypa/gh-action-pypi-publish@release/v1`. Trust between the GitHub workflow and PyPI is brokered by OIDC — no long-lived secrets.

**Tech Stack:** PyPI Trusted Publishing (OIDC), `uv build`, `pypa/gh-action-pypi-publish` GitHub Action.

---

## Prerequisite: Plans `01_a` → `01_d` are complete

The repo must already have: working `pyproject.toml`, `src/toolkitsy/`, `_version.py = "0.0.1"`, CI green, tag `v0.0.1` pushed.

---

## File Structure

```
toolkitsy/
└── .github/
    └── workflows/
        └── release.yml        # NEW: build + publish on tag push
```

Plus one-time setup outside the repo:
- PyPI account + project registration
- TestPyPI account
- Trusted Publisher entry on PyPI/TestPyPI pointing at this GitHub workflow

---

### Task 1: Verify the name `toolkitsy` is available on PyPI

- [ ] **Step 1: Open PyPI search page**

Visit: `https://pypi.org/project/toolkitsy/`

Expected: **404 Not Found** (name is free). If 200 (someone else owns it), STOP — pick a different name, then update `pyproject.toml` `name = "..."` and every reference in `README.md` and other plan files before proceeding.

- [ ] **Step 2: Check TestPyPI too**

Visit: `https://test.pypi.org/project/toolkitsy/`

Expected: 404. Same fail-stop rule.

---

### Task 2: Create PyPI and TestPyPI accounts (manual, one-time)

- [ ] **Step 1: Register PyPI account**

Visit `https://pypi.org/account/register/`. Use a real email. **Enable 2FA** — PyPI requires it for publishers.

- [ ] **Step 2: Register TestPyPI account**

Visit `https://test.pypi.org/account/register/`. Different database from PyPI, register separately. Enable 2FA.

---

### Task 3: Build the package locally and validate metadata

- [ ] **Step 1: Build sdist + wheel**

Run: `uv build`
Expected: creates `dist/toolkitsy-0.0.1-py3-none-any.whl` and `dist/toolkitsy-0.0.1.tar.gz`.

- [ ] **Step 2: Inspect the wheel contents**

Run: `unzip -l dist/toolkitsy-0.0.1-py3-none-any.whl`
Expected: contains `toolkitsy/__init__.py`, `toolkitsy/_version.py`, `toolkitsy-0.0.1.dist-info/METADATA`.

- [ ] **Step 3: Validate metadata with twine**

Run:
```bash
uv pip install twine
uv run twine check dist/*
```
Expected: `PASSED` for both files. Catches malformed README / missing metadata before upload.

- [ ] **Step 4: Add `dist/` to `.gitignore` (it is already, but verify)**

Run: `grep -q '^dist/' .gitignore && echo OK || echo MISSING`
Expected: `OK`. If `MISSING`, append `dist/` to `.gitignore` and commit.

---

### Task 4: First manual upload to **TestPyPI** to prove the pipeline

This is a smoke test before automating. TestPyPI is a separate ecosystem — uploading here does not affect real PyPI.

- [ ] **Step 1: Create an API token on TestPyPI**

1. Log into `https://test.pypi.org/manage/account/`.
2. Account settings → API tokens → **Add API token**.
3. Name: `toolkitsy-bootstrap`. Scope: **Entire account** (first upload only — we will narrow it after the project exists).
4. Copy the token (starts with `pypi-`). It is shown **once**.

- [ ] **Step 2: Upload to TestPyPI**

Run:
```bash
uv run twine upload --repository testpypi dist/*
```
When prompted:
- Username: `__token__`
- Password: paste the token from Step 1

Expected: `View at: https://test.pypi.org/project/toolkitsy/0.0.1/`

- [ ] **Step 3: Install from TestPyPI in a throwaway venv**

```bash
cd /tmp
uv venv toolkitsy-testpypi
source toolkitsy-testpypi/bin/activate
pip install --index-url https://test.pypi.org/simple/ toolkitsy==0.0.1
python -c "import toolkitsy; print(toolkitsy.__version__)"
```
Expected: prints `0.0.1`.

- [ ] **Step 4: Cleanup smoke venv**

```bash
deactivate
rm -rf /tmp/toolkitsy-testpypi
```

- [ ] **Step 5: Revoke the bootstrap token**

On TestPyPI → API tokens → delete the `toolkitsy-bootstrap` token. We will use Trusted Publishing from now on; no token needed.

---

### Task 5: Configure Trusted Publishing on TestPyPI

Trusted Publishing lets GitHub Actions authenticate to PyPI/TestPyPI via OIDC. No secrets stored in the repo.

- [ ] **Step 1: Register the project's Trusted Publisher on TestPyPI**

1. Visit `https://test.pypi.org/manage/project/toolkitsy/settings/publishing/`.
2. Under **Trusted publishers** → **Add a new publisher** → GitHub.
3. Fill in:
   - **PyPI Project Name:** `toolkitsy`
   - **Owner:** `shyinlim`
   - **Repository name:** `toolkitsy`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi` (leave blank for now; we add the environment in Task 7)
4. Save.

---

### Task 6: First upload to **real PyPI** (manual, one-time)

Real PyPI requires the project to exist before Trusted Publishing can be configured (the publisher entry attaches to an existing project name). We do this once by hand, then never again.

- [ ] **Step 1: Create a scoped API token on PyPI**

1. Log into `https://pypi.org/manage/account/`.
2. API tokens → Add API token → name `toolkitsy-bootstrap`, scope **Entire account** (we will narrow after upload).
3. Copy the token.

- [ ] **Step 2: Upload to PyPI**

Run:
```bash
uv run twine upload dist/*
```
Username `__token__`, password = the token.

Expected: `View at: https://pypi.org/project/toolkitsy/0.0.1/`

- [ ] **Step 3: Install from real PyPI**

```bash
cd /tmp
uv venv toolkitsy-pypi
source toolkitsy-pypi/bin/activate
pip install toolkitsy==0.0.1
python -c "import toolkitsy; print(toolkitsy.__version__)"
deactivate
rm -rf /tmp/toolkitsy-pypi
```
Expected: `0.0.1` — and yes, the short `pip install toolkitsy` form now works. ✅

- [ ] **Step 4: Configure Trusted Publishing on real PyPI**

1. Visit `https://pypi.org/manage/project/toolkitsy/settings/publishing/`.
2. Add a GitHub publisher, same fields as Task 5 Step 1:
   - Owner: `shyinlim`
   - Repository: `toolkitsy`
   - Workflow: `release.yml`
   - Environment: `pypi`
3. Save.

- [ ] **Step 5: Revoke the bootstrap token**

PyPI account settings → API tokens → delete `toolkitsy-bootstrap`. From now on, only OIDC (no secrets) publishes.

---

### Task 7: Add the GitHub Actions release workflow

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Create the workflow file**

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  build:
    name: Build distribution
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

      - name: Build sdist and wheel
        run: uv build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish-testpypi:
    name: Publish to TestPyPI
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: testpypi
      url: https://test.pypi.org/project/toolkitsy/
    permissions:
      id-token: write  # required for Trusted Publishing OIDC
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

  publish-pypi:
    name: Publish to PyPI
    needs: publish-testpypi
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/project/toolkitsy/
    permissions:
      id-token: write
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 2: Create GitHub Environments**

1. On GitHub: `https://github.com/shyinlim/toolkitsy/settings/environments`.
2. Click **New environment** → name `testpypi` → Save.
3. Click **New environment** → name `pypi` → Save.
4. Optional: add a **required reviewer** (yourself) to the `pypi` environment so production publishes need a click. Recommended.

- [ ] **Step 3: Commit and push the workflow**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add PyPI release workflow with trusted publishing"
git push
```

---

### Task 8: End-to-end automated release for v0.0.2

Prove the automation works by cutting a real release.

- [ ] **Step 1: Bump version**

Edit `src/toolkitsy/_version.py`:

```python
__version__ = "0.0.2"
```

- [ ] **Step 2: Commit, tag, push**

```bash
git commit -am "chore: release v0.0.2"
git tag -a v0.0.2 -m "Release 0.0.2"
git push
git push --tags
```

- [ ] **Step 3: Watch the workflow**

Visit `https://github.com/shyinlim/toolkitsy/actions`. Expected sequence:
1. `Release` workflow starts.
2. `build` job completes (~30s).
3. `publish-testpypi` runs; check `https://test.pypi.org/project/toolkitsy/0.0.2/`.
4. `publish-pypi` waits for required reviewer approval (if configured); approve it.
5. `publish-pypi` completes; check `https://pypi.org/project/toolkitsy/0.0.2/`.

- [ ] **Step 4: Verify short install command works**

```bash
cd /tmp
uv venv toolkitsy-final
source toolkitsy-final/bin/activate
pip install toolkitsy==0.0.2
python -c "import toolkitsy; print(toolkitsy.__version__)"
deactivate
rm -rf /tmp/toolkitsy-final
```
Expected: prints `0.0.2`. The short form `pip install toolkitsy` is now permanently the recommended path.

- [ ] **Step 5: Update README install instructions**

Modify `README.md` install section:

```markdown
## Install

```bash
pip install toolkitsy
```

Or install from a specific git tag (pre-PyPI consumers or unreleased commits):

```bash
pip install "toolkitsy @ git+https://github.com/shyinlim/toolkitsy.git@v0.0.2"
```
```

Commit:

```bash
git add README.md
git commit -m "docs: update README — pip install toolkitsy is the primary path"
git push
```

---

## Self-Review Notes

- Req #1 (no token for consumers): consumers now use `pip install toolkitsy`, no GitHub credentials at all. Publishers use OIDC, also no stored secrets.
- Project name conflict checked at Task 1 — fail-stop.
- TestPyPI step (Task 4) catches build/metadata errors before they pollute real PyPI.
- Bootstrap tokens are revoked after first manual upload — repo has zero long-lived secrets.
- `pypi` environment has optional required-reviewer gate so production publishes are explicit.
- No placeholders. Every step has the exact command, URL, or code.

## Release procedure going forward (cheat sheet)

```bash
# 1. Bump
edit src/toolkitsy/_version.py  # change X.Y.Z

# 2. Tag and push
git commit -am "chore: release vX.Y.Z"
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push && git push --tags

# 3. Approve the pypi environment in GitHub Actions UI when prompted.
# Done — pip install toolkitsy==X.Y.Z works within a minute.
```
