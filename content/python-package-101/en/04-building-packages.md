---
title: "Python Package 101 (4/10): Building Packages — wheel and sdist"
series: python-package-101
episode: 4
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
- wheel
- sdist
- Build
- Packaging
- Distribution
last_reviewed: '2026-05-15'
seo_description: A wheel is a pre-built package file and an sdist is a source archive.
  You need both so your package can be installed anywhere.
---

# Python Package 101 (4/10): Building Packages — wheel and sdist

Once your package structure is stable, the next question is whether you can produce artifacts that install cleanly outside your repository. That is where wheel, sdist, and post-build verification start to matter.

This is post 4 in the Python Package 101 series. Here we compare wheel and sdist, inspect what `python -m build` actually produces, and validate the output in a fresh environment before publishing anything.

![Python Package 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/04/04-01-mental-model.en.png)
*Python Package 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What is the difference between wheel and sdist?
- What files does `python -m build` generate?
- What is inside a `.whl` file?

## What you will learn

- The difference between sdist (source distribution) and wheel (built distribution)
- How to generate both distribution types with `python -m build`
- The internal structure of a `.whl` file
- How to control which files are included in the build

## Why it matters

`pip install` downloads a package from PyPI and installs it. The downloaded file is either a wheel or an sdist. To distribute your own package, you need to create these files.

> When you run `pip install mylib`, pip looks for a wheel first. If no wheel exists, it downloads the sdist and builds locally. Packages without wheels install slowly and require build tools.

## Mental Model

> An sdist is a recipe (source code + ingredient list) and a wheel is a frozen meal (ready to eat). You can share the recipe or the finished product, but the finished product is faster to consume.

```text
source code → python -m build → dist/
                                ├── mylib-0.1.0.tar.gz     (sdist)
                                └── mylib-0.1.0-py3-none-any.whl  (wheel)
```

## Core Concepts

| Term | Description | File Format |
|---|---|---|
| sdist | Source code + metadata archive | `.tar.gz` |
| wheel | Pre-built distribution | `.whl` (ZIP format) |
| build frontend | Tool that runs the build | `python -m build`, `uv build` |
| build backend | Tool that performs the actual build logic | `setuptools`, `hatchling` |
| dist/ | Directory where build artifacts are saved | `dist/mylib-0.1.0.tar.gz` |

## Before / After

**Before (sdist only)**

```bash
pip install mylib
# Downloading mylib-0.1.0.tar.gz
# Building wheel from source...  ← local build (slow)
# Successfully installed mylib
```

**After (wheel available)**

```bash
pip install mylib
# Downloading mylib-0.1.0-py3-none-any.whl
# Successfully installed mylib  ← no build needed (fast)
```

## Step-by-step practice

### Step 1. Install the build tool

```bash
cd ~/practice/mylib-project
source .venv/bin/activate
pip install build
```

### Step 2. Run the build

```bash
python -m build

# * Creating sdist...
# * Creating wheel...
# Successfully built mylib-0.1.0.tar.gz and mylib-0.1.0-py3-none-any.whl

ls dist/
# mylib-0.1.0-py3-none-any.whl
# mylib-0.1.0.tar.gz
```

### Step 3. Inspect the wheel file

```bash
# .whl is a ZIP file
unzip -l dist/mylib-0.1.0-py3-none-any.whl
# mylib/__init__.py
# mylib/core.py
# mylib-0.1.0.dist-info/METADATA
# mylib-0.1.0.dist-info/WHEEL
# mylib-0.1.0.dist-info/RECORD
```

### Step 4. Inspect the sdist file

```bash
tar tzf dist/mylib-0.1.0.tar.gz
# mylib-0.1.0/
# mylib-0.1.0/pyproject.toml
# mylib-0.1.0/src/mylib/__init__.py
# mylib-0.1.0/src/mylib/core.py
# mylib-0.1.0/PKG-INFO
```

### Step 5. Test installing the built package

```bash
# Test wheel install in a fresh virtual environment
python -m venv /tmp/test-install
source /tmp/test-install/bin/activate
pip install dist/mylib-0.1.0-py3-none-any.whl

python -c "from mylib.core import greet; print(greet('Test'))"
# Hello, Test!
deactivate
```

