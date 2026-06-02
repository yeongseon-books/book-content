---
title: "Python Package 101 (10/10): Production Package Template"
series: python-package-101
episode: 10
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
- Template
- cookiecutter
- copier
- GitHub Template
- Best Practices
last_reviewed: '2026-05-15'
seo_description: A package template automates the repetitive setup work when starting
  a project, and cookiecutter and copier are the tools that make it happen.
---

# Python Package 101 (10/10): Production Package Template

Repeating the same package setup by hand is where team standards drift. A good template turns one-off setup decisions into defaults that every new project inherits on day one.

This is the final post in the Python Package 101 series. Here we combine structure, testing, typing, documentation, and CI into a reusable template that can produce a production-ready package skeleton in minutes.

![Python Package 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/10/10-01-mental-model.en.png)
*Python Package 101 chapter 10 flow overview*

## Questions to Keep in Mind

- How do you automate the repetitive setup that comes with every new package?
- What is the difference between cookiecutter and copier?
- When should you use a GitHub Template Repository?

## What you will learn

- How to create project templates with cookiecutter and copier
- How to use GitHub Template Repositories
- A production template structure that integrates everything from this series
- A complete package setup with CI/CD, docs, and tests

## Why it matters

Writing pyproject.toml, src layout, mypy config, CI/CD, README, and .gitignore from scratch for every new package is inefficient. With a well-built template, you can start a production-grade project in 30 seconds.

> Every time your team creates a new microservice, someone copies config files from an existing project. Unnecessary code gets carried over, and forgetting to change the package name in pyproject.toml breaks CI.

## Mental Model

> A template is a cookie cutter. You provide the dough (project name, description) and the same shaped cookie (project structure) comes out every time. A well-made cutter produces consistent quality projects.

```text
cookiecutter/copier + template
        +
  user input (name, description)
        ↓
  complete project structure
    src/mylib/
    tests/
    pyproject.toml
    .github/workflows/
    README.md
    ...
```

## Core Concepts

| Term | Description | Example |
|---|---|---|
| cookiecutter | Jinja2-based project template tool | `cookiecutter gh:user/template` |
| copier | Updatable project template tool | `copier copy gh:user/template .` |
| GitHub Template | GitHub feature to use a repo as a template | "Use this template" button |
| Jinja2 | Template variable substitution syntax | `{{ project_name }}` |
| .github/workflows | GitHub Actions CI/CD configuration | `ci.yml`, `publish.yml` |

## Before / After

**Before (manual setup)**

```bash
mkdir myproject && cd myproject
# write pyproject.toml (10 min)
# set up src layout (5 min)
# write .gitignore, README (5 min)
# configure CI/CD (15 min)
# configure mypy, ruff (5 min)
# → 40 minutes before writing the first line of code
```

**After (template)**

```bash
copier copy gh:yourname/python-template myproject
# Project name? myproject
# Description? A useful tool
# → 30 seconds, all config done, start coding immediately
```

## Step-by-step practice

### Step 1. Design the production template structure

```text
python-template/
├── {{ project_slug }}/
│   ├── src/
│   │   └── {{ project_slug }}/
│   │       ├── __init__.py
│   │       ├── core.py
│   │       ├── cli.py
│   │       └── py.typed
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_core.py
│   ├── docs/
│   │   ├── index.md
│   │   └── api.md
│   ├── .github/
│   │   └── workflows/
│   │       ├── ci.yml
│   │       └── publish.yml
│   ├── pyproject.toml
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── LICENSE
│   ├── .gitignore
│   └── mkdocs.yml
└── copier.yml
```

### Step 2. Write the copier configuration

```yaml
# copier.yml
_subdirectory: "{{ project_slug }}"

project_name:
  type: str
  help: "Project name (e.g., My Library)"

project_slug:
  type: str
  default: "{{ project_name | lower | replace(' ', '-') }}"
  help: "Package directory name"

module_name:
  type: str
  default: "{{ project_slug | replace('-', '_') }}"
  help: "Python module name"

description:
  type: str
  default: "A Python package"

author_name:
  type: str
  help: "Author full name"

author_email:
  type: str
  help: "Author email"

python_version:
  type: str
  default: "3.11"
  choices: ["3.9", "3.10", "3.11", "3.12"]
```

