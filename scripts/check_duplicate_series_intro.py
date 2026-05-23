#!/usr/bin/env python3
"""Guard: detect duplicate series-intro lines in ko/en article bodies.

A series-intro line matches the pattern '이 글은 ... 시리즈의 N번째 글입니다' (ko)
or 'This is the Nth article in the ... series' (en). Each article must contain
at most ONE such line. Multiple lines are typically a copy-paste leftover from
template generation (a short stub line + an enriched line both survived).

Skips code fences and front matter.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

KO_PAT = re.compile(r"이 글은 [^\n]{1,120}시리즈의 [^\n]{1,15}글입니다")
EN_PAT = re.compile(
    r"This is the [^\n]{1,40} (?:article|post) in the [^\n]{1,80} series",
    re.IGNORECASE,
)


def body_without_fences(text: str) -> str:
    """Strip front matter and fenced code blocks."""
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    out: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    body = body_without_fences(text)
    pat = KO_PAT if path.parent.name == "ko" else EN_PAT
    matches = pat.findall(body)
    if len(matches) >= 2:
        return [f"{path}: {len(matches)} series-intro lines (expected 1)"]
    return []


def main() -> int:
    errors: list[str] = []
    for md in sorted(CONTENT.glob("*/ko/*.md")) + sorted(CONTENT.glob("*/en/*.md")):
        errors.extend(check_file(md))
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print(f"\n{len(errors)} files with duplicate series-intro lines", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
