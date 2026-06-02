---
title: "Python Package 101 (7/10): CLI Packages"
series: python-package-101
episode: 7
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
- CLI
- Entry Point
- click
- argparse
- Command Line
last_reviewed: '2026-05-15'
seo_description: An entry point registers a terminal command that runs after pip install,
  and click is a library for building CLI interfaces declaratively.
---

# Python Package 101 (7/10): CLI Packages

Packaging becomes much more tangible once `pip install` gives a user an actual command to run. A polished CLI turns your package from shared code into a repeatable workflow.

This is the 7th post in the Python Package 101 series. Here we connect `[project.scripts]` entry points to real Python functions, compare `argparse` with `click`, and design CLIs that hold up in everyday tooling.

![Python Package 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/07/07-01-mental-model.en.png)
*Python Package 101 chapter 7 flow overview*

## Questions to Keep in Mind

- How do you create a command that runs directly in the terminal after `pip install`?
- How does a `[project.scripts]` entry point work?
- What is the difference between `argparse` and `click`?

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

## How Entry Points Work Under the Hood

When you register an entry point in `[project.scripts]`, `pip install` generates an executable wrapper script.

### Configuration and generated files

```toml
# pyproject.toml
[project.scripts]
acme = "acme_utils.cli:main"
```

```bash
pip install -e .
which acme
# /home/user/.local/bin/acme (or .venv/bin/acme)
```

```python
# Generated wrapper script (auto-generated, no manual editing needed)
#!/path/to/.venv/bin/python
from acme_utils.cli import main
import sys
sys.exit(main())
```

### Entry point types

| Type | Config key | Purpose |
|---|---|---|
| console_scripts | `[project.scripts]` | Terminal commands |
| gui_scripts | `[project.gui-scripts]` | GUI apps (no console window on Windows) |
| plugins | `[project.entry-points]` | Plugin extension points |

## Building CLIs with Click

Click is the most widely used Python CLI framework. It declares commands, options, and arguments through decorators.

### Basic structure

```python
# src/acme_utils/cli.py
import click

@click.group()
@click.version_option()
def main():
    """Acme utility CLI."""
    pass

@main.command()
@click.argument("name")
@click.option("--greeting", "-g", default="Hello", help="Greeting message")
def hello(name: str, greeting: str):
    """Greet someone."""
    click.echo(f"{greeting}, {name}!")

@main.command()
@click.option("--format", "-f", type=click.Choice(["json", "yaml", "toml"]), default="json")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def config(format: str, output: str | None):
    """Generate configuration template."""
    import json
    template = {"name": "acme-app", "version": "1.0.0", "debug": False}

    result = json.dumps(template, indent=2)

    if output:
        with open(output, "w") as f:
            f.write(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)
```

```bash
# Usage examples
acme --version
# acme-utils, version 0.1.0

acme hello World
# Hello, World!

acme hello --greeting "Hi" Alice
# Hi, Alice!

acme config --format json --output config.json
# Written to config.json
```

### Click's automatic help

```bash
acme --help
# Usage: acme [OPTIONS] COMMAND [ARGS]...
#
#   Acme utility CLI.
#
# Options:
#   --version  Show the version and exit.
#   --help     Show this message and exit.
#
# Commands:
#   config  Generate configuration template.
#   hello   Greet someone.
```

## Typer: A Modern Alternative to Click

Typer is built on top of Click but leverages type hints for more concise code.

```python
# src/acme_utils/cli.py
import typer
from typing import Annotated

app = typer.Typer(help="Acme utility CLI.")

@app.command()
def hello(
    name: str,
    greeting: Annotated[str, typer.Option("--greeting", "-g")] = "Hello",
):
    """Greet someone."""
    typer.echo(f"{greeting}, {name}!")

@app.command()
def init(
    project_name: str,
    force: Annotated[bool, typer.Option("--force", "-f")] = False,
):
    """Initialize a new project."""
    if force:
        typer.echo(f"Force creating {project_name}...")
    else:
        typer.echo(f"Creating {project_name}...")

def main():
    app()
```

