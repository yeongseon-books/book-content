"""Export a series as an eBook source bundle for the private mkdocs-ebook builder.

Status: skeleton. Output goes to `exports/ebook-source/<series>-<lang>/`.

Usage (target):
    python3 scripts/export_ebook_source.py <series-id> --lang <ko|en>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_ROOT = REPO_ROOT / "exports" / "ebook-source"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a series as an eBook source bundle.")
    parser.add_argument("series", help="series id, e.g. azure-functions-101")
    parser.add_argument("--lang", choices=["ko", "en"], required=True, help="language variant")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_dir = EXPORT_ROOT / f"{args.series}-{args.lang}"
    print(f"export_ebook_source: series={args.series} lang={args.lang}")
    print(f"target bundle: {bundle_dir}")
    print("TODO: copy chapters in series.yaml episode order, strip blog-only blocks, "
          "keep ebook-only, drop visible Tags + TOC, copy assets, render mkdocs.yml + preface.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
