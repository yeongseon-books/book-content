#!/usr/bin/env python3
"""Guard: no orphan image assets in assets/ tree.

Walks all canonical .md files (content/<series>/{ko,en}/*.md), collects
image references in two forms:
  - relative paths (resolved from the markdown file's directory)
  - basenames (handles public CDN URLs that point to the same filename)

Any PNG under assets/ whose path AND basename are both unreferenced is
considered orphan and reported. Helps catch leftover diagrams from old
content patterns (e.g., issue #1241: 'questions-this-post-answers' batch).

Refs: #1241
"""
from __future__ import annotations

import glob
import os
import re
import sys

IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def collect_refs() -> tuple[set[str], set[str]]:
    refs_path: set[str] = set()
    refs_base: set[str] = set()
    for f in glob.glob("content/**/*.md", recursive=True):
        if "/medium/" in f:
            continue
        try:
            text = open(f, encoding="utf-8").read()
        except Exception:
            continue
        base = os.path.dirname(f)
        for m in IMG_RE.finditer(text):
            url = m.group(1).split("#")[0].split(" ")[0]
            if url.startswith("http"):
                refs_base.add(url.split("/")[-1])
            else:
                target = os.path.normpath(os.path.join(base, url))
                refs_path.add(target)
                refs_base.add(os.path.basename(target))
    return refs_path, refs_base


def main() -> int:
    refs_path, refs_base = collect_refs()
    orphans: list[str] = []
    for a in sorted(glob.glob("assets/**/*.png", recursive=True)):
        if a in refs_path:
            continue
        if os.path.basename(a) in refs_base:
            continue
        orphans.append(a)

    if orphans:
        print(f"FAIL: {len(orphans)} orphan PNG asset(s) under assets/.", file=sys.stderr)
        for o in orphans[:20]:
            print(f"  {o}", file=sys.stderr)
        if len(orphans) > 20:
            print(f"  ... and {len(orphans) - 20} more", file=sys.stderr)
        return 1

    print("PASS: No orphan PNG assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