### Click vs Typer comparison

| Aspect | Click | Typer |
|---|---|---|
| Type declaration | Decorator parameters | Python type hints |
| Learning curve | Medium | Low |
| Ecosystem | Very broad | Leverages Click ecosystem |
| Auto-completion | Separate setup | Built-in support |
| Minimum Python | 3.7+ | 3.7+ |

## argparse: The Standard Library Option

If you want no external dependencies, `argparse` is available out of the box.

```python
# src/acme_utils/cli.py
import argparse
import sys

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acme",
        description="Acme utility CLI",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command")

    # hello subcommand
    hello_parser = subparsers.add_parser("hello", help="Greet someone")
    hello_parser.add_argument("name")
    hello_parser.add_argument("--greeting", "-g", default="Hello")

    # init subcommand
    init_parser = subparsers.add_parser("init", help="Initialize project")
    init_parser.add_argument("project_name")
    init_parser.add_argument("--force", "-f", action="store_true")

    return parser

def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "hello":
        print(f"{args.greeting}, {args.name}!")
    elif args.command == "init":
        print(f"Creating {args.project_name}...")
    else:
        parser.print_help()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## CLI Testing

### Click testing

```python
# tests/test_cli.py
from click.testing import CliRunner
from acme_utils.cli import main

def test_hello():
    runner = CliRunner()
    result = runner.invoke(main, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output

def test_hello_with_greeting():
    runner = CliRunner()
    result = runner.invoke(main, ["hello", "--greeting", "Hi", "Alice"])
    assert result.exit_code == 0
    assert "Hi, Alice!" in result.output

def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output
```

### Typer testing

```python
from typer.testing import CliRunner
from acme_utils.cli import app

runner = CliRunner()

def test_hello():
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output
```

## Exit Code Management

CLI tools must return appropriate exit codes for correct behavior in scripts and CI.

```python
import sys
import click

@click.command()
@click.argument("path", type=click.Path(exists=True))
def lint(path: str):
    """Lint Python files."""
    errors = run_linter(path)

    if errors:
        for err in errors:
            click.echo(f"ERROR: {err}", err=True)
        sys.exit(1)  # Failure: non-zero exit code

    click.echo("All checks passed!")
    sys.exit(0)  # Success
```

```text
Exit code conventions:
0   - Success
1   - General error
2   - CLI usage error (invalid arguments)
130 - Interrupted by Ctrl+C (128 + SIGINT)
```

## Rich Terminal Output

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track
import time

console = Console()

def show_packages():
    table = Table(title="Installed Packages")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Location")

    table.add_row("httpx", "0.27.2", "site-packages/httpx")
    table.add_row("pydantic", "2.8.2", "site-packages/pydantic")

    console.print(table)

def process_files(files: list[str]):
    for file in track(files, description="Processing..."):
        time.sleep(0.1)  # Actual work
    console.print("[green]Done![/green]")
```

## Shell Completion Setup

### Click completion

```bash
# Bash
_ACME_COMPLETE=bash_source acme > ~/.acme-complete.bash
echo '. ~/.acme-complete.bash' >> ~/.bashrc

# Zsh
_ACME_COMPLETE=zsh_source acme > ~/.acme-complete.zsh
echo '. ~/.acme-complete.zsh' >> ~/.zshrc

# Fish
_ACME_COMPLETE=fish_source acme > ~/.config/fish/completions/acme.fish
```

### Typer completion

```bash
# Typer has built-in support
acme --install-completion
# Automatically installs the completion script for your shell
```

## CLI Package Distribution Structure

The complete project structure and pyproject.toml for a CLI package.

```text
acme-cli/
├── src/
│   └── acme_cli/
│       ├── __init__.py
│       ├── __main__.py      # python -m acme_cli support
│       ├── cli.py           # Click/Typer app definition
│       ├── commands/        # Subcommand modules
│       │   ├── __init__.py
│       │   ├── init.py
│       │   ├── build.py
│       │   └── deploy.py
│       └── utils.py         # Shared helpers
├── tests/
│   ├── test_cli.py
│   └── test_commands/
├── pyproject.toml
└── README.md
```

### `__main__.py`: `python -m` support

```python
# src/acme_cli/__main__.py
from .cli import main

if __name__ == "__main__":
    main()
```

```bash
# Both execution methods work
acme --help                # entry point
python -m acme_cli --help  # __main__.py
```

### Full pyproject.toml configuration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "acme-cli"
version = "0.1.0"
description = "Command-line tools for Acme platform"
requires-python = ">=3.10"
dependencies = [
    "click>=8.1",
    "rich>=13.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]

[project.scripts]
acme = "acme_cli.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/acme_cli"]
```

## Configuration File Management

CLI tools often persist user settings in configuration files.

```python
# src/acme_cli/config.py
from pathlib import Path
import tomllib  # Python 3.11+

def get_config_dir() -> Path:
    """Config directory following XDG Base Directory specification."""
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config_dir = xdg / "acme"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def load_config() -> dict:
    config_path = get_config_dir() / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}
