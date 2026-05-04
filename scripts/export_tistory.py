"""Export a Korean source post for Tistory paste-publishing.

Reads `content/<series>/ko/<NN>-<slug>.md` and writes to
`exports/tistory/<series>/<NN>-<slug>.md`.

Per PUBLISHING.md (Tistory column):
- strip YAML front matter (Tistory has its own meta fields)
- keep blog-only blocks (markers stripped, body kept)
- strip ebook-only blocks
- keep TOC and series nav (visible to readers)
- keep visible bottom `Tags: A, B, C, D` line — this is the copy-paste source
  for Tistory's tag input field

Image handling:
- By default, local image paths are rewritten to public GitHub Pages URLs
  using series.yaml meta.asset_base_url.
- With --local-assets, relative `../../../assets/...` paths are kept unchanged
  for interactive Tistory upload.

Usage:
    python3 scripts/export_tistory.py <series-id> --episode N
    python3 scripts/export_tistory.py <series-id> --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = REPO_ROOT / "exports" / "tistory"
SERIES_YAML = REPO_ROOT / "series.yaml"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _transform import append_copyright, rewrite_public_asset_urls, transform_for_tistory


def _load_meta() -> dict:
    """Read meta block from series.yaml."""
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    return catalog.get("meta") or {}


def _load_asset_base_url() -> str:
    """Read asset_base_url from series.yaml meta block."""
    meta = _load_meta()
    url = meta.get("asset_base_url", "")
    if not url:
        raise SystemExit("series.yaml meta.asset_base_url is required for public asset export.")
    return url


def load_series(series_id: str) -> dict:
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))["series"]
    for s in catalog:
        if s["id"] == series_id:
            return s
    raise SystemExit(f"unknown series: {series_id}")


def find_article(series_dir: Path, episode: int) -> Path:
    matches = sorted(series_dir.glob(f"{episode:02d}-*.md"))
    if not matches:
        raise SystemExit(f"no article found for episode {episode} in {series_dir}")
    return matches[0]


def export_one(src: Path, dst: Path, *, local_assets: bool = False) -> None:
    text = src.read_text(encoding="utf-8")
    out = transform_for_tistory(text)
    if not local_assets:
        out = rewrite_public_asset_urls(out, _load_asset_base_url())
    meta = _load_meta()
    out = append_copyright(
        out,
        meta.get("copyright_holder", "YeongseonBooks"),
        meta.get("copyright_year", "2026"),
        meta.get("license", "all-rights-reserved"),
        visible=True,
        lang="ko",
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("series", help="series id, e.g. azure-functions-101")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--episode", "-e", type=int, help="episode number (1-based)")
    g.add_argument("--all", action="store_true", help="export every episode in the series")
    ap.add_argument("--local-assets", action="store_true",
                    help="keep relative image paths instead of rewriting to public URLs")
    args = ap.parse_args()

    s = load_series(args.series)
    if not s.get("targets", {}).get("tistory"):
        raise SystemExit(f"series {args.series} does not target tistory (targets.tistory=false)")
    if "ko" not in s.get("languages", []):
        raise SystemExit(f"series {args.series} has no ko/ language")
    series_ko = REPO_ROOT / s["path"] / "ko"
    series_out = EXPORT_DIR / args.series

    if args.all:
        sources = sorted(series_ko.glob("*.md"))
    else:
        sources = [find_article(series_ko, args.episode)]

    for src in sources:
        dst = series_out / src.name
        export_one(src, dst, local_assets=args.local_assets)
        print(f"wrote {dst.relative_to(REPO_ROOT)}")
    print(f"\ntotal: {len(sources)} file(s) -> {series_out.relative_to(REPO_ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
