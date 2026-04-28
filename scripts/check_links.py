"""Validate internal markdown links and image paths across the repo.

Status: skeleton. Will replace ad-hoc checks scattered across .sisyphus/.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    print(f"check_links: scanning {REPO_ROOT}")
    print("TODO: walk *.md, extract [text](path) links and ![alt](path) images, "
          "verify each path resolves on disk, report broken links with file:line.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
