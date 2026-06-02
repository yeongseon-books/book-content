---
title: "Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements"
series: python-package-101
episode: 3
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
- venv
- pip
- uv
- Dependencies
- Virtual Environment
last_reviewed: '2026-05-15'
seo_description: A virtual environment gives each project its own package space, and
  dependency management records which packages at which versions are needed.
---

# Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements

The same code can behave differently just because two environments installed different package versions. Dependency management is how you turn that uncertainty into something reproducible.

This is the 3rd post in the Python Package 101 series. Here we cover virtual environments, the different jobs of `requirements.txt` and `pyproject.toml`, and why `uv` is becoming the fast path for new Python projects.

![Python Package 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/03/03-01-mental-model.en.png)
*Python Package 101 chapter 3 flow overview*

## Questions to Keep in Mind

- Why do we need virtual environments and how do they work?
- What is the relationship between `pip freeze` and `requirements.txt`?
- How does `uv` differ from `pip`?

## What you will learn

- How to create and activate a virtual environment with `python -m venv`
- How to manage dependencies with `pip install` and `pip freeze`
- The difference between `requirements.txt` and pyproject.toml `dependencies`
- How to manage environments and packages faster with `uv`

## Why it matters

Project A uses `requests==2.28` and Project B uses `requests==2.31`. Installing both into the system Python causes version conflicts.

> You ran `pip install requests==2.28` for Project A, and Project B broke. B was using a feature added in 2.31.

Virtual environments solve this by giving each project an isolated `site-packages` directory.

## Mental Model

> A virtual environment is like giving each project its own refrigerator. If everyone shares one fridge (system Python), someone might accidentally use your ingredients. A dedicated fridge keeps your project safe from others.

```text
System Python               Virtual Environment
─────────────              ─────────────────────
site-packages/             project-a/.venv/site-packages/
  requests 2.28               requests 2.28
  flask 2.3
                           project-b/.venv/site-packages/
                              requests 2.31
                              django 4.2
```

## Core Concepts

| Term | Description | Example |
|---|---|---|
| venv | Python built-in virtual environment module | `python -m venv .venv` |
| site-packages | Directory where packages are installed | `.venv/lib/python3.11/site-packages/` |
| pip freeze | Prints installed packages with exact versions | `pip freeze > requirements.txt` |
| requirements.txt | Version-pinned file for reproducible installs | `requests==2.31.0` |
| uv | High-speed package manager written in Rust | `uv pip install requests` |

## Before / After

**Before (shared system Python)**

```bash
pip install requests==2.28   # for Project A
pip install requests==2.31   # for Project B → A breaks
```

**After (isolated virtual environments)**

```bash
cd project-a && python -m venv .venv && source .venv/bin/activate
pip install requests==2.28   # project-a only

cd project-b && python -m venv .venv && source .venv/bin/activate
pip install requests==2.31   # project-b only
```

## Step-by-step practice

### Step 1. Create a virtual environment

```bash
cd ~/practice/mylib-project
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows

which python
# /home/user/practice/mylib-project/.venv/bin/python
```

### Step 2. Install packages and freeze

```bash
pip install requests flask
pip list
# requests  2.31.0
# flask     3.0.0
# ...

pip freeze > requirements.txt
cat requirements.txt
# blinker==1.7.0
# certifi==2024.2.2
# flask==3.0.0
# requests==2.31.0
# ...
```

### Step 3. Reproduce with requirements.txt

```bash
# Install the same packages in another environment
deactivate
python -m venv .venv-test
source .venv-test/bin/activate
pip install -r requirements.txt
pip list  # same packages, same versions
```

### Step 4. pyproject.toml dependencies

```toml
# pyproject.toml
[project]
name = "mylib"
version = "0.1.0"
dependencies = [
    "requests>=2.28",
    "flask>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
]
```

```bash
pip install -e .            # install dependencies
pip install -e ".[dev]"     # install dev dependencies too
```

### Step 5. Manage faster with uv