### Step 3. Template pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{{ project_slug }}"
version = "0.1.0"
description = "{{ description }}"
requires-python = ">={{ python_version }}"
license = {text = "MIT"}
authors = [
    {name = "{{ author_name }}", email = "{{ author_email }}"},
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "mypy>=1.0",
    "ruff>=0.1",
]

[project.scripts]
{{ project_slug }} = "{{ module_name }}.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.mypy]
python_version = "{{ python_version }}"
strict = true

[tool.ruff]
target-version = "py{{ python_version | replace('.', '') }}"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

### Step 4. CI/CD workflow template

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["{{ python_version }}"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ "{{" }} matrix.python-version {{ "}}" }}
      - run: pip install -e ".[dev]"
      - run: ruff check src/
      - run: mypy src/
      - run: pytest tests/
```

### Step 5. Generate a project from the template

```bash
pip install copier
copier copy ./python-template my-new-project

# ? project_name: My New Project
# ? project_slug: my-new-project
# ? module_name: my_new_project
# ? description: A useful Python tool
# ? author_name: Your Name
# ? author_email: you@example.com
# ? python_version: 3.11

cd my-new-project
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/    # 1 passed
mypy src/        # Success
```

## What to notice in this code

- Copier's `{{ }}` syntax is the Jinja2 template engine, substituting user inputs into file contents and names
- Copier can push template updates to existing projects via `copier update`, giving it a maintenance advantage over cookiecutter
- The CI workflow runs `ruff check`, `mypy`, and `pytest` in sequence to ensure code quality
- `[project.scripts]` is pre-configured so you can implement a CLI immediately

## Common mistakes

### Mistake 1. Creating a template and never updating it

The Python ecosystem evolves fast. Regularly update dependency versions and settings in your template.

### Mistake 2. Adding too many options

If the template asks more than 10 questions, users give up. Keep only essential options and set sensible defaults for the rest.

### Mistake 3. Generated projects that do not pass tests immediately

A project generated from the template must pass `pip install -e ".[dev]" && pytest` right away. A broken template loses trust.

### Mistake 4. Using GitHub Template without variable substitution

GitHub Template copies the repository but does not replace variables in file contents. The name `my-template` remains as-is.

### Mistake 5. Forgetting the license

Without a license, usage rights are legally ambiguous. Include MIT or Apache 2.0 by default.

## Practical applications

- **Internal templates**: Standardize team coding rules, CI/CD config, and common dependencies in a template
- **Open source kickstart**: Reference public templates like hypermodern-python and scikit-hep
- **Microservices**: Create service templates that include FastAPI + Docker + Kubernetes config
- **copier update**: When you improve the template, apply changes to existing projects with `copier update`
- **CI for templates**: Test the template itself in CI by generating, building, and testing a project

## How practitioners think about this

A good template is a "snapshot of best practices." When your team encodes agreed-upon coding rules, CI/CD patterns, and documentation structure into a template, no one has to ask "how should I set this up?" for new projects.

Choosing between cookiecutter and copier is straightforward: if you use the template once and move on, cookiecutter is fine; if you want template updates to propagate to existing projects, use copier. For new projects, copier is the recommended choice.

## Checklist

- [ ] You can create a project template with copier or cookiecutter
- [ ] Projects generated from the template pass tests immediately
- [ ] CI/CD workflows are included in the template
- [ ] You know when to use a GitHub Template Repository
- [ ] You can propagate template changes to existing projects with copier update

## Exercises

1. Build a copier template that includes everything from this series (src layout, pyproject.toml, mypy, CLI entry point, README, CI).
2. Generate a new project from the template and verify `pip install -e ".[dev]" && pytest && mypy src/` passes.
3. Create a template repository on GitHub and generate a new project using the "Use this template" button.

## Summary and next

- Package templates automate repetitive project setup.
- Copier supports variable substitution and updates, making it more maintainable than cookiecutter.
- Projects generated from a template must pass tests immediately.
- Including CI/CD, docs, type checking, and linting in the template speeds up project starts.
- A good template codifies your team's best practices.

This concludes the Python Package 101 series. From the concept of a package through structure, building, publishing, versioning, CLI, type hints, documentation, and templates — we have covered the entire Python packaging workflow. Now go package your code and share it with the world.

## cookiecutter vs copier: Detailed Comparison

### cookiecutter workflow

```text
cookiecutter gh:acme/template
    │
    ▼
