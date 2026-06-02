---
title: "Python Package 101 (9/10): Documentation — README, MkDocs, API Reference"
series: python-package-101
episode: 9
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
- Documentation
- MkDocs
- README
- API Reference
- Sphinx
last_reviewed: '2026-05-15'
seo_description: A README is the front door of your package and an API Reference is
  the manual for every function. A package without docs does not get used.
---

# Python Package 101 (9/10): Documentation — README, MkDocs, API Reference

Even a solid package gets ignored if a reader cannot figure out installation and the first useful call within half a minute. Documentation is not decoration around code; it is part of the product surface.

This is the 9th post in the Python Package 101 series. Here we connect README, guides, and API reference into a documentation stack that helps users decide, start, and verify.

![Python Package 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/09/09-01-mental-model.en.png)
*Python Package 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What should a good README include?
- What is the difference between MkDocs and Sphinx?
- How do you auto-generate an API Reference from docstrings?

## What you will learn

- The structure and essential sections of a good README
- How to build a documentation site with MkDocs
- How to auto-generate API Reference from docstrings
- How to deploy documentation to GitHub Pages

## Why it matters

No matter how good your package is, it will not be used if there are no usage instructions. When a user discovers your package on PyPI, they need to decide within 30 seconds: "does this solve my problem?" The README serves that purpose.

> You found a useful package but the README has no installation instructions or examples. You would have to read the source code to figure out how to use it. You end up choosing a different package with similar features.

## Mental Model

> Documentation has three layers. Layer 1 (README) answers "what is it and how do I start?" Layer 2 (Guide) answers "how do I use it?" Layer 3 (API Reference) provides "detailed specs for every function." Users start at layer 1 and go deeper as needed.

```text
README.md          →  30-second decision: install, quick start
docs/guide.md      →  5-minute tutorial: main features
docs/api.md        →  detailed reference: specs for every function/class
```

## Core Concepts

| Term | Description | File |
|---|---|---|
| README | Project introduction, installation, quick start | `README.md` |
| docstring | Documentation string attached to functions/classes | `"""..."""` |
| MkDocs | Markdown-based documentation site generator | `mkdocs.yml` |
| mkdocstrings | Plugin that auto-generates API docs from docstrings | MkDocs plugin |
| GitHub Pages | Free static site hosting | `gh-pages` branch |

## Before / After

**Before (no documentation)**

```text
README.md:
# mylib
A Python library.
```

**After (structured documentation)**

```text
README.md:
# mylib
One-line description.

## Installation
pip install mylib

## Quick Start
from mylib import greet
print(greet("World"))

## Documentation
https://yourname.github.io/mylib/
```

## Step-by-step practice

### Step 1. Write a README

```markdown
# mylib

A simple greeting library for Python.

## Installation

```bash
pip install mylib
```

## Quick Start

```python
from mylib.core import greet

print(greet("World"))  # Hello, World!
```

## Features

- Simple and lightweight
- Type-annotated
- CLI support via `greet` command

## Development

```bash
git clone https://github.com/yourname/mylib
cd mylib
pip install -e ".[dev]"
pytest tests/
```

## License

MIT
```text

### Step 2. Add docstrings

```python
# src/mylib/core.py
def greet(name: str) -> str:
    """Return a greeting message.

    Args:
        name: The name to greet.

    Returns:
        A formatted greeting string.

    Examples:
        >>> greet("Alice")
        'Hello, Alice!'
    """
    return f"Hello, {name}!"
```

### Step 3. Set up MkDocs

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]

cat > mkdocs.yml << 'EOF'
site_name: mylib
theme:
  name: material

nav:
  - Home: index.md
  - Guide: guide.md
  - API Reference: api.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
EOF

mkdir docs
echo "# mylib" > docs/index.md
echo "# Guide" > docs/guide.md
```

### Step 4. Auto-generate API Reference

```markdown
<!-- docs/api.md -->
# API Reference

::: mylib.core
    options:
      show_root_heading: true
      show_source: true
