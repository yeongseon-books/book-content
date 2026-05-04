---
title: What Is a Python Package?
series: python-package-101
episode: 1
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
- Package
- Module
- Import
- pip
- Library
last_reviewed: '2026-05-04'
seo_description: A Python package bundles reusable code for sharing. Everything you
  import is a package.
---

# What Is a Python Package?

> Python Package 101 series (1/10)

---

<!-- a-grade-intro:begin -->

## Key Questions

- What is the difference between a module and a package?
- What happens when you run `import requests`?
- What does `pip install` actually install?
- Why should you turn your code into a package?

> A Python package bundles reusable code for sharing. Everything you `import` is a package.

<!-- a-grade-intro:end -->

## What you will learn

- The definitions of module, package, library, and distribution
- The import search path (`sys.path`)
- Where `pip install` puts packages and how it works
- When to package your own code

## Why it matters

As a project grows, you split code across files and `import` between them. That is modules. Bundle modules together and you have a package. Copying shared code across projects means fixing a bug requires changes everywhere.

> You have the same utility functions copied into three projects. You find a bug but only patch two of them. The third causes an outage in production.

Turn it into a package, fix it in one place, and run `pip install --upgrade` in every project.

## Mental Model

> A Python package is a LEGO set. A single brick (module) holds a specific feature. Bricks grouped into a set (package) form a theme. Upload the set to a store (PyPI) and anyone can grab it.

```text
Module              Package                  Distribution
──────              ───────                  ────────────
utils.py    ->     mylib/               ->  mylib-1.0.0.tar.gz
                     __init__.py             (uploaded to PyPI)
                     utils.py
                     models.py
```

## Core Concepts

| Term | Description | Example |
|---|---|---|
| module | A single `.py` file | `utils.py` |
| package | A directory with `__init__.py` | `mylib/` |
| library | Informal name for a package | `requests`, `flask` |
| distribution | An installable archive | `mylib-1.0.0.tar.gz` |
| PyPI | Python Package Index, the package repository | pypi.org |

## Before / After

**Before (copy-paste code)**

```text
project-a/utils.py   # copy 1
project-b/utils.py   # copy 2
project-c/utils.py   # copy 3
# -> Fix a bug? Edit all three.
```

**After (packaged)**

```text
mylib/               # one package
  utils.py

project-a/           # pip install mylib
project-b/           # pip install mylib
project-c/           # pip install mylib
# -> Fix mylib once, pip install --upgrade everywhere
```

## Step-by-step practice

### Step 1. Create a module

```python
# ~/practice/python-pkg/calculator.py
def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b
```

```python
# ~/practice/python-pkg/main.py
from calculator import add, subtract

print(add(3, 5))        # 8
print(subtract(10, 4))  # 6
```

### Step 2. Create a package structure

```bash
mkdir -p ~/practice/python-pkg/mymath
cat > ~/practice/python-pkg/mymath/__init__.py << 'EOF'
from .calculator import add, subtract
EOF

cat > ~/practice/python-pkg/mymath/calculator.py << 'EOF'
def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b
EOF
```

```python
# ~/practice/python-pkg/main.py
from mymath import add, subtract

print(add(3, 5))        # 8
```

### Step 3. Inspect sys.path

```python
import sys
for path in sys.path:
    print(path)
# '' (current directory)
# /usr/lib/python3.11
# /usr/lib/python3.11/lib-dynload
# /home/user/.local/lib/python3.11/site-packages
```

### Step 4. Inspect installed packages

```bash
pip list                          # List installed packages
pip show requests                 # Details for requests
pip show requests | grep Location # Installation path
# Location: /home/user/.local/lib/python3.11/site-packages
```

### Step 5. Look inside an installed package

```bash
python -c "import requests; print(requests.__file__)"
# /home/user/.local/lib/python3.11/site-packages/requests/__init__.py

ls /home/user/.local/lib/python3.11/site-packages/requests/
# __init__.py  api.py  models.py  sessions.py  ...
```

## What to notice in this code

- `__init__.py` is what makes Python treat a directory as a package
- `from .calculator import add` uses a relative import — the `.` refers to the current package
- The order of `sys.path` determines Python's module search priority
- `pip install` ultimately copies files into `site-packages/`

## Common mistakes

### Mistake 1. Forgetting __init__.py

Without `__init__.py`, Python 3.3+ treats the directory as a namespace package, but explicitly including it is the convention. Some tools fail to recognize the package without it.

### Mistake 2. Naming a module the same as a standard library

```python
# If you create email.py
import email  # Your file shadows the standard library
```

Avoid names like `random.py`, `json.py`, `os.py`.

### Mistake 3. Circular imports

```python
# a.py: from b import func_b
# b.py: from a import func_a
# -> ImportError
```

Keep dependency direction one-way, or extract shared code into a common module.

### Mistake 4. Editing files in site-packages directly

Changes to installed packages get overwritten on the next `pip install`.

### Mistake 5. Confusing hyphens and underscores in package names

```bash
pip install my-package      # Install name: hyphen
import my_package           # Import name: underscore
```

## Practical applications

- **Internal shared libraries**: Unify auth, logging, and config management as a package
- **Microservice shared code**: Distribute gRPC stubs and data models as a package
- **CLI tools**: `pip install` turns your code into a terminal command
- **Open source**: Upload to PyPI and anyone can `pip install` it
- **Shared test fixtures**: Bundle test utilities used across multiple projects

## How practitioners think about this

"Is this code used in two or more projects?" — if so, it is time to package it. Copy-pasting means maintenance cost grows linearly with the number of projects. A package centralizes management, and versioning ensures stability.

At first, packaging feels like overhead. In reality, a single `pyproject.toml` is all you need. This series walks through the process step by step.

## Checklist

- [ ] You can explain the difference between a module, a package, and a distribution
- [ ] You understand the role of `__init__.py`
- [ ] You can inspect the module search path with `sys.path`
- [ ] You can find the install location of a package with `pip show`
- [ ] You can judge when code should be turned into a package

## Exercises

1. Create a `mymath/` package with `multiply` and `divide` functions, then import them from `main.py`.
2. Print `sys.path` and explore the file structure of one installed package in `site-packages`.
3. Create a file named `string.py` and run `import string` to observe what happens.

## Summary and next

- A module is a `.py` file; a package is a directory with `__init__.py`.
- Python searches for modules in `sys.path` order.
- `pip install` copies package files into `site-packages/`.
- Code used in two or more projects should become a package.
- Package names must not collide with standard library modules.

The next post covers **project structure** — src layout and pyproject.toml.

<!-- toc:begin -->
## Series Table of Contents

- **What Is a Python Package? (current)**
- Project Structure — src layout and pyproject.toml (upcoming)
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

- [Python Packaging User Guide](https://packaging.python.org/)
- [Python Modules Tutorial](https://docs.python.org/3/tutorial/modules.html)
- [Real Python - Python Packages](https://realpython.com/python-modules-packages/)
- [PyPI - Python Package Index](https://pypi.org/)

Tags: Python, Package, Module, Import, pip, Library
