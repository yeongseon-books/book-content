---
series: type-hints-python-101
episode: 8
title: "Type Hints in Python 101 (8/10): Using mypy and pyright"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - Type Hints
  - mypy
  - pyright
  - Static Analysis
  - CI
seo_description: Set up mypy and pyright for Python projects with gradual adoption, strict mode, and CI integration strategies.
last_reviewed: '2026-05-17'
---

# Type Hints in Python 101 (8/10): Using mypy and pyright

Writing type hints is only half the job. If nobody runs a checker, a wrong return type or a missing `None` guard can sit quietly in the repository until runtime finally exposes it.

This is post 8 in the Type Hints in Python 101 series. In this article, we will follow one small repository from broken code to mypy output, pyright output, stricter configuration, and finally a CI gate so the same workflow stays enforceable after the first local fix.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Using mypy and pyright?
- Which signal should the example or diagram make visible for Using mypy and pyright?
- What failure should be prevented first when Using mypy and pyright reaches a real system?

## Big Picture

![Type Hints in Python 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/08/08-01-concept-at-a-glance.en.png)

*Type Hints in Python 101 chapter 8 flow overview*

This picture places Using mypy and pyright inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Using mypy and pyright is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- How to verify type hints without executing the program
- How mypy and pyright report the same bug on the same codebase
- How to tighten configuration gradually instead of enabling strict mode everywhere
- How to turn local type checking into a team-wide CI rule

> Type hints become valuable when they fail the build before production does.

## Why It Matters

Python does not enforce type hints at runtime. A function can declare `-> str` and still return `None`, and the interpreter will not object. Static type checkers close that gap by turning annotations into pre-runtime feedback.

mypy and pyright both do that, but the useful operational question is bigger than tool choice. You need one example that fails, gets fixed, becomes stricter, and then gets enforced in CI. Otherwise the article stops at installation commands instead of giving readers a runnable workflow.

## Key Concepts

| Term | Description |
| --- | --- |
| mypy | The most widely used static type checker in the Python ecosystem |
| pyright | A fast type checker by Microsoft and the engine behind Pylance |
| strict mode | A tighter configuration that treats missing annotations and loose inference more aggressively |
| override | Per-module configuration that lets one directory be stricter than another |
| CI gate | An automated step that blocks merges when type checking fails |

## Before / After

```python
def normalize_user_id(raw_user_id: str) -> int:
    return raw_user_id

def build_greeting(name: str | None) -> str:
    return "Hello, " + name.upper()
```

```text
$ mypy src
src/accounts.py:5: error: Incompatible return value type (got "str", expected "int")
src/accounts.py:9: error: Item "None" of "str | None" has no attribute "upper"
Found 2 errors in 1 file (checked 1 source file)
```

That transition is the whole point: the code looked fine until a checker turned the contract into a failing workflow.

## Follow One Mini Repository End to End

This entire article uses the same example structure.

```text
typecheck-demo/
├── pyproject.toml
├── pyrightconfig.json
├── src/
│   └── accounts.py
└── .github/
    └── workflows/
        └── type-check.yml
```

### Step 1: Start with a file that contains real type bugs

```python
# src/accounts.py
from typing import TypedDict

class UserRow(TypedDict):
    id: int
    email: str
    display_name: str | None

def normalize_user_id(raw_user_id: str) -> int:
    return raw_user_id

def build_greeting(user: UserRow) -> str:
    return "Hello, " + user["display_name"].upper()

def list_admin_emails(rows: list[UserRow]) -> list[str]:
    return [row["email"] for row in rows if row["id"] in {1, 2, 3}]
```

Two deliberate problems are doing the teaching work here.

- `normalize_user_id()` promises `int` but returns `str`.
- `build_greeting()` assumes `display_name` is always present even though the type says `str | None`.

### Step 2: Run mypy on that exact file

```bash
python -m pip install mypy
mypy src
```

