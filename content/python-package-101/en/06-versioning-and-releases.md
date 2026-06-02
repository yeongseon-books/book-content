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

This is the 6th post in the Python Package 101 series. Here we translate code changes into SemVer decisions, keep package metadata in sync, and turn release history into something users can trust.

![Python Package 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/06/06-01-mental-model.en.png)
*Python Package 101 chapter 6 flow overview*

## Questions to Keep in Mind

- When do you bump each part of MAJOR.MINOR.PATCH in SemVer?
- Where in the code should the version be recorded?
- What is the relationship between Git tags and releases?

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

## SemVer (Semantic Versioning) Detailed Rules

SemVer uses `MAJOR.MINOR.PATCH` format, where each number communicates the nature of the change.

### Version Bump Decision Criteria

| Change Type | Which to Bump | Example |
|---|---|---|
| Breaks existing API compat | MAJOR | `1.2.3 → 2.0.0` |
| New feature (backward compatible) | MINOR | `1.2.3 → 1.3.0` |
| Bug fix | PATCH | `1.2.3 → 1.2.4` |

### Decision Flowchart for Practice

```text
There is a change
    │
    ▼
Does it break existing user code?
    ├── Yes → Bump MAJOR
    │         - Function/class deleted
    │         - Parameter name changed
    │         - Return type changed
    │         - Exception type changed
    │
    └── No → Is it a new feature?
              ├── Yes → Bump MINOR
              │         - New function added
              │         - New parameter (with default)
              │         - New class added
              │
              └── No → Bump PATCH
                        - Bug fix
                        - Performance improvement
                        - Internal refactoring
```

### PEP 440: Python's Version Rules

Python packages must follow PEP 440 format. Similar to SemVer but with additional expressions.

```text
Final releases:    1.0.0, 1.2.3
Pre-releases:      1.0.0a1 (alpha), 1.0.0b2 (beta), 1.0.0rc1 (release candidate)
Post-releases:     1.0.0.post1 (documentation fixes, etc.)
Dev versions:      1.0.0.dev1 (not yet released)

# Version comparison order
1.0.0.dev1 < 1.0.0a1 < 1.0.0b1 < 1.0.0rc1 < 1.0.0 < 1.0.0.post1
```

```python
from packaging.version import Version

v1 = Version("1.0.0a1")
v2 = Version("1.0.0")
print(v1 < v2)  # True
print(v1.is_prerelease)  # True
```

## How to Record Version in Code

### Method 1: Static in pyproject.toml

```toml
[project]
version = "1.2.3"
```

```python
# src/acme_utils/__init__.py
__version__ = "1.2.3"  # must manually sync with pyproject.toml
```

**Drawback**: Two places must be updated simultaneously.

### Method 2: Dynamic Version (Single Source of Truth)

```toml
[project]
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "acme_utils.__version__"}
```

```python
# src/acme_utils/__init__.py
__version__ = "1.2.3"  # this is the only version source
```

### Method 3: Auto-Extract from Git Tags (setuptools-scm)

```toml
[build-system]
requires = ["setuptools>=68", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
dynamic = ["version"]

[tool.setuptools_scm]
write_to = "src/acme_utils/_version.py"
version_scheme = "guess-next-dev"
```

```bash
git tag v1.2.3
python -m build
# _version.py auto-generated at build time: __version__ = "1.2.3"

# If there are commits after the tag:
# __version__ = "1.2.4.dev3+g1234567"
```

### Method 4: hatch-vcs

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/acme_utils/_version.py"
```

## CHANGELOG Management

### Keep a Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New `retry` decorator for HTTP calls

### Fixed
- Connection timeout handling in `Client.get()`

## [1.2.0] - 2024-03-15

### Added
- `Client.stream()` method for large responses
- Type stubs for all public APIs

### Changed
- Minimum Python version raised to 3.10

### Deprecated
- `Client.fetch()` - use `Client.get()` instead

## [1.1.0] - 2024-02-01

### Added
- `Config.from_env()` class method

[Unreleased]: https://github.com/acme/acme-utils/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/acme/acme-utils/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/acme/acme-utils/releases/tag/v1.1.0
```

### Automated CHANGELOG Generation

