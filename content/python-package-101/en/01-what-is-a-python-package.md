---
title: "Python Package 101 (1/10): What Is a Python Package?"
series: python-package-101
episode: 1
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
- Package
- Module
- Import
- pip
- Library
last_reviewed: '2026-05-15'
seo_description: A Python package bundles reusable code for sharing. Everything you
  import is a package.
---

# Python Package 101 (1/10): What Is a Python Package?

As soon as a Python project stops fitting in one file, you start importing code across modules. That is usually the point where packaging stops feeling optional and starts shaping how you share and maintain code.

This is the first post in the Python Package 101 series. Here we define modules, packages, and distributions, trace what `pip install` actually installs, and set the baseline for the rest of the series.

![Python Package 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/01/01-01-mental-model.en.png)
*Python Package 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What is the difference between a module and a package?
- What happens when you run `import requests`?
- What does `pip install` actually install?

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

## How the Import System Works Internally

When you run `import requests`, the Python interpreter performs the following steps in order.

### Step 1: Check the sys.modules Cache

```python
import sys

# Modules already imported are stored in the cache.
print("requests" in sys.modules)  # Before first import: False

import requests
print("requests" in sys.modules)  # After import: True

# A second import returns immediately from the cache.
import requests  # Does not re-read the file
```

Python looks in the `sys.modules` dictionary first. If the module is already there, it returns the cached module object without touching the file system. This is why top-level code in a module executes only once during the lifetime of the process.

### Step 2: Finders and Loaders

```python
import sys

for finder in sys.meta_path:
    print(type(finder).__name__)
# BuiltinImporter   - built-in modules (sys, builtins)
# FrozenImporter    - frozen modules
# PathFinder        - sys.path-based search
```

`sys.meta_path` finders are tried in order. `PathFinder` runs last, iterating over each entry in `sys.path` looking for `.py` files or package directories.

### Step 3: Module Execution and Binding

```python
# Simplified view of what Python does internally:
# 1. Create an empty module object
# 2. Register it in sys.modules (prevents circular import loops)
# 3. Execute the module file (top-level code in .py)
# 4. Bind the name in the caller's namespace

# What this means:
import mylib          # 'mylib' name bound in current namespace
from mylib import f   # only 'f' is bound; 'mylib' is not
```

### Full Import Flow Diagram

```text
import mylib
    │
    ▼
In sys.modules? ──Yes──> Return cached object
    │ No
    ▼
Iterate finders in sys.meta_path
    │
    ▼
PathFinder: search each path in sys.path
    │
    ▼
Found mylib/ directory (__init__.py exists)
    │
    ▼
Create module object → register in sys.modules
    │
    ▼
Execute __init__.py
    │
    ▼
Bind 'mylib' in caller's namespace
```

## Namespace Packages vs Regular Packages

Since Python 3.3, directories without `__init__.py` can be recognized as namespace packages. However, the two kinds behave differently.

| Aspect | Regular Package | Namespace Package |
|---|---|---|
| `__init__.py` | Required | Absent |
| `__path__` | Single directory | Multiple directories possible |
| Initialization code | Written in `__init__.py` | Not possible |
| Tool compatibility | All tools support it | Some tools lack support |
| Use case | General packages | Plugins, distributed packages |

```python
# Regular package: mylib/__init__.py exists
import mylib
print(mylib.__file__)
# /home/user/.local/lib/python3.11/site-packages/mylib/__init__.py

# Namespace package: no __init__.py
import google.cloud  # google is a namespace package
print(google.__path__)
# _NamespacePath(['/path/to/site-packages/google'])
# Multiple distributions each install sub-packages under google/
```

The canonical real-world example of namespace packages is the `google-cloud-*` family. `google.cloud.storage` and `google.cloud.bigquery` are separate distributions that share the same `google.cloud` namespace.

**Recommendation**: For most projects, use a Regular Package (with `__init__.py`). Choose Namespace Package only when multiple independent distributions need to share one top-level namespace.

## `__init__.py` Usage Patterns

`__init__.py` does more than just declare "this directory is a package."

### Pattern 1: Define the Public API

```python
# mylib/__init__.py
from .core import Engine
from .config import Settings
from .exceptions import MyLibError

__all__ = ["Engine", "Settings", "MyLibError"]
```

Users can write `from mylib import Engine` directly, while internal implementation files (`core.py`, `config.py`) stay hidden. Specifying `__all__` controls which names are exposed by `from mylib import *`.

