---
title: 'Chunking strategies — optimizing by document type'
series: document-ingestion-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-01'
---

# Chunking strategies — optimizing by document type

## Questions this post answers

- Should FAQ pages, manuals, and policy documents use the same chunk size?
- How does RecursiveCharacterTextSplitter decide where to split?
- Which quick stats should you inspect before embedding the chunks?

> Chunking is not just cutting text smaller; it is designing the smallest context unit retrieval can still trust.

Example code: `/root/Github/document-ingestion-101/en/02-chunking-strategies/main.py`

![Questions this post answers](../../../assets/document-ingestion-101/02/02-01-questions-this-post-answers.en.png)
A bad chunking choice leaks into every later stage. Too small means broken context, too large means noisy retrieval.

This example runs FAQ, manual, and policy-style text through the same splitter and shows with numbers why per-document presets matter.

## Runnable example

```python
from __future__ import annotations

from statistics import mean

from langchain_text_splitters import RecursiveCharacterTextSplitter

SAMPLES = {
    'faq': 'Question: what is the upload limit? Answer: the default limit is 20MB and can be tuned. '
    'Question: how do we reprocess failed files? Answer: rerun only the failed documents in the incremental job. ' * 4,
    'manual': '# Deployment guide

1. Review the config file.
2. Validate sample documents before rollout.
3. Check logs and chunk counts after deployment.

'
    'When the structure is explicit, larger chunks can stay readable. ' * 4,
    'policy': 'Policy documents use long paragraphs and repeated definitions. They describe access control, retention, and deletion '
    'rules together, so context breaks if the overlap is too small. ' * 5,
}

CONFIGS = {
    'faq': {'chunk_size': 120, 'chunk_overlap': 20},
    'manual': {'chunk_size': 220, 'chunk_overlap': 40},
    'policy': {'chunk_size': 320, 'chunk_overlap': 60},
}

def summarize(name: str, text: str, chunk_size: int, chunk_overlap: int) -> None:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=['

', '
', '. ', ' '],
    )
    chunks = splitter.split_text(text)
    sizes = [len(chunk) for chunk in chunks]
    print(f'[{name}] chunks={len(chunks)} avg={mean(sizes):.1f} min={min(sizes)} max={max(sizes)}')
    print(f'  first_chunk={chunks[0][:90]!r}')

def main() -> None:
    for name, text in SAMPLES.items():
        summarize(name, text, **CONFIGS[name])

if __name__ == '__main__':
    main()
```

## How to run it

```bash
python main.py
```

## Verified run output

```text
[faq] chunks=8 avg=97.9 min=86 max=109
[manual] chunks=5 avg=163.8 min=64 max=205
[policy] chunks=4 avg=224.8 min=118 max=297
```

## What to notice in this code

- The example makes it obvious that small changes in `chunk_size`, `chunk_overlap`, and `separators` change the output a lot.
- It prints min and max length alongside the average so skewed chunks stand out immediately.
- The first-chunk preview is a cheap way to verify that headings and numbered lists survive the split.

## Where engineers get confused

- Better chunking does not always mean smaller chunks. Quality depends on boundary choice and overlap together.
- Per-document presets are starting points, not universal truths. Retrieval logs should tune them later.
- Sentence boundaries are not always the best boundary. In manuals, preserving structure can matter more.

## Checklist

- [ ] You split presets by at least three document types.
- [ ] You checked chunk count and length distribution numerically.
- [ ] You used the first-chunk preview to validate structure preservation.
- [ ] You defined thresholds for chunks that are too long or too short before embedding.

<!-- blog-only:start -->

## Summary

Chunking should vary by document type, and comparing the output numerically is the fastest quality check.

The next post shows which metadata fields make those chunks filterable at retrieval time.

<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [PDF parsing and text extraction](./01-pdf-parsing.md)
- **Chunking strategies — optimizing by document type (current)**
- Metadata design and filtering (upcoming)
- Incremental indexing — updating only changed documents (upcoming)
- Multi-format document pipeline (upcoming)
- Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

## References

- https://python.langchain.com/docs/how_to/recursive_text_splitter/

Tags: RAG, Document Processing, LangChain, Python
