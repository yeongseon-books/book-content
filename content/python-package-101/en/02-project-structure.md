---
title: "Python Package 101 (2/10): Project Structure — src layout and pyproject.toml"
series: python-package-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- pyproject.toml
- src layout
- Project Structure
- Packaging
- setuptools
last_reviewed: '2026-05-15'
seo_description: src layout separates source code from the project root to enforce
  install-before-test, and pyproject.toml defines how to build.
---

# Python Package 101 (2/10): Project Structure — src layout and pyproject.toml

Project structure is where many packaging bugs begin. If tests read local source by accident, you can ship a package that only works on your machine.

This is the 2nd post in the Python Package 101 series. Here we compare flat layout and src layout, explain why `pyproject.toml` replaced `setup.py`, and build a minimal package skeleton that behaves like a real install.

![Python Package 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/02/02-01-mental-model.en.png)
*Python Package 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What is the difference between flat layout and src layout?
- What is `pyproject.toml` and why does it replace `setup.py`?
- What goes in `[build-system]` and `[project]`?

## What you will learn

- The difference between flat layout and src layout, and when to choose each
- The required sections of pyproject.toml
- How to write a minimal pyproject.toml
- Real-world project directory structures

## Why it matters

A broken project structure leads to import errors, build tools that cannot find files, and tests that fail in CI. Starting with a standard structure prevents these problems.

> You run `pytest` at the project root and everything passes. But after `pip install .`, importing from a different directory fails. The tests were reading local source instead of the installed package.

src layout prevents this structurally.

## Mental Model

> Flat layout displays products right at the storefront. src layout puts them in a warehouse (src/) so they can only be accessed through the shelf (installation). With the warehouse, the illusion of "it works without installation" is impossible.

```text
flat layout              src layout
────────────            ────────────
mylib/                  src/
  __init__.py             mylib/
  core.py                   __init__.py
tests/                      core.py
pyproject.toml          tests/
                        pyproject.toml
```

## Core Concepts

| Term | Description | Notes |
|---|---|---|
| flat layout | Package sits at the project root | Simple but prone to import illusions |
| src layout | Package lives under `src/` | Forces install-before-import |
| pyproject.toml | PEP 518/621 standard project config | Replaces setup.py/setup.cfg |
| build-system | Section specifying build tools | `[build-system]` |
| [project] | Package name, version, dependencies metadata | PEP 621 |

## Before / After

**Before (setup.py + flat layout)**

```python
# setup.py
from setuptools import setup, find_packages
setup(
    name="mylib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests>=2.28"],
)
```

**After (pyproject.toml + src layout)**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mylib"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = ["requests>=2.28"]
```

## Step-by-step practice

### Step 1. Create a src layout project

```bash
mkdir -p ~/practice/mylib-project/src/mylib
mkdir -p ~/practice/mylib-project/tests
cd ~/practice/mylib-project

cat > src/mylib/__init__.py << 'EOF'
"""mylib - A sample Python package."""
__version__ = "0.1.0"
EOF

cat > src/mylib/core.py << 'EOF'
def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"
EOF
```

### Step 2. Write pyproject.toml

```bash
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mylib"
version = "0.1.0"
description = "A sample Python package"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"},
]
dependencies = []

[project.urls]
Repository = "https://github.com/yourname/mylib"
EOF
```

### Step 3. Editable install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

python -c "from mylib.core import greet; print(greet('World'))"
# Hello, World!
```

### Step 4. Add tests

```bash
cat > tests/test_core.py << 'EOF'
from mylib.core import greet

def test_greet():
    assert greet("Alice") == "Hello, Alice!"

def test_greet_empty():
    assert greet("") == "Hello, !"
EOF

pip install pytest
pytest tests/
# 2 passed
```

### Step 5. Configure setuptools package discovery

```toml
# Add to pyproject.toml
[tool.setuptools.packages.find]
where = ["src"]
```

```bash
# Verify install
pip install -e .
python -c "import mylib; print(mylib.__version__)"
# 0.1.0
```

## What to notice in this code

- `[build-system]` specifies the build tool; besides `setuptools`, you can use `hatchling`, `flit-core`, or `pdm-backend`
- `pip install -e .` is an editable install — source changes are reflected without reinstalling
- `where = ["src"]` in `[tool.setuptools.packages.find]` is the key setting for src layout
- `requires-python` specifies the supported Python version range

