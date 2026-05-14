---
title: Documentation — README, MkDocs, API Reference
series: python-package-101
episode: 9
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
- Documentation
- MkDocs
- README
- API Reference
- Sphinx
last_reviewed: '2026-05-04'
seo_description: A README is the front door of your package and an API Reference is
  the manual for every function. A package without docs does not get used.
---

# Documentation — README, MkDocs, API Reference

This is post 9 in the Python Package 101 series.

> Python Package 101 series (9/10)

---

<!-- a-grade-intro:begin -->

## Key Questions

- What should a good README include?
- What is the difference between MkDocs and Sphinx?
- How do you auto-generate an API Reference from docstrings?
- How do you deploy documentation to GitHub Pages?

> A README is the front door of your package and an API Reference is the manual for every function. A package without docs does not get used.

<!-- a-grade-intro:end -->

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
```

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

<!-- toc:begin -->
## Series Table of Contents

- [What Is a Python Package?](./01-what-is-a-python-package.md)
- [Project Structure — src layout and pyproject.toml](./02-project-structure.md)
- [Dependency Management — venv, pip, uv, requirements](./03-dependency-management.md)
- [Building Packages — wheel and sdist](./04-building-packages.md)
- [Publishing to PyPI — from TestPyPI to production](./05-publishing-to-pypi.md)
- [Versioning and Releases](./06-versioning-and-releases.md)
- [CLI Packages](./07-cli-packages.md)
- [Type Hints and Static Analysis](./08-type-hints-and-static-analysis.md)
- **Documentation — README, MkDocs, API Reference (current)**
- Production Package Template (upcoming)

<!-- toc:end -->

## References

- [MkDocs documentation](https://www.mkdocs.org/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Write the Docs - Documentation Guide](https://www.writethedocs.org/guide/)

Tags: Python, Documentation, MkDocs, README, API Reference, Sphinx
