#!/usr/bin/env python3
"""Fix literal backslash-n sequences in ```python fenced blocks."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

FENCE = re.compile(r"^(\s*)```(\w*)\s*$")


def try_parse(src: str) -> bool:
    try:
        ast.parse(src)
        return True
    except SyntaxError:
        return False


def expand_line(line: str) -> str:
    nl = "\n" if line.endswith("\n") else ""
    body = line[:-1] if nl else line
    return body.replace("\\n", "\n") + nl


def fix_block(lines: list[str]) -> list[str]:
    original = "".join(lines)
    if try_parse(original):
        return lines

    expanded = "".join(expand_line(l) for l in lines)
    if try_parse(expanded):
        return expanded.splitlines(keepends=True)

    candidate_lines = []
    for line in lines:
        if "\\n" in line and re.search(r"\\n\s*[A-Za-z_#@]", line):
            candidate_lines.append(expand_line(line))
        else:
            candidate_lines.append(line)
    candidate = "".join(candidate_lines)
    if try_parse(candidate):
        return candidate.splitlines(keepends=True)

    return lines


def process_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    fixes = 0
    while i < len(lines):
        line = lines[i]
        m = FENCE.match(line)
        if not m or m.group(2).lower() not in ("python", "py"):
            out.append(line)
            i += 1
            continue
        indent = m.group(1)
        j = i + 1
        while j < len(lines):
            cm = FENCE.match(lines[j])
            if cm and cm.group(1) == indent and cm.group(2) == "":
                break
            j += 1
        if j >= len(lines):
            out.append(line)
            i += 1
            continue
        block = lines[i + 1 : j]
        fixed = fix_block(block)
        if fixed != block:
            fixes += 1
        out.append(line)
        out.extend(fixed)
        out.append(lines[j])
        i = j + 1
    if fixes:
        path.write_text("".join(out), encoding="utf-8")
    return fixes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()
    total = 0
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"skip {p}: not found", file=sys.stderr)
            continue
        n = process_file(path)
        print(f"  {p}: {n} blocks fixed")
        total += n
    print(f"\nTotal: {total} blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
