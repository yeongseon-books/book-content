"""Validate YAML front matter on every article.

Status: skeleton. Activated once Phase 7 introduces front matter.

Required fields (per STYLE_GUIDE.md and templates/article.{ko,en}.md):
    title, seo_title, series, episode, language, status, targets, tags, last_reviewed

Note on status enum: `planned` is a series-level state (in series.yaml) only.
Article-level front matter must be one of: draft, ready, published, needs-update.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FIELDS = {
    "title",
    "seo_title",
    "series",
    "episode",
    "language",
    "status",
    "targets",
    "tags",
    "last_reviewed",
}

VALID_STATUS = {"draft", "ready", "published", "needs-update"}
VALID_LANGUAGE = {"ko", "en"}


def main() -> int:
    print(f"check_frontmatter: scanning {REPO_ROOT}")
    print(f"required fields: {sorted(REQUIRED_FIELDS)}")
    print(f"status enum: {sorted(VALID_STATUS)}")
    print(f"language enum: {sorted(VALID_LANGUAGE)}")
    print("TODO: walk content/**/*.md (post Phase 6), parse front matter via python-frontmatter, "
          "fail on missing fields or invalid enums.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