```bash
pip install uv

uv venv .venv               # create venv (0.1 seconds)
source .venv/bin/activate
uv pip install requests     # install (10-100x faster than pip)
uv pip freeze               # freeze
uv pip install -r requirements.txt  # reproduce
```

## What to notice in this code

- `source .venv/bin/activate` prepends `.venv/bin` to `PATH` so the virtual environment Python takes priority
- `pip freeze` outputs all transitive dependencies, not just the packages you installed directly
- pyproject.toml `dependencies` uses minimum versions (`>=`) while `requirements.txt` uses exact versions (`==`)
- `uv` is a drop-in replacement for pip with the same command structure but much faster execution

## Common mistakes

### Mistake 1. Committing the virtual environment to Git

`.venv/` is tens of megabytes and OS-specific. Add `.venv/` to `.gitignore`.

### Mistake 2. Putting pip freeze output directly into dependencies

```toml
# Wrong: exact versions in pyproject.toml reduce compatibility
dependencies = ["requests==2.31.0", "certifi==2024.2.2"]

# Correct: minimum compatible version ranges
dependencies = ["requests>=2.28"]
```

### Mistake 3. Forgetting to activate the virtual environment

`pip install` goes into the system Python. Check the path with `which python`.

### Mistake 4. Not updating requirements.txt

If you forget to run `pip freeze > requirements.txt` after adding or removing packages, other environments cannot reproduce yours.

### Mistake 5. Confusing dependencies and requirements.txt

`dependencies` answers "what does this package need to work?" while `requirements.txt` answers "what exactly is needed to reproduce this environment?"

## Practical applications

- **CI/CD**: Reproduce the build environment with `pip install -r requirements.txt`
- **Docker**: Use `COPY requirements.txt . && pip install -r requirements.txt` to leverage layer caching
- **Dev dependency separation**: Use `[project.optional-dependencies]` to separate prod and dev dependencies
- **Security auditing**: Scan installed packages for vulnerabilities with `pip audit`
- **Speed improvement**: Cut CI/CD install times by 10x with `uv`

## How practitioners think about this

The core of dependency management is **reproducibility**. "It works on my machine" almost always comes from environment differences. Pinning exact versions with `requirements.txt` (or `uv.lock`) ensures identical results everywhere.

`uv` is rapidly becoming the standard. It handles virtual environment creation, package installation, and lock file generation in a single tool, running 10-100x faster than pip. For new projects, consider `uv` first.

## Checklist

- [ ] You can create and activate a virtual environment with `python -m venv`
- [ ] You can pin your environment with `pip freeze > requirements.txt`
- [ ] You can explain the difference between pyproject.toml `dependencies` and `requirements.txt`
- [ ] You can separate dev dependencies with `optional-dependencies`
- [ ] You know the basics of `uv`

## Exercises

1. Create a new virtual environment, install `httpx` and `rich`, and generate a `requirements.txt`.
2. Write both `dependencies` and `[project.optional-dependencies]` `dev` in pyproject.toml, and install with `pip install -e ".[dev]"`.
3. Install `uv` and use `uv venv` + `uv pip install` to feel the speed difference compared to `pip`.

## Summary and next

- Virtual environments provide each project with an isolated package space.
- `pip freeze` pins exact versions, and `requirements.txt` reproduces them.
- pyproject.toml `dependencies` records minimum compatible versions; `requirements.txt` records exact versions.
- `optional-dependencies` separates development-only packages.
- `uv` is a high-speed pip replacement that is rapidly becoming the standard.

The next post covers **building packages** — wheel and sdist.

## Virtual Environment Internals

Running `python -m venv .venv` creates specific directories and files. Let's examine what's inside.

```bash
python -m venv .venv
tree .venv -L 2
```

```text
.venv/
├── bin/                         # (Windows: Scripts/)
│   ├── activate                 # shell activation script
│   ├── activate.fish
│   ├── pip                      # venv-specific pip
│   ├── pip3
│   ├── python -> python3.11     # symlink to system Python
│   └── python3
├── include/                     # C extension build headers
├── lib/
│   └── python3.11/
│       └── site-packages/       # package install path for this venv
├── lib64 -> lib
└── pyvenv.cfg                   # venv configuration
```

