---
title: Production Package Template
series: python-package-101
episode: 10
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
- Template
- cookiecutter
- copier
- GitHub Template
- Best Practices
last_reviewed: '2026-05-04'
seo_description: A package template automates the repetitive setup work when starting
  a project, and cookiecutter and copier are the tools that make it happen.
---

# Production Package Template

> Python Package 101 series (10/10)

---

<!-- a-grade-intro:begin -->

## Key Questions

- How do you automate the repetitive setup that comes with every new package?
- What is the difference between cookiecutter and copier?
- When should you use a GitHub Template Repository?
- How do you combine everything from this series into a single template?

> A package template automates the repetitive setup work when starting a project, and cookiecutter and copier are the tools that make it happen.

<!-- a-grade-intro:end -->

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
- [Documentation — README, MkDocs, API Reference](./09-documentation.md)
- **Production Package Template (current)**

<!-- toc:end -->

## References

- [copier documentation](https://copier.readthedocs.io/)
- [cookiecutter documentation](https://cookiecutter.readthedocs.io/)
- [Hypermodern Python - Claudio Jolowicz](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
- [GitHub - Creating a template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)

Tags: Python, Template, cookiecutter, copier, GitHub Template, Best Practices
