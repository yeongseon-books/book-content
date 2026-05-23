#!/usr/bin/env python3
"""Guard: forbid English-translation residue pronouns in ko prose.

Triggers on '당신은 / 당신의 / 그것은' when they appear in narrative prose.
Skips:
  - YAML frontmatter
  - Fenced code blocks (``` and ~~~)
  - Lines where the phrase is inside a quoted string literal — these are
    legitimate LLM system-prompt examples (e.g., `"role": "system",
    "content": "당신은 한국어 도우미입니다."`) which use the standard
    Korean prompt convention and must not be rewritten.

Refs: #1230, humanize-korean/quick-rules.md S1
"""
from __future__ import annotations

import glob
import re
import sys

PATTERNS = [
    re.compile(r"당신은"),
    re.compile(r"당신의"),
    re.compile(r"그것은"),
]
QUOTED_RE = re.compile(r"""["'`].*(?:당신은|당신의|그것은).*["'`]""")


def scan(path: str) -> list[tuple[int, str]]:
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return []
    lines = text.split("\n")
    fm_end = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm_end = i + 1
                break

    in_fence = False
    fence_marker = ""
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(lines, 1):
        if i <= fm_end:
            continue
        stripped = line.lstrip()
        if not in_fence and (stripped.startswith("```") or stripped.startswith("~~~")):
            in_fence = True
            fence_marker = stripped[:3]
            continue
        if in_fence:
            if stripped.startswith(fence_marker):
                in_fence = False
            continue
        if QUOTED_RE.search(line):
            continue
        for pat in PATTERNS:
            if pat.search(line):
                hits.append((i, line.rstrip()[:100]))
                break
    return hits


def main() -> int:
    total = 0
    by_file: dict[str, list[tuple[int, str]]] = {}
    for f in sorted(glob.glob("content/**/*.md", recursive=True)):
        if "/medium/" in f:
            continue
        hits = scan(f)
        if hits:
            by_file[f] = hits
            total += len(hits)

    if total:
        print(f"FAIL: {total} translation-residue pronoun hit(s).", file=sys.stderr)
        for f, hits in by_file.items():
            for ln, txt in hits:
                print(f"  {f}:{ln}: {txt}", file=sys.stderr)
        return 1
    print("PASS: No translation-residue pronouns.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
