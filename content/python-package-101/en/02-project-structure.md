---
title: Project Structure — src layout and pyproject.toml
series: python-package-101
episode: 2
language: en
status: content-ready
targets:
  tistory: true
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
last_reviewed: '2026-05-04'
seo_description: src layout separates source code from the project root to enforce
  install-before-test, and pyproject.toml defines how to build.
---

# Project Structure — src layout and pyproject.toml

> Python Package 101 series (2/10)

---

<!-- a-grade-intro:begin -->

## Key Questions

- What is the difference between flat layout and src layout?
- What is `pyproject.toml` and why does it replace `setup.py`?
- What goes in `[build-system]` and `[project]`?
- What does a minimal pyproject.toml look like?

> src layout separates source code from the project root to enforce install-before-test, and pyproject.toml defines how to build the package.

<!-- a-grade-intro:end -->

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

<!-- toc:begin -->
## Series Table of Contents

- [What Is a Python Package?](./01-what-is-a-python-package.md)
- **Project Structure — src layout and pyproject.toml (current)**
- Dependency Management — venv, pip, uv, requirements (upcoming)
- Building Packages — wheel and sdist (upcoming)
- Publishing to PyPI — from TestPyPI to production (upcoming)
- Versioning and Releases (upcoming)
- CLI Packages (upcoming)
- Type Hints and Static Analysis (upcoming)
- Documentation — README, MkDocs, API Reference (upcoming)
- Production Package Template (upcoming)

<!-- toc:end -->

## References

- [Python Packaging User Guide - Project Structure](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [setuptools - src layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html)
- [Hynek Schlawack - Testing & Packaging](https://hynek.me/articles/testing-packaging/)

Tags: Python, pyproject.toml, src layout, Project Structure, Packaging, setuptools
