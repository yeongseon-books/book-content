#!/usr/bin/env python3
"""Guard: no emoji / pictograph in ko/en body prose.

AGENTS.md "No emoji (use text Pass/Fail)" policy.

Coverage:
- BMP misc symbols & dingbats (✓ ✗ ✅ ❌ ⚠ etc.)
- Misc pictographs, transport, supplemental SMP blocks (👍 👎 🎉 🚀 ...)
- Regional indicators / flags

Skips:
- Fenced code blocks (commands/logs/output may legitimately echo unicode)
- YAML front matter

Refs: #1229 (ko), #1244 (en)
"""
from __future__ import annotations

import glob
import re
import sys

EMOJI_RE = re.compile(
    r"[\u2600-\u27BF"
    r"\U0001F300-\U0001FAFF"
    r"\U0001F1E6-\U0001F1FF]"
)


def scan(path: str) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    in_fence = False
    in_frontmatter = False
    with open(path, encoding="utf-8") as fh:
        for idx, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            if idx == 1 and line == "---":
                in_frontmatter = True
                continue
            if in_frontmatter:
                if line == "---":
                    in_frontmatter = False
                continue
            if line.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in EMOJI_RE.finditer(line):
                hits.append((idx, m.group(0)))
    return hits


def main() -> int:
    failures: list[str] = []
    for path in sorted(glob.glob("content/*/ko/*.md") + glob.glob("content/*/en/*.md")):
        for line_no, ch in scan(path):
            failures.append(f"{path}:{line_no}: '{ch}' (U+{ord(ch):04X})")

    if failures:
        print("FAIL: emoji/pictograph in body prose.", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(f"\nTotal: {len(failures)} occurrence(s).", file=sys.stderr)
        return 1

    print("PASS: No emoji in body prose.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