```

```bash
mkdocs serve
# INFO - Serving on http://127.0.0.1:8000/
```

### Step 5. Deploy to GitHub Pages

```bash
mkdocs gh-deploy
# INFO - Deployed to https://yourname.github.io/mylib/
```

## What to notice in this code

- Google style docstrings (`Args:`, `Returns:`) are the most widely used format
- `mkdocstrings` uses `::: mylib.core` to auto-render docstrings from that module
- `mkdocs serve` previews locally; `mkdocs gh-deploy` publishes
- The `Examples:` section with `>>>` can be auto-tested with `doctest`

## Common mistakes

### Mistake 1. Omitting installation instructions from the README

The first thing users try is "how do I install this?" Always include `pip install mylib`.

### Mistake 2. Docstrings that do not match the code

If you change the code but not the docstring, the documentation lies. Run `doctest` in CI to verify examples still work.

### Mistake 3. Having a docs site but no README

The first thing users see on PyPI and GitHub is the README. Link to the docs site from the README, but make the README independently useful.

### Mistake 4. Having only API Reference but no guide

An API Reference lists every function, but what users want to know is "in what order do I call which functions?" A guide serves that purpose.

### Mistake 5. Not deploying the documentation

Running `mkdocs serve` locally but never deploying means users cannot access it. Use `mkdocs gh-deploy` or automate deployment in CI.

## Practical applications

- **PyPI README**: Use `[project.readme]` to render the README on the PyPI page
- **CI docs build**: Verify docs build on every PR to catch broken links and rendering errors
- **Versioned docs**: Use `mike` (MkDocs plugin) to host docs for multiple versions
- **Jupyter integration**: Users can view docstrings with `?` or `help()` in notebooks
- **Auto CHANGELOG**: Use `towncrier` to aggregate per-PR change entries automatically

## How practitioners think about this

Documentation is part of the code. When a PR changes code, docs changes should be reviewed alongside. "Code changed but docs stayed the same" is technical debt.

MkDocs + Material theme is the de facto standard in the Python ecosystem today. Sphinx is more powerful but has a higher learning curve. For new projects, start with MkDocs.

## Checklist

- [ ] Your README includes installation, quick start, and license
- [ ] All public functions have docstrings
- [ ] You can generate a docs site with MkDocs
- [ ] You can auto-generate API Reference with mkdocstrings
- [ ] You can deploy documentation to GitHub Pages

## Exercises

1. Write a README.md for the package from the previous post. Include installation, quick start, features, development setup, and license.
2. Add Google style docstrings to all public functions and verify examples work with `python -m doctest`.
3. Set up MkDocs and preview the documentation locally with `mkdocs serve`.

## Summary and next

- A README is the front door: installation, quick start, and feature overview are essential.
- Write docstrings in Google style and verify examples with doctest.
- MkDocs + mkdocstrings auto-generates API Reference from docstrings.
- `mkdocs gh-deploy` hosts documentation on GitHub Pages for free.
- Documentation is part of the code — update docs whenever code changes.

The next post covers **production package template** — cookiecutter, copier, and GitHub Template.

## README Writing Guide

The README is the first impression of your package and the first document users read. It appears on PyPI, GitHub, and documentation sites.

### Required sections

```markdown
# acme-utils

> Production-ready utility library for Acme microservices.

