---
title: "Document Ingestion 101 (2/6): Chunking strategies — optimizing by document type"
series: document-ingestion-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-15'
seo_description: Chunking is not just cutting text smaller; it is designing the smallest
  context unit retrieval can still trust.
---

# Document Ingestion 101 (2/6): Chunking strategies — optimizing by document type

Chunking is where many retrieval systems quietly lose quality. A splitter that works well for an FAQ can easily damage the structure of a manual or a policy document.

This is the second post in the Document Ingestion 101 series. Here, we compare chunking presets by document shape and look at the quick signals that tell you whether a split is trustworthy.

## Questions to Keep in Mind

- Why does one chunk_size for every document type make retrieval quality unstable?
- In what order does a Recursive splitter give up boundaries while splitting text?
- What should be reviewed before embedding to catch bad chunks quickly?

## Big Picture

![Chunking strategy selection flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-01-chunking-flow-by-document-type.en.png)

*Chunking strategy selection flow*

This picture shows different document types passing through splitter settings into searchable chunks. Good chunking is not choosing one size; it is matching document structure to retrieval questions.

> Chunking is not just cutting text smaller; it is designing the smallest context unit retrieval can still trust.

## Chunking flow by document type

Even with one splitter, the starting chunk size and overlap should differ by document shape.

## Recursive splitter fallback order

![Recursive separator fallback flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-02-recursive-splitter-fallback-order.en.png)

*Recursive separator fallback flow*
The strength of recursive splitting is that it preserves larger semantic boundaries first and only falls back when needed.

## Runnable example

```python
from __future__ import annotations

from statistics import mean

from langchain_text_splitters import RecursiveCharacterTextSplitter

SAMPLES = {
    'faq': 'Question: what is the upload limit? Answer: the default limit is 20MB and can be tuned. '
    'Question: how do we reprocess failed files? Answer: rerun only the failed documents in the incremental job. ' * 4,
    'manual': '# Deployment guide\n\n1. Review the config file.\n2. Validate sample documents before rollout.\n3. Check logs and chunk counts after deployment.\n\n'
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
        separators=['\n\n', '\n', '. ', ' '],
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

Those numbers can make the policy preset look strongest at first glance. But fewer chunks alone do not mean better retrieval. In practice, you still need to inspect **which structure survived** and **which failure mode the preset introduced**.

## Starting presets by document type

| Document type | Starting `chunk_size` | Starting `chunk_overlap` | First signal to inspect | Common failure |
| --- | ---: | ---: | --- | --- |
| FAQ | 120 | 20 | Does one chunk still contain both question and answer? | The question survives but the answer drifts away |
| Manual | 220 | 40 | Do heading and numbered steps stay together? | Step 2 lands in another chunk and execution order gets fuzzy |
| Policy | 320 | 60 | Do definitions and exception clauses stay together? | Exception text gets detached from the surrounding rule |

The key is not the number itself but the failure mode each document shape produces. FAQs degrade when question-answer pairs split apart. Manuals degrade when step order breaks. Policy documents degrade when long clauses lose their nearby exceptions.

## Quick review loop before embedding

Before paying embedding cost, a lightweight review loop catches most bad presets early. I usually check **length distribution**, **first and last chunk preview**, and **warning counts by document type**.

```python
from __future__ import annotations

from collections.abc import Iterable

def review_chunks(name: str, chunks: list[str], min_len: int, max_len: int) -> None:
    too_short = [chunk for chunk in chunks if len(chunk) < min_len]
    too_long = [chunk for chunk in chunks if len(chunk) > max_len]
    print(f'[{name}] warnings short={len(too_short)} long={len(too_long)} total={len(chunks)}')
    if chunks:
        print(f'  first={chunks[0][:100]!r}')
        print(f'  last={chunks[-1][:100]!r}')

def batch_review(items: Iterable[tuple[str, list[str]]]) -> None:
    thresholds = {
        'faq': (60, 160),
        'manual': (100, 260),
        'policy': (140, 360),
    }
    for name, chunks in items:
        min_len, max_len = thresholds[name]
        review_chunks(name, chunks, min_len=min_len, max_len=max_len)
