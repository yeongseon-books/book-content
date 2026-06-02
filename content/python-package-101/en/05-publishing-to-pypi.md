---
title: "Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production"
series: python-package-101
episode: 5
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
- PyPI
- twine
- Publishing
- TestPyPI
- Distribution
last_reviewed: '2026-05-15'
seo_description: PyPI is the app store for Python packages and twine is the tool that
  uploads your built package to PyPI.
---

# Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production

Publishing is where packaging shifts from local correctness to operational discipline. Account setup, token handling, staging uploads, and install verification all matter before you expose a package to real users.

This is the 5th post in the Python Package 101 series. Here we separate TestPyPI from PyPI, walk through the `twine` upload flow, and build a safer release habit around staging-first validation.

![Python Package 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/05/05-01-mental-model.en.png)
*Python Package 101 chapter 5 flow overview*

## Questions to Keep in Mind

- What is the difference between PyPI and TestPyPI?
- What role does `twine` play?
- How do you generate and manage API tokens?

## What you will learn

- How to create PyPI and TestPyPI accounts and generate API tokens
- How to upload packages with `twine`
- The workflow of testing on TestPyPI before publishing to PyPI
- How to handle upload failures

## Why it matters

Once you have built a package, you need to publish it so others can install it with `pip install`. Uploading to PyPI makes your package available to anyone worldwide. Uploading to an internal repository shares it within your team.

> Your team installs a shared utility library directly from Git: `pip install git+https://...`. When the branch changes, behavior changes too, and installation is slow.

Publishing to PyPI pins the version and makes installation stable.

## Mental Model

> PyPI is the app store and twine is the submission tool. TestPyPI is staging and PyPI is production. Test on staging first, then deploy to production.

```text
python -m build → dist/*.whl, dist/*.tar.gz
                     ↓
              twine check dist/*       (validate)
                     ↓
          twine upload --repository testpypi dist/*  (staging)
                     ↓
              pip install --index-url https://test.pypi.org/simple/ mylib  (test)
                     ↓
          twine upload dist/*          (production)
```

## Core Concepts

| Term | Description | URL |
|---|---|---|
| PyPI | Python Package Index, the official package repository | pypi.org |
| TestPyPI | Test environment for PyPI | test.pypi.org |
| twine | Package upload tool | `pip install twine` |
| API token | Authentication token used instead of passwords | `pypi-` prefix |
| Trusted Publisher | Token-free publishing from GitHub Actions | OIDC-based |

## Before / After

**Before (install directly from Git)**

```bash
pip install git+https://github.com/team/mylib.git@main
# → behavior changes when the branch changes
# → slow install (clone + build)
# → hard to pin versions
```

**After (install from PyPI)**

```bash
pip install mylib==0.1.0
# → pinned to a version
# → instant install if wheel exists
# → identical result everywhere
```

## Step-by-step practice

### Step 1. Create a TestPyPI account and token

```text
1. Register at https://test.pypi.org/account/register/
2. Generate an API token at https://test.pypi.org/manage/account/
3. Save the token securely (a string starting with pypi-)
```

### Step 2. Install twine and validate the build

```bash
pip install twine
python -m build                 # build from previous post

twine check dist/*
# Checking dist/mylib-0.1.0-py3-none-any.whl: PASSED
# Checking dist/mylib-0.1.0.tar.gz: PASSED
```

### Step 3. Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
# Enter your API token: pypi-...

# Uploading mylib-0.1.0-py3-none-any.whl
# Uploading mylib-0.1.0.tar.gz
# View at: https://test.pypi.org/project/mylib/0.1.0/
```

### Step 4. Test install from TestPyPI

```bash
python -m venv /tmp/test-pypi
source /tmp/test-pypi/bin/activate

pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    mylib