### Pattern 2: Provide Version Info

```python
# mylib/__init__.py
__version__ = "1.2.0"
```

```python
import mylib
print(mylib.__version__)  # "1.2.0"
```

### Pattern 3: Leave It Empty

```python
# mylib/__init__.py
# (empty)
```

When a package has deep nesting and users import sub-modules directly, leaving `__init__.py` empty is the simplest approach. Django's `migrations/` package uses this pattern.

### Pattern 4: Lazy Import

```python
# mylib/__init__.py
def __getattr__(name):
    if name == "HeavyModule":
        from .heavy import HeavyModule
        return HeavyModule
    raise AttributeError(f"module 'mylib' has no attribute {name}")
```

This defers loading of sub-modules with heavy dependencies until they are actually accessed. `import mylib` alone does not execute `heavy.py`.

## Wheel Internal Structure

What `pip install` installs is almost always a wheel (`.whl`) file. A wheel is simply a ZIP file with a defined internal layout.

```bash
# Inspect a real wheel file
pip download requests --no-deps -d /tmp/wheels
unzip -l /tmp/wheels/requests-2.32.3-py3-none-any.whl | head -20
```

```text
requests-2.32.3-py3-none-any.whl contents:
├── requests/
│   ├── __init__.py
│   ├── api.py
│   ├── sessions.py
│   ├── models.py
│   └── ...
├── requests-2.32.3.dist-info/
│   ├── METADATA        # Package metadata (name, version, dependencies)
│   ├── WHEEL           # Wheel format info
│   ├── RECORD          # Installed file list + hashes
│   ├── top_level.txt   # Top-level package name
│   └── LICENSE
```

### Wheel File Naming Convention

```text
{distribution}-{version}(-{build})?-{python}-{abi}-{platform}.whl

Examples:
requests-2.32.3-py3-none-any.whl
├── distribution: requests
├── version: 2.32.3
├── python: py3 (Python 3)
├── abi: none (pure Python)
└── platform: any (all platforms)

numpy-1.26.4-cp312-cp312-manylinux_2_17_x86_64.whl
├── distribution: numpy
├── version: 1.26.4
├── python: cp312 (CPython 3.12)
├── abi: cp312 (CPython 3.12 ABI)
└── platform: manylinux_2_17_x86_64 (Linux x86_64)
```

Pure Python packages use `py3-none-any` and share a single wheel across all environments. Packages with C extensions need separate wheels per platform.

## Editable Install Internals

During development you use `pip install -e .` (editable install). In this mode, source code is not copied into `site-packages`; instead the original directory is referenced directly.

```bash
# Normal install: files copied to site-packages
pip install .
# site-packages/mylib/__init__.py (copy)

# Editable install: a link to the original is created
pip install -e .
# site-packages/mylib.egg-link or
# site-packages/__editable__.mylib-0.1.0.pth
```

```python
# After editable install
import mylib
print(mylib.__file__)
# /home/user/projects/mylib/src/mylib/__init__.py (the original!)
```

The key advantage is that source edits are reflected immediately without reinstalling. This speeds up the develop-test cycle.

### Modern Editable Install (PEP 660)

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

```bash
pip install -e .
# setuptools >= 64 uses a .pth file approach for editable installs
# Correctly recognizes src/ layout without import hooks
```

## Package Naming: Strategies to Avoid Collisions

Over 500,000 packages are registered on PyPI. Choosing a name that avoids collisions while remaining discoverable is important.

### Naming Rules

| Rule | Example |
|---|---|
| Lowercase + hyphens (distribution name) | `my-utils` |
| Lowercase + underscores (import name) | `my_utils` |
| PyPI normalizes names | `my-utils` == `my_utils` == `My.Utils` |
| 3+ characters recommended | `fileio` over `io` |

### Internal Package Naming Pattern

```text
{company/org}-{domain}-{function}
e.g.: acme-auth-client, acme-logging, acme-config
```

A consistent prefix lets you spot all internal packages at a glance with `pip list | grep acme-`.

### Checking PyPI Name Availability

```bash
# Check if a name is available
pip index versions my-desired-name
# ERROR: No matching distribution found -> available

# Or via the API
curl -s https://pypi.org/pypi/my-desired-name/json | python -m json.tool
# 404 -> available
```

## The Full pip install Flow

Here is what actually happens when you run `pip install requests`.

