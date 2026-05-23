#!/usr/bin/env python3
"""Guard: no '다음 글' / 'next post' forward-reference in article intro section.

AGENTS.md Question Loop Body Standard §2:
  "도입부에 다음 글 링크는 넣지 않는다."

Forward references create coupling: when a series is reordered, every "next post"
mention has to be edited. The narrative bridge belongs in TOC and series structure,
not prose.

Scope: from H1 to either the first '## 먼저 던지는 질문' / '## Questions to Keep in Mind'
or the first '## ' heading, whichever comes first.

Refs: #1249
"""
from __future__ import annotations

import glob
import re
import sys

KO_PHRASES = ("다음 글", "다음 글에서", "다음 글의", "다음 글로", "다음 화")
EN_PHRASES = ("next post", "next article", "next chapter", "the next post")


def intro_lines(path: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    in_frontmatter = False
    after_h1 = False
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
            if line.startswith("# ") and not after_h1:
                after_h1 = True
                continue
            if not after_h1:
                continue
            if line.startswith("## "):
                break
            lines.append((idx, line))
    return lines


def main() -> int:
    failures: list[str] = []
    for path in sorted(glob.glob("content/*/ko/*.md")):
        for idx, line in intro_lines(path):
            stripped = line.strip()
            if any(p in stripped for p in KO_PHRASES):
                failures.append(f"{path}:{idx}: {stripped[:140]}")
    for path in sorted(glob.glob("content/*/en/*.md")):
        for idx, line in intro_lines(path):
            low = line.lower()
            if any(p in low for p in EN_PHRASES):
                failures.append(f"{path}:{idx}: {line.strip()[:140]}")

    if failures:
        print("FAIL: intro section contains forward-reference to next post.", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(f"\nTotal: {len(failures)} occurrence(s).", file=sys.stderr)
        return 1

    print("PASS: No '다음 글' / 'next post' forward-references in intro sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