```ini
# pyvenv.cfg contents
home = /usr/bin
include-system-site-packages = false
version = 3.11.9
executable = /usr/bin/python3.11
command = /usr/bin/python3.11 -m venv .venv
```

### What activate Actually Does

```bash
# Core behavior of the activate script (simplified):
export VIRTUAL_ENV="/path/to/.venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
export PS1="(.venv) $PS1"

# Deactivation
deactivate  # restores PATH and PS1 to original values
```

`activate` prepends `.venv/bin` to `PATH`. After that, running `python` or `pip` executes the binaries inside the venv, not the system ones.

### Using venv Without activate

```bash
# You can use the venv without activate by specifying paths directly
.venv/bin/python -m pip install requests
.venv/bin/python main.py

# CI pipelines often use direct paths instead of activate
```

## pip's Dependency Resolution Algorithm

pip 20.3+ uses a backtracking resolver. This resolver finds a combination of versions where all package requirements are simultaneously satisfied.

### Resolution Process Visualization

```bash
pip install "packageA>=1.0" "packageB>=2.0" --verbose 2>&1 | grep -i "trying\|conflict"
```

```text
Resolution process:
1. packageA>=1.0 → select latest version 1.5
2. packageA 1.5 dependencies: shared-lib>=3.0
3. packageB>=2.0 → select latest version 2.3
4. packageB 2.3 dependencies: shared-lib>=2.0,<3.0
5. Conflict! shared-lib>=3.0 AND <3.0 is impossible
6. Backtrack: try packageA 1.4
7. packageA 1.4 dependencies: shared-lib>=2.5
8. shared-lib>=2.5 AND >=2.0,<3.0 → select shared-lib 2.9
9. Resolution complete!
```

### Debugging Dependency Conflicts

```bash
# Check conflict cause
pip install "packageA>=1.0" "packageB>=2.0" --dry-run

# Visualize dependency tree
pip install pipdeptree
pipdeptree --warn fail  # returns error if conflicts exist
pipdeptree -r -p shared-lib  # reverse-trace packages depending on shared-lib
```

## Requirements File Strategies

### requirements.txt vs pyproject.toml dependencies

| Purpose | File | Characteristics |
|---|---|---|
| Library dependencies | `pyproject.toml` `[project.dependencies]` | Range specifiers (`>=1.0,<2.0`) |
| Application lock | `requirements.txt` | Exact version pins (`==1.2.3`) |
| Dev tools | `pyproject.toml` `[project.optional-dependencies]` | Group-based management |

### Layered Requirements Structure

```text
requirements/
├── base.txt          # production dependencies
├── dev.txt           # dev tools (includes base)
├── test.txt          # test-only (includes base)
└── ci.txt            # CI-only (test + lint)
```

```text
# requirements/base.txt
httpx==0.27.2
pydantic==2.8.2
sqlalchemy==2.0.31

# requirements/dev.txt
-r base.txt
pytest==8.3.2
ruff==0.5.5
mypy==1.11.0
ipython==8.26.0

# requirements/test.txt
-r base.txt
pytest==8.3.2
pytest-cov==5.0.0
factory-boy==3.3.0
```

### The Pitfall of pip freeze

```bash
pip freeze > requirements.txt
```

Problems with this approach:
1. Direct and transitive dependencies are not distinguished
2. Dev tools are included alongside production packages
3. It's hard to determine later which packages can be safely removed

```bash
# Better approach: use pip-compile
pip install pip-tools
echo "httpx>=0.27" > requirements.in
echo "pydantic>=2.5" >> requirements.in
pip-compile requirements.in -o requirements.txt
```

```text
# requirements.txt (generated by pip-compile)
# This file is autogenerated by pip-compile
anyio==4.4.0
    # via httpx
certifi==2024.7.4
    # via httpx
httpcore==1.0.5
    # via httpx
httpx==0.27.2
    # via -r requirements.in
pydantic==2.8.2
    # via -r requirements.in
# ... transitive dependencies show their source
```