## Common mistakes

### Mistake 1. Forgetting the where setting in src layout

```toml
# Wrong: cannot find packages under src/
[tool.setuptools.packages.find]

# Correct
[tool.setuptools.packages.find]
where = ["src"]
```

### Mistake 2. Having both setup.py and pyproject.toml

The two files can conflict and confuse build tools. Use pyproject.toml only.

### Mistake 3. Testing local imports without an editable install

Without `pip install -e .`, tests in flat layout pass but fail after actual installation.

### Mistake 4. Putting heavy code in __init__.py

Heavy initialization code in `__init__.py` slows down `import mylib`. Expose only the version and minimal public API.

### Mistake 5. Including the tests directory in the package

If `tests/` is inside `src/`, tests ship with the distribution. Keep tests at the project root.

## Practical applications

- **Internal libraries**: Standardize on src layout + pyproject.toml for faster new-project starts
- **Open source**: Most modern Python projects (black, ruff, httpx) use src layout
- **Monorepos**: src layout prevents path collisions when hosting multiple packages in one repository
- **CI/CD**: `pip install .` as the first gate to confirm the package builds
- **Docker**: `COPY . . && pip install .` installs the package inside the container

## How practitioners think about this

Spending five minutes on structure at the start saves hours of "why won't this import?" later. src layout requires a small extra config (`where = ["src"]`), but structurally prevents the "works locally, fails after install" class of problems.

For the build backend, `setuptools` is the most widely used, but `hatchling` and `flit-core` are worth considering for new projects. Regardless of backend, the `[project]` section is identical.

## Checklist

- [ ] You can explain the difference between flat layout and src layout
- [ ] You can write a minimal pyproject.toml
- [ ] You can do an editable install with `pip install -e .`
- [ ] You understand the roles of `[build-system]` and `[project]`
- [ ] You can verify that tests run against the installed package

## Exercises

1. Create a `myutils` package in src layout with a `string_utils.py` module containing a `capitalize_words` function, and test it.
2. Write a pyproject.toml that includes `description`, `authors`, `license`, and `requires-python`.
3. Create both flat layout and src layout projects, run `pip install -e .`, and compare whether imports work from a different directory.

## Summary and next

- src layout places source under `src/` to prevent direct imports without installation.
- `pyproject.toml` is the PEP 518/621 standard that replaces `setup.py`.
- `[build-system]` defines the build tool; `[project]` defines package metadata.
- `pip install -e .` lets you test imports during development.
- Tests belong outside `src/` to stay out of the distribution.

The next post covers **dependency management** — venv, pip, uv, and requirements.

## Deep Dive into pyproject.toml

`pyproject.toml` combines PEP 518 (build system declaration) and PEP 621 (project metadata). A single file manages build tools, metadata, and tool configuration.

### Full Structure Map

```toml
# === Build System (PEP 518) ===
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

# === Project Metadata (PEP 621) ===
[project]
name = "acme-utils"
version = "0.1.0"
description = "Internal utility library for Acme Corp"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Platform Team", email = "platform@acme.dev"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Typing :: Typed",
]
dependencies = [
    "httpx>=0.27,<0.29",
    "pydantic>=2.5",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.5",
    "mypy>=1.10",
    "build>=1.2",
    "twine>=5.1",
]
docs = [
    "mkdocs>=1.6",
    "mkdocstrings[python]>=0.25",
]

[project.urls]
Homepage = "https://github.com/acme/acme-utils"
Documentation = "https://acme.github.io/acme-utils"
Changelog = "https://github.com/acme/acme-utils/blob/main/CHANGELOG.md"

[project.scripts]
acme = "acme_utils.cli:main"

# === Tool Configuration ===
[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.mypy]
strict = true
```

### `[build-system]` in Detail

| Field | Role | Example |
|---|---|---|
| `requires` | Packages needed to build | `["setuptools>=68", "wheel"]` |
| `build-backend` | Build entry point | `"setuptools.build_meta"` |
| `backend-path` | Custom backend path (rare) | `["."]` |

When you run `pip install .`, pip first creates an isolated environment, installs the packages listed in `requires`, then calls `build_wheel()` or `build_sdist()` from the module pointed to by `build-backend`.

### `[project]` Required vs Optional Fields

