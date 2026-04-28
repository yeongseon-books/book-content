"""Generate SERIES.md and mkdocs nav from series.yaml.

Status: skeleton. Will replace the hand-maintained tables in SERIES.md once
front matter is in place and per-series series.yaml episodes are populated.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"


def main() -> int:
    if not SERIES_YAML.exists():
        raise SystemExit(f"missing {SERIES_YAML}")
    with SERIES_YAML.open("r", encoding="utf-8") as f:
        catalog = yaml.safe_load(f) or {}
    series = catalog.get("series", [])
    print(f"build_series_index: {len(series)} series in catalog")
    for s in series:
        langs = ",".join(s.get("languages", []))
        print(f"  - {s['id']:<32} [{s.get('status'):<14}] languages={langs}")
    print("TODO: rewrite SERIES.md tables and emit mkdocs nav fragment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
