"""Lint article-level targets that misalign with file language.

Per PUBLISHING.md mapping:
  - Tistory  <- content/<series>/ko/*.md
  - Hashnode <- content/<series>/en/*.md
  - Medium   <- content/<series>/en/*.md (adaptation)

So semantically:
  - ko/*.md  should NOT have targets.hashnode = true (Hashnode never publishes ko)
  - ko/*.md  should NOT have targets.medium   = true (Medium never publishes ko)
  - en/*.md  should NOT have targets.tistory  = true (Tistory never publishes en)

This is metadata-correctness only. Exporters gate on series-level
`series.yaml > targets`, not on article frontmatter, so misalignment
does not break publishing. But it misleads readers of the metadata.

Exit code: always 0 (warnings only) unless --strict is given.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
LANG_DIRS = {"ko", "en"}

KO_FORBIDDEN = ("hashnode", "medium")
EN_FORBIDDEN = ("tistory",)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint article targets vs. language alignment"
    )
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
    try:
        post = frontmatter.load(path)
    except Exception as e:
        return [f"front matter parse error: {e}"]
    fm = post.metadata
    targets = fm.get("targets") or {}
    if not isinstance(targets, dict):
        return []
    lang = fm.get("language") or path.parent.name
    if lang not in LANG_DIRS:
        return []
    forbidden = KO_FORBIDDEN if lang == "ko" else EN_FORBIDDEN
    warnings: list[str] = []
    for key in forbidden:
        if targets.get(key) is True:
            warnings.append(f"targets.{key}=true is meaningless in a {lang}/ article")
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
