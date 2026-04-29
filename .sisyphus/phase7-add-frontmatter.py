"""Bulk-insert YAML front matter into every content/<series>/{ko,en}/*.md.

Source of truth:
- content/<series>/series.yaml: per-article status, slug, idx
- root series.yaml: series-level title, languages, targets, tags

Idempotent: if a file already starts with `---`, it is skipped (re-run safe).

Title source: the article's H1 line (first `# ` heading) is used as `title:`.
This keeps front matter aligned with the visible H1 — single source of truth.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
SERIES_YAML = REPO_ROOT / "series.yaml"
TODAY = "2026-04-29"


def first_h1(text: str) -> str | None:
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return m.group(1)
    return None


def build_frontmatter(*, title: str, series: str, episode: int, language: str,
                      status: str, targets: dict, tags: list[str]) -> str:
    fm = {
        "title": title,
        "series": series,
        "episode": episode,
        "language": language,
        "status": status,
        "targets": targets,
        "tags": tags,
        "last_reviewed": TODAY,
    }
    body = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return f"---\n{body}---\n\n"


def process_series(series_meta: dict, per_series_yaml: Path) -> tuple[int, int]:
    sid = series_meta["id"]
    series_dir = REPO_ROOT / series_meta["path"]
    languages = series_meta.get("languages", [])
    targets = series_meta.get("targets", {})
    per = yaml.safe_load(per_series_yaml.read_text(encoding="utf-8"))
    tags = per.get("tags") or series_meta.get("tags", [])
    article_status = {a["idx"]: a["status"] for a in per.get("articles", [])}

    written = 0
    skipped = 0
    for lang in languages:
        if lang not in {"ko", "en"}:
            continue
        lang_dir = series_dir / lang
        if not lang_dir.is_dir():
            continue
        for md in sorted(lang_dir.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            if text.startswith("---\n"):
                skipped += 1
                continue
            m = re.match(r"^(\d+)", md.stem)
            if not m:
                print(f"  SKIP no idx prefix: {md.relative_to(REPO_ROOT)}")
                skipped += 1
                continue
            idx = int(m.group(1))
            title = first_h1(text)
            if not title:
                print(f"  SKIP no H1: {md.relative_to(REPO_ROOT)}")
                skipped += 1
                continue
            status = article_status.get(idx, "draft")
            fm_block = build_frontmatter(
                title=title, series=sid, episode=idx, language=lang,
                status=status, targets=targets, tags=tags,
            )
            md.write_text(fm_block + text, encoding="utf-8")
            written += 1
    return written, skipped


def main() -> int:
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    total_w = total_s = 0
    for s in catalog["series"]:
        per = REPO_ROOT / s["path"] / "series.yaml"
        if not per.is_file():
            print(f"skip {s['id']} (no per-series series.yaml)")
            continue
        w, sk = process_series(s, per)
        total_w += w
        total_s += sk
        print(f"{s['id']}: wrote={w} skipped={sk}")
    print(f"\nTOTAL: wrote={total_w} skipped={total_s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
