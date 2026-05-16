# Versioning Policy

`toolkitsy` follows [semantic versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

## Single source of truth: the git tag

The version is **derived from git tags** via [`hatch-vcs`](https://github.com/ofek/hatch-vcs). There is no version constant to bump manually.

- A tagged commit (e.g. `v0.1.0`) produces version `0.1.0`.
- An untagged commit after `v0.1.0` produces a dev version, e.g. `0.1.1.dev3+gabc1234`.
- Before the first tag exists, the fallback version `0.0.1` is used (configured in `pyproject.toml`).

`hatch-vcs` writes the resolved version into `src/toolkitsy/_version.py` at build/install time. That file is **generated** and gitignored — never edit or commit it.

## Release procedure

```bash
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push && git push --tags
```

That's it. The CI release workflow (`.github/workflows/release.yml`) picks up the `v*` tag, builds the sdist + wheel with version `X.Y.Z` baked in, and publishes to PyPI.

Downstream consumers can pin:

```bash
pip install "toolkitsy==X.Y.Z"
# or, pre-PyPI:
pip install "toolkitsy @ git+https://github.com/shyinlim/toolkitsy.git@vX.Y.Z"
```

## Why not manual `_version.py` or date+hash?

- **Manual `_version.py`:** Footgun — you can tag `v0.1.0` but forget to bump the file, producing a wheel whose internal version disagrees with the tag.
- **Date+hash (`YYYY.MM.DD+sha`):** Convenient but unpinnable. PEP 440 ordering surprises consumers (`1.0.0 < 2026.05.16+abc1234`), and pip can't reliably resolve such versions.

`hatch-vcs` gives you the convenience of "tag = version" with the discipline of clean semver.
