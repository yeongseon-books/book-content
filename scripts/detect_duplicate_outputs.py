#!/usr/bin/env python3
"""Detect duplicate output blocks: injected-output followed by old hardcoded code blocks."""

import re
import sys
from pathlib import Path


def find_duplicates(filepath: Path) -> list[dict]:
    """Find cases where injected-output:end is followed by a code block with output data."""
    text = filepath.read_text()
    lines = text.split("\n")
    issues = []

    i = 0
    while i < len(lines):
        # Find injected-output:end
        if "<!-- injected-output:end -->" in lines[i]:
            end_line = i
            # Skip blank lines after end marker
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1

            if j >= len(lines):
                i += 1
                continue

            # Check if next non-blank content leads to a code block
            # Pattern 1: optional paragraph text, then ``` code block
            # Pattern 2: directly a ``` code block

            start_of_old = j

            # If it's a paragraph (not a heading, not code, not HTML comment)
            if (
                not lines[j].startswith("```")
                and not lines[j].startswith("#")
                and not lines[j].startswith("<!--")
            ):
                # It could be a bridge paragraph like "결과는 대략 이렇습니다."
                # Skip past it and any blank lines
                while (
                    j < len(lines)
                    and lines[j].strip() != ""
                    and not lines[j].startswith("```")
                ):
                    j += 1
                # Skip blank lines
                while j < len(lines) and lines[j].strip() == "":
                    j += 1

            # Now check if we're at a code block
            if j < len(lines) and lines[j].strip().startswith("```"):
                code_start = j
                # Find the closing ```
                k = j + 1
                while k < len(lines) and not lines[k].strip().startswith("```"):
                    k += 1

                if k < len(lines):
                    code_end = k
                    # Check if this code block looks like output (not Python code)
                    code_content = "\n".join(lines[code_start + 1 : code_end])

                    # Heuristics: output blocks typically don't have def/import/class
                    # and often contain patterns like "유사도:", "코사인", numbers, indented text
                    has_code_keywords = any(
                        kw in code_content
                        for kw in [
                            "def ",
                            "import ",
                            "class ",
                            "from ",
                            "print(",
                            "for ",
                            "if ",
                            "return ",
                        ]
                    )
                    looks_like_output = (
                        not has_code_keywords
                        and (
                            lines[code_start].strip() == "```"
                            or lines[code_start].strip() == "```text"
                        )
                        and len(code_content.strip()) > 0
                    )

                    if looks_like_output:
                        issues.append(
                            {
                                "injected_end": end_line + 1,
                                "old_block_start": start_of_old + 1,
                                "old_block_end": code_end + 1,
                                "bridge_text": "\n".join(
                                    lines[start_of_old:code_start]
                                ).strip()
                                if start_of_old < code_start
                                else "",
                                "code_preview": code_content[:100],
                            }
                        )
        i += 1

    return issues


def main():
    content_dir = Path("/data/GitHub/tech-writing/content")
    total_issues = 0
    affected_files = []

    for md_file in sorted(content_dir.rglob("*.md")):
        # Only canonical sources (ko/*.md, en/*.md)
        parts = md_file.parts
        if "/medium/" in str(md_file):
            continue

        issues = find_duplicates(md_file)
        if issues:
            rel = md_file.relative_to(content_dir)
            affected_files.append((rel, issues))
            total_issues += len(issues)
            print(f"\n=== {rel} ({len(issues)} duplicate(s)) ===")
            for iss in issues:
                print(f"  injected-output:end at line {iss['injected_end']}")
                print(
                    f"  old block lines {iss['old_block_start']}-{iss['old_block_end']}"
                )
                if iss["bridge_text"]:
                    print(f"  bridge: '{iss['bridge_text'][:60]}...'")
                print(f"  preview: '{iss['code_preview'][:60]}...'")

    print(
        f"\n\nTotal: {total_issues} duplicate output blocks in {len(affected_files)} files"
    )


if __name__ == "__main__":
    main()
