---
title: CLI Packages
series: python-package-101
episode: 7
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
- CLI
- Entry Point
- click
- argparse
- Command Line
last_reviewed: '2026-05-04'
seo_description: An entry point registers a terminal command that runs after pip install,
  and click is a library for building CLI interfaces declaratively.
---

# CLI Packages

This is post 7 in the Python Package 101 series.

> Python Package 101 series (7/10)

---

<!-- a-grade-intro:begin -->

## Key Questions

- How do you create a command that runs directly in the terminal after `pip install`?
- How does a `[project.scripts]` entry point work?
- What is the difference between `argparse` and `click`?
- How do you build a subcommand structure?

> An entry point registers a terminal command that runs after `pip install`, and click is a library for building CLI interfaces declaratively.

<!-- a-grade-intro:end -->

## What you will learn

- How to register a CLI entry point with `[project.scripts]`
- How to build a basic CLI with `argparse`
- How to build a declarative CLI with `click`
- How to implement subcommand structures

## Why it matters

Running `mytool` directly is more convenient than `python my_script.py`. When you set an entry point in your package, `pip install` makes the command available in the terminal immediately.

> Your team runs a data conversion script as `python /opt/scripts/convert.py --input data.csv`. Everyone has to remember the path and invoke Python directly.

After `pip install mytools`, running `convert --input data.csv` is far simpler.

## Mental Model

> An entry point is like installing an app from the app store and getting an icon on your home screen. `pip install` is the installation and the entry point is the icon. Tapping the icon (typing the command) launches the app (Python function).

```text
pyproject.toml                     Terminal
─────────────                     ──────
[project.scripts]                 $ greet Alice
greet = "mylib.cli:main"    →    Hello, Alice!
         ↓
   runs the main() function in mylib/cli.py
```

## Core Concepts

| Term | Description | Example |
|---|---|---|
| entry point | Executable command registered on package install | `greet = "mylib.cli:main"` |
| [project.scripts] | pyproject.toml section for CLI entry points | see above |
| argparse | Python built-in CLI argument parser | `parser.add_argument('--name')` |
| click | Decorator-based CLI framework | `@click.command()` |
| subcommand | A command nested under a parent command | `git commit`, `git push` |

## Before / After

**Before (run script directly)**

```bash
python /path/to/mylib/cli.py --name Alice
# must remember the path, must invoke python
```

**After (entry point)**

```bash
pip install mylib
greet --name Alice
# runs anywhere, no python invocation needed
```

## Step-by-step practice

### Step 1. Build a basic CLI with argparse

```python
# src/mylib/cli.py
import argparse

def main():
    parser = argparse.ArgumentParser(description="Greet someone")
    parser.add_argument("name", help="Name to greet")
    parser.add_argument("--count", type=int, default=1, help="Number of greetings")
    args = parser.parse_args()

    for i in range(args.count):
        print(f"[{i+1}] Hello, {args.name}!")

if __name__ == "__main__":
    main()
```

### Step 2. Register the entry point in pyproject.toml

```toml
[project.scripts]
greet = "mylib.cli:main"
```

```bash
pip install -e .
greet Alice
# [1] Hello, Alice!

greet Alice --count 3
# [1] Hello, Alice!
# [2] Hello, Alice!
# [3] Hello, Alice!
```

### Step 3. Refactor with click

```python
# src/mylib/cli.py
import click

@click.command()
@click.argument("name")
@click.option("--count", default=1, help="Number of greetings")
def main(name: str, count: int):
    """Greet someone."""
    for i in range(count):
        click.echo(f"[{i+1}] Hello, {name}!")

if __name__ == "__main__":
    main()
```

```toml
# Add click dependency to pyproject.toml
[project]
dependencies = ["click>=8.0"]
```

```bash
pip install -e .
greet Alice --count 3
greet --help
# Usage: greet [OPTIONS] NAME
#   Greet someone.
# Options:
#   --count INTEGER  Number of greetings
#   --help           Show this message and exit.
```

### Step 4. Subcommand structure

```python
# src/mylib/cli.py
import click

@click.group()
def main():
    """mylib CLI tool."""
    pass

@main.command()
@click.argument("name")
def greet(name: str):
    """Greet someone."""
    click.echo(f"Hello, {name}!")

@main.command()
@click.argument("path", type=click.Path(exists=True))
def check(path: str):
    """Check a file."""
    click.echo(f"Checking: {path}")
```

```bash
pip install -e .
greet                    # prints usage
greet greet Alice        # Hello, Alice!
greet check README.md    # Checking: README.md
```

