#!/usr/bin/env python3
"""Guard: H2/H3 headings must not end with ':' (excluding code-fence contents).

Trailing-colon headings are usually a symptom of pasting structured data
(e.g. Alpaca dataset format: '### Instruction:', '### Input:', '### Response:')
as markdown headings instead of inside a fenced code block. They corrupt the
document outline, TOC, and rendered structure.

This guard is code-fence aware (skips content inside ```...``` blocks).

Refs: #1234
"""
from __future__ import annotations

import glob
import re
import sys

HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^```")


def offending_headings(path: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    in_fence = False
    in_frontmatter = False
    with open(path, encoding="utf-8") as fh:
        for idx, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            # Front matter skip (only at top of file)
            if idx == 1 and line == "---":
                in_frontmatter = True
                continue
            if in_frontmatter:
                if line == "---":
                    in_frontmatter = False
                continue
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING_RE.match(line)
            if not m:
                continue
            heading = m.group(2)
            if heading.endswith(":") or heading.endswith("\uFF1A"):
                hits.append((idx, line))
    return hits


def main() -> int:
    failures: list[str] = []
    for path in sorted(glob.glob("content/*/ko/*.md") + glob.glob("content/*/en/*.md")):
        for line_no, line in offending_headings(path):
            failures.append(f"{path}:{line_no}: {line}")

    if failures:
        print("FAIL: H2/H3 headings ending with ':' (likely structured data pasted as heading).", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(f"\nTotal: {len(failures)} offending heading(s).", file=sys.stderr)
        return 1

    print("PASS: No H2/H3 headings end with ':'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
