---
title: "Python 101 (7/10): Modules and packages: import, __init__, __name__"
series: python-101
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
- import-system
- module-vs-package
- init-py
- name-main-guard
- relative-imports
- namespace-packages
last_reviewed: '2026-05-03'
seo_description: A module in Python is "a namespace that is loaded once and cached";
  a package is "a directory grouped by __init__.py that holds modules".
---

# Python 101 (7/10): Modules and packages: import, __init__, __name__

In Python, a module is a namespace that is loaded once and cached, and a package is the directory-level unit that groups related modules. Once you see what `import` really loads and names, project structure becomes less mysterious.

This is the 7th post in the Python 101 series.

This post is the 7th article in the Python 101 series. This is the part of the series where single files turn into a real project layout.


![Python 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-101/07/07-01-mental-model.en.png)
*Python 101 chapter 7 flow overview*

## Questions to Keep in Mind

- Treat any `.py` file as a module and pull it into another file with `import`?
- Turn a directory into a package by adding `__init__.py`, and group modules inside it?
- Explain the difference between `import x`, `from x import y`, and `import x as alias`?

## Why it matters

Once you are comfortable writing functions, code starts piling up. A single file with hundreds of lines usually runs into familiar problems:

- Function and variable names start to clash.
- It is hard to find where any given function was defined.
- Reusing the same code in another project becomes a copy-paste exercise.

Modules and packages are among Python's main tools for solving this. You break code into files, group files into directories, and import only the parts you need. CLI scripts, web servers, and data pipelines often rely on this structure. Learning it on a tiny project makes the jump to larger projects much smoother.

## Mental model

> A module in Python is "a namespace that is loaded once and cached"; a package is "a directory grouped by `__init__.py` that holds modules". Hold those two definitions and most import behavior collapses into one diagram.
A module is "a `.py` file that runs once and produces a namespace." A package is "a directory that holds such modules." `import` is the act of attaching that namespace to your current code.

Two ideas matter most. First, **module top-level code runs once, top to bottom, the first time it is imported**. Second, **the resulting namespace object is cached and reused**. A second import does not re-read the file; it pulls the same object from cache.

## Core concepts

### 1. Module

One `.py` file is a module. The module name is the file name with `.py` removed. A file called `math.py` is imported as `import math`.

### 2. Package

A directory containing `__init__.py` is a package. A package can hold other modules and subpackages. `__init__.py` may be empty, or it may hold code that runs the first time the package is loaded.

```text
myapp/
    __init__.py
    cli.py
    db/
        __init__.py
        sqlite_store.py
        migrations.py
```

In this layout, `myapp.db.sqlite_store` refers to the `sqlite_store` module inside the `db` subpackage inside the `myapp` package.

### 3. Forms of import

```python
import math                # bring in the whole math namespace as 'math'
from math import sqrt      # bring just sqrt into the current namespace
import numpy as np         # use a short alias 'np' for numpy
from .sibling import foo   # import foo from a sibling module in the same package
```

`import x` brings in `x` itself, and you call into it as `x.func()`. `from x import y` only brings in `y`, which makes the call site shorter but hides where `y` came from. For small projects either style is fine; as code grows, `import x` tends to make sources easier to follow.

### 4. `__name__` and the `__main__` guard

In normal Python code, a module exposes a string attribute called `__name__`. When a module is imported by another file, `__name__` is the module name. When the file is run directly with `python file.py`, `__name__` becomes `"__main__"`.

```python
def main():
    print("hello")

if __name__ == "__main__":
    main()
```

This pattern separates "the part that should run when the file is launched as a script" from "the part that should be exposed when the file is imported as a library."

### 5. Relative imports

Inside a package, you can refer to sibling modules with leading dots. One dot means the same package, two dots mean the parent package.

```python
# myapp/db/sqlite_store.py
from .migrations import latest_version       # migrations in the same db package
from ..cli import parse_args                 # cli one level up, in myapp
```

Relative imports only make sense inside a package. They cannot be used in a file that is run directly as a script.

### 6. `sys.path` and the import path

When `import x` runs, Python walks a list of directories called `sys.path` looking for `x.py` or a package directory named `x/`. `sys.path` typically includes:

- The directory of the script that started the program
- Paths from the `PYTHONPATH` environment variable
- The standard library location
- Installed `site-packages`

When the same module name exists in more than one location, the first hit along `sys.path` wins.

## Before / after

The same payment-processing logic, first crammed into a single file and then split across modules in a package.

**Before — everything in one file**

