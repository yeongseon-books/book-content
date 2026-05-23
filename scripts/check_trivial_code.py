#!/usr/bin/env python3
"""Guard: detect AI-slop trivial code fences (concept memos disguised as code).

Issue #1227 root cause: an expand-template script inserted one-line fenced
``python`` blocks like::

    ```python
    flow = "register -> upload -> share"
    ```

    ```python
    value = "spot conflicts fast"
    ```

These are NOT Python code; they are concept memos wrapped in a fence to
simulate structure. They violate AGENTS.md Prime Directive §7 (byte-target
boilerplate) and degrade syntax highlighters.

This guard distinguishes the AI-slop pattern from LEGITIMATE one-line code
demos that the repository uses heavily for pedagogy:

- ``SELECT * FROM users;`` (real SQL teaching)
- ``GET /users/42`` (real HTTP example)
- ``<a href="/about">About</a>`` (real HTML)
- ``.\\.venv\\Scripts\\Activate.ps1`` (real PowerShell)
- ``cache[user_prompt] = response_text`` (real Python statement)

Heuristic
=========

A one-line python fence is flagged ONLY when ALL of:

1. Language tag is ``python`` or ``py``.
2. Body is a single line and matches::

       <bareword>(_<bareword>)* = "<string literal with no python ops>"

   i.e., a memo assignment such as ``flow = "..."``, ``value = "..."``,
   ``success = "..."``. Real Python (function calls, attribute access,
   list/dict/set literals, comparisons, arithmetic, ``import``, ``from``,
   indexing) is allowed.

3. The string value is short prose (no parentheses, no ``->`` operator
   converted to code intent, no dict/list literal characters). We DO allow
   ``->`` in the value because the original AI-slop heavily used it; we
   detect it as part of (2).

For non-python languages (``sql``, ``http``, ``html``, ``markdown``,
``powershell``, ``jsx``, ``js``, ``javascript``, ``csharp``, ``promql``)
one-line fences are NOT flagged: they are routinely used for legitimate
teaching demos (``SELECT * FROM users;`` etc.).

Exemption: ``content/azure-app-service-101/**`` is the gold reference.

Usage
=====

    python3 scripts/check_trivial_code.py [paths...]

Exit codes:
    0 - clean
    1 - violations found

See also
========
- AGENTS.md Prime Directive §7
- AGENTS.md Audit Issue Close Protocol (#1225)
- Issue #1227
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

PY_LANGS = {"python", "py"}

FRONT_RE = re.compile(r"^---\n.*?\n---\n", re.S)
FENCE_RE = re.compile(r"```([a-z0-9_+-]*)\n(.*?)```", re.S)

# memo assignment: identifier (or dotted) = "string with no Python operators"
MEMO_RE = re.compile(
    r"""
    ^\s*
    [A-Za-z_][A-Za-z0-9_]*                 # bare identifier
    \s*=\s*
    (?:
        "[^"\n]*"                           # double-quoted string
        | '[^'\n]*'                         # single-quoted string
    )
    \s*(?:\#.*)?$                           # optional trailing comment
    """,
    re.X,
)


def is_memo_assignment(code: str) -> bool:
    """True if code is a single-line ``name = "string"`` memo."""
    stripped = code.strip()
    if "\n" in stripped:
        return False
    return bool(MEMO_RE.match(stripped))


def scan_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    text = FRONT_RE.sub("", text, count=1)
    violations: list[str] = []
    for m in FENCE_RE.finditer(text):
        lang = m.group(1)
        body = m.group(2).rstrip("\n")
        if lang not in PY_LANGS:
            continue
        if "\n" in body:
            continue  # multi-line python is fine
        if is_memo_assignment(body):
            line_no = text[: m.start()].count("\n") + 1
            violations.append(
                f"{path}:{line_no}: AI-slop memo disguised as python: "
                f"{body.strip()[:80]}"
            )
    return violations


def iter_targets(args: list[str]) -> list[Path]:
    if args:
        out: list[Path] = []
        for a in args:
            p = Path(a)
            if p.is_dir():
                out.extend(sorted(p.rglob("*.md")))
            elif p.is_file():
                out.append(p)
        return out
    # default: all ko + en, skip gold reference
    files = sorted(CONTENT.glob("*/ko/*.md")) + sorted(CONTENT.glob("*/en/*.md"))
    return [f for f in files if "azure-app-service-101" not in f.parts]


def main(argv: list[str]) -> int:
    files = iter_targets(argv)
    all_violations: list[str] = []
    for f in files:
        all_violations.extend(scan_file(f))
    if all_violations:
        for v in all_violations:
            print(v, file=sys.stderr)
        print(
            f"\n{len(all_violations)} AI-slop python memo fences found "
            f"(see Issue #1227)",
            file=sys.stderr,
        )
        return 1
    print(f"{len(files)} files checked, 0 AI-slop python memo fences")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