```text
Required (for PyPI upload):
├── name          # distribution name
├── version       # semantic version
Effectively required:
├── description   # one-line summary
├── requires-python
Recommended:
├── readme
├── license
├── authors
├── classifiers
├── dependencies
Optional:
├── optional-dependencies
├── urls
├── scripts / gui-scripts
├── entry-points
```

### Build Backend Comparison

| Backend | Pros | Cons |
|---|---|---|
| setuptools | Largest ecosystem, legacy compat | Can require verbose config |
| hatchling | Fast builds, concise config | Relatively new |
| flit-core | Extremely simple | Limited features (no C extensions) |
| maturin | Rust extension builds | Rust-only |
| pdm-backend | pdm ecosystem integration | Proprietary lock format |

```toml
# hatchling example
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/acme_utils"]
```

```toml
# flit-core example
[build-system]
requires = ["flit_core>=3.9,<4"]
build-backend = "flit_core.buildapi"
```

## How src Layout Prevents Import Illusions

In a flat layout, tests can pass locally but fail after installation. Let's reproduce this scenario.

```bash
# flat layout structure
myproject/
├── mylib/
│   ├── __init__.py
│   └── core.py
├── tests/
│   └── test_core.py
└── pyproject.toml
```

```bash
# Running pytest from the project root
cd myproject
pytest tests/
# PASSED - imports mylib/ directly from the current directory

# Trying to import from a different directory (without installation)
cd /tmp
python -c "import mylib"
# ModuleNotFoundError!
```

```bash
# src layout structure
myproject/
├── src/
│   └── mylib/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
└── pyproject.toml
```

```bash
# Running pytest from the project root (without installation)
cd myproject
pytest tests/
# ModuleNotFoundError - src/mylib/ is not on sys.path!
# -> You MUST run pip install -e . before testing
```

The src layout makes it structurally impossible to have "tests pass without installation." You always test under the same conditions as CI.

## Complete Real-World Project Directory

```text
acme-utils/
├── src/
│   └── acme_utils/
│       ├── __init__.py          # __version__, public API
│       ├── py.typed             # PEP 561 marker
│       ├── core.py              # core business logic
│       ├── config.py            # configuration loading
│       ├── exceptions.py        # custom exceptions
│       └── _internal.py         # internal only (_prefix)
├── tests/
│   ├── conftest.py              # shared fixtures
│   ├── test_core.py
│   └── test_config.py
├── docs/
│   ├── index.md
│   └── api.md
├── pyproject.toml               # single config file
├── README.md                    # rendered on PyPI
├── CHANGELOG.md                 # release history
├── LICENSE
└── .github/
    └── workflows/
        └── ci.yml               # CI pipeline
```

### Role of Each File

| File | Role |
|---|---|
| `py.typed` | Empty file. Declares this package provides type hints (PEP 561) |
| `_internal.py` | `_` prefix signals this is not for external use |
| `conftest.py` | Module auto-loaded by pytest for shared fixtures |
| `CHANGELOG.md` | Per-version changes. Keep a Changelog format recommended |

## Migrating from setup.py to pyproject.toml

A step-by-step procedure for moving a legacy project to modern structure.

### Before Migration (Legacy)

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="acme-utils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27",
        "pydantic>=2.5",
    ],
    python_requires=">=3.10",
)
```

### After Migration (Modern)

```toml
# pyproject.toml - content migrated from setup.py
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "acme-utils"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.5",
]

[tool.setuptools.packages.find]
where = ["src"]
```

### Migration Checklist

```bash
# 1. Create pyproject.toml
# 2. Move source under src/
mkdir -p src
mv acme_utils src/

# 3. Remove setup.py (or keep as shim for legacy tool compat)
cat > setup.py << 'EOF'
from setuptools import setup
setup()
EOF

# 4. Verify editable install
pip install -e .
python -c "import acme_utils; print(acme_utils.__version__)"

# 5. Verify tests pass
pytest

