"""Verify series.yaml catalog consistency.

Checks:
- path field starts with content/
- path directory exists on disk (for non-planned series)
- languages listed match subdirectories present
- targets.medium=true requires an en language
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"


def main() -> int:
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    errors: list[str] = []

    for s in catalog["series"]:
        sid = s["id"]
        path_str: str = s.get("path", "")
        status: str = s.get("status", "planned")
        languages: list[str] = s.get("languages", [])
        targets: dict = s.get("targets", {})

        if not path_str.startswith("content/"):
            errors.append(f"{sid}: path must start with 'content/' — got '{path_str}'")
            continue

        series_path = REPO_ROOT / path_str

        if status != "planned" and not series_path.is_dir():
            errors.append(f"{sid}: path '{path_str}' does not exist (status={status})")
            continue

        if series_path.is_dir():
            for lang in languages:
                lang_dir = series_path / lang
                if not lang_dir.is_dir():
                    errors.append(f"{sid}: language '{lang}' listed but '{path_str}/{lang}/' missing")

        if targets.get("medium") and "en" not in languages:
            errors.append(f"{sid}: targets.medium=true but 'en' not in languages")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(catalog['series'])} series validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
