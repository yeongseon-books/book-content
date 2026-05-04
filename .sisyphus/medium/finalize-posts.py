#!/usr/bin/env python3
"""All-in-one post finalizer for Azure series (ko/en/medium).

Three operations, idempotent, safe to re-run:

1. Insert/update visible tag line ('Tags: A, B, C, D') as the very last line.
   Any legacy '<!-- tags: ... -->' on line 1 is removed.
2. Rename References heading to '참고 자료' (ko only).
3. Insert/refresh series TOC immediately above the references section.

Source of truth for titles: each post's H1 (first '# ' line).
Series ordering: numeric prefix of filename (01, 02, ...).
TOC entry for the current post: bold, no link.
TOC links: ko->ko/<file>.md, en->en/<file>.md, medium->medium/<NN>.md (relative within series dir).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from _catalog import ROOT, is_present, load_catalog

SERIES_TAGS: dict[str, list[str]] = {
    "azure-app-service-101": ["Azure", "App Service", "Cloud", "Web Apps"],
    "azure-app-service-deep-dive": ["Azure", "App Service", "Distributed Systems", "Platform Engineering"],
    "azure-functions-101": ["Azure", "Azure Functions", "Serverless", "Cloud"],
    "azure-functions-deep-dive": ["Azure Functions", "Serverless", "Distributed Systems", "gRPC"],
    "azure-aks-101": ["Azure", "AKS", "Kubernetes", "Cloud"],
    "azure-aks-deep-dive": ["AKS", "Kubernetes", "Distributed Systems", "Containers"],
    "azure-aca-101": ["Azure", "Container Apps", "Serverless", "Containers"],
    "azure-aca-deep-dive": ["Container Apps", "KEDA", "Dapr", "Envoy"],
    "llm-from-scratch-101": ["LLM", "PyTorch", "Transformer", "Tutorial"],
    "rag-deep-dive": ["RAG", "LangChain", "Vector Search", "LLM"],
    "llm-app-foundations-101": ["LLM", "OpenAI", "Prompt Engineering", "Python"],
    "llm-api-production-101": ["LLM", "OpenAI", "Streaming", "Python"],
    "vector-search-101": ["Vector Search", "FAISS", "Embeddings", "Python"],
    "langchain-101": ["LangChain", "LCEL", "Python", "LLM"],
    "ai-app-patterns-101": ["LLM", "RAG", "Agent", "Python"],
    "korean-ai-stack-101": ["Korean NLP", "LLM", "Embeddings", "OCR"],
    "document-ingestion-101": ["RAG", "Document Processing", "LangChain", "Python"],
    "llm-apps-ops-101": ["LLMOps", "Observability", "Python", "LLM"],
    "rag-benchmark-101": ["RAG", "VectorDB", "Benchmarking", "LLM"],
    "langgraph-101": ["LangGraph", "Agent", "Python", "LLM"],
    "llm-finetuning-101": ["Fine-tuning", "LoRA", "LLM", "Python"],
    "python-dbapi-101": ["Python", "DB-API", "PEP 249", "Database"],
    "sqlalchemy-101": ["Python", "SQLAlchemy", "ORM", "Database"],
    "ai-agent-101": ["AI Agent", "LLM", "Tool Use", "Python"],
    "harness-engineering-101": ["AI Agent", "Harness", "Production", "Reliability"],
}

REFERENCES_HEADINGS_ANY = ("## References", "## 참고 자료", "## 참고문헌", "## 참고")
KO_REF_HEADING = "## 참고 자료"
TOC_HEADING_KO = "## 시리즈 목차"
TOC_HEADING_EN = "## In this series"
TOC_BEGIN = "<!-- toc:begin -->"
TOC_END = "<!-- toc:end -->"
TAG_COMMENT_PREFIX = "<!-- tags:"
TAG_LINE_PREFIX = "Tags: "
H1_RE = re.compile(r"^#\s+(.+?)\s*$")


def numeric_prefix(name: str) -> str | None:
    m = re.match(r"^(\d+)", name)
    return m.group(1) if m else None


def read_h1(text: str) -> str | None:
    lines = text.split("\n")
    i = 0
    if lines and lines[0].rstrip() == "---":
        i = 1
        while i < len(lines) and lines[i].rstrip() != "---":
            i += 1
        i += 1
    while i < len(lines):
        line = lines[i]
        i += 1
        if line.startswith(TAG_COMMENT_PREFIX):
            continue
        s = line.strip()
        if not s:
            continue
        m = H1_RE.match(s)
        if m:
            return m.group(1).strip()
        return None
    return None


def load_planned(series_dir: Path) -> dict[str, dict[int, dict[str, str]]]:
    """Load planned.yaml if present; returns {variant: {idx: {title, filename}}}."""
    planned_path = series_dir / "planned.yaml"
    if not planned_path.exists():
        return {}
    raw = yaml.safe_load(planned_path.read_text(encoding="utf-8")) or {}
    result: dict[str, dict[int, dict[str, str]]] = {}
    for variant, posts in raw.items():
        if not isinstance(posts, dict):
            continue
        result[variant] = {int(k): v for k, v in posts.items()}
    return result


def collect_series(series_dir: Path) -> dict[str, dict[int, dict[str, str]]]:
    """Return {variant: {idx: {'title':..., 'filename':...}}} for ko/en/medium.

    Actual files on disk take priority. planned.yaml fills in missing entries.
    """
    planned = load_planned(series_dir)
    result: dict[str, dict[int, dict[str, str]]] = {"ko": {}, "en": {}, "medium": {}}
    if not series_dir.is_dir():
        return result
    for variant in ("ko", "en", "medium"):
        sub = series_dir / variant
        if sub.is_dir():
            for md in sorted(sub.glob("*.md")):
                prefix = numeric_prefix(md.name)
                if not prefix:
                    continue
                idx = int(prefix)
                title = read_h1(md.read_text(encoding="utf-8")) or md.stem
                result[variant][idx] = {"title": title, "filename": md.name}
        for idx, info in planned.get(variant, {}).items():
            if idx not in result[variant]:
                result[variant][idx] = info
    return result


def build_toc(entries: dict[int, dict[str, str]], current_idx: int, variant: str) -> list[str]:
    heading = TOC_HEADING_KO if variant == "ko" else TOC_HEADING_EN
    current_label = "현재 글" if variant == "ko" else "current"
    upcoming_label = "예정" if variant == "ko" else "upcoming"
    lines = [TOC_BEGIN, heading, ""]
    for idx in sorted(entries):
        e = entries[idx]
        if idx < current_idx:
            lines.append(f"- [{e['title']}](./{e['filename']})")
        elif idx == current_idx:
            lines.append(f"- **{e['title']} ({current_label})**")
        else:
            lines.append(f"- {e['title']} ({upcoming_label})")
    lines.append("")
    lines.append(TOC_END)
    return lines


def apply_tag_line(lines: list[str], series: str) -> list[str]:
    desired = f"{TAG_LINE_PREFIX}{', '.join(SERIES_TAGS[series])}"
    out = [ln for ln in lines if not ln.startswith(TAG_COMMENT_PREFIX)]
    out = [ln for ln in out if not ln.startswith(TAG_LINE_PREFIX)]
    while out and out[-1].strip() == "":
        out.pop()
    out.append("")
    out.append(desired)
    return out


def rename_ko_references(lines: list[str]) -> list[str]:
    out = []
    for line in lines:
        if line.startswith("## ") and line.strip() in {"## References", "## 참고문헌", "## 참고"}:
            out.append(KO_REF_HEADING)
        else:
            out.append(line)
    return out


def find_references_index(lines: list[str]) -> int | None:
    for i, line in enumerate(lines):
        s = line.strip()
        if s in REFERENCES_HEADINGS_ANY:
            return i
    return None


def strip_existing_toc(lines: list[str]) -> list[str]:
    """Remove any block between TOC_BEGIN and TOC_END (inclusive)."""
    if TOC_BEGIN not in "\n".join(lines):
        return lines
    out = []
    skip = False
    for line in lines:
        if line.strip() == TOC_BEGIN:
            skip = True
            continue
        if line.strip() == TOC_END:
            skip = False
            continue
        if not skip:
            out.append(line)
    return out


def find_toc_insert_point(lines: list[str], ref_idx: int) -> int:
    """Walk back from ref_idx skipping blank lines and a '---' divider line."""
    i = ref_idx - 1
    while i >= 0 and lines[i].strip() == "":
        i -= 1
    if i >= 0 and lines[i].strip() == "---":
        i -= 1
        while i >= 0 and lines[i].strip() == "":
            i -= 1
    return i + 1


def process_post(path: Path, series: str, idx: int, variant: str, entries: dict[int, dict[str, str]], dry_run: bool = False) -> str:
    if variant == "medium":
        return "skipped-medium"
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if variant == "ko":
        lines = rename_ko_references(lines)
    lines = strip_existing_toc(lines)
    lines = [ln for ln in lines if not ln.startswith(TAG_COMMENT_PREFIX)]
    lines = [ln for ln in lines if not ln.startswith(TAG_LINE_PREFIX)]
    ref_idx = find_references_index(lines)
    if ref_idx is None:
        return "no-references-section"
    insert_at = find_toc_insert_point(lines, ref_idx)
    toc_block = build_toc(entries, idx, variant)
    new_lines = lines[:insert_at] + [""] + toc_block + [""] + lines[insert_at:]
    new_lines = collapse_redundant(new_lines)
    new_lines = apply_tag_line(new_lines, series)
    new_text = "\n".join(new_lines) + "\n"
    if new_text != text:
        if not dry_run:
            path.write_text(new_text, encoding="utf-8")
        return "updated"
    return "unchanged"


def collapse_redundant(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        s = line.strip()
        if s == "":
            if out and out[-1].strip() == "":
                continue
        elif s == "---":
            j = len(out) - 1
            while j >= 0 and out[j].strip() == "":
                j -= 1
            if j >= 0 and out[j].strip() == "---":
                continue
        out.append(line)
    while out and out[-1].strip() == "":
        out.pop()
    out.append("")
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Finalize tags, TOC, and ko refs for all series.")
    ap.add_argument("--check", action="store_true",
                    help="Dry-run: report files that would change and exit 1 if any found.")
    args = ap.parse_args()

    totals = {"updated": 0, "unchanged": 0, "no-references-section": 0, "skipped-medium": 0}
    would_change: list[str] = []
    catalog = {e.id: e for e in load_catalog()}
    for series_id in sorted(SERIES_TAGS):
        entry = catalog.get(series_id)
        if entry is None:
            print(f"SKIP not in series.yaml: {series_id}")
            continue
        if not is_present(entry):
            print(f"SKIP not on disk: {series_id} ({entry.path.relative_to(ROOT)})")
            continue
        series_dir = entry.path
        print(f"== {series_id} ({series_dir.relative_to(ROOT)})")
        variants = collect_series(series_dir)
        for variant, entries in variants.items():
            for idx, info in sorted(entries.items()):
                path = series_dir / variant / info["filename"]
                if not path.exists():
                    continue
                if args.check:
                    r = process_post(path, series_id, idx, variant, entries, dry_run=True)
                else:
                    r = process_post(path, series_id, idx, variant, entries)
                totals[r] = totals.get(r, 0) + 1
                if r == "updated":
                    rel = str(path.relative_to(ROOT))
                    would_change.append(rel)
                    print(f"  {'would-update' if args.check else 'updated':12s} {rel}")
                elif r not in ("unchanged", "skipped-medium"):
                    print(f"  {r:12s} {path.relative_to(ROOT)}")
    print("\nTotals:")
    for k, v in sorted(totals.items()):
        print(f"  {k}: {v}")
    if args.check and would_change:
        print(f"\nCheck failed: {len(would_change)} file(s) need finalize-posts.py to be run.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
