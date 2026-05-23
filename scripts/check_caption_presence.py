#!/usr/bin/env python3
"""Guard: every standalone non-badge image must be followed by an italic caption.

Pattern enforced:
    ![alt](url)

    *caption*

Skips:
- Inline images (image not on its own line)
- Code/text fences (``` and ~~~)
- Badge URLs (shields.io, codecov.io, /badge/, /badges/, badgen.net)

Exit 1 on any violation. Intended for `make check`.

See AGENTS.md image caption policy + STYLE_GUIDE.md §캡션 정책.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

IMG_RE = re.compile(r"^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$")
CAPTION_RE = re.compile(r"^\s*\*[^*]+\*\s*$")
BADGE_HINTS = (
    "shields.io",
    "badge.svg",
    "codecov.io",
    "badgen.net",
    "img.shields.io",
    "github.com/badges",
    "/badge",
    "/badges/",
    "pepy.tech",
    "badge.fury.io",
)


def is_badge(url: str) -> bool:
    return any(h in url for h in BADGE_HINTS)


def check_file(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    violations: list[tuple[int, str]] = []
    in_fence = False
    fence = ""
    for i, line in enumerate(lines):
        s = line.lstrip()
        if not in_fence and (s.startswith("```") or s.startswith("~~~")):
            in_fence = True
            fence = s[:3]
            continue
        if in_fence:
            if s.startswith(fence):
                in_fence = False
            continue
        m = IMG_RE.match(line)
        if not m:
            continue
        alt = m.group(1).strip()
        url = m.group(2).strip()
        if is_badge(url):
            continue
        if not alt:
            # Empty alt is a separate concern; not enforced here.
            continue
        # Look for caption on next non-blank line (within 3 lines)
        has_caption = False
        for j in range(i + 1, min(i + 4, len(lines))):
            nxt = lines[j].strip()
            if not nxt:
                continue
            if CAPTION_RE.match(nxt):
                has_caption = True
            break
        if not has_caption:
            violations.append((i + 1, alt[:60]))
    return violations


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for fp in sorted((ROOT / "content").rglob("*.md")):
        if "/medium/" in str(fp):
            continue
        files.append(fp)
    return files


def main() -> int:
    files = iter_markdown_files()
    total_violations = 0
    affected_files = 0
    for fp in files:
        vs = check_file(fp)
        if not vs:
            continue
        affected_files += 1
        total_violations += len(vs)
        rel = fp.relative_to(ROOT)
        for ln, alt in vs:
            print(f"  {rel}:{ln}: ![{alt}] missing *caption* on next line")

    if total_violations == 0:
        print(f"OK: every standalone image has an italic caption ({len(files)} files)")
        return 0

    print()
    print(
        f"FAIL: {total_violations} images missing italic captions across "
        f"{affected_files} files"
    )
    print(
        "Fix: add a blank line, then '*<caption>*', then a blank line right after "
        "each '![alt](url)' that is not a badge."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