python -c "from mylib.core import greet; print(greet('PyPI'))"
# Hello, PyPI!
deactivate
```

### Step 5. Publish to the real PyPI

```bash
# PyPI account and token are separate (pypi.org)
twine upload dist/*
# Enter your API token: pypi-...

# View at: https://pypi.org/project/mylib/0.1.0/
```

## What to notice in this code

- `twine check` catches metadata errors before uploading
- TestPyPI needs `--extra-index-url` because dependency packages may not exist on TestPyPI
- API tokens use `__token__` as the username and the token string as the password
- Once a version is uploaded, it cannot be modified. You must bump the version and upload again

## Common mistakes

### Mistake 1. Trying to re-upload the same version

PyPI does not allow overwriting an existing version. If you need to fix something, bump the version number.

### Mistake 2. Hardcoding the API token in code

```bash
# Wrong: token ends up in Git history
twine upload --password pypi-abc123 dist/*

# Correct: use environment variables or .pypirc
export TWINE_PASSWORD=pypi-abc123
```

### Mistake 3. Skipping TestPyPI and uploading directly to PyPI

Test on TestPyPI first. Once uploaded to PyPI, a release cannot be deleted (only the entire project can be removed within 72 hours).

### Mistake 4. Not checking if the package name is already taken

If a name is already registered on PyPI, you cannot use it. Check with `pip index versions mylib` or search pypi.org beforehand.

### Mistake 5. Uploading with old version files still in dist/

```bash
rm -rf dist/
python -m build
twine upload dist/*    # upload only the current version
```

## Practical applications

- **CI/CD automated publishing**: GitHub Actions triggers PyPI upload on tag push
- **Trusted Publisher**: OIDC-based publishing from GitHub Actions without API tokens
- **Internal repositories**: Publish internal packages to Artifactory, Nexus, or devpi
- **Pre-release**: Use versions like `0.1.0rc1` for beta testing
- **README rendering**: The README shown on PyPI is specified via `[project.readme]`

## How practitioners think about this

Manual publishing invites mistakes. Automating build-test-upload in CI/CD is the standard practice. GitHub Actions + Trusted Publisher eliminates the need for token management entirely.

Package names are hard to change once chosen. Pick a name that is intuitive, does not conflict with existing packages, and is easy to search. Search PyPI and run `pip index versions` before publishing.

## Checklist

- [ ] You can create a TestPyPI account and generate an API token
- [ ] You can validate build artifacts with `twine check`
- [ ] You can upload to TestPyPI and test-install from it
- [ ] You can publish to the real PyPI
- [ ] You can manage API tokens securely via environment variables

## Exercises

1. Create a TestPyPI account and upload the package you built in the previous post.
2. Install your package from TestPyPI in a fresh virtual environment and verify the import works.
3. Write a `~/.pypirc` file so that `twine upload --repository testpypi dist/*` uses the token automatically.

## Summary and next

- PyPI is the official Python package repository; TestPyPI is its test environment.
- `twine check` validates and `twine upload` publishes.
- Always test on TestPyPI before publishing to the real PyPI.
- Once a version is uploaded, it cannot be modified — you must bump the version.
- Keep API tokens out of code; use environment variables or `.pypirc`.

The next post covers **versioning and releases** — SemVer, Git tags, and CHANGELOG.

## Complete PyPI Upload Flow

Publishing a package to PyPI follows four stages: build → verify → upload → confirm.

```text
Development complete
    │
    ▼
python -m build          # generate sdist + wheel
    │
    ▼
python -m twine check dist/*   # validate metadata
    │
    ▼
python -m twine upload --repository testpypi dist/*  # upload to TestPyPI first
    │
    ▼
pip install --index-url https://test.pypi.org/simple/ acme-utils  # verify install
    │
    ▼
python -m twine upload dist/*   # upload to real PyPI
    │
    ▼
pip install acme-utils          # final confirmation
```

## TestPyPI vs PyPI

| Item | TestPyPI | PyPI |
|---|---|---|
| URL | https://test.pypi.org | https://pypi.org |
| Purpose | Test upload workflow | Production distribution |
| Account | Separate account required | Separate account required |
| Package lifetime | May be periodically deleted | Permanent |
| Dependencies | Can only reference TestPyPI packages | References all packages |

### TestPyPI Usage Notes

```bash
# When installing from TestPyPI, dependencies must come from real PyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    acme-utils
```

Your package's dependencies (`httpx`, `pydantic`, etc.) don't exist on TestPyPI, so you need `--extra-index-url` to add the real PyPI.

## twine Detailed Usage

`twine` is the tool for safely uploading packages to PyPI. It enforces HTTPS and pre-validates metadata.

### twine check: Pre-Upload Validation

```bash
python -m twine check dist/*
```

```text
Checking dist/acme_utils-0.1.0.tar.gz: PASSED
Checking dist/acme_utils-0.1.0-py3-none-any.whl: PASSED
```

Issues twine check catches:
- README rendering errors (Markdown/RST syntax)
- Missing required metadata
- Invalid classifiers
- Invalid URLs

### twine upload: Executing the Upload

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to real PyPI
python -m twine upload dist/*

# Upload specific files only
python -m twine upload dist/acme_utils-0.1.0-py3-none-any.whl
```

### .pypirc Configuration File

```ini
# ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxx

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxx
```

**Security note**: Instead of putting tokens directly in `.pypirc`, using environment variables or keyring is more secure.

## API Token Management

### PyPI Token Generation Procedure

```text
1. Go to https://pypi.org/manage/account/
2. Find the "API tokens" section
3. Click "Add API token"
4. Select scope:
   - "Entire account" (all projects) — for initial upload
   - "Project: acme-utils" (specific project) — for subsequent updates
5. Copy the token (starts with pypi-)
```

### Token Storage Method Comparison

| Method | Security | Convenience | Best For |
|---|---|---|---|
| `.pypirc` file | Low | High | Personal dev machine |
| Environment variables | Medium | Medium | CI/CD |
| keyring | High | Medium | Team environments |
| GitHub Secrets | High | High | GitHub Actions |

### Passing Tokens via Environment Variables

```bash
# Authenticate without .pypirc using env vars
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-xxxxxxxxxxxxxxxxxxxxx
python -m twine upload dist/*
```

### Using keyring

```bash
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
# Enter token at prompt

# twine will automatically retrieve the token from keyring
python -m twine upload dist/*
```

## GitHub Actions Automated Deployment

A workflow that automatically deploys to PyPI when a tag is pushed.

### Trusted Publisher (Recommended)

PyPI's Trusted Publisher feature allows uploading directly from GitHub Actions without tokens.

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  push:
    tags: ["v*"]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # required for Trusted Publisher
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
        # Trusted Publisher: no token configuration needed!
```

### Trusted Publisher Setup Procedure

```text
1. In PyPI project settings → "Publishing" tab
2. Click "Add a new publisher"
3. Enter GitHub repository info:
   - Owner: acme
   - Repository: acme-utils
   - Workflow name: publish.yml
   - Environment: (leave empty or 'release')
4. Save
```

This approach eliminates token leak risk and authenticates via GitHub's OIDC token.

### Token-Based Deployment (Alternative)

```yaml
name: Publish to PyPI
on:
  push:
    tags: ["v*"]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build twine
      - run: python -m build
      - run: python -m twine check dist/*
      - run: python -m twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

## Post-Deployment Verification

```bash
# 1. Check PyPI page
# https://pypi.org/project/acme-utils/0.1.0/

# 2. Installation test in a clean environment
python -m venv /tmp/test-deploy
source /tmp/test-deploy/bin/activate
pip install acme-utils==0.1.0
python -c "import acme_utils; print(acme_utils.__version__)"
# 0.1.0

# 3. CLI entry point verification (if applicable)
acme --version
```

## Handling Deployment Mistakes

### You Cannot Re-Upload the Same Version

```bash
python -m twine upload dist/*
# HTTPError: 400 Bad Request
# "File already exists"
```

PyPI does not allow overwriting a published version. If you uploaded a broken version:

1. **Bug fix**: Upload a new patch version (`0.1.1`)
2. **Security issue**: Yank the version on PyPI
3. **Complete removal**: Contact PyPI support (very rare)

### yank: Hiding a Version

```bash
# Yank a specific version from PyPI web UI or API
# Yanked versions are skipped unless explicitly specified
pip install acme-utils         # skips yanked versions
pip install acme-utils==0.1.0  # installs even if yanked (with warning)
```

## Private PyPI Servers

When internal packages cannot be published to public PyPI, use a private registry.

### Simple Approach: devpi

```bash
pip install devpi-server devpi-client
devpi-server --init
devpi-server --start --port 3141

# Usage
pip install --index-url http://localhost:3141/root/pypi/+simple/ acme-utils
```

### AWS CodeArtifact

```bash
# Obtain token from AWS CodeArtifact
aws codeartifact get-authorization-token --domain mycompany --query authorizationToken --output text

# pip configuration
pip install --index-url https://aws:TOKEN@mycompany-123456789.d.codeartifact.us-east-1.amazonaws.com/pypi/internal/simple/ acme-utils
```

### Setting Default Registry with pip.conf

```ini
# ~/.config/pip/pip.conf (Linux)
[global]
extra-index-url = https://pypi.mycompany.com/simple/
trusted-host = pypi.mycompany.com
```

## Release Automation Full Pipeline

In production, releases are managed through automated pipelines rather than manual commands.

### Release Flow Example

```text
1. Developer: git tag v0.2.0 && git push --tags
2. GitHub Actions: detect tag → build → test → deploy
3. PyPI: new version registered
4. GitHub: Release page auto-generated
```

### Full Workflow (Test + Deploy + Release)

```yaml
name: Release
on:
  push:
    tags: ["v*"]

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
      - run: pip install -e ".[dev]"
      - run: pytest -q
      - run: ruff check .
      - run: mypy src

  publish:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write  # for GitHub Release creation
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
      - uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          files: dist/*
```

### Release Checklist

```text
Before deployment:
□ Update CHANGELOG.md
□ Verify version number (pyproject.toml or Git tag)
□ All tests passing
□ Installation verified on TestPyPI
□ README rendering confirmed

After deployment:
□ Metadata verified on PyPI page
□ pip install confirmed
□ import + __version__ output verified
□ GitHub Release notes confirmed
□ Documentation site updated
```

## Upload Troubleshooting

### Problem 1: File Size Exceeded

```text
HTTPError: 400 Bad Request
"File too large"
```

PyPI's default file size limit is 100MB. Don't include large models or data—use a separate download mechanism.

### Problem 2: README Rendering Error

```bash
# Preview README rendering locally
pip install readme-renderer
python -m readme_renderer README.md -o /tmp/readme.html
# Open /tmp/readme.html in browser to verify
```

### Problem 3: Network Timeout

```bash
# Add retry options
python -m twine upload --verbose --disable-progress-bar dist/*

# Or configure proxy
export HTTPS_PROXY=http://proxy.company.com:8080
python -m twine upload dist/*
```

### Problem 4: Version Already Exists

```bash
# Trying to re-upload an existing version causes an error
# Solution: increment the version number
# pyproject.toml: version = "0.1.1"
# Or use post-release: version = "0.1.0.post1"
```

## PyPI Project Page Optimization

Your PyPI page is the first impression of your package. Well-filled metadata improves search visibility and trustworthiness.

```toml
[project]
name = "acme-utils"
description = "Production-ready utility library for Acme microservices"
readme = "README.md"
license = {text = "MIT"}
keywords = ["utility", "microservices", "acme"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries",
    "Typing :: Typed",
]

[project.urls]
Homepage = "https://github.com/acme/acme-utils"
Documentation = "https://acme.github.io/acme-utils"
Changelog = "https://github.com/acme/acme-utils/blob/main/CHANGELOG.md"
"Bug Tracker" = "https://github.com/acme/acme-utils/issues"
```

### Recommended README Structure

```markdown
# acme-utils

Production-ready utility library for Acme microservices.

## Installation

pip install acme-utils

## Quick Start

(3-5 line code example)

## Features

- Feature 1
- Feature 2

## Documentation

Full docs: https://acme.github.io/acme-utils

## License

MIT
```

### Checking PyPI Download Statistics

```bash
pip install pypistats
pypistats overall acme-utils        # total downloads
pypistats python_minor acme-utils   # downloads by Python version
pypistats system acme-utils         # downloads by OS
```

Understanding usage patterns helps you make data-driven decisions about which Python versions and platforms to support.

## Answering the Opening Questions

- **What's the difference between PyPI and TestPyPI?**
  - TestPyPI is a separate environment for validating upload flows—accounts and tokens are independent from PyPI. Packages uploaded to TestPyPI may be periodically deleted and cannot reference actual PyPI packages during dependency resolution. Use it as a rehearsal before real deployment.
- **What exactly does `twine` do?**
  - twine uploads built sdist/wheel to PyPI over HTTPS. Before uploading, `twine check` validates metadata, README rendering, and classifier accuracy. Unlike `setup.py upload`, it separates build from upload to ensure security and reproducibility.
- **How do you create and manage API tokens?**
  - Generate tokens with project scope in PyPI account settings. Locally use keyring; in CI use GitHub Secrets or Trusted Publisher. Trusted Publisher uses OIDC to eliminate the need for tokens entirely, fundamentally removing leak risk.

<!-- toc:begin -->
## In this series

- [Python Package 101 (1/10): What Is a Python Package?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): Project Structure — src layout and pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): Building Packages — wheel and sdist](./04-building-packages.md)
- **Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production (current)**
- Python Package 101 (6/10): Versioning and Releases (upcoming)
- Python Package 101 (7/10): CLI Packages (upcoming)
- Python Package 101 (8/10): Type Hints and Static Analysis (upcoming)
- Python Package 101 (9/10): Documentation — README, MkDocs, API Reference (upcoming)
- Python Package 101 (10/10): Production Package Template (upcoming)

<!-- toc:end -->

## References

- [Python Packaging User Guide - Uploading](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives)
- [PyPI - Publishing with Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [twine documentation](https://twine.readthedocs.io/)
- [TestPyPI](https://test.pypi.org/)

Tags: Python, Packaging, PyPI, pyproject.toml
