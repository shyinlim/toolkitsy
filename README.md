# toolkitsy

Personal Python toolkit. A namespace package for cross-repo utilities — logger first, more modules to come (http client, database helpers, etc.).

## Install

```bash
pip install toolkitsy
```

Pin to a specific version:

```bash
pip install toolkitsy==0.1.0
```

With uv:

```bash
uv pip install toolkitsy
```

Install an unreleased commit directly from GitHub (for pre-PyPI testing):

```bash
pip install "toolkitsy @ git+https://github.com/shyinlim/toolkitsy.git@<tag-or-sha>"
```

## Modules

| Module             | Status   | Extras flag           |
|--------------------|----------|-----------------------|
| `toolkitsy.logger` | planned  | (none — stdlib only)  |

Future modules will be opt-in via extras, e.g. `pip install "toolkitsy[db]"`.

## Version

```python
import toolkitsy
print(toolkitsy.__version__)
```

Versioning policy: see [`VERSIONING.md`](VERSIONING.md).

## Development

```bash
git clone git@github.com:shyinlim/toolkitsy.git
cd toolkitsy
uv venv
uv pip install -e ".[dev]"
uv run pytest
uv run ruff check .
```

## License

MIT — see [`LICENSE`](LICENSE).
