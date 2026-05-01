#!/usr/bin/env python3
"""
add_ebook_only_blocks.py
각 시리즈의 ko/en 파일(중간 글 + 첫 글)에 ebook-only 블록을 삽입한다.
- 삽입 위치: YAML front matter 직후, 첫 본문 ## 섹션 이전
- 내용: "이 장의 위치" (앞 장 / 이 장 / 다음 장 관계)
- 이미 ebook-only:start 가 있는 파일은 건너뜀
"""
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SERIES_DIRS = [
    "azure-app-service-101",
    "azure-app-service-deep-dive",
    "azure-functions-101",
    "azure-functions-deep-dive",
    "azure-aks-101",
    "azure-aks-deep-dive",
    "azure-aca-101",
    "azure-aca-deep-dive",
    "ai-web-dev-101",
    "llm-from-scratch-101",
    "rag-deep-dive",
    "llm-app-foundations-101",
    "llm-api-production-101",
    "vector-search-101",
    "langchain-101",
    "ai-app-patterns-101",
    "korean-ai-stack-101",
    "document-ingestion-101",
    "llm-apps-ops-101",
    "rag-benchmark-101",
    "langgraph-101",
    "llm-finetuning-101",
]

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)


def get_h1(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("# ") and not s.startswith("## "):
            return s[2:].strip()
    return path.stem


def make_ebook_block_ko(idx: int, titles: list[str]) -> str:
    current = titles[idx]
    prev_title = titles[idx - 1] if idx > 0 else None
    next_title = titles[idx + 1] if idx < len(titles) - 1 else None
    total = len(titles)
    chapter = idx + 1

    lines = [f"\n<!-- ebook-only:start -->"]
    lines.append(f"## 이 장의 위치\n")
    lines.append(f"이 글은 시리즈 {total}편 중 {chapter}번째 장입니다.")
    if prev_title:
        lines.append(f"앞 장에서는 **{prev_title}**을 다뤘습니다.")
    if next_title:
        lines.append(f"이 장을 마치면 다음 장에서 **{next_title}**으로 이어집니다.")
    lines.append(f"<!-- ebook-only:end -->\n")
    return "\n".join(lines)


def make_ebook_block_en(idx: int, titles: list[str]) -> str:
    current = titles[idx]
    prev_title = titles[idx - 1] if idx > 0 else None
    next_title = titles[idx + 1] if idx < len(titles) - 1 else None
    total = len(titles)
    chapter = idx + 1

    lines = [f"\n<!-- ebook-only:start -->"]
    lines.append(f"## Where this chapter fits\n")
    lines.append(f"This is chapter {chapter} of {total} in the series.")
    if prev_title:
        lines.append(f"The previous chapter covered **{prev_title}**.")
    if next_title:
        lines.append(f"After this chapter, the next one moves on to **{next_title}**.")
    lines.append(f"<!-- ebook-only:end -->\n")
    return "\n".join(lines)


def insert_ebook_block(path: Path, block: str) -> bool:
    text = path.read_text(encoding="utf-8")

    if "ebook-only:start" in text:
        return False

    lines = text.splitlines(keepends=True)
    h1_idx = None
    first_h2_idx = None

    in_frontmatter = False
    frontmatter_done = False
    fm_count = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---" and i == 0:
            in_frontmatter = True
            fm_count += 1
            continue
        if in_frontmatter and stripped == "---":
            fm_count += 1
            if fm_count == 2:
                in_frontmatter = False
                frontmatter_done = True
            continue

        if not frontmatter_done and not in_frontmatter and fm_count == 0:
            frontmatter_done = True

        if frontmatter_done and h1_idx is None:
            if stripped.startswith("# ") and not stripped.startswith("## "):
                h1_idx = i
                continue

        if h1_idx is not None and first_h2_idx is None:
            if stripped.startswith("## "):
                first_h2_idx = i
                break

    if h1_idx is None:
        print(f"  SKIP (no H1): {path.name}")
        return False

    insert_at = first_h2_idx if first_h2_idx is not None else h1_idx + 1

    block_lines = (block + "\n").splitlines(keepends=True)
    new_lines = lines[:insert_at] + block_lines + lines[insert_at:]
    path.write_text("".join(new_lines), encoding="utf-8")
    return True


def process_lang_dir(lang_dir: Path, lang: str):
    if not lang_dir.is_dir():
        return
    files = sorted(f for f in lang_dir.iterdir() if f.suffix == ".md")
    if not files:
        return

    titles = [get_h1(f) for f in files]

    make_block = make_ebook_block_ko if lang == "ko" else make_ebook_block_en

    modified = skipped = 0
    for i, path in enumerate(files):
        block = make_block(i, titles)
        result = insert_ebook_block(path, block)
        if result:
            print(f"  + {path.name}")
            modified += 1
        else:
            skipped += 1

    print(f"  {lang}: {modified} modified, {skipped} skipped")


def main():
    for series_id in SERIES_DIRS:
        series_dir = REPO / "content" / series_id
        if not series_dir.is_dir():
            print(f"[SKIP] {series_id}")
            continue
        print(f"\n[{series_id}]")

        if (series_dir / "ko").is_dir():
            process_lang_dir(series_dir / "ko", "ko")
        elif series_id == "ai-web-dev-101":
            process_lang_dir(series_dir, "ko")

        if (series_dir / "en").is_dir():
            process_lang_dir(series_dir / "en", "en")


if __name__ == "__main__":
    main()