```

```toml
# ~/.config/acme/config.toml
[defaults]
output_format = "json"
verbose = false

[auth]
api_url = "https://api.acme.dev"
```

## Environment Variables and CLI Option Precedence

Configuration values for CLI tools can come from multiple sources. The standard precedence order is:

```text
Precedence (high to low):
1. CLI options (--format json)
2. Environment variables (ACME_FORMAT=json)
3. Configuration files (~/.config/acme/config.toml)
4. Defaults (hardcoded in source)
```

```python
@click.command()
@click.option(
    "--api-url",
    envvar="ACME_API_URL",       # Also reads from environment variable
    default="https://api.acme.dev",
    help="API endpoint URL",
)
def deploy(api_url: str):
    """Deploy to Acme platform."""
    click.echo(f"Deploying to {api_url}...")
```

```bash
# All three methods produce the same result
acme deploy --api-url https://staging.acme.dev
ACME_API_URL=https://staging.acme.dev acme deploy
# Or set in config.toml
```

A well-designed precedence system lets users avoid repetitive option typing while retaining the ability to override values explicitly when needed. Most mature CLI tools (`aws`, `gh`, `docker`) follow this pattern.

## Answering the Opening Questions

- **How do you create a command that's immediately runnable after `pip install`?**
  - Register an entry point in `[project.scripts]` of `pyproject.toml` using the format `command-name = "package.module:function"`. During `pip install`, a wrapper script calling that function is automatically generated in the `bin/` directory, making it executable directly from the terminal.
- **How does the `[project.scripts]` entry point work?**
  - During installation, pip records the mapping in `site-packages`' `.dist-info/entry_points.txt` and creates a Python wrapper script in `bin/`. This script imports the specified module, calls the specified function, and passes the function's return value to `sys.exit()`.
- **Which CLI framework should you choose?**
  - Choose `argparse` to avoid external dependencies, `click` for a rich ecosystem and plugins, or `typer` for concise type-hint-based code. `typer` uses `click` internally, so all click features remain available.

<!-- toc:begin -->
## In this series

- [Python Package 101 (1/10): What Is a Python Package?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): Project Structure — src layout and pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): Dependency Management — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): Building Packages — wheel and sdist](./04-building-packages.md)
- [Python Package 101 (5/10): Publishing to PyPI — from TestPyPI to production](./05-publishing-to-pypi.md)
- [Python Package 101 (6/10): Versioning and Releases](./06-versioning-and-releases.md)
- **Python Package 101 (7/10): CLI Packages (current)**
- Python Package 101 (8/10): Type Hints and Static Analysis (upcoming)
- Python Package 101 (9/10): Documentation — README, MkDocs, API Reference (upcoming)
- Python Package 101 (10/10): Production Package Template (upcoming)

<!-- toc:end -->

## References

- [Python Packaging - Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/)
- [click documentation](https://click.palletsprojects.com/)
- [argparse documentation](https://docs.python.org/3/library/argparse.html)
- [Real Python - Python CLI with Click](https://realpython.com/python-click/)

Tags: Python, Packaging, PyPI, pyproject.toml
