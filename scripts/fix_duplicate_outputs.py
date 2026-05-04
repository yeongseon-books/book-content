#!/usr/bin/env python3
"""Remove duplicate output blocks that follow <!-- injected-output:end --> markers."""

import re
from pathlib import Path


def fix_file(filepath: Path) -> int:
    """Remove old hardcoded output blocks after injected-output:end markers. Returns count of fixes."""
    text = filepath.read_text()
    lines = text.split("\n")
    fixes = 0
    lines_to_remove: set[int] = set()

    i = 0
    while i < len(lines):
        if "<!-- injected-output:end -->" in lines[i]:
            end_line = i
            j = i + 1
            # Skip blank lines
            while j < len(lines) and lines[j].strip() == "":
                j += 1

            if j >= len(lines):
                i += 1
                continue

            start_of_old = j

            # If it's a bridge paragraph (not heading, not code, not HTML comment)
            if (
                not lines[j].startswith("```")
                and not lines[j].startswith("#")
                and not lines[j].startswith("<!--")
            ):
                # Skip bridge paragraph
                bridge_start = j
                while (
                    j < len(lines)
                    and lines[j].strip() != ""
                    and not lines[j].startswith("```")
                ):
                    j += 1
                # Skip blank lines after bridge
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
            else:
                bridge_start = j

            # Check if we're at a code block
            if j < len(lines) and lines[j].strip().startswith("```"):
                code_start = j
                k = j + 1
                while k < len(lines) and not lines[k].strip().startswith("```"):
                    k += 1

                if k < len(lines):
                    code_end = k
                    code_content = "\n".join(lines[code_start + 1 : code_end])

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
                        # Mark lines for removal: from first blank after injected-output:end
                        # through the closing ``` of the old block
                        for idx in range(end_line + 1, code_end + 1):
                            lines_to_remove.add(idx)
                        fixes += 1

        i += 1

    if fixes > 0:
        new_lines = [
            line for idx, line in enumerate(lines) if idx not in lines_to_remove
        ]
        # Clean up triple+ blank lines
        cleaned = []
        blank_count = 0
        for line in new_lines:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= 2:
                    cleaned.append(line)
            else:
                blank_count = 0
                cleaned.append(line)
        filepath.write_text("\n".join(cleaned))

    return fixes


def main():
    content_dir = Path("/data/GitHub/tech-writing/content")
    total = 0

    for md_file in sorted(content_dir.rglob("*.md")):
        if "/medium/" in str(md_file):
            continue
        fixes = fix_file(md_file)
        if fixes:
            rel = md_file.relative_to(content_dir)
            print(f"  Fixed {fixes} duplicate(s) in {rel}")
            total += fixes

    print(f"\nTotal: {total} duplicate output blocks removed")


if __name__ == "__main__":
    main()
