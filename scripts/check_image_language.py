"""Lint image language suffix mismatches.

Rule (WARN): an image referenced from content/<series>/ko/*.md should not use
a `.en.png|.en.jpg|.en.jpeg|.en.svg|.en.webp` suffix, and vice versa.

Detection: scan markdown image references `![alt](path)` outside fenced code blocks.

Exit code: always 0 (warnings only) unless --strict is given.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
LANG_DIRS = {"ko", "en"}

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
SUFFIX_RE = re.compile(r"\.(ko|en)\.(png|jpg|jpeg|svg|webp|gif)$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint KO/EN image suffix mismatches")
    _ = parser.add_argument("--series", help="check only one series id")
    _ = parser.add_argument(
        "--strict", action="store_true", help="exit 1 on any warning"
    )
    return parser.parse_args()


def iter_articles(series: str | None) -> list[Path]:
    if series:
        roots = [CONTENT_DIR / series]
    else:
        roots = [p for p in sorted(CONTENT_DIR.iterdir()) if p.is_dir()]
    items: list[Path] = []
    for root in roots:
        for lang in LANG_DIRS:
            d = root / lang
            if d.is_dir():
                items.extend(sorted(d.glob("*.md")))
    return items


def check_article(path: Path) -> list[str]:
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        post = frontmatter.loads(text)
    except Exception as e:
        return [f"front matter parse error: {e}"]

    fm = post.metadata
    language = fm.get("language") or path.parent.name
    if language not in LANG_DIRS:
        return []
    other = "en" if language == "ko" else "ko"

    in_fence = False
    for line_no, line in enumerate(post.content.splitlines(), start=1):
        if FENCE_RE.match(line.lstrip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in IMAGE_RE.finditer(line):
            url = m.group(1).strip()
            sm = SUFFIX_RE.search(url)
            if sm and sm.group(1).lower() == other:
                warnings.append(
                    f"line {line_no}: image '{url}' uses .{other}. suffix in {language} article"
                )
    return warnings


def main() -> int:
    args = parse_args()
    if not CONTENT_DIR.is_dir():
        print(f"missing content directory: {CONTENT_DIR}", file=sys.stderr)
        return 1
    articles = iter_articles(args.series)
    warned = 0
    checked = 0
    for md in articles:
        if md.parent.name not in LANG_DIRS:
            continue
        checked += 1
        warns = check_article(md)
        if warns:
            warned += 1
            rel = md.relative_to(REPO_ROOT)
            print(f"WARN {rel}")
            for w in warns:
                print(f"  - {w}")
    print(f"\nchecked: {checked}, warnings: {warned}")
    return 1 if (args.strict and warned) else 0


if __name__ == "__main__":
    sys.exit(main())
