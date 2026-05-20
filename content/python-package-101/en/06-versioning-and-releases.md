---
title: "Python Package 101 (6/10): Versioning and Releases"
series: python-package-101
episode: 6
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
- Versioning
- SemVer
- Release
- CHANGELOG
- Git Tag
last_reviewed: '2026-05-15'
seo_description: SemVer assigns meaning to version numbers, and Git tags mark specific
  commits as release points.
---

# Python Package 101 (6/10): Versioning and Releases

After the first public release, users stop asking only “does it work?” and start asking “is this update safe?” Version numbers, tags, and changelogs are the signals they rely on.

This is post 6 in the Python Package 101 series. Here we translate code changes into SemVer decisions, keep package metadata in sync, and turn release history into something users can trust.

## Questions to Keep in Mind

- When do you bump each part of MAJOR.MINOR.PATCH in SemVer?
- Where in the code should the version be recorded?
- What is the relationship between Git tags and releases?

## Big Picture

![Python Package 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/06/06-01-mental-model.en.png)

*Python Package 101 chapter 6 flow overview*

This picture places Versioning and Releases inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Versioning and Releases is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What you will learn

- SemVer rules and when to bump each part
- How to keep the version in sync between pyproject.toml and `__version__`
- How to mark and manage releases with Git tags
- How to write a CHANGELOG and automate it

## Why it matters

When you update a package, users need to judge "is this update safe?" The version number is that signal. Meaningless version bumps confuse users, and shipping a breaking change as a PATCH breaks their code.

> You ran `pip install mylib --upgrade` for a patch update, but the API changed and production broke. The bump was `0.2.3 → 0.2.4`, so you assumed it was safe — but a function signature had changed.

## Mental Model

> SemVer is a traffic light. PATCH (green) is safe to upgrade, MINOR (yellow) adds new features but keeps existing ones, MAJOR (red) may require changes to your code.

```text
MAJOR . MINOR . PATCH
  1   .   2   .   3

PATCH  (1.2.3 → 1.2.4): Bug fix, no API changes
MINOR  (1.2.4 → 1.3.0): New feature, existing API preserved
MAJOR  (1.3.0 → 2.0.0): API changed or removed (breaking)
```

## Core Concepts

| Term | Description | Example |
|---|---|---|
| SemVer | Semantic Versioning rules | `1.2.3` |
| pre-release | Test version before a stable release | `1.0.0rc1`, `1.0.0a1` |
| Git tag | A label attached to a specific commit | `git tag v1.0.0` |
| CHANGELOG | Document recording changes per version | `CHANGELOG.md` |
| single source of truth | Version managed from exactly one place | pyproject.toml or `__version__` |

## Before / After

**Before (no version management)**

```text
# commit messages only
"fixed bug"
"added feature"
"more fixes"
# → no way to tell which commit is which release
```

**After (SemVer + Git tag + CHANGELOG)**

```text
v1.2.3 ← git tag
  CHANGELOG.md:
  ## 1.2.3 (2026-05-04)
  ### Fixed
  - Fixed timeout error in API client
```

## Step-by-step practice

### Step 1. Set the version in pyproject.toml

```toml
[project]
name = "mylib"
version = "0.1.0"
```

### Step 2. Sync __version__

```python
# src/mylib/__init__.py
"""mylib - A sample Python package."""
__version__ = "0.1.0"
```

```python
# How users check the version
import mylib
print(mylib.__version__)  # 0.1.0
```

### Step 3. Mark a release with a Git tag

```bash
git add .
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main --tags

# List tags
git tag
# v0.1.0
```

### Step 4. Write a CHANGELOG

```markdown
# CHANGELOG.md

## 0.1.0 (2026-05-04)

### Added
- Initial release
- `core.greet()` function
- src layout project structure
- pyproject.toml configuration
```

### Step 5. Bump the version and release

```bash
# pyproject.toml: version = "0.2.0"
# src/mylib/__init__.py: __version__ = "0.2.0"

git add .
git commit -m "Release v0.2.0: add string utilities"
git tag v0.2.0
python -m build
twine upload dist/*
```

