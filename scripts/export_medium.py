"""Export an English post to Medium import-ready Markdown.

Thin wrapper around `.sisyphus/medium/to-medium.py`, which already produces
the canonical Medium artifact at `content/<series>/medium/<NN>.md` with:
- raw.githubusercontent.com asset URLs (commit-pinned via TAG)
- bullet-list tables (Medium import quirk)
- demoted H3+ as bold paragraphs (Medium import quirk)
- TOC marker comments stripped
- bottom Tags line surfaced as leading <!-- Tags: ... --> HTML comment

This wrapper:
1. Runs `to-medium.py` to (re)generate `content/<series>/medium/`
2. Copies the requested file(s) to `exports/medium/<series>/<NN>.md`

The exports/ copy is what the human uploads to Medium's import URL.

Usage:
    python3 scripts/export_medium.py <series-id> --episode N
    python3 scripts/export_medium.py <series-id> --all
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = REPO_ROOT / "exports" / "medium"
SERIES_YAML = REPO_ROOT / "series.yaml"
TO_MEDIUM = REPO_ROOT / ".sisyphus" / "medium" / "to-medium.py"


def load_series(series_id: str) -> dict:
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))["series"]
    for s in catalog:
        if s["id"] == series_id:
            return s
    raise SystemExit(f"unknown series: {series_id}")


def regenerate_medium(series_path: Path) -> None:
    en_dir = series_path / "en"
    if not en_dir.is_dir():
        raise SystemExit(f"no en/ directory under {series_path}")
    subprocess.run(
        [sys.executable, str(TO_MEDIUM), str(en_dir.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT, check=True,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("series", help="series id, e.g. azure-functions-101")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--episode", "-e", type=int, help="episode number (1-based)")
    g.add_argument("--all", action="store_true", help="export every episode in the series")
    ap.add_argument("--skip-regen", action="store_true",
                    help="don't re-run to-medium.py; copy whatever is in content/<series>/medium/")
    args = ap.parse_args()

    s = load_series(args.series)
    targets = s.get("targets", {})
    if not targets.get("medium"):
        raise SystemExit(f"series {args.series} does not target medium (targets.medium=false)")
    if "en" not in s.get("languages", []):
        raise SystemExit(f"series {args.series} has no en/ language; medium export requires en")

    series_path = REPO_ROOT / s["path"]
    medium_dir = series_path / "medium"
    if not args.skip_regen:
        regenerate_medium(series_path)

    series_out = EXPORT_DIR / args.series
    series_out.mkdir(parents=True, exist_ok=True)

    if args.all:
        sources = sorted(medium_dir.glob("*.md"))
    else:
        src = medium_dir / f"{args.episode:02d}.md"
        if not src.is_file():
            raise SystemExit(f"missing {src}; run without --skip-regen?")
        sources = [src]

    for src in sources:
        dst = series_out / src.name
        shutil.copyfile(src, dst)
        print(f"wrote {dst.relative_to(REPO_ROOT)}")
    print(f"\ntotal: {len(sources)} file(s) -> {series_out.relative_to(REPO_ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
