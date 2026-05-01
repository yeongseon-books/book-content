"""Add missing YAML front matter to content files that have none.

Reads each *.md under content/<series>/{ko,en}/ and if no front matter
block is present, injects one derived from:
  - series id, episode number, language → from file path
  - title → from first H1 in the file
  - tags → from SERIES_TAGS map below

Only inserts; never overwrites existing front matter.
Run with --dry-run to preview without writing.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"

TODAY = date.today().isoformat()

# Tags per series (from AGENTS.md)
SERIES_TAGS: dict[str, list[str]] = {
    "vector-search-101": ["Vector Search", "FAISS", "Embeddings", "Python"],
    "langchain-101": ["LangChain", "LCEL", "Python", "LLM"],
    "ai-app-patterns-101": ["LLM", "RAG", "Agent", "Python"],
    "korean-ai-stack-101": ["Korean NLP", "LLM", "Embeddings", "OCR"],
    "document-ingestion-101": ["RAG", "Document Processing", "LangChain", "Python"],
    "llm-apps-ops-101": ["LLMOps", "Observability", "Python", "LLM"],
    "rag-benchmark-101": ["RAG", "VectorDB", "Benchmarking", "LLM"],
    "langgraph-101": ["LangGraph", "Agent", "Python", "LLM"],
    "llm-finetuning-101": ["Fine-tuning", "LoRA", "LLM", "Python"],
    # fallback for other series
    "llm-from-scratch-101": ["LLM", "PyTorch", "Transformer", "Tutorial"],
    "rag-deep-dive": ["RAG", "LangChain", "Vector Search", "LLM"],
    "llm-app-foundations-101": ["LLM", "OpenAI", "Prompt Engineering", "Python"],
    "llm-api-production-101": ["LLM", "OpenAI", "Streaming", "Python"],
}

H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
PREFIX_RE = re.compile(r"^(\d+)")


def has_frontmatter(text: str) -> bool:
    return text.startswith("---")


def extract_title(text: str) -> str:
    m = H1_RE.search(text)
    return m.group(1) if m else "Untitled"


def build_frontmatter(series: str, episode: int, lang: str, title: str) -> str:
    tags = SERIES_TAGS.get(series, ["Python"])
    tags_yaml = "\n".join(f"- {t}" for t in tags)
    return f"""---
title: '{title}'
series: {series}
episode: {episode}
language: {lang}
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
{tags_yaml}
last_reviewed: '{TODAY}'
---

"""


def process_file(path: Path, dry_run: bool) -> bool:
    """Returns True if file was (or would be) modified."""
    text = path.read_text(encoding="utf-8")
    if has_frontmatter(text):
        return False

    # Derive metadata from path: content/<series>/<lang>/<NN>-<slug>.md
    parts = path.relative_to(CONTENT_DIR).parts  # (series, lang, filename)
    if len(parts) < 3:
        print(f"SKIP {path} — unexpected path depth", file=sys.stderr)
        return False

    series = parts[0]
    lang = parts[1]
    filename = parts[2]

    m = PREFIX_RE.match(filename)
    episode = int(m.group(1)) if m else 0

    title = extract_title(text)
    fm = build_frontmatter(series, episode, lang, title)

    if dry_run:
        print(f"DRY-RUN {path}")
    else:
        path.write_text(fm + text, encoding="utf-8")
        print(f"UPDATED {path}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("series", nargs="*", help="Series ids to process (default: all)")
    args = parser.parse_args()

    modified = 0
    for lang_dir in sorted(CONTENT_DIR.glob("*/ko"), key=str):
        series_dir = lang_dir.parent
        series_id = series_dir.name
        if args.series and series_id not in args.series:
            continue
        for lang in ("ko", "en"):
            for md in sorted((series_dir / lang).glob("*.md")):
                if process_file(md, args.dry_run):
                    modified += 1

    action = "Would modify" if args.dry_run else "Modified"
    print(f"\n{action}: {modified} files")


if __name__ == "__main__":
    main()