```bash
# git-cliff: generate CHANGELOG from commit messages
pip install git-cliff
git-cliff --output CHANGELOG.md

# Easier automation when following Conventional Commits format
# feat: add retry decorator
# fix: handle connection timeout
# BREAKING CHANGE: drop Python 3.9 support
```

## Release Branch Strategy

### Simple Strategy (Small Projects)

```text
main ─────●─────●─────●─────●──── (always releasable)
          v1.0  v1.1  v1.2  v2.0
```

### Release Branches (Large Projects)

```text
main ─────●─────●─────●─────●────
          │           │
          └── release/1.x ──●──●── (1.x hotfixes)
                      │
                      └── release/2.x ──●── (2.x hotfixes)
```

```bash
# Release procedure
git checkout main
git pull
# Update CHANGELOG, verify version
git tag v1.3.0
git push --tags
# CI automatically deploys to PyPI
```

## Deprecation Policy

You must provide users with adequate warning before removing an API.

```python
import warnings

def old_function():
    warnings.warn(
        "old_function() is deprecated, use new_function() instead. "
        "It will be removed in version 2.0.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return new_function()
```

### Deprecation Timeline Example

```text
v1.3.0: Add DeprecationWarning to old_function()
v1.4.0: Remove old_function() from docs (code remains)
v2.0.0: Completely remove old_function()
```

## CalVer: Date-Based Versioning

Some projects use CalVer (Calendar Versioning) instead of SemVer.

```text
Format examples:
YYYY.MM.DD  → 2024.03.15
YYYY.MM     → 2024.3
YY.MM       → 24.3

Projects using CalVer:
- pip: 24.0, 24.1
- Ubuntu: 24.04
- Black: 24.3.0
```

CalVer suits projects with regular release cycles where backward compatibility isn't guaranteed between releases. For libraries, SemVer gives users a clearer signal.

## bump2version / bump-my-version Automation

A tool that modifies multiple files simultaneously when bumping versions and automatically creates tags.

### Configuration

```toml
# pyproject.toml
[tool.bumpversion]
current_version = "1.2.3"
commit = true
tag = true
tag_name = "v{new_version}"

[[tool.bumpversion.files]]
filename = "src/acme_utils/__init__.py"
search = '__version__ = "{current_version}"'
replace = '__version__ = "{new_version}"'

[[tool.bumpversion.files]]
filename = "pyproject.toml"
search = 'version = "{current_version}"'
replace = 'version = "{new_version}"'
```

### Usage

```bash
pip install bump-my-version

# Bump patch: 1.2.3 → 1.2.4
bump-my-version bump patch

# Minor version: 1.2.3 → 1.3.0
bump-my-version bump minor

# Major version: 1.2.3 → 2.0.0
bump-my-version bump major

# Pre-release: 1.2.3 → 1.3.0a1
bump-my-version bump minor --new-version 1.3.0a1
```

```bash
# Execution result
$ bump-my-version bump patch
Bumping version from 1.2.3 to 1.2.4
  Updated src/acme_utils/__init__.py
  Updated pyproject.toml
  Created commit: Bump version: 1.2.3 → 1.2.4
  Created tag: v1.2.4
```

## GitHub Release Integration

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ["v*"]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # full history needed (for CHANGELOG generation)
      - name: Generate release notes
        run: |
          # Extract commits between previous and current tag
          PREV_TAG=$(git describe --tags --abbrev=0 HEAD^)
          git log --pretty=format:"- %s" ${PREV_TAG}..HEAD > release_notes.md
      - uses: softprops/action-gh-release@v2
        with:
          body_path: release_notes.md
          generate_release_notes: true
```

## Version Compatibility Declaration and Support Policy

### Python Version Support Policy

```text
NEP 29 (NumPy Enhancement Proposal 29) based recommendation:
- Support latest 3 Python minor versions
- Current (2024): 3.10, 3.11, 3.12