[![PyPI version](https://img.shields.io/pypi/v/acme-utils.svg)](https://pypi.org/project/acme-utils/)
[![Python versions](https://img.shields.io/pypi/pyversions/acme-utils.svg)](https://pypi.org/project/acme-utils/)
[![CI](https://github.com/acme/acme-utils/actions/workflows/ci.yml/badge.svg)](https://github.com/acme/acme-utils/actions)

## Installation

```bash
pip install acme-utils
```

## Quick Start

```python
from acme_utils import Engine, Settings

settings = Settings.from_env()
engine = Engine(settings)
result = engine.run("SELECT * FROM users")
```

## Features

- **Type-safe configuration** — Pydantic-based settings with env var support
- **Retry logic** — Configurable retry with exponential backoff
- **Structured logging** — JSON logging for production environments

## Documentation

Full documentation: https://acme.github.io/acme-utils

## Development

```bash
git clone https://github.com/acme/acme-utils.git
cd acme-utils
pip install -e ".[dev]"
pytest
```

## License

MIT License. See [LICENSE](LICENSE) for details.
```

### README writing principles

| Principle | Description |
|---|---|
| 30-second rule | Users must understand what the package does in 30 seconds |
| Copy-paste-ready code | Quick Start must be runnable as-is |
| Badges | Build status, version, and Python versions at a glance |
| Links | Connect to detailed docs, changelog, and issue tracker |

## Building a Documentation Site with MkDocs

MkDocs is a Markdown-based static documentation site generator. Combined with the Material theme, you can build modern documentation quickly.

### Initial setup

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs new docs
```

```yaml
# mkdocs.yml
site_name: Acme Utils
site_url: https://acme.github.io/acme-utils
repo_url: https://github.com/acme/acme-utils

theme:
  name: material
  features:
    - content.code.copy
    - navigation.sections
    - navigation.expand
    - search.suggest
  palette:
    - scheme: default
      primary: indigo

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true
            docstring_style: google

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
  - User Guide:
    - Configuration: guide/configuration.md
    - Retry Logic: guide/retry.md
  - API Reference:
    - Core: api/core.md
    - Config: api/config.md
  - Changelog: changelog.md

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - admonitions
  - pymdownx.tabbed:
      alternate_style: true
```

### Directory structure

```text
docs/
├── index.md                    # Homepage
├── getting-started/
│   ├── installation.md
│   └── quickstart.md
├── guide/
│   ├── configuration.md
│   └── retry.md
├── api/
│   ├── core.md                 # Auto-generated API docs
│   └── config.md
└── changelog.md
```

### Auto-generating API Reference

```markdown
<!-- docs/api/core.md -->
# Core Module

::: acme_utils.core
    options:
      members:
        - Engine
        - Result
      show_source: true
```

mkdocstrings reads docstrings from source code and generates API documentation automatically.

### Local preview

```bash
mkdocs serve
# INFO - Serving on http://127.0.0.1:8000/
# Auto-reloads on file changes
```

## Docstring Writing Rules

### Google style (recommended)

```python
def retry(
    func: Callable[[], T],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> T:
    """Retry a function with exponential backoff.

    Executes the function up to the specified number of times,
    increasing wait time exponentially after each failure.

    Args:
        func: Function to execute. Must be callable with no arguments.
        max_attempts: Maximum number of attempts. Default 3.
        delay: Wait time before first retry in seconds. Default 1.0.
        backoff: Multiplier for wait time increase. Default 2.0.

    Returns:
        The function's return value.

    Raises:
        RetryError: When all attempts fail.

    Example:
        >>> result = retry(lambda: fetch_data(), max_attempts=5)
    """
```

### NumPy style

```python
def calculate_mean(values: list[float]) -> float:
    """
    Calculate the arithmetic mean of given values.

    Parameters
    ----------
    values : list[float]
        List of numbers to average. Must not be empty.

    Returns
    -------
    float
        The arithmetic mean.

    Raises
    ------
    ValueError
        If values is empty.
    """
```

## Automatic Deployment to GitHub Pages

```yaml
# .github/workflows/docs.yml
name: Deploy docs
on:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install mkdocs-material mkdocstrings[python]
      - run: mkdocs gh-deploy --force
```

```bash
# Manual deployment
mkdocs gh-deploy
# Automatically deploys to GitHub Pages
# https://acme.github.io/acme-utils/
```

## Sphinx vs MkDocs Comparison

| Aspect | MkDocs | Sphinx |
|---|---|---|
| Syntax | Markdown | reStructuredText (default) |
| Config | YAML | Python (conf.py) |
| Theme | Material (modern) | Read the Docs (traditional) |
| API auto-gen | mkdocstrings | autodoc (built-in) |
| Build speed | Fast | Moderate |
| Ecosystem | Growing | Very broad |
| Best for | New projects, concise docs | Large-scale, academic, legacy |

### Sphinx minimal setup (for reference)

```python
# docs/conf.py
project = "acme-utils"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # Google/NumPy docstring support
    "sphinx_rtd_theme",
]
html_theme = "sphinx_rtd_theme"
```

## Documentation Quality Management

### Link verification

```bash
# mkdocs-linkcheck plugin
pip install mkdocs-linkcheck
# Add to mkdocs.yml:
# plugins:
#   - linkcheck
```

### Code example verification

```bash
# Use pytest's doctest feature
pytest --doctest-modules src/acme_utils/

# Or executable code blocks in mkdocs
# pymdownx.superfences + pytest-examples combination
```

### Documentation coverage

```bash
# interrogate: measure docstring coverage
pip install interrogate
interrogate src/acme_utils/ -v
```

```text
Name                              Stmts  Miss  Cover
---------------------------------------------------
src/acme_utils/__init__.py            5     0   100%
src/acme_utils/core.py               45     3    93%
src/acme_utils/config.py             20     5    75%
---------------------------------------------------
TOTAL                                70     8    89%
```

```toml
# pyproject.toml
[tool.interrogate]
ignore-init-method = true
ignore-init-module = true
fail-under = 80
```

## Versioned Documentation

```bash
# mike: MkDocs version management tool
pip install mike

# Deploy per version
mike deploy 1.0 latest --push
mike deploy 1.1 latest --push --update-aliases

# Users can select documentation version
# https://acme.github.io/acme-utils/1.0/
# https://acme.github.io/acme-utils/latest/
```

## CHANGELOG Documentation

The CHANGELOG is both a release note and a contract with users.

### Keep a Changelog format — practical example

````markdown
# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- `Engine.stream()` method for large result sets (#45)

### Fixed
- Connection pool exhaustion under high concurrency (#42)

## [1.3.0] - 2024-07-01

### Added
- Retry decorator with configurable backoff strategy
- `Settings.from_toml()` class method

### Changed
- Default timeout increased from 5s to 30s

### Deprecated
- `Engine.execute()` - use `Engine.run()` instead

## [1.2.0] - 2024-05-15

### Added
- Python 3.12 support
- Type stubs for all public APIs

### Removed
- Python 3.9 support (EOL)

[Unreleased]: https://github.com/acme/acme-utils/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/acme/acme-utils/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/acme/acme-utils/releases/tag/v1.2.0
````

### CHANGELOG auto-generation tools

```bash
# git-cliff: Generate CHANGELOG from Conventional Commits
pip install git-cliff

# cliff.toml configuration
cat > cliff.toml << 'EOF'
[changelog]
header = "# Changelog\n"
body = """
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})
{% endfor %}
{% endfor %}
"""

[git]
conventional_commits = true
commit_parsers = [
    { message = "^feat", group = "Added" },
    { message = "^fix", group = "Fixed" },
    { message = "^doc", group = "Documentation" },
    { message = "^perf", group = "Performance" },
    { message = "^refactor", group = "Changed" },
]
EOF

# Run
git-cliff --output CHANGELOG.md
```

## Search Optimization for Documentation Sites

MkDocs Material's built-in search uses client-side indexing.

```yaml
# mkdocs.yml
plugins:
  - search:
      lang: en
      separator: '[\s\-\.]+' 
  - tags:
      tags_file: tags.md

# Add metadata to each page
# docs/guide/configuration.md top:
# ---
# tags:
#   - configuration
#   - settings
#   - environment variables
# ---
```

### SEO metadata

```yaml
# mkdocs.yml
plugins:
  - social  # Auto-generate Open Graph images
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/acme/acme-utils
    - icon: fontawesome/brands/python
      link: https://pypi.org/project/acme-utils/
```

## Practical Documentation Workflow

```text
Code change
    │
    ▼
Write/update docstrings
    │
    ▼
Local preview with mkdocs serve
    │
    ▼
Create PR → Review
    │
    ▼
Merge to main → CI deploys automatically
    │
    ▼
https://acme.github.io/acme-utils/ updated
```

### Documentation review checklist

```text
□ New public APIs have docstrings
□ Code examples are runnable
□ Internal links are not broken
□ Screenshots/diagrams are up to date
□ CHANGELOG has been updated
```

## Using Admonitions

MkDocs Material admonitions (warning/info boxes) significantly improve documentation readability.

````markdown
!!! tip "Best Practice"
    Read configuration from environment variables, but always provide defaults.

!!! warning "Breaking Change"
    `Engine.execute()` will be removed in v2.0. Use `Engine.run()` instead.

!!! example "Usage Example"
    ```python
    from acme_utils import Engine
    engine = Engine.from_env()
    ```

!!! note
    This feature is only available on Python 3.11 and above.
````

## Answering the Opening Questions

- **What should a good README contain?**
  - A one-line description that conveys the package's purpose within 30 seconds, copy-paste-ready install commands and Quick Start code, key feature list, and links to detailed docs are essential. Badges (CI status, version, Python support) show trustworthiness, and including contribution guidelines is a bonus.
- **What's the difference between MkDocs and Sphinx?**
  - MkDocs uses Markdown + YAML for simple setup and produces modern docs quickly with the Material theme. Sphinx is reStructuredText-based with rich features but complex configuration. For new Python projects, MkDocs + mkdocstrings is most productive; for large legacy projects, Sphinx is more suitable.
- **How do you auto-generate API documentation?**
  - The mkdocstrings plugin reads source code docstrings to auto-generate API docs. Writing Google-style docstrings with `Args`, `Returns`, `Raises`, `Example` produces structured API documentation. Auto-deploying to GitHub Pages with `mkdocs gh-deploy` in CI keeps docs updated automatically with code changes.

<!-- toc:begin -->
## In this series

- [Python Package 101 (1/10): What Is a Python Package?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): Project Structure — src layout and pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): Building Packages — wheel and sdist](./04-building-packages.md)
- [Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production](./05-publishing-to-pypi.md)
- [Python Package 101 (6/10): Versioning and Releases](./06-versioning-and-releases.md)
- [Python Package 101 (7/10): CLI Packages](./07-cli-packages.md)
- [Python Package 101 (8/10): Type Hints and Static Analysis](./08-type-hints-and-static-analysis.md)
- **Python Package 101 (9/10): Documentation — README, MkDocs, API Reference (current)**
- Python Package 101 (10/10): Production Package Template (upcoming)

<!-- toc:end -->

## References

- [MkDocs documentation](https://www.mkdocs.org/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Write the Docs - Documentation Guide](https://www.writethedocs.org/guide/)

Tags: Python, Packaging, PyPI, pyproject.toml
