"""Auto-fix REPL transcript code fences in canonical content.

A ```python``` block whose contents start with `>>>` (after optional blank
lines) is a Python REPL transcript, not source code. The repo convention
(documented in python-101/ko/10-standard-library-tour.md) is to label such
blocks as ```text``` so they render verbatim and never confuse linters.

Usage:
    python3 scripts/_fix_repl_fences.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"
LANGS = {"ko", "en"}


def is_repl_block(body_lines: list[str]) -> bool:
    for ln in body_lines:
        s = ln.strip()
        if not s:
            continue
        return s.startswith(">>>")
    return False


def transform_text(text: str) -> tuple[str, int]:
    """Return (new_text, count_of_fixes)."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    fixes = 0
    while i < len(lines):
        ln = lines[i]
        stripped = ln.lstrip()
        indent_len = len(ln) - len(stripped)
        indent = ln[:indent_len]
        opener_text = stripped.rstrip("\r\n")
        if opener_text == "```python":
            body: list[str] = []
            j = i + 1
            while j < len(lines):
                cand = lines[j]
                cand_stripped = cand.lstrip()
                cand_indent = len(cand) - len(cand_stripped)
                if cand_stripped.rstrip("\r\n") == "```" and cand_indent == indent_len:
                    break
                body.append(cand)
                j += 1
            if j < len(lines) and is_repl_block(body):
                out.append(f"{indent}```text\n")
                out.extend(body)
                out.append(lines[j])
                fixes += 1
                i = j + 1
                continue
        out.append(ln)
        i += 1
    return "".join(out), fixes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--series")
    args = ap.parse_args()

    total_fixes = 0
    files_changed = 0
    targets: list[Path] = []
    for series_dir in sorted(CONTENT.iterdir()):
        if not series_dir.is_dir():
            continue
        if args.series and series_dir.name != args.series:
            continue
        for lang in LANGS:
            d = series_dir / lang
            if not d.is_dir():
                continue
            targets.extend(sorted(d.glob("*.md")))

    for md in targets:
        text = md.read_text(encoding="utf-8")
        new_text, fixes = transform_text(text)
        if fixes:
            total_fixes += fixes
            files_changed += 1
            rel = md.relative_to(REPO)
            print(f"  {rel}: {fixes} REPL fence(s)")
            if not args.dry_run:
                md.write_text(new_text, encoding="utf-8")

    action = "would fix" if args.dry_run else "fixed"
    print(f"\n{action} {total_fixes} REPL fences across {files_changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