When dropping support, bump MAJOR or MINOR:
- "Drop Python 3.9 support" → MINOR (some projects)
- "Drop Python 3.9 support" → MAJOR (strict projects)
```

```toml
[project]
requires-python = ">=3.10"
classifiers = [
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
```

### Version Matrix Testing in CI

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
    os: [ubuntu-latest, macos-latest, windows-latest]
```

## Real-World Release Scenarios

### Scenario 1: Hotfix Release

```bash
# Bug found on main, immediate patch needed
git checkout main
git pull

# After fixing
git add .
git commit -m "fix: handle null response in Client.get()"
bump-my-version bump patch  # 1.2.3 → 1.2.4
git push --tags
# CI auto-deploys
```

### Scenario 2: Feature Release

```bash
# Feature branch merged to main
git checkout main
git merge feature/retry-decorator

# Update CHANGELOG
vim CHANGELOG.md  # Move [Unreleased] content to new version

bump-my-version bump minor  # 1.2.4 → 1.3.0
git push --tags
```

### Scenario 3: Pre-Release

```bash
# Test a big change before going stable
bump-my-version bump major --new-version 2.0.0a1
git push --tags
# Users: pip install acme-utils==2.0.0a1

# After incorporating feedback
bump-my-version bump major --new-version 2.0.0b1
git push --tags

# After stabilization, final release
bump-my-version bump major --new-version 2.0.0
git push --tags
```

### Scenario 4: Hotfix for Older Version

```bash
# Patch for v1.x users (main is already at v2.x)
git checkout -b release/1.x v1.5.0
# Bug fix
git cherry-pick <commit-hash>
bump-my-version bump patch  # 1.5.0 → 1.5.1
git push origin release/1.x --tags
```

## Dependency Version Ranges and Their Relationship to Releases

How you set dependency version ranges when releasing directly affects user experience.

### Too Narrow Range Problem

```toml
# Too narrow: high conflict probability in user environments
dependencies = ["httpx==0.27.2"]
```

When only `0.27.2` is allowed, version conflicts become frequent when users install alongside other packages.

### Too Wide Range Problem

```toml
# Too wide: runtime errors on incompatible versions
dependencies = ["httpx"]
```

Allowing all versions without an upper bound means future major updates can break your code.

### Recommended Range

```toml
# Appropriate range: flexible within current major
dependencies = [
    "httpx>=0.25,<1.0",
    "pydantic>=2.0,<3.0",
]
```

This approach automatically accepts patch and minor updates while blocking at major boundaries where breaking changes are expected.

### Testing Dependency Ranges at Release Time

```yaml
# Test both ends of the dependency range in CI
jobs:
  test-min-versions:
    steps:
      - run: pip install "httpx==0.25" "pydantic==2.0"  # minimum supported
      - run: pytest

  test-latest:
    steps:
      - run: pip install "httpx" "pydantic"  # latest versions
      - run: pytest
```

Tests must pass on both minimum and latest versions to be confident the dependency range is correct.

## Post-Release Monitoring

Deployment is not the end of a release. You must monitor user reactions.

```text
Checklist:
□ No new bug reports on GitHub Issues
□ PyPI download count increasing normally
□ No error rate changes in internal services after upgrade
□ Dependabot PRs not failing on this version
```

```bash
# Check issues within 24 hours of release
gh issue list --label bug --since "24 hours ago"
```

If problems are found, prepare an immediate patch release, or consider yanking in severe cases.

### Rollback Strategy

```bash
# User-side rollback
pip install acme-utils==1.2.3  # revert to previous stable version

# Package maintainer side: yank + hotfix
# 1. Yank the problematic version on PyPI
# 2. Fix and release new patch version
# 3. Notify users to upgrade
```

If issues are severe after a new release, yank immediately but prefer a hotfix release over complete deletion.

## Answering the Opening Questions

- **When should you bump MAJOR.MINOR.PATCH in SemVer?**
  - Bump MAJOR when existing user code breaks, MINOR for backward-compatible new features, PATCH for bug fixes. "Does user code break?" is the first question, with function deletion, parameter renaming, and return type changes as classic breaking changes.
- **Where in the code should the version be recorded?**
  - The most recommended approach uses Git tags as the single source and extracts automatically at build time with `setuptools-scm` or `hatch-vcs`. If manual management is needed, reading `__version__` from `__init__.py` via `[tool.setuptools.dynamic]` in `pyproject.toml` prevents inconsistency between two locations.
- **How should CHANGELOG be managed?**
  - Use Keep a Changelog format with `Added`, `Changed`, `Fixed`, `Deprecated`, `Removed` categories. Following Conventional Commits enables auto-generation with tools like `git-cliff`. Add comparison links to each release so the change scope is visible at a glance.

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
