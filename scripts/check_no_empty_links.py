#!/usr/bin/env python3
"""Guard: ko/en posts must not contain empty markdown links '[text]()' outside code fences.

Empty markdown links commonly appear from:
- Placeholder leakage (forgotten 'add URL here' markers in shipped prose)
- Code-as-link conversion accidents (Python/JS expressions like 'reg[key]()'
  mis-parsed by markdown tools as links)

This guard is code-fence aware: occurrences inside ```...``` blocks are
intentional (real code, or template examples for readers to fill in) and
are ignored. Front matter is also skipped.

Refs: #1233
"""
from __future__ import annotations

import glob
import re
import sys

LINK_RE = re.compile(r"\[[^\]]+\]\(\s*\)")
FENCE_RE = re.compile(r"^```")


def scan(path: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    in_fence = False
    in_frontmatter = False
    with open(path, encoding="utf-8") as fh:
        for idx, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
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
            for m in LINK_RE.finditer(line):
                hits.append((idx, m.group(0)))
    return hits


def main() -> int:
    failures: list[str] = []
    for path in sorted(glob.glob("content/*/ko/*.md") + glob.glob("content/*/en/*.md")):
        for line_no, snippet in scan(path):
            failures.append(f"{path}:{line_no}: {snippet}")

    if failures:
        print("FAIL: empty markdown link(s) '[text]()' outside code fences.", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(f"\nTotal: {len(failures)} offending link(s).", file=sys.stderr)
        return 1

    print("PASS: No empty markdown links in prose.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
