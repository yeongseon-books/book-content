#!/usr/bin/env python3
"""Guard against empty boilerplate H2 headings.

Detects template-only H2 headings that have no body content beneath them
(immediately followed by another H2, TOC block, or EOF). Such headings are
copy-paste leftovers from earlier template-driven generation and harm reader
experience.

Specifically blocks the following headings (ko + en variants):
- 한눈에 보는 개념 / Concept at a glance
- 핵심 개념 한눈에 보기
- 한눈에 보는 흐름 / The flow at a glance
- 핵심 흐름 / Core flow

Also flags ANY H2 whose body (until next H2 / TOC / EOF) is empty.

Exit code: 0 on success, 1 on any defect.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"

BANNED_EMPTY_HEADINGS = {
    "한눈에 보는 개념",
    "핵심 개념 한눈에 보기",
    "한눈에 보는 흐름",
    "핵심 흐름",
    "The flow at a glance",
    "Concept at a glance",
    "Core flow",
}

H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"^```", re.MULTILINE)


FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
SUBHEADING_RE = re.compile(r"^#+\s+.*$", re.MULTILINE)


def neutralize_code_fences(text: str) -> str:
    text = FRONTMATTER_RE.sub("", text, count=1)
    out = []
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def find_empty_headings(text: str) -> list[tuple[str, int]]:
    """Return (heading_text, line_number) tuples for banned H2s lacking body content."""
    stripped = neutralize_code_fences(text)
    lines = stripped.split("\n")
    raw_lines = text.split("\n")
    h2_positions: list[tuple[int, str]] = []
    for i, ln in enumerate(lines):
        m = re.match(r"^##\s+(.+?)\s*$", ln)
        if m:
            h2_positions.append((i, m.group(1).strip()))

    defects: list[tuple[str, int]] = []
    for idx, (line_idx, heading) in enumerate(h2_positions):
        end = h2_positions[idx + 1][0] if idx + 1 < len(h2_positions) else len(lines)
        body_lines = lines[line_idx + 1 : end]
        for j, bl in enumerate(body_lines):
            if bl.strip().startswith("<!-- toc:"):
                body_lines = body_lines[:j]
                break
        body = "\n".join(body_lines).strip()
        body_text = SUBHEADING_RE.sub("", body).strip()
        if len(body_text) == 0 and heading in BANNED_EMPTY_HEADINGS:
            actual_line = next(
                (k for k, raw_ln in enumerate(raw_lines, 1)
                 if raw_ln.strip() == f"## {heading}"),
                0,
            )
            defects.append((heading, actual_line))
    return defects


def main() -> int:
    defects_total = 0
    files_with_defects = 0
    for md_file in sorted(CONTENT_DIR.glob("*/ko/*.md")) + sorted(
        CONTENT_DIR.glob("*/en/*.md")
    ):
        text = md_file.read_text(encoding="utf-8")
        defects = find_empty_headings(text)
        if defects:
            files_with_defects += 1
            for heading, line in defects:
                rel = md_file.relative_to(REPO_ROOT)
                print(f"{rel}:{line}: empty boilerplate heading: '## {heading}'")
                defects_total += 1

    if defects_total > 0:
        print(
            f"\nFAIL: {defects_total} empty boilerplate heading(s) in "
            f"{files_with_defects} file(s)",
            file=sys.stderr,
        )
        return 1
    print("OK: no empty boilerplate headings found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
