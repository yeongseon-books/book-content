"""Build MkDocs `docs/` from `content/`.

Status: skeleton. The actual content/ directory is empty until Phase 6 file moves.

Scope: this script materializes content -> docs files only. It does NOT touch
mkdocs.yml `nav`; nav generation is owned by scripts/build_series_index.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
DOCS_DIR = REPO_ROOT / "docs"
SERIES_YAML = REPO_ROOT / "series.yaml"


def load_series_catalog() -> list[dict]:
    if not SERIES_YAML.exists():
        raise SystemExit(f"missing series catalog: {SERIES_YAML}")
    with SERIES_YAML.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return list(data.get("series", []))


def main() -> int:
    catalog = load_series_catalog()
    print(f"loaded {len(catalog)} series from {SERIES_YAML.name}")

    if not CONTENT_DIR.exists() or not any(CONTENT_DIR.iterdir()):
        print("content/ is empty (Phase 6 not started). Nothing to build.")
        return 0

    print("TODO: implement content/ -> docs/ conversion (Phase 4 follow-up).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