## What to notice in this code

- The wheel filename `mylib-0.1.0-py3-none-any.whl` means `py3` (Python 3), `none` (no ABI), `any` (all platforms)
- The sdist includes `pyproject.toml` so the recipient can build from source
- `dist-info/METADATA` is the transformed content of `[project]` in pyproject.toml
- `dist-info/RECORD` records hashes for every installed file

## Common mistakes

### Mistake 1. Committing dist/ to Git

Build artifacts should not be committed. Add `dist/` to `.gitignore`.

### Mistake 2. Uploading only the wheel and skipping the sdist

Packages with C extensions need platform-specific wheels. Having an sdist means anyone can build from source on any platform.

### Mistake 3. Rebuilding with old artifacts still in dist/

```bash
rm -rf dist/ build/ *.egg-info
python -m build    # build from a clean state
```

### Mistake 4. Not testing the install after building

A successful build can still have missing files. Always install in a fresh virtual environment and verify imports.

### Mistake 5. Not understanding wheel filename tags

`py3-none-any` means a pure Python package. C extensions produce platform-specific tags like `cp311-cp311-manylinux_2_17_x86_64`.

## Practical applications

- **CI/CD pipelines**: `python -m build` is the first step in the build-test-upload flow
- **Internal package repositories**: Upload wheels to Artifactory or Nexus for team sharing
- **Docker optimization**: Pre-building wheels reduces Docker image build time
- **Cross-platform**: Use `cibuildwheel` to build wheels for multiple platforms at once
- **Reproducibility**: Record artifact hashes to verify identical inputs produce identical outputs

## How practitioners think about this

For pure Python packages, building is straightforward. `python -m build` is all you need. Complexity arises with C extensions. That is why packages like NumPy and pandas provide dozens of wheels for each OS and Python version combination.

Most application developers only create pure Python packages, so a `py3-none-any` wheel is sufficient. What matters is the habit of building and then testing the install in a fresh environment.

## Checklist

- [ ] You can explain the difference between sdist and wheel
- [ ] You can generate both distribution types with `python -m build`
- [ ] You can inspect the internal structure of a wheel file
- [ ] You can test-install build artifacts in a fresh virtual environment
- [ ] You can interpret wheel filename tags (py3-none-any)

## Exercises

1. Build the project from the previous post with `python -m build` and inspect the contents of `dist/`.
2. Open the `.whl` file with `unzip -l` to see which files are included, and read the `METADATA` file.
3. Create a fresh virtual environment, install the built wheel, and verify that imports work correctly.

## Summary and next

- An sdist is a source archive; a wheel is a pre-built distribution.
- `python -m build` generates both.
- Wheels make installation fast; sdists make building possible anywhere.
- Always test-install in a fresh environment after building.
- Pure Python packages produce `py3-none-any` wheels.

The next post covers **publishing to PyPI** — from TestPyPI to production.

## Answering the Opening Questions

- **What is the difference between wheel and sdist?**
  - The article treats Building Packages — wheel and sdist as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What files does `python -m build` generate?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What is inside a `.whl` file?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Python Package 101 (1/10): What Is a Python Package?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): Project Structure — src layout and pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements](./03-dependency-management.md)
- **Python Package 101 (4/10): Building Packages — wheel and sdist (current)**
- Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production (upcoming)
- Python Package 101 (6/10): Versioning and Releases (upcoming)
- Python Package 101 (7/10): CLI Packages (upcoming)
- Python Package 101 (8/10): Type Hints and Static Analysis (upcoming)
- Python Package 101 (9/10): Documentation — README, MkDocs, API Reference (upcoming)
- Python Package 101 (10/10): Production Package Template (upcoming)

<!-- toc:end -->

## References

- [Python Packaging User Guide - Packaging your project](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives)
- [PEP 427 - The Wheel Binary Package Format](https://peps.python.org/pep-0427/)
- [PyPA build - A simple PEP 517 build frontend](https://build.pypa.io/en/stable/)
- [Real Python - Python Wheels](https://realpython.com/python-wheels/)

Tags: Python, Packaging, PyPI, pyproject.toml