```text
src/accounts.py:10: error: Incompatible return value type (got "str", expected "int")  [return-value]
src/accounts.py:14: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
Found 2 errors in 1 file (checked 1 source file)
```

mypy separates the return-type mismatch from the missing `None` handling. That is already more useful than “run a checker sometime” because the failure is concrete and reproducible.

### Step 3: Run pyright on the same file

```bash
python -m pip install pyright
pyright src
```

```text
/Users/username/typecheck-demo/src/accounts.py
  /Users/username/typecheck-demo/src/accounts.py:10:12 - error: Type "str" is not assignable to return type "int"
    "str" is not assignable to "int" (reportReturnType)
  /Users/username/typecheck-demo/src/accounts.py:14:38 - error: "upper" is not a known attribute of "None" (reportOptionalMemberAccess)
2 errors, 0 warnings, 0 informations
```

pyright catches the same two bugs but formats them differently. That is why many teams use **pyright for editor feedback** and **mypy for the merge gate**, or vice versa. The point is not to force both as equals everywhere; it is to give each tool a clear role.

### Step 4: Fix the code and confirm both checkers pass

```python
# src/accounts.py
from typing import TypedDict

class UserRow(TypedDict):
    id: int
    email: str
    display_name: str | None

def normalize_user_id(raw_user_id: str) -> int:
    return int(raw_user_id)

def build_greeting(user: UserRow) -> str:
    display_name = user["display_name"]
    if display_name is None:
        return "Hello, anonymous"
    return "Hello, " + display_name.upper()

def list_admin_emails(rows: list[UserRow]) -> list[str]:
    return [row["email"] for row in rows if row["id"] in {1, 2, 3}]
```

```text
$ mypy src
Success: no issues found in 1 source file

$ pyright src
0 errors, 0 warnings, 0 informations
```

Now the annotations are not just documentation. They are a verified contract that fails when the implementation drifts.

### Step 5: Establish a loose but repeatable baseline

Do not begin with repository-wide strict mode. First, make sure the checker always looks at the same code and reports the same class of failures.

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
files = ["src"]
check_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true
```

```json
{
  "include": ["src"],
  "pythonVersion": "3.11",
  "typeCheckingMode": "basic",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false
}
```

This baseline does two jobs.

- It makes the tool target explicit.
- It gives the team a stable “this must pass” starting point before stricter rollout begins.

### Step 6: Tighten one important module first

The most common migration mistake is enabling strict mode for the entire repository in one shot. A safer pattern is to harden high-value paths first.

```toml
[tool.mypy]
python_version = "3.11"
files = ["src"]
check_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "src.accounts"
strict = true

[[tool.mypy.overrides]]
module = "src.legacy.*"
ignore_errors = true
```

```json
{
  "include": ["src"],
  "pythonVersion": "3.11",
  "typeCheckingMode": "basic",
  "strict": ["src/accounts.py"],
  "exclude": ["src/legacy"]
}
```

That is the practical rollout pattern: new or important modules fail harder first, while legacy code gets a temporary quarantine rather than blocking all progress.

### Step 7: Put the same workflow into CI

```yaml
# .github/workflows/type-check.yml
name: Type Check

on:
  pull_request:
  push:
    branches:
      - master

jobs:
  static-type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install checkers
        run: |
          python -m pip install --upgrade pip
          python -m pip install mypy pyright
      - name: Run mypy
        run: mypy src
      - name: Run pyright
        run: pyright src
```

At this point the article finally reaches the operational finish line. The same repository that failed locally now fails automatically in pull requests, which is what turns type hints into a team standard rather than a personal preference.

### Step 8: Add operating rules so the workflow stays useful

Once checkers are in place, the next failure mode is noise. A few lightweight rules prevent that.

1. **Choose one merge gate.** For example, block PRs on mypy and keep pyright as fast editor feedback.
2. **Require reasons for `type: ignore`.** Distinguish between missing stubs, tool limitations, and temporary exceptions.
3. **Review strict-scope growth regularly.** `legacy` should be a migration zone, not a permanent exemption.

```python
from third_party_sdk import build_client

