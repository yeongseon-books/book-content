"""Export a single article to `exports/tistory/<series>/<NN>-<slug>.md`.

Status: skeleton. Real conversion logic lands in Phase 5 follow-up.

Usage (target):
    python3 scripts/export_tistory.py <series-id> --episode <N>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a Korean article to Tistory format.")
    parser.add_argument("series", help="series id, e.g. azure-functions-101")
    parser.add_argument("--episode", "-e", type=int, required=True, help="episode number (1-based)")
    parser.add_argument("--out", default=None, help="override output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f"export_tistory: series={args.series} episode={args.episode}")
    print("TODO: read content/<series>/ko/<NN>-*.md, strip ebook-only blocks, "
          "keep blog-only and visible Tags line, write to exports/tistory/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
