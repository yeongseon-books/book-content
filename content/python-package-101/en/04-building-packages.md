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

This is the 4th post in the Python Package 101 series. Here we compare wheel and sdist, inspect what `python -m build` actually produces, and validate the output in a fresh environment before publishing anything.

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

## Build Process Internals

When you run `python -m build`, here's what happens step by step.

### Build Isolation Environment

```text
python -m build execution flow:
    │
    ▼
1. Create temporary directory (/tmp/build-env-xxxx/)
    │
    ▼
2. Read [build-system].requires from pyproject.toml
    │
    ▼
3. Install build dependencies in isolated environment
   (setuptools, wheel, etc.)
    │
    ▼
4. Call build-backend's build_sdist() → .tar.gz created
    │
    ▼
5. Call build-backend's build_wheel() → .whl created
    │
    ▼
6. Place artifacts in dist/ directory
```

```bash
# View detailed build logs
python -m build --no-isolation 2>&1 | head -30
# --no-isolation: build with current environment tools (for debugging)
```

### sdist vs wheel Detailed Comparison

| Property | sdist (.tar.gz) | wheel (.whl) |
|---|---|---|
| Contents | Source code + build scripts | Pre-built files |
| Build on install | Required (runs setup.py) | Not needed (just unzip) |
| C extensions | Compiled in user's environment | Pre-compiled binaries |
| Install speed | Slow | Fast |
| Platform dependency | Determined at build time | Encoded in filename |
| PyPI recommendation | Upload sdist + wheel together | Primary install target |

### sdist Internal Structure

```bash
tar tzf dist/acme_utils-0.1.0.tar.gz | head -15
```

```text
acme_utils-0.1.0/
├── PKG-INFO                    # metadata (similar to METADATA)
├── pyproject.toml              # original build config
├── README.md
├── src/
│   └── acme_utils/
│       ├── __init__.py
│       ├── core.py
│       └── config.py
└── tests/                      # inclusion depends on config
    └── test_core.py
```

### wheel Internal Structure

```bash
unzip -l dist/acme_utils-0.1.0-py3-none-any.whl
```

```text
acme_utils/__init__.py
acme_utils/core.py
acme_utils/config.py
acme_utils/py.typed
acme_utils-0.1.0.dist-info/METADATA
acme_utils-0.1.0.dist-info/WHEEL
acme_utils-0.1.0.dist-info/RECORD
acme_utils-0.1.0.dist-info/entry_points.txt
acme_utils-0.1.0.dist-info/top_level.txt
```

## MANIFEST.in and File Inclusion/Exclusion

Controls which files are included in the sdist.

### setuptools Default Inclusion Rules

```text
Auto-included:
- pyproject.toml, setup.py, setup.cfg
- README, README.md, README.rst
- LICENSE, LICENCE
- Python files (.py) under src/

Auto-excluded:
- __pycache__/
- *.pyc, *.pyo
- .git/, .hg/
- dist/, build/, *.egg-info/
```

### Adding Files with MANIFEST.in

```text
# MANIFEST.in
include CHANGELOG.md
include src/acme_utils/py.typed
recursive-include src *.pyi        # type stubs
recursive-include tests *.py       # include tests (optional)
global-exclude *.pyc __pycache__
```

### Controlling via pyproject.toml (setuptools)

```toml
[tool.setuptools.package-data]
acme_utils = ["py.typed", "*.pyi"]

[tool.setuptools.packages.find]
where = ["src"]
exclude = ["tests*"]
```

## Building C Extension Packages

Packages with non-pure-Python code have a more complex build process.

```toml
# pyproject.toml with C extensions
[build-system]
requires = ["setuptools>=68", "wheel", "cython>=3.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
ext-modules = [
    {name = "acme_utils._speedups", sources = ["src/acme_utils/_speedups.c"]}
]
```

```bash
# Platform-specific wheel generation
python -m build
ls dist/
# acme_utils-0.1.0.tar.gz
# acme_utils-0.1.0-cp311-cp311-linux_x86_64.whl    <- platform-specific!
```

### Multi-Platform Wheels with cibuildwheel

