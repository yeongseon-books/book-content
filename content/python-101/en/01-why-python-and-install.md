---
title: "Why Python, and how to install and use venv"
series: python-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
  - Python
  - install
  - venv
  - pip
  - version
  - beginner
last_reviewed: '2026-05-03'
---

# Why Python, and how to install and use venv

## What you will learn

- Why Python is the most common first language
- How to install Python on macOS, Linux, and Windows
- Why you must not touch the system Python directly, and what venv solves
- The standard flow to create and activate a venv
- How to install packages with pip and pin versions

## Why this matters

The most common mistake when first installing Python is to install packages directly into the Python the system uses. It works at first, but the moment you start a second project the package versions collide and eventually OS tooling breaks. If you make venv a habit from day one, you will never face this problem. The first skill a beginner needs is not syntax — it is environment isolation.

## Mental Model

> The Python environment story is one line: **"system Python belongs to the OS, my projects belong to my venvs."** The system Python is the interpreter the operating system uses to run its own tools, and every project you work on lives inside a venv in its own directory.

If git is the analogy, a venv is like a project directory. You would not throw all your code into one folder; you give each project its own directory. The same applies to Python environments — one per project.

## Core concepts

### Why Python is a great first language

- **Readable syntax**: indentation-based blocks, near-natural-language keywords (`if`, `for`, `in`, `not`)
- **Huge ecosystem**: data, web, AI, automation — libraries exist for every domain
- **Run immediately**: no compile step, just `python script.py`
- **REPL**: type `python` to launch an interactive shell and try things line by line
- **Wide job market**: data, backend, ML, DevOps — Python shows up everywhere

### Python version: only 3.x

Python 2 reached end of life in 2020. New code should target Python 3.10 or later. Check `python --version`, and reinstall if you only have 2.x.

| OS | Recommended install |
| --- | --- |
| macOS | `brew install python@3.12` |
| Ubuntu/Debian | `apt install python3.12 python3.12-venv` |
| Windows | python.org installer (check "Add to PATH") or `winget install Python.Python.3.12` |
| All OSes (alternative) | `pyenv` (manage multiple versions on one machine) |

### Why you must not touch the system Python

macOS and Linux ship with a Python that the OS itself uses. Installing packages into `/usr/bin/python3` directly can break OS tools. Also, if two projects need different versions of the same package, a single environment can never satisfy both at the same time.

The solution is venv. A venv gives each project its own isolated Python environment, and packages installed inside it never affect other projects or the system.

### How venv works

`python -m venv .venv` creates a `.venv/` directory containing a copy of (or link to) the Python interpreter. Activation (`source .venv/bin/activate`) flips your PATH so that `python` resolves to `.venv/bin/python`, and `pip install` writes packages into `.venv/lib/`. Deactivation (`deactivate`) restores the original PATH.

### pip and requirements.txt

`pip` is Python's default package manager. `pip install requests` installs a package; `pip freeze > requirements.txt` saves all currently installed package versions to a file. On another machine you reproduce the same environment with `pip install -r requirements.txt`.

## Before-After

```bash
# Before: install directly into system Python
$ pip install requests          # written into /usr/lib/python3
$ pip install requests==2.20    # collides with another project
ERROR: Cannot uninstall 'requests'. It is a distutils installed project.
```

```bash
# After: use a venv
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install requests==2.20    # only into .venv/lib
(.venv) $ deactivate                    # system unchanged
```

The After pattern stays conflict-free even with 100 projects.

## Step-by-step walkthrough

### Step 1: confirm your Python install

```bash
python3 --version
# something like Python 3.12.0 means OK
```

If lower than 3.10, reinstall using the table above.

### Step 2: create a project directory

```bash
mkdir my-first-project
cd my-first-project
```

### Step 3: create and activate a venv

```bash
python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

When activated, your prompt will show `(.venv)` in front.

### Step 4: install a package

```bash
(.venv) $ pip install requests
(.venv) $ pip list
Package    Version
---------- -------
pip        24.0
requests   2.32.3
...
```

### Step 5: pin and reproduce versions

```bash
(.venv) $ pip freeze > requirements.txt
(.venv) $ cat requirements.txt
requests==2.32.3
...

# on another machine
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
```

### Step 6: run your first script

```python
# hello.py
import requests
response = requests.get("https://httpbin.org/get")
print(response.status_code)
print(response.json()["url"])
```

```bash
(.venv) $ python hello.py
200
https://httpbin.org/get
```

## Common mistakes

- **Running `sudo pip install`.** Modifies the system Python and can break OS tools.
- **`pip install` without activating the venv.** Things install in unexpected locations and become hard to track.
- **Committing `.venv/` to git.** Hundreds of MB land in your repo. Add `.venv/` to `.gitignore`.
- **Skipping `requirements.txt`.** No way to reproduce the environment elsewhere.
- **Installing Python 2.** It ended in 2020. Always 3.10+.

## Production patterns

- **Fix `.venv/` at the project root.** A consistent rule across projects keeps IDE setup simple.
- **Always `.gitignore` `.venv/`, `__pycache__/`, `*.pyc`.**
- **Pin versions explicitly (`pip install requests==2.32.3`).** Be kind to your future self.
- **Migrate to `pyproject.toml` gradually.** Start with requirements.txt; once comfortable, switch to `pyproject.toml` plus `uv` or `poetry`.
- **Use `pyenv` when you need multiple Python versions.** Each project can pin its own Python.

## Checklist

- [ ] `python3 --version` is 3.10 or later
- [ ] Each project has its own `.venv/`
- [ ] When activated, the prompt shows `(.venv)`
- [ ] `.venv/` is in `.gitignore`
- [ ] `requirements.txt` is committed to the repo
- [ ] You never use `sudo pip install`

## Exercises

1. Create a venv in a fresh directory, install `requests`, then save `pip freeze > requirements.txt`.
2. In the same folder, delete the venv (`rm -rf .venv`), recreate it, and reproduce the environment from `requirements.txt`.
3. Create venvs in two folders; install `requests==2.20` in one and `requests==2.32` in the other. Confirm both work without conflict.

## Wrap-up and next post

All you need to start with Python is one interpreter and the habit of using venv. Leave the system Python alone for OS tooling, and run all your code inside a venv. Keep this one rule from day one and you avoid environment incidents for life.

The next post covers Python's variables, types, and operators. We will look at how a dynamically typed language works and why type hints are increasingly becoming the standard.

## References

- Python docs: venv — https://docs.python.org/3/library/venv.html
- Python Packaging User Guide: pip — https://packaging.python.org/en/latest/tutorials/installing-packages/
- pyenv — https://github.com/pyenv/pyenv
- Real Python: Python Virtual Environments Primer — https://realpython.com/python-virtual-environments-a-primer/

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, install, venv, pip, version, beginner