## What to notice in this code

- The `version` in pyproject.toml and `__version__` must always match
- Adding a `v` prefix to Git tags is a widely followed convention (`v0.1.0`)
- CHANGELOG follows the [Keep a Changelog](https://keepachangelog.com/) format as a standard
- Without the `--tags` option, `git push` does not push tags to the remote

## Common mistakes

### Mistake 1. pyproject.toml and __version__ are different

When the two versions diverge, `pip show` and `import` report different values. Manage from a single source.

### Mistake 2. Shipping a breaking change as a PATCH

Changing function signatures, return values, or adding required arguments is a MAJOR bump.

### Mistake 3. Expecting stability from 0.x versions

In SemVer, `0.x.y` signals initial development where the API can change at any time. `1.0.0` is the first stable release.

### Mistake 4. Not writing a CHANGELOG

Users need to know "what changed in this update?" Git log alone is not enough.

### Mistake 5. Tagging before testing

Tags should be applied after the build and tests pass. In CI/CD, a tag push triggers deployment, so tagging early deploys broken code.

## Practical applications

- **CI/CD trigger**: Git tag push triggers automatic build and PyPI upload
- **Dependabot/Renovate**: Automatically creates PRs when dependencies release new versions
- **Dynamic versioning**: `setuptools-scm` extracts the version from Git tags automatically
- **Pre-release**: Staged releases via `1.0.0a1 → 1.0.0b1 → 1.0.0rc1 → 1.0.0`
- **GitHub Releases**: Link Git tags with CHANGELOG entries to auto-generate release notes

## How practitioners think about this

The hardest part of versioning is deciding "is this change MINOR or MAJOR?" The rule is simple: **if existing users' code works without modification, it is MINOR; if they need to change their code, it is MAJOR**.

If managing versions in two places is tedious, use `setuptools-scm`. Just tag a commit (`v0.1.0`) and the version in pyproject.toml is determined automatically.

## Checklist

- [ ] You can explain the criteria for each part of MAJOR.MINOR.PATCH
- [ ] You know how to sync pyproject.toml and `__version__`
- [ ] You can mark releases with Git tags
- [ ] You can write a CHANGELOG in Keep a Changelog format
- [ ] You understand what pre-release versions mean

## Exercises

1. Add a `v0.1.0` tag to the project from the previous post and verify with `git log --oneline --decorate`.
2. Add a new function, bump to `0.2.0`, and record the changes in CHANGELOG.md.
3. Install `setuptools-scm` and configure dynamic versioning in pyproject.toml.

## Summary and next

- SemVer is MAJOR (breaking).MINOR (new feature).PATCH (bug fix).
- Keep pyproject.toml and `__version__` in sync.
- Git tags mark specific commits as release points.
- CHANGELOG is the official document where users check what changed.
- Tag after tests pass; tags trigger deployment.

The next post covers **CLI packages** — entry points and click.

## Answering the Opening Questions

- **When do you bump each part of MAJOR.MINOR.PATCH in SemVer?**
  - The article treats Versioning and Releases as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Where in the code should the version be recorded?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What is the relationship between Git tags and releases?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Python Package 101 (1/10): What Is a Python Package?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): Project Structure — src layout and pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): Building Packages — wheel and sdist](./04-building-packages.md)
- [Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production](./05-publishing-to-pypi.md)
- **Python Package 101 (6/10): Versioning and Releases (current)**
- Python Package 101 (7/10): CLI Packages (upcoming)
- Python Package 101 (8/10): Type Hints and Static Analysis (upcoming)
- Python Package 101 (9/10): Documentation — README, MkDocs, API Reference (upcoming)
- Python Package 101 (10/10): Production Package Template (upcoming)

<!-- toc:end -->

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PEP 440 - Version Identification and Dependency Specification](https://peps.python.org/pep-0440/)
- [setuptools-scm](https://setuptools-scm.readthedocs.io/)

Tags: Python, Packaging, PyPI, pyproject.toml
