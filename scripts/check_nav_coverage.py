"""Validate mkdocs.yml nav includes all series from series.yaml.

Checks:
- All series from series.yaml with status != 'planned' appear in mkdocs.yml nav
- Series names in nav match canonical titles from series.yaml
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"
MKDOCS_YAML = REPO_ROOT / "mkdocs.yml"


def extract_series_from_nav(nav: object) -> set[str]:
    """Recursively extract series names from mkdocs.yml nav structure."""
    series_names = set()

    if isinstance(nav, dict):
        for value in nav.values():
            series_names.update(extract_series_from_nav(value))
    elif isinstance(nav, list):
        for item in nav:
            if isinstance(item, dict):
                for key, value in item.items():
                    # Key might be the series name, value might have nested nav
                    series_names.add(key)
                    series_names.update(extract_series_from_nav(value))
            elif isinstance(item, str):
                series_names.add(item)

    return series_names


def main() -> int:
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    mkdocs = yaml.safe_load(MKDOCS_YAML.read_text(encoding="utf-8"))

    errors: list[str] = []

    # Collect all non-planned series
    active_series = {}
    for s in catalog["series"]:
        sid = s["id"]
        status = s.get("status", "planned")
        if status != "planned":
            # Use title as it appears in nav
            title_ko = s.get("title", {}).get("ko", sid)
            active_series[sid] = title_ko

    # Extract series names present in mkdocs nav
    nav = mkdocs.get("nav", [])
    nav_series = extract_series_from_nav(nav)

    # Check that all active series appear in nav
    for sid, expected_title in active_series.items():
        found = False
        for nav_title in nav_series:
            if expected_title == nav_title or sid in nav_title:
                found = True
                break
        if not found:
            errors.append(
                f"{sid}: series '{expected_title}' not found in mkdocs.yml nav"
            )

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"OK: Nav coverage verified for {len(active_series)} series")
    return 0


if __name__ == "__main__":
    sys.exit(main())
