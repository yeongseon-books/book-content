#!/usr/bin/env python3
"""
add_next_post_links.py
각 시리즈의 ko/en 파일에서 마지막 글을 제외한 모든 글에
blog-only 블록으로 다음 글 링크를 삽입한다.

삽입 위치: 시리즈 TOC block 바로 위 (<!-- toc:begin --> 앞)
이미 blog-only:start가 있는 파일은 건너뛴다.
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

TOC_MARKER = "<!-- toc:begin -->"
REFS_KO = "## 참고 자료"
REFS_EN = "## References"


def get_h1(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("# ") and not line.startswith("## "):
            return line[2:].strip()
    return path.stem


def insert_blog_only_link(path: Path, next_path: Path, lang: str) -> bool:
    text = path.read_text(encoding="utf-8")

    if "blog-only:start" in text:
        return False

    next_title = get_h1(next_path)
    next_filename = next_path.name

    if lang == "ko":
        block = (
            f"\n<!-- blog-only:start -->\n"
            f"다음 글: [{next_title}](./{next_filename})\n"
            f"<!-- blog-only:end -->\n"
        )
        insert_before = TOC_MARKER
        if insert_before not in text:
            insert_before = REFS_KO
    else:
        block = (
            f"\n<!-- blog-only:start -->\n"
            f"Next: [{next_title}](./{next_filename})\n"
            f"<!-- blog-only:end -->\n"
        )
        insert_before = TOC_MARKER
        if insert_before not in text:
            insert_before = REFS_EN

    if insert_before not in text:
        print(f"  SKIP (no anchor): {path.name}")
        return False

    new_text = text.replace(insert_before, block + insert_before, 1)
    path.write_text(new_text, encoding="utf-8")
    return True


def process_lang_dir(lang_dir: Path, lang: str):
    if not lang_dir.is_dir():
        return
    files = sorted(f for f in lang_dir.iterdir() if f.suffix == ".md")
    if len(files) < 2:
        return

    modified = 0
    skipped = 0
    for i, path in enumerate(files[:-1]):
        next_path = files[i + 1]
        result = insert_blog_only_link(path, next_path, lang)
        if result:
            print(f"  + {path.name} → {next_path.name}")
            modified += 1
        else:
            skipped += 1

    print(f"  {lang}: {modified} modified, {skipped} skipped")


def main():
    for series_id in SERIES_DIRS:
        series_dir = REPO / "content" / series_id
        if not series_dir.is_dir():
            print(f"[SKIP] {series_id} — not found")
            continue
        print(f"\n[{series_id}]")

        if (series_dir / "ko").is_dir():
            process_lang_dir(series_dir / "ko", "ko")

        if (series_dir / "en").is_dir():
            process_lang_dir(series_dir / "en", "en")

        if not (series_dir / "ko").is_dir() and not (series_dir / "en").is_dir():
            process_lang_dir(series_dir, "ko")


if __name__ == "__main__":
    main()
