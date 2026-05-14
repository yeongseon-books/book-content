"""Lint seo_description quality across all articles.

Rules (FAIL):
- contains a URL (http:// or https://)
- contains a markdown link `[text](url)` or image `![alt](url)`
- contains a newline
- equals or starts with a generic boilerplate "예제 코드:" / "Code:" line only

Rules (WARN):
- ko length < 40 NFC code-points
- en length < 70 NFC code-points

Exit code: 0 if no failures, 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
LANG_DIRS = {"ko", "en"}

URL_RE = re.compile(r"https?://", re.IGNORECASE)
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\([^)]+\)")
BOILERPLATE_RE = re.compile(
    r"^\s*(예제 코드|코드|Code|Example code)\s*[:：]?\s*$", re.IGNORECASE
)

MIN_LEN = {"ko": 40, "en": 70}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint seo_description quality")
    _ = parser.add_argument("--series", help="check only one series id")
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


def check_article(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        post = frontmatter.loads(text)
    except Exception as e:
        return [f"front matter parse error: {e}"], []

    fm = post.metadata
    desc = fm.get("seo_description")
    if desc is None:
        return [], []
    if not isinstance(desc, str):
        return [f"seo_description must be string, got {type(desc).__name__}"], []

    norm = unicodedata.normalize("NFC", desc)

    if URL_RE.search(norm):
        errors.append(
            "seo_description contains a URL (http/https). Describe the article instead."
        )
    if MD_LINK_RE.search(norm):
        errors.append(
            "seo_description contains markdown link/image syntax. Use plain prose."
        )
    if "\n" in desc or "\r" in desc:
        errors.append("seo_description contains a newline. Must be a single line.")
    if BOILERPLATE_RE.match(norm):
        errors.append(
            "seo_description is a generic boilerplate ('예제 코드:' / 'Code:'). Write a substantive summary."
        )

    language = fm.get("language")
    if isinstance(language, str):
        limit = MIN_LEN.get(language)
        if limit and len(norm) < limit:
            warnings.append(
                f"seo_description is short for {language}: {len(norm)} < {limit} NFC code-points"
            )

    return errors, warnings


def main() -> int:
    args = parse_args()
    series = args.series
    if not CONTENT_DIR.is_dir():
        print(f"missing content directory: {CONTENT_DIR}", file=sys.stderr)
        return 1

    articles = iter_articles(series)
    failures = 0
    warned = 0
    checked = 0
    for md in articles:
        if md.parent.name not in LANG_DIRS:
            continue
        checked += 1
        errs, warns = check_article(md)
        if errs or warns:
            rel = md.relative_to(REPO_ROOT)
            if errs:
                failures += 1
                print(f"FAIL {rel}")
                for e in errs:
                    print(f"  - {e}")
            if warns:
                warned += 1
                if not errs:
                    print(f"WARN {rel}")
                for w in warns:
                    print(f"  - [warning] {w}")

    print(f"\nchecked: {checked}, failures: {failures}, warnings: {warned}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