## uv: Next-Generation Package Manager

uv is a Rust-based package manager that provides 10-100x faster dependency resolution and installation compared to pip.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv (faster than pip)
uv venv .venv

# Install packages
uv pip install httpx pydantic

# Install from requirements.txt
uv pip install -r requirements.txt

# Generate lock file
uv pip compile requirements.in -o requirements.txt
```

### uv vs pip Performance Comparison

```bash
# Approximate install time comparison with the same requirements.txt
time pip install -r requirements.txt     # ~15s
time uv pip install -r requirements.txt  # ~1.5s
```

### uv Project Management Mode

```bash
# Use uv as a project manager (pyproject.toml-based)
uv init myproject
cd myproject
uv add httpx pydantic      # add dependency + lock
uv remove pydantic         # remove dependency + update lock
uv sync                    # sync based on lock file
uv run pytest              # run command inside venv
```

```text
myproject/
├── pyproject.toml
├── uv.lock              # exact versions + hash lock
└── src/
    └── myproject/
```

## Dependency Version Specifier Strategies

```toml
[project]
dependencies = [
    # Minimum version only (for libraries)
    "httpx>=0.27",

    # Upper bound included (compatible range)
    "pydantic>=2.5,<3.0",

    # Compatible release (~= operator)
    "sqlalchemy~=2.0",      # equivalent to >=2.0, <3.0

    # Exact version (rare cases)
    "legacy-lib==1.2.3",

    # Environment markers
    "tomli>=2.0; python_version < '3.11'",
]
```

### Library vs Application Strategy

| | Library | Application |
|---|---|---|
| Version specifiers | Loose (`>=1.0,<3.0`) | Exact (`==1.2.3`) |
| Lock file | None | Required |
| Reason | Flexibility in user environments | Reproducible deployments |

## Dependency Caching in GitHub Actions

```yaml
name: ci
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"                    # enable pip cache automatically
          cache-dependency-path: |
            requirements/dev.txt
            pyproject.toml
      - run: python -m pip install -e ".[dev]"
      - run: pytest
```

Enabling the cache reduces installation time to a few seconds when dependencies haven't changed.

## Security: Dependency Vulnerability Management

Installed packages may contain security vulnerabilities. Regular auditing is essential.

### Scanning Vulnerabilities with pip-audit

```bash
pip install pip-audit
pip-audit
```

```text
Name       Version  ID             Fix Versions
---------- -------- -------------- ------------
cryptography 41.0.0 GHSA-xxxx-yyyy >=41.0.2
urllib3      1.26.15 PYSEC-2023-212 >=1.26.18,>=2.0.7
```

### GitHub Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

### Dependency Hash Verification

```bash
# Include hashes in requirements.txt (supply chain protection)
pip-compile --generate-hashes requirements.in
```

```text
# requirements.txt
httpx==0.27.2 \
    --hash=sha256:abc123... \
    --hash=sha256:def456...
```

Using a requirements.txt with hashes will refuse installation if a package has been tampered with.

## Virtual Environment Tool Comparison

| Tool | Features | Best For |
|---|---|---|
| `python -m venv` | Standard library, no extra install | Simple projects, CI |
| `virtualenv` | Faster than venv, more options | When venv features are insufficient |
| `uv venv` | Rust-based, fastest | When speed matters |
| `conda` | Manages non-Python binaries too | Data science, C libraries |
| `poetry` | lock + venv + build integrated | All-in-one tool preference |
| `pdm` | PEP 582 support, modern | Standards compliance + convenience |

### Poetry Basic Usage

```bash
poetry init                    # create pyproject.toml
poetry add httpx               # add dependency + lock
poetry add --group dev pytest  # add dev dependency
poetry install                 # install from lock
poetry run pytest              # run inside venv
poetry build                   # create wheel + sdist
```

```text
# poetry.lock (auto-generated, should be committed)
[[package]]
name = "httpx"
version = "0.27.2"
python-versions = ">=3.8"

