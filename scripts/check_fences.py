"""Check that all markdown files have properly balanced code fences.

Simulates GitHub's fence rendering: tracks open/close state for both
``` and ~~~ fences, and reports files where a fence is left unclosed.

Usage:
    python3 scripts/check_fences.py              # check all content/
    python3 scripts/check_fences.py content/llm-app-foundations-101/
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def check_file(path: str) -> str | None:
    lines = open(path, encoding="utf-8").read().split("\n")
    in_fence = False
    fence_char = None
    for line in lines:
        if not in_fence:
            if line.startswith("```"):
                in_fence = True
                fence_char = "```"
            elif line.startswith("~~~"):
                in_fence = True
                fence_char = "~~~"
        else:
            if line.strip() == fence_char:
                in_fence = False
                fence_char = None
    return fence_char if in_fence else None


def main() -> int:
    roots = sys.argv[1:] if len(sys.argv) > 1 else [str(REPO_ROOT / "content")]
    files = []
    for r in roots:
        p = Path(r)
        if p.is_file():
            files.append(str(p))
        else:
            files.extend(sorted(glob.glob(str(p / "**" / "*.md"), recursive=True)))

    files = [f for f in files if "/ko/" in f or "/en/" in f]

    broken = []
    for f in files:
        unclosed = check_file(f)
        if unclosed:
            broken.append(f)
            print(f"BROKEN (unclosed {unclosed}): {f}")

    print(f"\n{len(files)} files checked, {len(broken)} broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