```python
# pay.py
import sqlite3

def connect():
    return sqlite3.connect("pay.db")

def insert_order(order):
    conn = connect()
    conn.execute("insert into orders(amount) values (?)", [order["amount"]])
    conn.commit()
    conn.close()

def calc_tax(amount):
    return round(amount * 0.1, 2)

def send_receipt(email, amount):
    print(f"sending receipt to {email}: {amount}")

def main():
    order = {"amount": 100, "email": "a@b.c"}
    insert_order(order)
    send_receipt(order["email"], order["amount"] + calc_tax(order["amount"]))

if __name__ == "__main__":
    main()
```

DB access, tax math, and email handling all live in the same file, which makes it hard to test or reuse any one piece.

**After — one responsibility per module, grouped in a package**

```text
pay/
    __init__.py
    cli.py
    db.py
    tax.py
    notify.py
```

```python
# pay/db.py
import sqlite3

def connect():
    return sqlite3.connect("pay.db")

def insert_order(order):
    conn = connect()
    conn.execute("insert into orders(amount) values (?)", [order["amount"]])
    conn.commit()
    conn.close()
```

```python
# pay/tax.py
def calc_tax(amount):
    return round(amount * 0.1, 2)
```

```python
# pay/notify.py
def send_receipt(email, amount):
    print(f"sending receipt to {email}: {amount}")
```

```python
# pay/cli.py
from .db import insert_order
from .tax import calc_tax
from .notify import send_receipt

def main():
    order = {"amount": 100, "email": "a@b.c"}
    insert_order(order)
    send_receipt(order["email"], order["amount"] + calc_tax(order["amount"]))

if __name__ == "__main__":
    main()
```

Each module owns one responsibility, and `cli.py` composes them. `tax.py` is testable on its own with no DB involved, and another project can pull in just `pay.tax` if that is all it needs.

## Step-by-step practice

Build it yourself in a REPL. Lines beginning with `>>>` are what you type, and the lines below show the output.

### 1. Write a module

In a working directory, create `greet.py`:

```python
# greet.py
def hello(name):
    return f"hello, {name}"

print("greet module loaded")
```

Start a REPL in the same directory and import it:

```pycon
>>> import greet
greet module loaded
>>> greet.hello("ada")
'hello, ada'
>>> import greet
>>>
```

The `print` line shows up on the first import only. The second `import greet` reuses the cache, so the module body does not run again.

### 2. See the `__name__` guard in action

Add one more line at the bottom of `greet.py`:

```python
if __name__ == "__main__":
    print("running as a script")
```

Now `python greet.py` shows two lines:

```text
greet module loaded
running as a script
```

When another file does `import greet`, the `running as a script` line does not appear. That difference is what lets you keep a library and a CLI in the same file.

### 3. Build a small package

Create this layout:

```text
shop/
    __init__.py
    catalog.py
    cart.py
```

```python
# shop/catalog.py
PRICES = {"apple": 1000, "banana": 500}

def price_of(item):
    return PRICES.get(item, 0)
```

```python
# shop/cart.py
from .catalog import price_of

def total(items):
    return sum(price_of(i) for i in items)
```

Open a REPL in the directory that contains `shop/`:

```pycon
>>> from shop.cart import total
>>> total(["apple", "banana", "apple"])
2500
```

In `shop/cart.py`, the line `from .catalog import price_of` points at `catalog` inside the same package.

### 4. Look at `sys.path`

```pycon
>>> import sys
>>> sys.path[:3]
['', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload']
```

The leading empty string means "the current working directory," which is why `import greet` in step 1 found a sibling file.

## Common mistakes

1. **Treating a directory without `__init__.py` as a regular package.**
   It can sometimes work as a namespace package, but for ordinary packages an empty `__init__.py` makes intent obvious and makes import paths easier to follow.

2. **Using `from x import *` in production code.**
   Names appear in your namespace without any visible source. When something clashes, you have nowhere to look. Save it for the REPL or a quick notebook.

3. **Running a file with relative imports as a script.**
   `python pay/cli.py` does not treat `cli.py` as part of a package, so `from .db import ...` fails. Use `python -m pay.cli` instead, or keep the entry point outside the package.

4. **Doing heavy work at module top level.**
   If a single import triggers a network call or a large file load, that cost shows up as soon as the module is imported. Move heavy work into functions and call them when needed.

5. **Circular imports.**
   If `a.py` imports `b` and `b.py` imports `a`, one side sees the other half-built. Pull the shared dependency into a third module, or move the import inside a function to break the cycle.

6. **Mutating `sys.path` from inside library code.**
   Scattered `sys.path.insert(0, "...")` calls make it hard to predict how any import resolves. Installing the package (`pip install -e .`) or setting `PYTHONPATH` is much easier to reason about.

## In practice

Real projects use modules and packages roughly like this.

