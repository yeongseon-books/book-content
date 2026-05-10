#!/usr/bin/env python3
"""
Restructure Korean articles from eBook-style to blog format per BLOG_WRITING_GUIDE §3.

This script:
1. Removes eBook-specific sections
2. Transforms sections to blog format
3. Preserves technical content, TOC, references, tags
4. SAFELY handles front matter without modifying it
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def split_frontmatter(content: str) -> Tuple[str, str]:
    """
    Split content into frontmatter and body.

    Returns:
        (frontmatter: str, body: str) where frontmatter includes --- delimiters
    """
    if not content.startswith("---\n"):
        return "", content

    # Find second ---
    end = content.find("\n---\n", 4)
    if end == -1:
        return "", content

    # Include closing ---\n
    end += 5
    return content[:end], content[end:]


def remove_section(content: str, heading: str) -> str:
    """Remove a section (heading + all content until next same-level heading)."""
    # Match ## heading followed by content until next ## heading or end
    pattern = rf"^(##\s+{re.escape(heading)}\s*\n)(.*?)(?=^##\s|\Z)"
    return re.sub(pattern, "", content, flags=re.MULTILINE | re.DOTALL)


def remove_marker_blocks(content: str) -> str:
    """Remove <!-- a-grade-*:begin --> ... <!-- a-grade-*:end --> blocks and standalone markers."""
    # Remove complete blocks with content
    content = re.sub(
        r"<!--\s*a-grade-[^>]+:begin\s*-->.*?<!--\s*a-grade-[^>]+:end\s*-->\n?",
        "",
        content,
        flags=re.DOTALL,
    )
    # Remove standalone begin/end markers
    content = re.sub(
        r"<!--\s*a-grade-[^>]+:(begin|end)\s*-->\n?",
        "",
        content,
    )
    # Remove ebook-only blocks
    content = re.sub(
        r"<!--\s*ebook-only:start\s*-->.*?<!--\s*ebook-only:end\s*-->\n?",
        "",
        content,
        flags=re.DOTALL,
    )
    return content


def transform_why_important_section(content: str) -> str:
    """Transform '## 왜 중요한가' into '## 이 글에서 다룰 문제'."""
    if "## 왜 중요한가" not in content:
        return content

    # Find the section
    pattern = r"^(##\s+왜 중요한가\s*\n)(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)
    if not match:
        return content

    section_content = match.group(2).strip()

    # Create new blog-style intro
    new_intro = f"## 이 글에서 다룰 문제\n\n{section_content}\n\n"

    return re.sub(pattern, new_intro, content, flags=re.MULTILINE | re.DOTALL)


def fix_toc_markers(content: str) -> str:
    """Ensure TOC has both begin and end markers."""
    # If has end but no begin, add begin before 시리즈 목차
    if "<!-- toc:end -->" in content and "<!-- toc:begin -->" not in content:
        content = re.sub(
            r"^(##\s+시리즈 목차\s*\n)",
            r"<!-- toc:begin -->\n\1",
            content,
            flags=re.MULTILINE,
        )
    return content


def restructure_article(filepath: Path) -> Tuple[bool, str]:
    """
    Restructure a single article file.

    Returns:
        (changed: bool, message: str)
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        original_content = content

        # CRITICAL: Split frontmatter and body
        frontmatter, body = split_frontmatter(content)

        if not body:
            return False, "No body content found"

        # Process only the body (leave frontmatter untouched)
        # Step 1: Remove eBook-specific sections
        ebook_sections = [
            "핵심 질문",
            "이 글에서 답할 질문",
            "이 글에서 배울 것",
            "배울 것",
            "핵심 용어 정리",
            "연습 문제",
            "시니어 엔지니어는 이렇게 생각합니다",
        ]

        for section in ebook_sections:
            body = remove_section(body, section)

        # Step 2: Remove a-grade marker blocks and ebook-only blocks
        body = remove_marker_blocks(body)

        # Step 3: Transform "왜 중요한가" to "이 글에서 다룰 문제"
        body = transform_why_important_section(body)

        # Step 4: Fix TOC markers
        body = fix_toc_markers(body)

        # Step 5: Clean up extra blank lines (max 2 consecutive)
        body = re.sub(r"\n{4,}", "\n\n\n", body)

        # Reconstruct content
        content = frontmatter + body

        if content == original_content:
            return False, "No changes needed"

        # Write back
        filepath.write_text(content, encoding="utf-8")
        return True, "Restructured successfully"

    except Exception as e:
        return False, f"Error: {e}"


def process_series(
    series_path: Path, dry_run: bool = False
) -> Tuple[int, int, List[str]]:
    """
    Process all Korean articles in a series.

    Returns:
        (total: int, changed: int, messages: List[str])
    """
    ko_dir = series_path / "ko"
    if not ko_dir.exists():
        return 0, 0, [f"No ko/ directory in {series_path.name}"]

    articles = sorted(ko_dir.glob("*.md"))
    if not articles:
        return 0, 0, [f"No articles in {series_path.name}/ko/"]

    total = len(articles)
    changed = 0
    messages = []

    for article in articles:
        if dry_run:
            messages.append(f"  [DRY RUN] Would process {article.name}")
            continue

        was_changed, msg = restructure_article(article)
        if was_changed:
            changed += 1
            messages.append(f"  ✓ {article.name}: {msg}")
        else:
            messages.append(f"  - {article.name}: {msg}")

    return total, changed, messages


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Restructure articles to blog format")
    parser.add_argument(
        "series_ids", nargs="*", help="Series IDs to process (default: all)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify no ebook patterns remain"
    )
    args = parser.parse_args()

    content_dir = Path(__file__).parent.parent / "content"

    if args.series_ids:
        series_dirs = [content_dir / sid for sid in args.series_ids]
    else:
        series_dirs = sorted([d for d in content_dir.iterdir() if d.is_dir()])

    total_series = 0
    total_articles = 0
    total_changed = 0

    for series_dir in series_dirs:
        if not series_dir.exists():
            print(f"⚠ Series not found: {series_dir.name}")
            continue

        print(f"\n## {series_dir.name}")
        articles, changed, messages = process_series(series_dir, args.dry_run)

        if articles == 0:
            continue

        total_series += 1
        total_articles += articles
        total_changed += changed

        for msg in messages:
            print(msg)

        print(f"  Summary: {changed}/{articles} articles changed")

    print(f"\n{'=' * 60}")
    print(
        f"TOTAL: {total_changed}/{total_articles} articles changed across {total_series} series"
    )

    if args.verify:
        print(f"\n{'=' * 60}")
        print("Verification: Checking for remaining eBook patterns...")
        import subprocess

        result = subprocess.run(
            [
                "grep",
                "-r",
                "-l",
                "핵심 용어 정리\\|연습 문제\\|시니어 엔지니어는\\|a-grade-intro\\|a-grade-example\\|ebook-only:start",
                str(content_dir / "*/ko/*.md"),
            ],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print("❌ Found remaining eBook patterns in:")
            print(result.stdout)
            return 1
        else:
            print("✓ No eBook patterns found")

    return 0


if __name__ == "__main__":
    sys.exit(main())
