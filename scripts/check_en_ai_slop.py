#!/usr/bin/env python3
"""Guard: AI slop / sycophantic openers in en/*.md prose.

Catches the senior-engineer-voice violations from issue #1243.

Skips:
- YAML front matter
- Fenced code blocks (``` ... ```)
- Indented (4-space) blocks - these are typically quoted LLM output / sample answers
- Table rows (lines starting with `|`) - "Excellent" can appear as a rating cell

Patterns are word-boundary anchored where it matters; "Excellent" only fires
when it opens a sentence (start of line or after `. ` / `! ` / `? `).

Refs: #1243
"""
from __future__ import annotations

import glob
import re
import sys

# Phrase -> (regex, description)
SLOP_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bLet's explore\b", re.IGNORECASE), "AI slop: 'Let's explore' (use 'This section covers' / 'We examine')"),
    (re.compile(r"(?:^|[.!?]\s+)In summary,", re.MULTILINE), "AI slop: 'In summary,' opener (drop the phrase)"),
    (re.compile(r"(?:^|[.!?]\s+)Excellent\b", re.MULTILINE), "Sycophantic opener: 'Excellent' (drop adjective)"),
    (re.compile(r"\bdive (?:deep|deeper) into\b", re.IGNORECASE), "AI slop: 'dive deep into'"),
    (re.compile(r"\bdelve into\b", re.IGNORECASE), "AI slop: 'delve into'"),
    (re.compile(r"\bIt's worth noting that\b", re.IGNORECASE), "AI slop: 'It's worth noting that'"),
]


def filtered_lines(path: str) -> list[tuple[int, str]]:
    """Return (line_no, line) tuples for prose lines only."""
    kept: list[tuple[int, str]] = []
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
            stripped_marker = line.lstrip()
            if stripped_marker.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            # 4-space indented blocks (treated as quoted output)
            if line.startswith("    ") and stripped_marker:
                continue
            # Table rows
            if line.lstrip().startswith("|"):
                continue
            kept.append((idx, line))
    return kept


def scan(path: str) -> list[str]:
    hits: list[str] = []
    for line_no, line in filtered_lines(path):
        for pat, desc in SLOP_PATTERNS:
            if pat.search(line):
                hits.append(f"{path}:{line_no}: {desc} — {line.strip()[:120]}")
    return hits


def main() -> int:
    failures: list[str] = []
    for path in sorted(glob.glob("content/*/en/*.md")):
        failures.extend(scan(path))

    if failures:
        print("FAIL: AI slop / sycophantic openers in en/ prose.", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(f"\nTotal: {len(failures)} occurrence(s).", file=sys.stderr)
        return 1

    print("PASS: No AI slop in en/ prose.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