Read cookiecutter.json (variable definitions)
    │
    ▼
Prompt user for variable values
    │
    ▼
Render filenames + contents with Jinja2
    │
    ▼
Run hooks/post_gen_project.py
    │
    ▼
Output completed project directory
```

### copier workflow

```text
copier copy gh:acme/template ./my-project
    │
    ▼
Read copier.yml (variables + types + validation)
    │
    ▼
Prompt user for values (with type validation)
    │
    ▼
Render with Jinja2 + conditional file generation
    │
    ▼
Generate .copier-answers.yml (records answers)
    │
    ▼
Output completed project
```

```yaml
# .copier-answers.yml (auto-generated, should be committed)
_commit: v1.2.0
_src_path: gh:acme/python-package-template
project_name: acme-auth
package_name: acme_auth
python_version: "3.11"
use_cli: true
build_backend: hatchling
```

### copier update: Template synchronization

```bash
# 6 months later, team template has new lint rules
cd acme-auth
copier update

# What copier does:
# 1. Downloads latest version of original template
# 2. Renders new version with .copier-answers.yml values
# 3. Performs 3-way merge with current project
# 4. Asks user to resolve conflicts if any
```

## GitHub Template Repositories

GitHub Templates are the simplest project template approach.

### Setup

```text
1. Go to GitHub repository Settings
2. Enable "Template repository" checkbox
3. Users: "Use this template" → "Create a new repository"
```

### Limitations

| Aspect | cookiecutter/copier | GitHub Template |
|---|---|---|
| Variable substitution | Automatic | Manual |
| Conditional files | Supported | Not possible |
| Template updates | copier update | Manual diff |
| Ease of use | CLI required | One web button |
| Best for | Team standardization | Simple starting point |

## Files to Include in a Production Template

### Minimal (all projects)

```text
├── src/{{package_name}}/
│   ├── __init__.py
│   └── py.typed
├── tests/
│   ├── conftest.py
│   └── test_placeholder.py
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
└── Makefile
```

### Standard (team projects)

```text
Above minimal +
├── .github/
│   ├── workflows/ci.yml
│   ├── workflows/publish.yml
│   └── dependabot.yml
├── .pre-commit-config.yaml
├── .editorconfig
├── CHANGELOG.md
└── docs/
    └── index.md
```

### Full (open source)

```text
Above standard +
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
├── docs/
│   ├── getting-started/
│   ├── guide/
│   └── api/
└── mkdocs.yml
```

## Template Makefile in Detail

A Makefile standardizes all everyday commands for the project. When a new team member joins, `make help` shows all available tasks at a glance.

```makefile
.DEFAULT_GOAL := help
.PHONY: help install dev test lint format typecheck build check clean publish docs

PACKAGE := acme_utils
SRC := src/$(PACKAGE)

help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install in development mode
	python -m pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest --cov=$(PACKAGE) --cov-report=term-missing -q

lint:  ## Run linter
	ruff check $(SRC) tests

format:  ## Format code
	ruff format $(SRC) tests
	ruff check --fix $(SRC) tests

typecheck:  ## Run type checker
	mypy $(SRC)

build:  ## Build packages
	rm -rf dist/
	python -m build