### Step 5. Error handling and exit codes

```python
import sys
import click

@click.command()
@click.argument("path", type=click.Path())
def main(path: str):
    """Process a file."""
    try:
        with open(path) as f:
            lines = f.readlines()
        click.echo(f"Processed {len(lines)} lines")
    except FileNotFoundError:
        click.echo(f"Error: {path} not found", err=True)
        sys.exit(1)
```

## What to notice in this code

- The entry point `"mylib.cli:main"` points to the `main` function in the `mylib/cli.py` module
- The `@click.command()` decorator turns a function into a CLI command
- `click.echo` is safer than `print` for Unicode and piped output
- `err=True` sends error messages to stderr

## Common mistakes

### Mistake 1. Not reinstalling after changing the entry point

When you modify `[project.scripts]`, you must run `pip install -e .` again. Even editable installs require reinstallation for entry point changes.

### Mistake 2. Adding parameters to main()

```python
# Wrong: entry point cannot pass arguments on its own
def main(name: str): ...

# Correct: let argparse/click handle arguments
def main():
    parser = argparse.ArgumentParser()
    ...
```

### Mistake 3. Putting if __name__ inside the entry point function

`if __name__ == "__main__": main()` belongs at the end of the file. It supports both entry point and `python -m` execution.

### Mistake 4. Not returning proper exit codes

CLI tools should return 0 on success and 1 or higher on failure. Pipelines use exit codes to decide whether to continue.

### Mistake 5. Not checking --help output

`--help` is the first documentation users see. Missing or inaccurate descriptions cause confusion.

## Practical applications

- **Dev tools**: `ruff`, `black`, and `pytest` are all CLI packages registered via entry points
- **Data pipelines**: Build CLI tools for CSV conversion, API calls, etc. and run them from cron
- **DevOps tools**: Distribute deployment, monitoring, and config management CLIs as internal packages
- **Prototyping**: Build a quick CLI with `click`, then add a web UI later
- **Testing**: Use `click.testing.CliRunner` to verify CLI output programmatically

## How practitioners think about this

The most important thing when building a CLI is a **consistent interface**. Standardizing common options like `--verbose`, `--output`, and `--format` lets users work intuitively.

`argparse` has no external dependencies and is lightweight, but `click` includes subcommands, prompts, colored output, and a test runner out of the box, making it more productive in practice. For a library, `argparse` is fine; for a standalone CLI tool, `click` is the better fit.

## Checklist

- [ ] You can register an entry point with `[project.scripts]`
- [ ] You can build a basic CLI with `argparse`
- [ ] You can build a decorator-based CLI with `click`
- [ ] You can implement subcommands with `click.group`
- [ ] You can handle exit codes and stderr output correctly

## Exercises

1. Build a CLI with `argparse` that takes two numbers and performs arithmetic (`calc add 3 5`, `calc mul 2 4`).
2. Refactor the same CLI using `click` and compare the `--help` output.
3. Write a pytest that uses `click.testing.CliRunner` to test CLI output.

## Summary and next

- `[project.scripts]` registers CLI commands available immediately after `pip install`.
- An entry point uses `"module:function"` format to specify the function to execute.
- `argparse` is built-in; `click` is a decorator-based framework that is more productive.
- `click.group()` creates subcommand structures.
- CLIs should return 0 on success and 1 or higher on failure.

The next post covers **type hints and static analysis** — mypy, py.typed, and type-safe packages.

<!-- toc:begin -->
## Series Table of Contents

- [What Is a Python Package?](./01-what-is-a-python-package.md)
- [Project Structure — src layout and pyproject.toml](./02-project-structure.md)
- [Dependency Management — venv, pip, uv, requirements](./03-dependency-management.md)
- [Building Packages — wheel and sdist](./04-building-packages.md)
- [Publishing to PyPI — from TestPyPI to production](./05-publishing-to-pypi.md)
- [Versioning and Releases](./06-versioning-and-releases.md)
- **CLI Packages (current)**
- Type Hints and Static Analysis (upcoming)
- Documentation — README, MkDocs, API Reference (upcoming)
- Production Package Template (upcoming)

<!-- toc:end -->

## References

- [Python Packaging - Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/)
- [click documentation](https://click.palletsprojects.com/)
- [argparse documentation](https://docs.python.org/3/library/argparse.html)
- [Real Python - Python CLI with Click](https://realpython.com/python-click/)

Tags: Python, CLI, Entry Point, click, argparse, Command Line