```text
pip install requests
    │
    ▼
1. Call PyPI API: GET https://pypi.org/simple/requests/
    │
    ▼
2. Select compatible wheel (Python version, platform)
    │
    ▼
3. Download wheel + verify hash
    │
    ▼
4. Resolve dependencies (urllib3, certifi, charset-normalizer, idna)
    │
    ▼
5. Install each dependency through the same process
    │
    ▼
6. Extract wheel → place files in site-packages/
    │
    ▼
7. Create .dist-info/ directory (METADATA, RECORD, etc.)
```

### The Dependency Resolver

Since pip 20.3, a new dependency resolver runs by default. It finds a combination of versions that simultaneously satisfies all package version requirements.

```bash
# View the dependency tree
pip install pipdeptree
pipdeptree -p requests
```

```text
requests==2.32.3
├── certifi [required: >=2017.4.17, installed: 2024.7.4]
├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
├── idna [required: >=2.5,<4, installed: 3.7]
└── urllib3 [required: >=1.21.1,<3, installed: 2.2.2]
```

### Directory State After Installation

```bash
ls site-packages/ | grep -E "requests|urllib3"
```

```text
requests/
requests-2.32.3.dist-info/
urllib3/
urllib3-2.2.2.dist-info/
```

Each package produces two directories: one containing the actual code and another (`.dist-info/`) holding metadata.

### The RECORD File: Installed File Manifest

```bash
head -5 site-packages/requests-2.32.3.dist-info/RECORD
```

```text
requests/__init__.py,sha256=abc123...,4567
requests/api.py,sha256=def456...,2345
requests/sessions.py,sha256=ghi789...,12345
requests/models.py,sha256=jkl012...,23456
requests/adapters.py,sha256=mno345...,8901
```

When you run `pip uninstall requests`, pip reads this RECORD file and removes exactly the files that were installed.

## Module Search Order Pitfalls

`sys.path` order is an effective priority list. If you do not understand this order, an unintended module may get imported.

```python
import sys
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")
```

```text
0:                          # empty string = current directory (highest priority)
1: /usr/lib/python3.11
2: /usr/lib/python3.11/lib-dynload
3: /home/user/.local/lib/python3.11/site-packages
4: /usr/lib/python3.11/site-packages
```

### The Shadow Import Problem

```bash
# Create a random.py in the current directory:
echo "print('This is NOT the stdlib random!')" > random.py
python -c "import random; print(random.randint(1, 10))"
# This is NOT the stdlib random!
# AttributeError: module 'random' has no attribute 'randint'
```

The current directory (`sys.path[0]`) is searched before the standard library. Renaming the file fixes the problem immediately.

### Recommended Verification Habit

```python
# Check which module was actually loaded
import json
print(json.__file__)  # /usr/lib/python3.11/json/__init__.py means correct

# When in doubt, inspect the spec
import importlib.util
spec = importlib.util.find_spec("json")
print(spec.origin)
```

## Answering the Opening Questions

- **What exactly is the difference between a module and a package?**
  - A module is a single `.py` file, and a package is a directory with `__init__.py`. Packages group multiple modules into a single namespace to create hierarchical structure. `import json` brings in one module, while `import requests` brings in an entire package (directory).
- **What happens internally when you run `import requests`?**
  - Python first checks the `sys.modules` cache. If not found, finders in `sys.meta_path` search for the module in order, and `PathFinder` looks for a `requests/` directory in each path on `sys.path`. Upon finding the directory, it creates a module object, executes `__init__.py`, and binds the name `requests` in the caller's namespace.
- **What does `pip install` actually install?**
  - `pip install` downloads a wheel (`.whl`) file from PyPI and extracts the package files into the `site-packages/` directory. It simultaneously creates a `.dist-info/` directory recording metadata, installed file lists, and dependency information. Since `site-packages/` is included in `sys.path`, the package becomes importable immediately.

<!-- toc:begin -->
## In this series

- **Python Package 101 (1/10): What Is a Python Package? (current)**
- Python Package 101 (2/10): Project Structure — src layout and pyproject.toml (upcoming)
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

- [Python Packaging User Guide](https://packaging.python.org/)
- [Python Modules Tutorial](https://docs.python.org/3/tutorial/modules.html)
- [Real Python - Python Packages](https://realpython.com/python-modules-packages/)
- [PyPI - Python Package Index](https://pypi.org/)

Tags: Python, Packaging, PyPI, pyproject.toml
