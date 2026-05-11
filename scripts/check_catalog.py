"""Verify series.yaml catalog consistency.

Checks:
- path field starts with content/
- path directory exists on disk (for non-planned series)
- languages listed match subdirectories present
- targets.medium=true requires an en language
- Root-level required fields: targets, level, lifecycle
- Per-series schema: either articles or episodes list exists
- Per-series articles/episodes structure is valid
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

    # Validate root-level required fields
    root = catalog.get("meta", {})
    required_root_fields = ["repo", "asset_base_url", "copyright_holder", "license"]
    for field in required_root_fields:
        if field not in root or not str(root[field]).strip():
            errors.append(f"meta.{field}: required field missing or empty")

    for s in catalog["series"]:
        sid = s["id"]
        path_str: str = s.get("path", "")
        status: str = s.get("status", "planned")
        languages: list[str] = s.get("languages", [])
        targets: dict[str, bool] = s.get("targets", {})

        # Validate root-level required fields per series
        if not targets or not isinstance(targets, dict) or len(targets) == 0:
            errors.append(f"{sid}: targets: required dict with at least one platform")
        if "level" not in s or not str(s.get("level", "")).strip():
            errors.append(f"{sid}: level: required field missing or empty")
        if "lifecycle" not in s or not str(s.get("lifecycle", "")).strip():
            errors.append(f"{sid}: lifecycle: required field missing or empty")

        if not path_str.startswith("content/"):
            errors.append(f"{sid}: path must start with 'content/' — got '{path_str}'")
            continue

        series_path = REPO_ROOT / path_str

        if status != "planned" and not series_path.is_dir():
            errors.append(f"{sid}: path '{path_str}' does not exist (status={status})")
            continue

        if series_path.is_dir() and status != "planned":
            for lang in languages:
                lang_dir = series_path / lang
                if not lang_dir.is_dir():
                    errors.append(
                        f"{sid}: language '{lang}' listed but '{path_str}/{lang}/' missing"
                    )

        if targets.get("medium") and "en" not in languages:
            errors.append(f"{sid}: targets.medium=true but 'en' not in languages")

        # Validate per-series schema (articles or episodes)
        if status != "planned":
            per_series_path = series_path / "series.yaml"
            if per_series_path.is_file():
                try:
                    per_series = yaml.safe_load(
                        per_series_path.read_text(encoding="utf-8")
                    )
                    articles = per_series.get("articles")
                    episodes = per_series.get("episodes")

                    # Check that at least one exists
                    if not articles and not episodes:
                        errors.append(
                            f"{sid}: series.yaml missing both 'articles' and 'episodes' lists"
                        )
                    # If articles exists, validate it's a non-empty list with valid items
                    elif articles:
                        if not isinstance(articles, list):
                            errors.append(f"{sid}: articles must be a list")
                        elif len(articles) == 0:
                            errors.append(f"{sid}: articles list is empty")
                        else:
                            for i, article in enumerate(articles):
                                if not isinstance(article, dict):
                                    errors.append(
                                        f"{sid}: articles[{i}] must be a dict"
                                    )
                                    continue
                                if (
                                    "slug" not in article
                                    or not str(article.get("slug", "")).strip()
                                ):
                                    errors.append(
                                        f"{sid}: articles[{i}] missing or empty 'slug'"
                                    )
                    # If episodes exists, validate it's a non-empty list with valid items
                    elif episodes:
                        if not isinstance(episodes, list):
                            errors.append(f"{sid}: episodes must be a list")
                        elif len(episodes) == 0:
                            errors.append(f"{sid}: episodes list is empty")
                        else:
                            for i, episode in enumerate(episodes):
                                if not isinstance(episode, dict):
                                    errors.append(
                                        f"{sid}: episodes[{i}] must be a dict"
                                    )
                                    continue
                                if (
                                    "slug" not in episode
                                    or not str(episode.get("slug", "")).strip()
                                ):
                                    errors.append(
                                        f"{sid}: episodes[{i}] missing or empty 'slug'"
                                    )
                except yaml.YAMLError as e:
                    errors.append(f"{sid}: series.yaml YAML parse error: {e}")
            elif status != "planned":
                errors.append(f"{sid}: series.yaml not found (status={status})")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(catalog['series'])} series validated (root meta + per-series schema)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