```

This is simple code, but it is operationally useful. Retrieval tuning gets much faster once you separate obviously too-short chunks from too-long chunks and define thresholds per document family.

## Failure mode example: tidy numbers, damaged structure

Smaller chunks can still look numerically neat while destroying the unit retrieval actually needed to preserve.

```text
[faq-small] chunks=14 avg=58.1 min=21 max=79
  first_chunk='Question: what is the upload limit?'
  last_chunk='incremental job.'

[manual-small] chunks=11 avg=73.5 min=18 max=97
  first_chunk='# Deployment guide'
  last_chunk='Check logs and chunk counts after deployment.'
```

The problem becomes obvious once you read the previews. FAQ chunks stop carrying full answers, and the manual loses step grouping. The count got higher, but the retrieval unit got worse.

## What to notice in this code

### How chunk overlap preserves context

![Chunk boundaries with overlap flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-01-how-chunk-overlap-preserves-context.en.png)

*Chunk boundaries with overlap flow*
Overlap is the handoff mechanism that keeps a bit of prior context alive across adjacent chunks.

- The example makes it obvious that small changes in `chunk_size`, `chunk_overlap`, and `separators` change the output a lot.
- It prints min and max length alongside the average so skewed chunks stand out immediately.
- The first-chunk preview is a cheap way to verify that headings and numbered lists survive the split.

## Where engineers get confused

### How to review chunk quality

![Chunk quality review flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-02-how-to-review-chunk-quality.en.png)

*Chunk quality review flow*
Chunk count alone is too weak. Distribution and preview checks reveal whether the split still respects structure.

- Better chunking does not always mean smaller chunks. Quality depends on boundary choice and overlap together.
- Per-document presets are starting points, not universal truths. Retrieval logs should tune them later.
- Sentence boundaries are not always the best boundary. In manuals, preserving structure can matter more.

## Checklist

- [ ] You split presets by at least three document types.
- [ ] You checked chunk count and length distribution numerically.
- [ ] You used the first-chunk preview to validate structure preservation.
- [ ] You defined thresholds for chunks that are too long or too short before embedding.

## How this gets tuned in practice

There is rarely a perfect preset on day one. The usual workflow is to set a starting profile per document type, then revisit the retrieval log for **boundaries that cut too aggressively** and **sentences that should have stayed together**. FAQs care about keeping question-answer pairs intact. Manuals care about keeping headings and steps together. Policy documents care about keeping exceptions adjacent to the rule they qualify.

Just as important, do not confuse chunking failure with embedding-model failure too early. When search results look wrong, inspect chunk previews and warning counts before you swap the model.

## Answering the Opening Questions

- **Why does one chunk_size for every document type make retrieval quality unstable?**
  Policies, FAQs, code, and tables have different semantic boundaries; one size can cut context in one type and mix noise in another.

- **In what order does a Recursive splitter give up boundaries while splitting text?**
  A Recursive splitter tries larger separators first and falls back to smaller ones until it can fit the target size.

- **What should be reviewed before embedding to catch bad chunks quickly?**
  Review length distribution, realized overlap, heading/body separation, very short or long chunks, and source-location metadata before embedding.

<!-- toc:begin -->
## In this series

- [Document Ingestion 101 (1/6): PDF parsing and text extraction](./01-pdf-parsing.md)
- **Document Ingestion 101 (2/6): Chunking strategies — optimizing by document type (current)**
- Document Ingestion 101 (3/6): Metadata design and filtering (upcoming)
- Document Ingestion 101 (4/6): Incremental indexing — updating only changed documents (upcoming)
- Document Ingestion 101 (5/6): Multi-format document pipeline (upcoming)
- Document Ingestion 101 (6/6): Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

## References

### Official docs

- [LangChain - How to recursively split text by characters](https://python.langchain.com/docs/how_to/recursive_text_splitter/)
- [LangChain text splitters integration package](https://docs.langchain.com/oss/python/integrations/splitters/index)

### Verification-friendly sources

- [LangChain RecursiveCharacterTextSplitter API reference](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html)
- [The Unicode Standard - Text segmentation overview](https://www.unicode.org/reports/tr29/)

Tags: RAG, Document Processing, LangChain, Python
