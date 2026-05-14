"""Verify status sync between content/<series>/series.yaml and article front matter.

For every entry in content/<series>/series.yaml.articles[] with a `status:`,
check that content/<series>/{ko,en}/<slug>.md front matter has the same status.

Exit code: 0 on success, 1 on any drift.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import frontmatter
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
LANG_DIRS = ("ko", "en")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check series.yaml ↔ article status sync"
    )
    _ = parser.add_argument("--series", help="check only one series id")
    return parser.parse_args()


def iter_series(series: str | None) -> list[Path]:
    if series:
        p = CONTENT_DIR / series / "series.yaml"
        return [p] if p.is_file() else []
    return sorted(CONTENT_DIR.glob("*/series.yaml"))


def check_series(series_yaml: Path) -> list[str]:
    errors: list[str] = []
    raw = yaml.safe_load(series_yaml.read_text(encoding="utf-8")) or {}
    series_id = raw.get("id") or series_yaml.parent.name
    articles = raw.get("articles") or []
    series_dir = series_yaml.parent

    for entry in articles:
        if not isinstance(entry, dict):
            continue
        slug = entry.get("slug")
        catalog_status = entry.get("status")
        if not slug or not catalog_status:
            continue
        for lang in LANG_DIRS:
            md = series_dir / lang / f"{slug}.md"
            if not md.is_file():
                continue
            try:
                post = frontmatter.loads(md.read_text(encoding="utf-8"))
            except Exception as e:
                errors.append(f"{lang}/{slug}.md: front matter parse error: {e}")
                continue
            article_status = post.metadata.get("status")
            if article_status != catalog_status:
                errors.append(
                    f"{lang}/{slug}.md: status drift "
                    f"(series.yaml={catalog_status!r}, article={article_status!r})"
                )
    return errors


def main() -> int:
    args = parse_args()
    if not CONTENT_DIR.is_dir():
        print(f"missing content directory: {CONTENT_DIR}", file=sys.stderr)
        return 1
    series_files = iter_series(args.series)
    failures = 0
    checked = 0
    for sy in series_files:
        checked += 1
        errs = check_series(sy)
        if errs:
            failures += 1
            print(f"FAIL {sy.relative_to(REPO_ROOT)}")
            for e in errs:
                print(f"  - {e}")
    print(f"\nchecked: {checked} series, failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
