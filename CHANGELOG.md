# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project skeleton (`src/` layout, namespace package `toolkitsy`)
- Build backend: `hatchling` with `hatch-vcs` for git-tag-driven versioning
- `pyproject.toml` with PEP 621 metadata, dev extras (pytest, pytest-cov, ruff)
- Smoke tests verifying package importability and PEP 440 version string
- GitHub Actions CI workflow: ruff lint, ruff format check, pytest on Python 3.12 + 3.13
- GitHub Actions release workflow: verify → build → TestPyPI → PyPI via OIDC trusted publishing
- `VERSIONING.md` documenting the tag-driven release procedure
- `uv.lock` committed for reproducible dev installs
