---
title: 'Chunking strategies — optimizing by document type'
series: document-ingestion-101
episode: 2
language: en
status: draft
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

> Document Ingestion 101 (2/6)

Example code: [github.com/yeongseon-books/document-ingestion-101](https://github.com/yeongseon-books/document-ingestion-101/tree/main/en/02-chunking-strategies)

Chunking splits documents into units small enough to embed. Chunks that are too large pull in irrelevant context alongside the relevant passage. Chunks that are too small leave the LLM without enough context to generate a useful answer. The right chunk size depends on the document type.

Topics:

- fixed-size chunking vs semantic-boundary chunking
- deep dive into RecursiveCharacterTextSplitter
- per-document-type parameter presets
- heading-aware chunking for structured documents

---

## Fixed-size vs semantic-boundary chunking

**Fixed-size chunking**: split at a fixed character count. Fast and predictable but may break mid-sentence.

**Semantic-boundary chunking**: split at natural boundaries like paragraphs, sentences, or headings. Better context preservation but uneven chunk sizes.

LangChain's `RecursiveCharacterTextSplitter` is the practical middle ground: it tries separators in priority order and splits only when the current chunk would exceed the size limit.

---

## RecursiveCharacterTextSplitter in depth

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

def analyze_chunks(text: str, chunk_size: int, chunk_overlap: int, separators: list[str]) -> dict:
    """Return statistics for a given chunking configuration."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    chunks = splitter.split_text(text)
    sizes = [len(c) for c in chunks]
    return {
        "chunk_count": len(chunks),
        "avg_size": sum(sizes) / len(sizes) if sizes else 0,
        "min_size": min(sizes) if sizes else 0,
        "max_size": max(sizes) if sizes else 0,
        "chunks": chunks,
    }

tech_doc = """
# Python Async Programming

## asyncio introduction

asyncio is Python's standard library framework for async I/O.
It lets a single thread handle many I/O operations concurrently.
It exploits wait time in network requests and file reads — not CPU work.

## Core concepts

A coroutine is a special function defined with async def.
The await keyword suspends execution until another coroutine completes.
The event loop manages the scheduling of coroutines.

## Basic pattern

```python
import asyncio

async def fetch_data(url: str) -> str:
    await asyncio.sleep(1)  # simulates HTTP request
    return f"data: {url}"

async def main():
    result = await fetch_data("https://example.com")
    print(result)

asyncio.run(main())
```

## Parallel execution

asyncio.gather() runs multiple coroutines concurrently.
Wall time drops significantly compared to sequential execution.
"""

configs = [
    {"chunk_size": 100, "chunk_overlap": 20, "desc": "small (100 chars)"},
    {"chunk_size": 300, "chunk_overlap": 50, "desc": "medium (300 chars)"},
    {"chunk_size": 600, "chunk_overlap": 100, "desc": "large (600 chars)"},
]

for config in configs:
    stats = analyze_chunks(
        text=tech_doc,
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        separators=["\n\n", "\n", ". ", " "],
    )
    print(f"\n{config['desc']}:")
    print(f"  chunks: {stats['chunk_count']}")
    print(f"  avg size: {stats['avg_size']:.0f} chars")
    print(f"  range: {stats['min_size']}–{stats['max_size']} chars")
```

---

## Per-document-type parameter presets

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNKING_PRESETS = {
    "legal": {
        # Legal: preserve article structure
        "chunk_size": 800,
        "chunk_overlap": 150,
        "separators": ["\n\n", "\n", ". "],
        "reason": "large chunks keep article numbers and their content together",
    },
    "news": {
        # News: short, self-contained paragraphs
        "chunk_size": 300,
        "chunk_overlap": 30,
        "separators": ["\n\n", "\n", ". "],
        "reason": "news paragraphs are typically 200–400 chars and self-contained",
    },
    "technical": {
        # Technical docs: preserve code block boundaries
        "chunk_size": 500,
        "chunk_overlap": 100,
        "separators": ["\n\n", "\n", "```", ". ", " "],
        "reason": "avoid splitting code blocks mid-block",
    },
    "academic": {
        # Academic papers: preserve section structure
        "chunk_size": 600,
        "chunk_overlap": 120,
        "separators": ["\n\n\n", "\n\n", "\n", ". "],
        "reason": "preserve section and paragraph structure",
    },
    "faq": {
        # FAQ: keep Q+A pairs together
        "chunk_size": 400,
        "chunk_overlap": 0,  # overlap would duplicate Q or A fragments
        "separators": ["\n\n", "Q:", "A:"],
        "reason": "question and answer must stay in the same chunk",
    },
}

def get_splitter(doc_type: str) -> RecursiveCharacterTextSplitter:
    """Return a splitter configured for the given document type."""
    preset = CHUNKING_PRESETS.get(doc_type, CHUNKING_PRESETS["technical"])
    return RecursiveCharacterTextSplitter(
        chunk_size=preset["chunk_size"],
        chunk_overlap=preset["chunk_overlap"],
        separators=preset["separators"],
    )

legal_text = """
Article 1 (Purpose)
The purpose of this Act is to protect the rights and interests of individuals
by providing for the processing and protection of personal information,
thereby realizing the dignity and worth of the individual.

Article 2 (Definitions)
The terms used in this Act are defined as follows:
1. "Personal information" means information about a living individual
that makes it possible to identify the individual by name, resident registration
number, image, or other information.
2. "Processing" means collection, generation, connection, interlinking,
recording, storage, retention, processing, editing, retrieval, output,
correction, recovery, use, provision, disclosure, or destruction.

Article 3 (Principles of personal information protection)
A personal information controller shall clarify the purpose of processing
personal information and collect only the minimum personal information
lawfully and legitimately within the scope necessary for the purpose.
"""

legal_splitter = get_splitter("legal")
legal_chunks = legal_splitter.split_text(legal_text)
print(f"legal document chunk count: {len(legal_chunks)}")
for i, chunk in enumerate(legal_chunks, start=1):
    print(f"  [{i}] {chunk[:80]}...")
```

---

## Heading-aware chunking for structured documents

```python
import re
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

@dataclass
class Section:
    heading: str
    level: int
    content: str

def split_by_headings(markdown_text: str) -> list[Section]:
    """Split markdown text at heading boundaries."""
    pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(markdown_text))

    sections = []
    for i, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        content = markdown_text[start:end].strip()
        if content:
            sections.append(Section(heading=heading, level=level, content=content))

    return sections

def heading_aware_chunks(markdown_text: str, max_chunk_size: int = 500) -> list[dict]:
    """Chunk a markdown document while preserving heading structure."""
    sections = split_by_headings(markdown_text)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". "],
    )

    chunks = []
    for section in sections:
        if len(section.content) > max_chunk_size:
            for sub in splitter.split_text(section.content):
                chunks.append({"heading": section.heading, "level": section.level, "text": sub})
        else:
            chunks.append({"heading": section.heading, "level": section.level, "text": section.content})

    return chunks

sample_md = """
# Cloud Architecture Design Principles

## Scalability

Design for horizontal scaling (scale-out) as the default.
Keep state in external stores (Redis, DB); keep servers stateless.
Distribute traffic across instances with a load balancer.

## High availability

Eliminate single points of failure.
Deploy across multiple availability zones.
Configure health checks and automatic failover.

## Security

Apply the principle of least privilege.
Encrypt data in transit and at rest.
Log access events and monitor for anomalies.
"""

heading_chunks = heading_aware_chunks(sample_md)
print(f"heading-aware chunk count: {len(heading_chunks)}")
for chunk in heading_chunks:
    print(f"\n  [H{chunk['level']}: {chunk['heading']}]")
    print(f"  {chunk['text'][:100]}...")
```

---

## Conclusion

Identify the document type before choosing a chunking strategy. Legal documents and FAQs have structural constraints that must be preserved in the chunks — otherwise, retrieved context loses meaning. Technical documentation benefits from code-block-aware separators. The next post covers metadata design: attaching structured metadata to each chunk and using it to filter retrieval results.

<!-- toc:begin -->
## In this series

- [PDF parsing and text extraction](./01-pdf-parsing.md)
- **Chunking strategies — optimizing by document type (current)**
- Metadata design and filtering (upcoming)
- Incremental indexing — updating only changed documents (upcoming)
- Multi-format document pipeline (upcoming)
- Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

---

## References

- [LangChain TextSplitter docs](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [Chunking strategies comparison (Pinecone)](https://www.pinecone.io/learn/chunking-strategies/)
- [RecursiveCharacterTextSplitter guide](https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter/)

Tags: RAG, Document Processing, LangChain, Python