```yaml
# .github/workflows/wheels.yml
name: Build wheels
on: [push]
jobs:
  build_wheels:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: pypa/cibuildwheel@v2.19
        env:
          CIBW_SKIP: "cp36-* cp37-* cp38-* cp39-*"
      - uses: actions/upload-artifact@v4
        with:
          name: wheels-${{ matrix.os }}
          path: wheelhouse/*.whl
```

## Build Verification Checklist

Items to check before distributing build artifacts.

```bash
# 1. Clean dist/ then build
rm -rf dist/
python -m build

# 2. twine check: validate metadata
python -m twine check dist/*
# PASSED acme_utils-0.1.0.tar.gz
# PASSED acme_utils-0.1.0-py3-none-any.whl

# 3. Inspect wheel contents
unzip -l dist/*.whl | grep -v dist-info

# 4. Installation test (in a clean venv)
python -m venv /tmp/test-install
/tmp/test-install/bin/pip install dist/*.whl
/tmp/test-install/bin/python -c "import acme_utils; print(acme_utils.__version__)"

# 5. Verify sdist can build
pip install dist/*.tar.gz
```

### Issues Caught by twine check

```text
WARNING: The long_description is not valid rst.    # README rendering error
ERROR: `long_description_content_type` missing.    # content type not specified
WARNING: No `project_urls` found.                  # no URLs
```

## Reproducible Builds

To always produce identical build artifacts from the same source, additional configuration is needed.

```bash
# Fix timestamps for reproducible builds
SOURCE_DATE_EPOCH=0 python -m build

# Verify: build twice and compare hashes
sha256sum dist/acme_utils-0.1.0-py3-none-any.whl
# Both builds should produce the same hash
```

```toml
# hatchling supports reproducible builds by default
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## setuptools vs hatchling Build Comparison

Comparing the same project built with both backends.

### Building with setuptools

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

```bash
time python -m build
# real    0m4.2s (isolation env creation + setuptools install + build)
ls dist/
# acme_utils-0.1.0.tar.gz  (sdist)
# acme_utils-0.1.0-py3-none-any.whl  (wheel)
```

### Building with hatchling

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/acme_utils"]
```

```bash
time python -m build
# real    0m2.1s (hatchling is lighter)
ls dist/
# acme_utils-0.1.0.tar.gz
# acme_utils-0.1.0-py3-none-any.whl
```

### Output Comparison

The wheel contents from both backends are identical. The difference lies in build speed and configuration style. setuptools excels at legacy compatibility; hatchling offers concise config and faster builds.

## Build Cache and Cleanup

```bash
# Clean build artifacts
rm -rf dist/ build/ src/*.egg-info/

# Leftover .egg-info can break editable installs
find . -name "*.egg-info" -type d -exec rm -rf {} +

# Clean __pycache__
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Build Automation with Makefile

```makefile
.PHONY: clean build check publish

