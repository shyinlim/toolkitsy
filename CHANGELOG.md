# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0](https://github.com/shyinlim/toolkitsy/compare/v0.1.0...v0.2.0) (2026-05-23)


### Added

* streamline release pipeline by removing TestPyPI publication ([54d2ffb](https://github.com/shyinlim/toolkitsy/commit/54d2ffbee7cbdbf6fce92f9a624b8792075ca42a))

## 0.1.0 (2026-05-17)


### Added

* implement configurable logger with correlation IDs ([7fffd15](https://github.com/shyinlim/toolkitsy/commit/7fffd1552dde67a043601d01f49bd2c3ed02d14f))
* implement configurable logger with correlation IDs ([4649dfc](https://github.com/shyinlim/toolkitsy/commit/4649dfc2547e8f21ae4a1026208a1a636ec152c7))
* setup packaging backend, release automation, and CI pipelines ([2806fb3](https://github.com/shyinlim/toolkitsy/commit/2806fb3fd478d930b260055260337c0dd99282a6))
* setup pre-commit hooks for ruff linting and formatting ([378bac2](https://github.com/shyinlim/toolkitsy/commit/378bac2c4016cc40b866b9e7d593288d3b88ca62))


### Documentation

* clarify library purpose in documentation ([517d7e3](https://github.com/shyinlim/toolkitsy/commit/517d7e3e7fa4e7185e413c9df6128264cb4c0a93))
* create repository scaffolding and development planning files ([4be1bf0](https://github.com/shyinlim/toolkitsy/commit/4be1bf079201ebb07fd8f567ff87006e2162e30f))
* scaffold superpowers specs/plans for logger work ([c14e1cd](https://github.com/shyinlim/toolkitsy/commit/c14e1cd1e5534bb89e18ff66d2bdd8d8d850a520))

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
