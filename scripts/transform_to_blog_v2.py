#!/usr/bin/env python3
"""
Transform Korean articles from eBook format to blog format per BLOG_WRITING_GUIDE §3.

Key principles:
1. REMOVE eBook-only pedagogical scaffolding (학습 목표, 용어 정리, 연습 문제, 시니어 조언)
2. TRANSFORM section titles to blog-natural style (왜 중요한가 → 이 글에서 다룰 문제)
3. PRESERVE ALL technical content (code, diagrams, comparisons, practical advice, checklists)

Blog articles should be richer and more standalone than eBook chapters, not thinner.
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


def remove_ebook_intro_blocks(content: str) -> str:
    """Remove <!-- a-grade-*:begin --> ... <!-- a-grade-*:end --> blocks."""
    # Remove complete blocks with content
    content = re.sub(
        r"<!--\s*a-grade-intro+:begin\s*-->.*?<!--\s*a-grade-intro+:end\s*-->\n?",
        "",
        content,
        flags=re.DOTALL,
    )
    # Remove any standalone markers
    content = re.sub(r"<!--\s*a-grade-intro+:(begin|end)\s*-->\n?", "", content)
    return content


def transform_why_important_section(content: str) -> str:
    """Transform '## 왜 중요한가' to '## 이 글에서 다룰 문제'."""
    pattern = r"^(##\s+왜 중요한가\s*\n)(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)

    if not match:
        return content

    section_content = match.group(2).strip()

    # Create new blog-style intro
    new_intro = f"## 이 글에서 다룰 문제\n\n{section_content}\n\n"

    return re.sub(pattern, new_intro, content, flags=re.MULTILINE | re.DOTALL)


def transform_concept_overview_section(content: str) -> str:
    """Transform '## 개념 한눈에 보기' to '## 전체 흐름 다이어그램' (or similar natural title)."""
    # Keep the section but make title more blog-natural
    content = re.sub(
        r"^##\s+개념 한눈에 보기\s*\n", "## 전체 흐름\n", content, flags=re.MULTILINE
    )
    return content


def transform_hands_on_sections(content: str) -> str:
    """Transform '## 실습: ...' titles to more natural blog titles."""

    # Pattern: ## 실습: {description}
    def replace_hands_on(match):
        description = match.group(1).strip()
        # Keep the description but remove "실습:" prefix
        return f"## {description}\n"

    content = re.sub(
        r"^##\s+실습:\s+(.+)\n", replace_hands_on, content, flags=re.MULTILINE
    )
    return content


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


def transform_article(filepath: Path) -> Tuple[bool, str]:
    """
    Transform a single article file from eBook to blog format.

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

        # ========================================
        # STEP 1: REMOVE eBook-only scaffolding
        # ========================================

        # Remove eBook-specific learning sections (but keep technical content sections)
        ebook_only_sections = [
            "이 글에서 배울 것",  # Learning objectives
            "이 글에서 답할 질문",  # Questions to answer
            "핵심 용어 정리",  # Glossary
            "연습 문제",  # Homework exercises
            "시니어 엔지니어는 이렇게 생각합니다",  # Senior engineer tips
        ]

        for section in ebook_only_sections:
            body = remove_section(body, section)

        # Remove a-grade marker blocks
        body = remove_ebook_intro_blocks(body)

        # ========================================
        # STEP 2: TRANSFORM section titles
        # ========================================

        # Transform "왜 중요한가" → "이 글에서 다룰 문제"
        body = transform_why_important_section(body)

        # Transform "개념 한눈에 보기" → "전체 흐름"
        body = transform_concept_overview_section(body)

        # Transform "실습: ..." → more natural titles
        body = transform_hands_on_sections(body)

        # ========================================
        # STEP 3: PRESERVE technical content
        # ========================================
        # These sections are KEPT as-is:
        # - "Before/After" (good comparison)
        # - "이 코드에서 주목할 점"
        # - "자주 하는 실수"
        # - "실무에서는 이렇게 쓰입니다"
        # - "체크리스트"
        # - All code blocks, diagrams
        # - TOC, References, Tags

        # ========================================
        # STEP 4: Fix TOC markers
        # ========================================
        body = fix_toc_markers(body)

        # ========================================
        # STEP 5: Clean up formatting
        # ========================================
        # Clean up extra blank lines (max 2 consecutive)
        body = re.sub(r"\n{4,}", "\n\n\n", body)

        # Reconstruct content
        content = frontmatter + body

        if content == original_content:
            return False, "No changes needed"

        # Write back
        filepath.write_text(content, encoding="utf-8")
        return True, "Transformed successfully"

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

        was_changed, msg = transform_article(article)
        if was_changed:
            changed += 1
            messages.append(f"  ✓ {article.name}: {msg}")
        else:
            messages.append(f"  - {article.name}: {msg}")

    return total, changed, messages


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Transform articles to blog format (v2 - correct approach)"
    )
    parser.add_argument(
        "series",
        nargs="*",
        help="Series IDs to process (e.g., langchain-101). If omitted, processes all.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )

    args = parser.parse_args()

    content_dir = Path("content")
    if not content_dir.exists():
        print("Error: content/ directory not found")
        sys.exit(1)

    # Determine which series to process
    if args.series:
        series_dirs = [content_dir / s for s in args.series]
        missing = [s for s in series_dirs if not s.exists()]
        if missing:
            print(f"Error: Series not found: {[s.name for s in missing]}")
            sys.exit(1)
    else:
        series_dirs = sorted([d for d in content_dir.iterdir() if d.is_dir()])

    total_articles = 0
    total_changed = 0

    for series_dir in series_dirs:
        print(f"## {series_dir.name}")
        total, changed, messages = process_series(series_dir, dry_run=args.dry_run)

        for msg in messages:
            print(msg)

        print(f"  Summary: {changed}/{total} articles changed\n")

        total_articles += total
        total_changed += changed

    print("=" * 60)
    print(
        f"TOTAL: {total_changed}/{total_articles} articles transformed across {len(series_dirs)} series"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