clean:
	rm -rf dist/ build/ src/*.egg-info/

build: clean
	python -m build

check: build
	python -m twine check dist/*

publish-test: check
	python -m twine upload --repository testpypi dist/*

publish: check
	python -m twine upload dist/*
```

```bash
make build    # clean + build
make check    # clean + build + verify
make publish  # clean + build + verify + PyPI upload
```

## Common Build Errors and Solutions

### Error 1: Package Not Found

```text
error: No packages found in `src`
```

```toml
# Cause: missing packages.find config or missing __init__.py
[tool.setuptools.packages.find]
where = ["src"]  # verify this setting exists

# Also verify src/acme_utils/__init__.py exists
```

### Error 2: README Rendering Failure

```text
WARNING: The long_description is not valid reStructuredText
```

```toml
# Solution: explicitly specify content-type
[project]
readme = {file = "README.md", content-type = "text/markdown"}
```

### Error 3: Invalid Version Format

```text
Invalid version: '0.1.0-beta'
```

```text
# PEP 440 valid versions:
0.1.0
0.1.0a1        # alpha
0.1.0b2        # beta
0.1.0rc1       # release candidate
0.1.0.post1    # post release
0.1.0.dev1     # development

# Invalid versions:
0.1.0-beta     # hyphens not allowed
v0.1.0         # v prefix not allowed
```

### Error 4: Dependency Build Failure

```text
error: subprocess-exited-with-error
× pip subprocess to install build dependencies did not run successfully
```

```bash
# Solution: upgrade build tools
pip install --upgrade pip setuptools wheel
# Or build without isolation for debugging
python -m build --no-isolation
```

## GitHub Actions Build + Artifact Storage

```yaml
name: build
on:
  push:
    tags: ["v*"]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build twine
      - run: python -m build
      - run: python -m twine check dist/*
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

Pushing a tag automatically triggers the build and stores artifacts. These artifacts can be used by subsequent deployment jobs.

## Build Artifact Size Optimization

Including unnecessary files in the distribution package increases install time and security risk.

### Checking for Unwanted Files

```bash
# Check wheel content sizes
python -m zipfile -l dist/acme_utils-0.1.0-py3-none-any.whl

# Check for accidentally included files
unzip -l dist/*.whl | grep -E "test_|__pycache__|.pyc"
```

### Exclusion Configuration

```toml
# setuptools
[tool.setuptools.packages.find]
where = ["src"]
exclude = ["tests*", "docs*", "benchmarks*"]

# hatchling
[tool.hatch.build.targets.wheel]
packages = ["src/acme_utils"]
exclude = ["*.test", "tests/"]
```

### Practical Size Guidelines

```text
Pure Python utility: 50-500 KB (wheel)
Web framework: 1-5 MB
Data science (NumPy, etc.): 10-50 MB (includes binaries)
```

If your wheel is unexpectedly large, check whether data files or tests were accidentally included.

## Keeping Local and CI Builds in Sync

Cases where `python -m build` passes locally but fails in CI. Causes and solutions.

### Cause 1: Python Version Difference

```bash
# Local
python --version  # 3.12.4
# CI
python --version  # 3.11.9

# If pyproject.toml has requires-python = ">=3.11"
# both build and tests must pass on 3.11 too.
```

### Cause 2: System Package Dependencies

```bash
# Libraries installed at system level locally
# may not be found in CI's clean environment.
# Solution: declare all dependencies in pyproject.toml
```

### Cause 3: File Permissions and Line Endings

```bash
# Git CRLF conversion can change hashes
# Unify with .gitattributes
echo "* text=auto eol=lf" > .gitattributes
```

### Solution: Use Identical Command Sets

```makefile
# Makefile (run identically in local and CI)
.PHONY: ci
ci: install lint typecheck test build check

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest -q

build:
	python -m build

check:
	python -m twine check dist/*
```

Running `make ci` in the CI workflow guarantees the same verification as local development.

### Is Distributing Only sdist Acceptable?

Uploading only sdist means the user's environment must run the build. For pure Python packages this is fine, but C extensions require users to have a compiler. The standard practice is to upload both wheel and sdist.

```bash
# Recommended for PyPI upload: include both sdist + wheel
ls dist/
# acme_utils-0.1.0.tar.gz           <- sdist
# acme_utils-0.1.0-py3-none-any.whl <- wheel
python -m twine upload dist/*        # upload both
```

pip prefers wheels when available, and only downloads sdist to build when no matching wheel exists for the platform.

The `py3-none-any` tag on a pure Python wheel means it works identically on any Python 3 environment. Build once, use on Linux, macOS, and Windows.

## Answering the Opening Questions

- **What's the difference between sdist and wheel?**
  - sdist is a source code archive requiring a build step during installation. Wheel is a pre-built binary distribution format where installation completes by simply extracting the archive. Upload both sdist and wheel to PyPI, but pip prefers wheel.
- **What does `python -m build` do internally?**
  - It creates an isolated temporary environment, installs the tools from `[build-system].requires`, then calls `build_sdist()` and `build_wheel()` functions from the module pointed to by `build-backend` in sequence. Results are generated as `.tar.gz` and `.whl` files in the `dist/` directory.
- **How do you verify build artifacts are correct?**
  - Use `twine check dist/*` to verify metadata and README rendering, then install the wheel in a clean venv to confirm import and version output work correctly. Separately verifying that the sdist also builds catches source distribution issues early.

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