[package.dependencies]
anyio = "*"
certifi = "*"
httpcore = "==1.*"
```

## Dependency Update Strategy

Neglecting dependencies leads to accumulated security vulnerabilities. Updating everything at once triggers compatibility issues simultaneously. The key is regular, incremental updates.

### Weekly Update Routine

```bash
# 1. Check packages with available updates
pip list --outdated

# 2. Apply only minor/patch updates
pip-compile --upgrade-package "httpx" requirements.in

# 3. Run tests
pytest

# 4. If everything passes, commit
git add requirements.txt
git commit -m "deps: upgrade httpx to 0.27.2"
```

### Major Update Checklist

Major version changes (`1.x → 2.x`) may include breaking changes.

```text
1. Read the CHANGELOG
2. Check migration guide
3. Upgrade on a separate branch
4. Run full test suite
5. Run type checking (mypy)
6. Verify behavior in staging environment
7. Merge to main branch
```

## Dependency Tree Visualization and Cleanup

As projects grow, transitive dependencies multiply to dozens. Periodic cleanup reduces install time and attack surface.

```bash
# Full dependency tree
pipdeptree

# Reverse dependencies of a specific package (who needs this?)
pipdeptree -r -p certifi

# Find unused packages
pip install deptry
deptry .
```

```text
# deptry output example
DEP002: 'black' is in requirements but not used in source code
DEP003: 'tomli' is imported but not in requirements (transitive dependency)
```

`DEP003` flags cases where you import a transitive dependency directly. If that package disappears in an update, your code breaks. Explicitly adding it to `dependencies` is safer.

### Should You Commit the Lock File?

| Project Type | Commit Lock File | Reason |
|---|---|---|
| Application | Yes | Guarantees deployment reproducibility |
| Library | No | Maintains flexibility in user environments |
| Monorepo (apps) | Yes | Exact version pinning per service |

## Answering the Opening Questions

- **Where does `pip install` put packages?**
  - `pip install` installs packages to the `site-packages/` directory of the currently active environment. Inside a venv, that's `.venv/lib/python3.11/site-packages/`; for system Python, it's `/usr/lib/python3.11/site-packages/`. You can verify with the Location field from `pip show <package>`.
- **What does a virtual environment isolate, and why is it needed?**
  - A virtual environment separates the `site-packages` path per project. When project A needs `requests==2.28` and project B needs `requests==2.32`, only one can be installed system-wide, but with venvs each project maintains an independent package set. This isolation works through nothing more than a `PATH` change.
- **How do you resolve dependency version conflicts?**
  - pip's backtracking resolver automatically searches for a combination satisfying all packages' version requirements simultaneously. When resolution is impossible, it outputs an error. Use `pipdeptree -r` to trace the conflict source, then adjust upper version bounds or find alternative packages.

<!-- toc:begin -->
## In this series

- [Python Package 101 (1/10): What Is a Python Package?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): Project Structure — src layout and pyproject.toml](./02-project-structure.md)
- **Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements (current)**
- Python Package 101 (4/10): Building Packages — wheel and sdist (upcoming)
- Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production (upcoming)
- Python Package 101 (6/10): Versioning and Releases (upcoming)
- Python Package 101 (7/10): CLI Packages (upcoming)
- Python Package 101 (8/10): Type Hints and Static Analysis (upcoming)
- Python Package 101 (9/10): Documentation — README, MkDocs, API Reference (upcoming)
- Python Package 101 (10/10): Production Package Template (upcoming)

<!-- toc:end -->

## References

- [Python Packaging User Guide - Managing Dependencies](https://packaging.python.org/en/latest/tutorials/managing-dependencies/)
- [PEP 405 - Python Virtual Environments](https://peps.python.org/pep-0405/)
- [uv - An extremely fast Python package installer](https://github.com/astral-sh/uv)
- [pip documentation - Requirements Files](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

Tags: Python, Packaging, PyPI, pyproject.toml
