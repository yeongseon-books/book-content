"""Export a single article to `exports/medium/<series>/<NN>.md`.

Status: skeleton. The current canonical Medium converter is
`.sisyphus/medium/to-medium.py`; this script will eventually wrap it.

Usage (target):
    python3 scripts/export_medium.py <series-id> --episode <N>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export an English article to Medium format.")
    parser.add_argument("series", help="series id, e.g. azure-functions-101")
    parser.add_argument("--episode", "-e", type=int, required=True, help="episode number (1-based)")
    parser.add_argument("--out", default=None, help="override output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f"export_medium: series={args.series} episode={args.episode}")
    print("TODO: invoke .sisyphus/medium/to-medium.py for now; later move logic here. "
          "Strip ebook-only, keep blog-only, demote H3+, bullet-table tables, commit-pinned URLs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
