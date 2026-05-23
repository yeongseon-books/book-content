#!/usr/bin/env python3
"""Guard: detect known Korean typos that have appeared in past audit fixes.

Each entry is `(typo, correct)` where `typo` is the regex-safe exact substring
that must not appear in any `content/*/ko/*.md` body (excluding front matter
and fenced code blocks).

When a new typo is discovered during review, add it here AFTER fixing it
in-place so the same misspelling cannot regress silently. This guard pairs
with `.sisyphus/style/check-ko.sh` (which only catches translation-smell
patterns, not orthography).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

TYPOS: tuple[tuple[str, str], ...] = (
    ("풀부합니다", "풍부합니다"),
    ("쉬습니다", "쉽습니다"),
    ("버튼 수 있게", "버틸 수 있게"),
    ("나눥니다", "나뉩니다"),
    ("줘인다", "줄인다"),
    ("만든는가", "만드는가"),
    ("나몘늾답닝니다", "(garbage insertion - delete block)"),
)


def body_without_fences(text: str) -> str:
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


def main() -> int:
    errors: list[str] = []
    for md in sorted(CONTENT.glob("*/ko/*.md")):
        if "azure-app-service-101" in str(md):
            continue
        body = body_without_fences(md.read_text(encoding="utf-8"))
        for typo, correct in TYPOS:
            if typo in body:
                errors.append(f"{md}: typo {typo!r} -> {correct!r}")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print(f"\n{len(errors)} typos found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
