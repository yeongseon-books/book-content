"""Verify that medium/ artifact files are .html and present for each en/ post."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_YAML = REPO_ROOT / "series.yaml"


def main() -> int:
    catalog = yaml.safe_load(SERIES_YAML.read_text(encoding="utf-8"))
    errors: list[str] = []
    checked = 0

    for s in catalog["series"]:
        sid = s["id"]
        targets: dict = s.get("targets", {})
        languages: list[str] = s.get("languages", [])
        status: str = s.get("status", "planned")

        if not targets.get("medium") or "en" not in languages or status == "planned":
            continue

        series_path = REPO_ROOT / s["path"]
        en_dir = series_path / "en"
        medium_dir = series_path / "medium"

        if not en_dir.is_dir():
            continue

        en_posts = sorted(en_dir.glob("[0-9][0-9]-*.md"))
        for en_post in en_posts:
            nn = en_post.name[:2]
            expected_html = medium_dir / f"{nn}.html"
            if not expected_html.is_file():
                errors.append(f"{sid}: missing {expected_html.relative_to(REPO_ROOT)}")
            else:
                stale_md = medium_dir / f"{nn}.md"
                if stale_md.is_file():
                    errors.append(f"{sid}: stale {stale_md.relative_to(REPO_ROOT)} — remove it, artifact is .html")
            checked += 1

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"OK: {checked} medium artifacts verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
