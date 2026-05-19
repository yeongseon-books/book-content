"""Repair Python string literals broken across lines.

Pattern targeted:
    line A: ...prefix Q content_A
    line B: content_B
    ...
    line K: content_K Q tail

where Q is the opening quote (' or ") and there's no matching close on
line A. The original source was almost certainly:
    ...prefix Q content_A \\n content_B \\n ... \\n content_K Q tail

i.e. '\\n' escape sequences were rendered as literal newlines during
some Markdown processing. We join the broken lines back into a single
line with '\\n' escape sequences.

Only operates inside ```python fences. Detection walks each line as a
character stream to find truly unmatched quotes (respecting backslash
escapes and comments).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def find_python_blocks(lines: list[str]) -> list[tuple[int, int]]:
    blocks = []
    i = 0
    while i < len(lines):
        if lines[i].rstrip() == "```python":
            start = i + 1
            j = i + 1
            while j < len(lines) and lines[j].rstrip() != "```":
                j += 1
            blocks.append((start, j))
            i = j + 1
        else:
            i += 1
    return blocks


def find_unmatched_open_quote(line: str) -> int | None:
    in_str: str | None = None
    start_pos = -1
    escape = False
    for k, ch in enumerate(line):
        if in_str is None:
            if ch == "#":
                return None
            if ch in ("'", '"'):
                in_str = ch
                start_pos = k
        else:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == in_str:
                in_str = None
                start_pos = -1
    return start_pos if in_str is not None else None


def find_close_quote(line: str, q: str) -> int | None:
    escape = False
    for k, ch in enumerate(line):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == q:
            return k
    return None


def repair_block(
    lines: list[str], start: int, end: int, max_span: int = 8
) -> tuple[list[str], int]:
    out: list[str] = []
    fixes = 0
    i = start
    while i < end:
        full = lines[i]
        ln = full.rstrip("\n").rstrip("\r")
        eol = full[len(ln) :]
        open_pos = find_unmatched_open_quote(ln)
        if open_pos is None:
            out.append(full)
            i += 1
            continue
        q = ln[open_pos]
        prefix = ln[:open_pos]
        open_tail = ln[open_pos + 1 :]
        chunks = [open_tail]
        j = i + 1
        found = False
        while j < end and j - i <= max_span:
            cand = lines[j].rstrip("\n").rstrip("\r")
            cp = find_close_quote(cand, q)
            if cp is not None:
                chunks.append(cand[:cp])
                close_tail = cand[cp + 1 :]
                joined = "\\n".join(chunks)
                new_line = f"{prefix}{q}{joined}{q}{close_tail}{eol}"
                out.append(new_line)
                i = j + 1
                fixes += 1
                found = True
                break
            chunks.append(cand)
            j += 1
        if not found:
            out.append(full)
            i += 1
    return out, fixes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    total = 0
    for fp in args.files:
        p = Path(fp)
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
        block_fixes = 0
        new_lines = list(lines)
        for start, end in reversed(find_python_blocks(new_lines)):
            repaired, fixes = repair_block(new_lines, start, end)
            if fixes:
                new_lines = new_lines[:start] + repaired + new_lines[end:]
                block_fixes += fixes
        if block_fixes:
            total += block_fixes
            print(f"  {fp}: {block_fixes} fixes")
            if not args.dry_run:
                p.write_text("".join(new_lines), encoding="utf-8")
    print(f"\nTotal: {total} repairs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