# 6. Verify build
python -m build
python -m twine check dist/*
```

## GitHub Actions CI Integration

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: python -m pip install -e ".[dev]"
      - run: pytest --cov=acme_utils --cov-report=term-missing
      - run: ruff check .
      - run: mypy src
      - run: python -m build
      - run: python -m twine check dist/*
```

This workflow runs lint, type checking, tests, and build verification across three Python versions. `pip install -e ".[dev]"` installs all development dependencies in one command.

## Dynamic Versioning in pyproject.toml

Instead of hardcoding the version in `pyproject.toml`, production projects often pull it dynamically.

### setuptools-scm: Extract Version from Git Tags

```toml
[build-system]
requires = ["setuptools>=68", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
name = "acme-utils"
dynamic = ["version"]

[tool.setuptools_scm]
write_to = "src/acme_utils/_version.py"
```

```bash
git tag v0.1.0
python -m build
# Version 0.1.0 is automatically set at build time
```

### hatchling Dynamic Version

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "acme-utils"
dynamic = ["version"]

[tool.hatch.version]
source = "vcs"
```

### Reading Version in __init__.py

```python
# src/acme_utils/__init__.py
try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"
```

With this pattern, the Git tag becomes the single source of truth for versioning. The version in `pyproject.toml`, `__init__.py`, and the Git tag always stay in sync.

## Package Structure in a Monorepo

Monorepo structures with multiple packages in a single repository are common in production.

```text
monorepo/
├── packages/
│   ├── acme-core/
│   │   ├── src/acme_core/
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── acme-auth/
│   │   ├── src/acme_auth/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── acme-cli/
│       ├── src/acme_cli/
│       ├── tests/
│       └── pyproject.toml
├── pyproject.toml              # root: dev tool config only
└── Makefile
```

```toml
# packages/acme-auth/pyproject.toml
[project]
name = "acme-auth"
dependencies = [
    "acme-core",  # reference another package in the same monorepo
]
```

```bash
# Install all packages as editable during development
pip install -e packages/acme-core
pip install -e packages/acme-auth
pip install -e packages/acme-cli
```

## EditorConfig and Dev Tool Configuration

Beyond `pyproject.toml`, the project root needs configuration files that keep the development experience consistent across team members.

```text
acme-utils/
├── .editorconfig           # editor-agnostic settings
├── .gitignore              # Git ignore patterns
├── .pre-commit-config.yaml # automated checks before commit
└── pyproject.toml          # all Python tool config unified
```

```ini
# .editorconfig
root = true

[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
indent_style = space
indent_size = 4

[*.{yml,yaml,toml}]
indent_size = 2
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.5
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
```

These configurations reduce code style differences between team members and eliminate time spent on formatting issues during code review.

## Answering the Opening Questions

- **What's the difference between flat layout and src layout?**
  - Flat layout places the package directory directly at the project root, making it importable without installation. Src layout puts the package under `src/`, making it unimportable without `pip install -e .`. This difference structurally prevents "works locally but fails in CI" problems.
- **What is `pyproject.toml` and why does it replace `setup.py`?**
  - `pyproject.toml` is the PEP 518/621 standard that places both build system and metadata in a single declarative TOML file. `setup.py` could execute arbitrary Python code, creating security and reproducibility issues, while `pyproject.toml` enables static analysis and guarantees inter-tool interoperability.
- **What goes in `[build-system]` and `[project]`?**
  - `[build-system]` declares the build tool (`requires`) and entry point (`build-backend`). pip reads this to build in an isolated environment. `[project]` contains metadata like package name, version, dependencies, and Python version requirements—the source of truth for information displayed on the PyPI page.

<!-- toc:begin -->
## In this series

- [Python Package 101 (1/10): What Is a Python Package?](./01-what-is-a-python-package.md)
- **Python Package 101 (2/10): Project Structure — src layout and pyproject.toml (current)**
- Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements (upcoming)
- Python Package 101 (4/10): Building Packages — wheel and sdist (upcoming)
- Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production (upcoming)
- Python Package 101 (6/10): Versioning and Releases (upcoming)
- Python Package 101 (7/10): CLI Packages (upcoming)
- Python Package 101 (8/10): Type Hints and Static Analysis (upcoming)
- Python Package 101 (9/10): Documentation — README, MkDocs, API Reference (upcoming)
- Python Package 101 (10/10): Production Package Template (upcoming)

<!-- toc:end -->

## References

- [Python Packaging User Guide - Project Structure](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [setuptools - src layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html)
- [Hynek Schlawack - Testing & Packaging](https://hynek.me/articles/testing-packaging/)

Tags: Python, Packaging, PyPI, pyproject.toml
