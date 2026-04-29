#!/usr/bin/env python3
"""One-shot Phase 6 mover: relocate <series>/ -> content/<series>/.

For each series passed as argv:
1. git mv <series> content/<series>
2. Rewrite ko/en image refs `../../assets/<series>/` -> `../../../assets/<series>/`
3. Update root series.yaml `path: <series>` -> `path: content/<series>`
4. Generate content/<series>/series.yaml from articles found in ko/

Caller is responsible for: running quality gates and committing per series.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def gen_series_yaml(series_id: str, root_entry: dict) -> str:
    series_dir = ROOT / "content" / series_id
    posts_dir = series_dir / "ko" if (series_dir / "ko").is_dir() else series_dir
    articles = []
    for md in sorted(posts_dir.glob("*.md")):
        m = re.match(r"^(\d+)", md.stem)
        if not m:
            continue
        articles.append({"idx": int(m.group(1)), "slug": md.stem, "status": "ready"})

    out = {
        "id": series_id,
        "category": root_entry["category"],
        "title": root_entry["title"],
        "description": root_entry["description"],
        "languages": root_entry.get("languages", ["ko"]),
        "targets": root_entry.get("targets", {}),
        "status": root_entry.get("status", "draft"),
        "articles": articles,
    }
    return yaml.safe_dump(out, allow_unicode=True, sort_keys=False)


def rewrite_image_paths(series_dir: Path, series_id: str) -> int:
    pat = re.compile(rf"\.\./\.\./assets/{re.escape(series_id)}/")
    repl = f"../../../assets/{series_id}/"
    count = 0
    for variant in ("ko", "en"):
        sub = series_dir / variant
        if not sub.is_dir():
            continue
        for md in sub.glob("*.md"):
            text = md.read_text(encoding="utf-8")
            new = pat.sub(repl, text)
            if new != text:
                md.write_text(new, encoding="utf-8")
                count += 1
    return count


def update_root_catalog(series_id: str) -> bool:
    catalog_path = ROOT / "series.yaml"
    text = catalog_path.read_text(encoding="utf-8")
    old = f"path: {series_id}"
    new = f"path: content/{series_id}"
    if old not in text:
        return False
    catalog_path.write_text(text.replace(old, new), encoding="utf-8")
    return True


def find_root_entry(series_id: str) -> dict | None:
    raw = yaml.safe_load((ROOT / "series.yaml").read_text(encoding="utf-8"))
    for s in raw.get("series", []):
        if s["id"] == series_id:
            return s
    return None


def move_series(series_id: str) -> None:
    src = ROOT / series_id
    dst = ROOT / "content" / series_id
    if not src.is_dir():
        print(f"  SKIP not found: {series_id}")
        return
    if dst.exists():
        print(f"  SKIP already moved: {series_id}")
        return

    (ROOT / "content").mkdir(exist_ok=True)
    subprocess.run(["git", "mv", series_id, f"content/{series_id}"], cwd=ROOT, check=True)

    rewrites = rewrite_image_paths(dst, series_id)
    catalog_updated = update_root_catalog(series_id)
    root_entry = find_root_entry(series_id)
    if root_entry is None:
        raise SystemExit(f"  ERROR: {series_id} not in root series.yaml")

    per_yaml = dst / "series.yaml"
    per_yaml.write_text(gen_series_yaml(series_id, root_entry), encoding="utf-8")

    print(f"  moved   {series_id}  (rewrites={rewrites}, root-catalog={catalog_updated})")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: phase6-move.py <series-id> [<series-id> ...]", file=sys.stderr)
        return 2
    for sid in argv[1:]:
        print(f"== {sid}")
        move_series(sid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