- **Layered structure**: subpackages such as `myapp/api`, `myapp/db`, and `myapp/services` keep responsibilities separated, and each module sticks to its layer.
- **CLI entry point**: shipping a `python -m myapp.cli` entry point lets relative imports inside the package work naturally.
- **Reuse surface**: re-exporting selected functions from `__init__.py` lets users write `from myapp import do_something` instead of digging into submodules.
- **Tests**: importing modules individually lets `pytest` pick out specific functions. A monolithic file forces tests to drag everything in.
- **Config split**: environment-specific settings live in their own modules (`config_dev.py`, `config_prod.py`) and the entry point picks one.

This shape often stays similar as a project grows. You can start with a single `myapp/__init__.py` and add subpackages later as needed.

## Checklist

- [ ] You can turn a `.py` file into a module and import it from another file.
- [ ] You can build a package by adding `__init__.py` to a directory and call its modules as `pkg.mod`.
- [ ] You can describe the difference between `import x`, `from x import y`, and `import x as alias` in one sentence each.
- [ ] You can explain `if __name__ == "__main__":` for both direct execution and import.
- [ ] You can use `from .sibling import ...` for relative imports inside a package.
- [ ] You can describe in one line how `sys.path` and `PYTHONPATH` participate in import lookup.

## Exercises

1. Write `mathx.py` with `square(x)` and `cube(x)`, then `import mathx` in a REPL and call them.
2. Build a `tools/` directory with `__init__.py`, `text.py`, and `numbers.py`, and have `text.py` use a relative import to call a function in `numbers.py`.
3. Add `tools/cli.py` so that `python -m tools.cli` runs it, and use the `__name__ == "__main__"` guard.
4. Make a module that prints one line when imported, then import it twice in the same REPL session and confirm the body runs only once.

## Summary and next chapter

- A module is one `.py` file; a package is a directory that contains `__init__.py`.
- Import runs a module's top-level code once and stores the result in `sys.modules` for later reuse.
- `import x`, `from x import y`, `as alias`, and `from .sibling import ...` are different ways of using the same import system.
- `if __name__ == "__main__":` lets one file act as both a library and a script.
- `sys.path` and `PYTHONPATH` are the source of truth for import lookup, so installing the package or setting an environment variable is safer than mutating the list at runtime.

The next chapter covers file I/O and exception handling, where the modules you just organized start touching outside resources.

## Answering the Opening Questions

- **Same-name functions and variables collide?**
  - Putting everything in one file makes name collisions easy. Splitting into modules gives namespace separation: `mod_a.process` vs `mod_b.process`. Using `import x` or explicit named imports instead of `from x import *` is the first line of defense.
- **Hard to find where a function is defined?**
  - A single bloated file makes definition tracking painful. Package structure (`mypkg/auth.py`, `mypkg/billing.py`) makes the import path itself tell you "where it lives." IDE go-to-definition also works properly only when module boundaries exist.
- **Difficult to reuse the same code in another project?**
  - A monolithic script resists reuse. Separating into modules/packages with a public API declared in `__init__.py` lets other projects `pip install` or sys.path-register and import directly. Adding an `if __name__ == "__main__":` guard lets the module serve both as importable library and standalone script.

<!-- toc:begin -->
## In this series

- [Python 101 (1/10): Why Python, and how to install and use venv](./01-why-python-and-install.md)
- [Python 101 (2/10): Variables, types, and operators](./02-variables-types-operators.md)
- [Python 101 (3/10): Strings and formatting](./03-strings-and-formatting.md)
- [Python 101 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- [Python 101 (5/10): Control flow: if, for, while, comprehension](./05-control-flow.md)
- [Python 101 (6/10): Functions and arguments: def, args, kwargs, default, lambda](./06-functions-and-arguments.md)
- **Modules and packages: import, __init__, __name__ (current)**
- File I/O and exception handling (upcoming)
- Classes and objects: bundling data with behavior (upcoming)
- Standard library tour: datetime, pathlib, json, collections, itertools (upcoming)

<!-- toc:end -->

## References

- [Python tutorial — Modules](https://docs.python.org/3/tutorial/modules.html) — Practical introduction to module execution, import caching, and `sys.path` lookup order.
- [Python Language Reference — The import system](https://docs.python.org/3/reference/import.html) — Formal description of finders, loaders, module caching, and package imports.
- [Python docs — `__main__`](https://docs.python.org/3/library/__main__.html) — Clarifies the `if __name__ == "__main__"` guard and package entry-point behavior.
- [PEP 328 — Imports: Multi-Line and Absolute/Relative](https://peps.python.org/pep-0328/) — Primary source for absolute imports and leading-dot relative imports.
- [PEP 420 — Implicit Namespace Packages](https://peps.python.org/pep-0420/) — Relevant for the chapter’s note on packages that do not rely on `__init__.py`.

Tags: import-system, module-vs-package, init-py, name-main-guard, relative-imports, namespace-packages
