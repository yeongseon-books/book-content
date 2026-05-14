"""Verify status sync between content/<series>/series.yaml and article front matter.

Convention: an episode's catalog-level status equals the FLOOR of its language
statuses. So if ko=publish-ready and en=content-ready, series.yaml must say
content-ready. Drift = series.yaml.status != floor(article statuses).

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

STATUS_ORDER = {
    "draft": 0,
    "needs-update": 0,
    "content-ready": 1,
    "publish-ready": 2,
    "ready": 2,
    "published": 3,
}


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
    articles = raw.get("articles") or []
    series_dir = series_yaml.parent

    for entry in articles:
        if not isinstance(entry, dict):
            continue
        slug = entry.get("slug")
        catalog_status = entry.get("status")
        if not slug or not catalog_status:
            continue
        lang_statuses: dict[str, str] = {}
        for lang in LANG_DIRS:
            md = series_dir / lang / f"{slug}.md"
            if not md.is_file():
                continue
            try:
                post = frontmatter.loads(md.read_text(encoding="utf-8"))
            except Exception as e:
                errors.append(f"{lang}/{slug}.md: front matter parse error: {e}")
                continue
            s = post.metadata.get("status")
            if s:
                lang_statuses[lang] = s
        if not lang_statuses:
            continue
        floor = min(lang_statuses.values(), key=lambda s: STATUS_ORDER.get(s, -1))
        if catalog_status != floor:
            langs_str = ", ".join(
                f"{k}={v!r}" for k, v in sorted(lang_statuses.items())
            )
            errors.append(
                f"{slug}: status drift "
                f"(series.yaml={catalog_status!r}, floor={floor!r}, langs: {langs_str})"
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