client = build_client()  # type: ignore[no-untyped-call]  # SDK v2 still has no type stubs
```

## What to Notice in This Code

- The important upgrade is not “install mypy” but “watch the same file fail, then pass”
- mypy and pyright surface the same bug with different wording and error codes
- Strictness scales better per module than per repository
- CI is what turns static checking into an enforced workflow

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Documenting commands without showing real failures | Readers never see what the checker actually catches | Use one broken file and include the output |
| Enabling strict mode everywhere at once | Error volume overwhelms the team | Tighten one directory or module at a time |
| Making both tools equal required gates | Edge-case differences create friction | Choose one merge gate and one support role |
| Leaving bare `type: ignore` comments | Exceptions become invisible debt | Include the error code and the reason |
| Relying on local runs only | Enforcement varies by developer habit | Run the checker in PR and push workflows |

## Real-World Applications

- VS Code + Pylance showing pyright feedback while code is being written
- GitHub Actions blocking PRs when mypy fails on service modules
- Gradual strict-mode rollout that starts with `src/core` or `src/api`
- Legacy directories quarantined temporarily while the team reduces debt in batches

## How Senior Engineers Think About This

Senior engineers treat type checking as infrastructure, not decoration. The first question is not “which checker is cooler?” but “where does failure happen, and is that failure reproducible in CI?” New projects can start with the baseline immediately. Existing projects need a ratcheting strategy that keeps error counts survivable.

Consistency matters more than theoretical purity. Decide which tool is the merge gate, which packages get strict treatment next, and what counts as an acceptable suppression. Once those rules exist, type hints stop being optional metadata and start functioning as an engineering control.

## Checklist

- [ ] Ran mypy and pyright on the same example module
- [ ] Captured real failure output and verified the fixed success output
- [ ] Added a baseline `pyproject.toml` and `pyrightconfig.json`
- [ ] Chosen which module gets stricter checking first
- [ ] Added a CI workflow that fails automatically on type errors

## Exercises

1. Add one return-type bug and one missing-`None` guard to a file under `src/`, then compare the mypy and pyright messages.

2. Write a config where `src/core` is strict and `src/legacy` is temporarily relaxed.

3. Document an operating policy where mypy blocks merges but pyright remains an editor-first feedback tool.

## Summary and Next Steps

mypy and pyright matter when they participate in one continuous workflow: a broken file, a reproducible error report, a fixed implementation, stricter config, and an automated CI gate. That end-to-end path is what turns type hints into an actual quality barrier.

In the next article, we will move from static verification to runtime validation with Pydantic.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Using mypy and pyright?**
  - The article treats Using mypy and pyright as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Using mypy and pyright?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Using mypy and pyright reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Type Hints in Python 101 (1/10): What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): Basic Types and Collection Types](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional and Union](./03-optional-and-union.md)
- [Type Hints in Python 101 (4/10): Function Type Hints](./04-function-type-hints.md)
- [Type Hints in Python 101 (5/10): TypedDict and dataclass](./05-typeddict-and-dataclass.md)
- [Type Hints in Python 101 (6/10): Protocol and Structural Typing](./06-protocol-and-structural-typing.md)
- [Type Hints in Python 101 (7/10): Understanding Generics](./07-generic.md)
- **Using mypy and pyright (current)**
- Pydantic and Type Hints (upcoming)
- Type Hint Best Practices (upcoming)

<!-- toc:end -->

## References

- [mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [pyright documentation](https://github.com/microsoft/pyright)
- [mypy configuration reference](https://mypy.readthedocs.io/en/stable/config_file.html)
- [mypy docs — Using mypy with an existing codebase](https://mypy.readthedocs.io/en/stable/existing_code.html)
- [pyright configuration docs](https://microsoft.github.io/pyright/#/configuration)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)

Tags: Python, Type Hints, mypy, pyright, Static Analysis, CI