check: build  ## Verify built packages
	twine check dist/*

clean:  ## Clean build artifacts
	rm -rf dist/ build/ src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true

docs:  ## Serve documentation locally
	mkdocs serve

docs-build:  ## Build documentation
	mkdocs build --strict

ci: lint format typecheck test build check  ## Run full CI locally
```

## Template Testing Automation

Templates themselves should be tested in CI. Verify that projects generated from the template work correctly.

```yaml
# .github/workflows/test-template.yml in the template repo
name: Test Template
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        build-backend: ["setuptools", "hatchling"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install copier
      - name: Generate project
        run: |
          copier copy --defaults \
            --data "project_name=test-project" \
            --data "build_backend=${{ matrix.build-backend }}" \
            . /tmp/test-project
      - name: Verify project
        working-directory: /tmp/test-project
        run: |
          pip install -e ".[dev]"
          make ci
```

## Designing Team Onboarding Experience

A good template reduces onboarding time for new team members.

```text
Day 1 (new team member):
1. copier copy gh:acme/python-package-template ./my-service
2. cd my-service
3. make install
4. make test    (green pass!)
5. make ci      (full pipeline local verification!)

→ Environment ready to submit first PR within 30 minutes.
```

This is the value of templates. They reduce friction when starting projects, codify team standards, and eliminate the question "How do I build this project?".

## Template Versioning Strategy

Managing templates with SemVer lets you track what changes are reflected when running `copier update`.

```text
v1.0.0: Initial template (setuptools)
v1.1.0: Add hatchling option
v1.2.0: Python 3.12 support, ruff config update
v2.0.0: Enforce src layout (breaking: remove flat layout)
```

```bash
# Generate from specific version
copier copy --vcs-ref v1.2.0 gh:acme/template ./project

# Check version range on update
copier update  # Compares .copier-answers.yml _commit with latest
```

### Template changelog management

```markdown
# Template CHANGELOG

## [1.2.0] - 2024-07-01

### Added
- Python 3.12 support in CI matrix
- Ruff 0.5+ configuration
- `make docs` command

### Changed
- Default ruff rules expanded (added SIM, TCH)
- pytest minimum version: 8.0

### Migration
After `copier update`:
- Review new ruff rules in pyproject.toml
- Update CI Python version matrix if needed
```

## Managing Internal Package Ecosystems

In large organizations, multiple templates are managed hierarchically.

```text
Organization level:
├── base-template/          # Common (LICENSE, .editorconfig, CI basics)
├── library-template/       # For libraries (src layout, PyPI publishing)
├── service-template/       # For microservices (Docker, K8s)
├── cli-template/           # For CLI tools (Click, entry points)
└── ml-template/            # For ML projects (notebooks, DVC)
```

### Standards verification tool

```bash
# Script to verify generated projects follow team standards
#!/bin/bash
# scripts/check-standards.sh

echo "Checking project standards..."

# pyproject.toml exists
[ -f pyproject.toml ] || { echo "FAIL: pyproject.toml missing"; exit 1; }

# Uses src layout
[ -d src ] || { echo "FAIL: src/ directory missing"; exit 1; }

# py.typed exists
find src -name "py.typed" | grep -q . || { echo "FAIL: py.typed missing"; exit 1; }

# CI workflow exists
[ -f .github/workflows/ci.yml ] || { echo "FAIL: CI workflow missing"; exit 1; }

# pre-commit config
[ -f .pre-commit-config.yaml ] || { echo "FAIL: pre-commit config missing"; exit 1; }

echo "All standards met!"
```

Adding this script as the first CI step catches any deviation from standards immediately in PRs.

In practice, templates are not a create-once-and-forget tool. You should update dependency versions, lint rules, and CI configuration quarterly, then propagate changes to all projects via `copier update`. Once this routine is established, even 20+ microservices can maintain consistent quality without configuration drift.

Ultimately, a good template is the team's consensus on "What is the best way to start a new project?" expressed as code.

## Answering the Opening Questions

- **How do you automate the repetitive setup for each new package?**
  - Create project templates with cookiecutter or copier, parameterizing `pyproject.toml`, CI workflows, Makefile, pre-commit config, and test boilerplate. A single `copier copy` instantly generates a project matching team standards, ready for verification with `make ci`.
- **What's the difference between `cookiecutter` and `copier`?**
  - cookiecutter disconnects from the template after generation, but copier can 3-way merge template improvements into existing projects via `copier update`. If team templates are frequently improved, copier significantly reduces maintenance costs.
- **When is a GitHub Template Repository a good fit?**
  - GitHub Template clones a repository with the "Use this template" button. Since there's no variable substitution, you must manually replace project names etc. It's suitable for quick starts with simple project structures or environments where installing external tools is difficult.

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
- [Python Package 101 (9/10): Documentation — README, MkDocs, API Reference](./09-documentation.md)
- **Python Package 101 (10/10): Production Package Template (current)**

<!-- toc:end -->

## References

- [copier documentation](https://copier.readthedocs.io/)
- [cookiecutter documentation](https://cookiecutter.readthedocs.io/)
- [Hypermodern Python - Claudio Jolowicz](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
- [GitHub - Creating a template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)

Tags: Python, Packaging, PyPI, pyproject.toml
