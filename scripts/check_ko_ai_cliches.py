#!/usr/bin/env python3
"""Guard: forbid common Korean AI-prose cliches in canonical sources.

Reasons:
  - These openers signal LLM-generated summary boilerplate
  - They add no information; the following sentence carries the meaning
  - Once removed, the prose reads as a senior engineer's voice

Skips:
  - YAML frontmatter (between leading --- lines)
  - Fenced code blocks (``` and ~~~)
  - Indented code blocks (4+ space indent following a blank line)

Refs: #1231 (결론적으로 batch), #1230 (translation residue)
"""
from __future__ import annotations

import glob
import re
import sys

# Phrases that almost always indicate AI-summary boilerplate when used as
# a sentence opener (start of line or after typical opener punctuation).
# Anchored to start-of-line + optional leading spaces to avoid false
# positives inside quoted sentences.
PATTERNS = [
    re.compile(r"^\s{0,3}결론적으로\b"),
    re.compile(r"^\s{0,3}요컨대\b"),
    re.compile(r"^\s{0,3}다시 한번 강조"),
    re.compile(r"^\s{0,3}간단히 말해"),
    re.compile(r"^\s{0,3}쉽게 말해"),
    re.compile(r"살펴보겠습니다"),
    re.compile(r"흥미롭게도"),
    re.compile(r"다음과 같습니다[:：]\s*$"),
]


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
        for pat in PATTERNS:
            if pat.search(line):
                hits.append((i, line.rstrip()[:100]))
                break
    return hits


def main() -> int:
    total = 0
    by_file: dict[str, list[tuple[int, str]]] = {}
    for f in sorted(glob.glob("content/**/ko/*.md", recursive=True)):
        if "/medium/" in f:
            continue
        hits = scan(f)
        if hits:
            by_file[f] = hits
            total += len(hits)

    if total:
        print(f"FAIL: {total} Korean AI-prose cliche hit(s).", file=sys.stderr)
        for f, hits in by_file.items():
            for ln, txt in hits:
                print(f"  {f}:{ln}: {txt}", file=sys.stderr)
        return 1
    print("PASS: No Korean AI-prose cliches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
