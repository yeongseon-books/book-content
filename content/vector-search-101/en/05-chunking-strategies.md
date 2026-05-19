---
episode: 5
language: en
last_reviewed: '2026-05-15'
series: vector-search-101
status: publish-ready
tags:
- Vector Search
- FAISS
- Embeddings
- Python
targets:
  ebook: true
  medium: true
  mkdocs: true
  tistory: false
title: Chunking strategies — how to split long documents
seo_description: Optimize retrieval quality by choosing effective chunking strategies, adjusting chunk size, and managing overlap to preserve context in vector search.
---

# Chunking strategies — how to split long documents

Embedding models have a hard token limit. `all-MiniLM-L6-v2` processes at most 256 subword tokens. A single page of a PDF often exceeds that. Feeding a long document as one input either truncates it — losing content at the boundary — or compresses too much information into one vector, which dilutes retrieval precision.

Chunking is the process of splitting a long document into embedding-sized pieces. How you split directly affects retrieval quality. Chunks that are too small lose context; chunks that are too large mix unrelated content.

This is post 5 in the Vector Search 101 series.

Here chunking is treated as a retrieval design choice, not a preprocessing afterthought. This post covers five things:

- the core parameters: chunk size and overlap
- implementing fixed-size chunking from scratch
- using LangChain's `RecursiveCharacterTextSplitter`
- how chunk boundaries affect retrieval quality
- choosing a chunking strategy for different document types

Example code: [github.com/yeongseon-books/vector-search-101](https://github.com/yeongseon-books/vector-search-101/tree/main/en/05-chunking-strategies)

![Chunk size and overlap structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-01-chunking-strategies-how-to-split-long-do.en.png)

*Chunk size and overlap structure*
<!-- ebook-only:start -->

**The key idea**: chunk size and overlap control retrieval quality. Too large adds noise; too small loses context.

## Where this chapter fits

This is chapter 5 of 6 in the series.
The previous chapter covered **FAISS fundamentals — fast approximate nearest-neighbor search**.
After this chapter, the next one moves on to **Vector search pipeline — from document ingestion to query**.
<!-- ebook-only:end -->

---

> Chunking is not just extra preprocessing work. It is a design step where you decide what unit of context your retrieval system will remember.

## Questions this chapter answers

- Why is embedding a long document as a single chunk a bad idea?
- When does fixed-size, sentence-based, or semantic chunking each shine or fall apart?
- Why introduce overlap between chunks, and how do you pick the ratio?
- How do you chunk documents that mix code, tables, and markdown headings without losing recall?
- What does storing metadata (section title, source) on each chunk actually buy you?

## Chunk size and overlap

![Chunk size and overlap structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-01-chunk-size-and-overlap.en.png)

*Chunk size and overlap structure*
Two parameters control chunking: `chunk_size` and `chunk_overlap`.

**chunk_size**: the maximum length of one chunk, measured in characters or tokens. A common starting range is 200–500 tokens.

**chunk_overlap**: the number of characters shared between adjacent chunks. Without overlap, a sentence may land exactly on a chunk boundary and be split in half. With overlap, the same content appears in two consecutive chunks, so content near any boundary is still retrievable.

```text
original: A B C D E F G H I J (each letter represents one word)

chunk_size=4, chunk_overlap=1:
chunk 0: A B C D
chunk 1: D E F G   ← D repeats
chunk 2: G H I J   ← G repeats
```

A common rule of thumb sets overlap at 10–20% of chunk size. Too much overlap inflates index size without proportional benefit.

---

## Fixed-size chunking from scratch

![Fixed size chunking execution flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-02-fixed-size-chunking-from-scratch.en.png)

*Fixed size chunking execution flow*
This implementation makes the concept concrete.

```python
def chunk_text(
    text: str,
    chunk_size: int = 200,
    chunk_overlap: int = 20,
) -> list[str]:
    """Fixed-size chunking by character count."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk:
            chunks.append(chunk)
        start += chunk_size - chunk_overlap
    return chunks

sample_text = (
    "Vector search converts text into numeric vectors for meaning-based retrieval. "
    "Embedding models place semantically similar text close together in vector space. "
    "FAISS is a high-speed vector search library developed at Facebook AI Research. "
    "Chunking strategies split long documents into units the embedding model can process. "
    "Choosing the right chunk size improves retrieval accuracy. "
    "Overlap settings reduce context loss at chunk boundaries."
)

chunks = chunk_text(sample_text, chunk_size=100, chunk_overlap=20)

print(f"total text length: {len(sample_text)} chars")
print(f"number of chunks: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"\n[{i}] {len(chunk)} chars: {chunk[:60]}...")
```

<!-- injected-output:start -->
**Output**

    total text length: 439 chars
    number of chunks: 6

    [0] 100 chars: Vector search converts text into numeric vectors for meaning...

    [1] 100 chars: bedding models place semantically similar text close togethe...

    [2] 100 chars: AISS is a high-speed vector search library developed at Face...

    [3] 100 chars: unking strategies split long documents into units the embedd...

    [4] 100 chars: s. Choosing the right chunk size improves retrieval accuracy...

    [5] 39 chars: educe context loss at chunk boundaries....

<!-- injected-output:end -->

This version is for illustration only. Splitting by raw character count often cuts sentences in the middle. For production use, the approach below works better.

---

## RecursiveCharacterTextSplitter

![Separator priority fallback path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-03-recursivecharactertextsplitter.en.png)

*Separator priority fallback path*
LangChain's `RecursiveCharacterTextSplitter` tries to split at natural boundaries. It works down a priority list of separators, trying `\n\n` first, then `\n`, then `. `, then space, finally individual characters. This keeps sentences intact in most cases.

```bash
pip install langchain-text-splitters
```

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)

document = """
Vector search converts text into numeric vectors for meaning-based retrieval.
Unlike keyword search, it matches content even when phrasing differs.

Embedding models place semantically similar text close together in vector space.
The sentence-transformers library provides models specialized for sentence-level embeddings.
all-MiniLM-L6-v2 is a lightweight model practical for CPU inference.

FAISS is a high-speed vector search library developed at Facebook AI Research.
It supports both exact and approximate search and can handle billions of vectors.
IndexFlatIP is an exact inner-product index equivalent to cosine search on normalized vectors.
"""

chunks = splitter.split_text(document)

print(f"number of chunks: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"\n[{i}] {len(chunk)} chars:")
    print(f"  {chunk[:80]}...")
```

<!-- injected-output:start -->
**Output**

    number of chunks: 5

    [0] 147 chars:
      Vector search converts text into numeric vectors for meaning-based retrieval.
    Un...

    [1] 173 chars:
      Embedding models place semantically similar text close together in vector space....

    [2] 68 chars:
      all-MiniLM-L6-v2 is a lightweight model practical for CPU inference....

    [3] 160 chars:
      FAISS is a high-speed vector search library developed at Facebook AI Research.
    I...

    [4] 94 chars:
      IndexFlatIP is an exact inner-product index equivalent to cosine search on norma...

<!-- injected-output:end -->

The `separators` list is tried in order. If `\n\n` produces a piece within `chunk_size`, that split is used. Otherwise the splitter tries the next separator. The result is chunks that usually end at paragraph or sentence boundaries.

---

## Full pipeline: chunking to FAISS

![Execution path from chunking to FAISS search](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-04-full-pipeline-chunking-to-faiss.en.png)

*Execution path from chunking to FAISS search*
Connecting chunking to embedding to index in one block.

```python
import json

import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30,
    separators=["\n\n", "\n", ". ", " ", ""],
)

document = """
Vector search converts text into numeric vectors for meaning-based retrieval.
Unlike keyword search, it matches content even when phrasing differs.

Embedding models place semantically similar text close together in vector space.
The sentence-transformers library provides models specialized for sentence-level embeddings.

FAISS is a high-speed vector search library developed at Facebook AI Research.
It supports both exact and approximate search and can handle billions of vectors.

Chunking strategies split long documents into units the embedding model can process.
Tuning chunk_size and chunk_overlap is necessary to achieve good retrieval quality.
"""

chunks = splitter.split_text(document)
print(f"chunks: {len(chunks)}")

vectors = np.array(embedding_model.embed_documents(chunks), dtype=np.float32)
dimension = vectors.shape[1]

index = faiss.IndexFlatIP(dimension)
index.add(vectors)

def search(query: str, top_k: int = 3) -> list[tuple[float, str]]:
    q_vec = np.array([embedding_model.embed_query(query)], dtype=np.float32)
    scores, indices = index.search(q_vec, top_k)
    return [
        (float(scores[0][i]), chunks[indices[0][i]])
        for i in range(top_k)
        if indices[0][i] != -1
    ]

for query in ["how vector search works", "FAISS library features", "setting chunk size"]:
    print(f"\nquery: '{query}'")
    for rank, (score, text) in enumerate(search(query, top_k=2), start=1):
        print(f"  [{rank}] {score:.4f} — {text[:60]}...")
```

<!-- injected-output:start -->
**Output**

    chunks: 4

    query: 'how vector search works'
      [1] 0.6897 — Vector search converts text into numeric vectors for meaning...
      [2] 0.5140 — FAISS is a high-speed vector search library developed at Fac...

    query: 'FAISS library features'
      [1] 0.5687 — FAISS is a high-speed vector search library developed at Fac...
      [2] 0.1739 — Chunking strategies split long documents into units the embe...

    query: 'setting chunk size'
      [1] 0.5347 — Chunking strategies split long documents into units the embe...
      [2] 0.0345 — FAISS is a high-speed vector search library developed at Fac...

<!-- injected-output:end -->

---

## Storing metadata with each chunk

Raw chunk text is not always enough. In production, you usually want to know which document produced the chunk, which section it came from, and where it sits in the source. That metadata makes citation, debugging, and deletion much easier.

```python
from dataclasses import asdict, dataclass

@dataclass
class ChunkRecord:
    chunk_id: str
    source: str
    section: str
    offset: int
    text: str

def build_chunk_records(chunks: list[str]) -> list[dict]:
    records = []
    for idx, chunk in enumerate(chunks):
        records.append(
            asdict(
                ChunkRecord(
                    chunk_id=f"doc-001-{idx}",
                    source="vector-search-notes.md",
                    section="FAISS basics" if idx < 2 else "chunking",
                    offset=idx * 170,
                    text=chunk,
                )
            )
        )
    return records

records = build_chunk_records(chunks)
print(records[0])
```

<!-- injected-output:start -->
**Output**

    {'chunk_id': 'doc-001-0', 'source': 'vector-search-notes.md', 'section': 'FAISS basics', 'offset': 0, 'text': 'Vector search converts text into numeric vectors for meaning-based retrieval.\nUnlike keyword search, it matches content even when phrasing differs.'}

<!-- injected-output:end -->

Metadata does not raise semantic accuracy by itself, but it raises operational quality. A retrieval result becomes much easier to inspect when you can see where it came from.

## What happens when chunk_size changes

Chunking strategy has to be validated through retrieval, not through aesthetics. Even a small experiment with two chunk sizes shows how ranking behavior shifts.

```python
import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

document = """
Vector search converts text into numeric vectors for meaning-based retrieval.
Unlike keyword search, it matches content even when phrasing differs.

FAISS is a high-speed vector search library developed at Facebook AI Research.
It supports both exact and approximate search.

Chunking strategies decide how much context each vector should carry.
Large chunks preserve context but can mix unrelated details.
Small chunks are precise but may lose the sentence that explains the point.
"""

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

def run_experiment(chunk_size: int) -> None:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=30,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(document)
    vectors = np.array(embedding_model.embed_documents(chunks), dtype=np.float32)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    query = "why chunk size affects retrieval quality"
    q_vec = np.array([embedding_model.embed_query(query)], dtype=np.float32)
    scores, indices = index.search(q_vec, 2)

    print(f"\nchunk_size={chunk_size}, chunks={len(chunks)}")
    for score, idx in zip(scores[0], indices[0]):
        print(f"  {score:.4f} | {chunks[idx][:70]}")

run_experiment(120)
run_experiment(260)
```

<!-- injected-output:start -->
**Output**

    chunk_size=120, chunks=5
      0.6908 | Chunking strategies decide how much context each vector should carry.
      0.3707 | Large chunks preserve context but can mix unrelated details.

    chunk_size=260, chunks=3
      0.6402 | Chunking strategies decide how much context each vector should carry.
      0.4684 | FAISS is a high-speed vector search library developed at Facebook AI Research.

<!-- injected-output:end -->

Small chunks surface direct answers more aggressively. Larger chunks keep more surrounding context, but they also pull in more neighboring detail. The right balance depends on the query shape: FAQ-style retrieval and long-form policy retrieval rarely want the same chunk size.

## How chunk size affects retrieval

![Retrieval quality across chunk sizes](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-05-how-chunk-size-affects-retrieval.en.png)

*Retrieval quality across chunk sizes*
Chunks that are too small lack enough context to match a query accurately. Chunks that are too large mix unrelated content and dilute the semantic signal.

Typical starting points:

| Document type | chunk_size | chunk_overlap |
|---|---|---|
| Short paragraphs, news | 200–300 | 20–30 |
| Technical docs, manuals | 300–500 | 30–50 |
| Legal documents, papers | 500–800 | 50–100 |

Start with a reasonable default, measure retrieval quality on your actual data, and adjust from there. Chunking parameters are empirical — no universal optimal value exists.

---

## Conclusion

Chunking is often the biggest lever for retrieval quality in a vector search system. The embedding model and index type matter, but poor chunking limits what any model can do with the input.

The final post assembles everything — document loading, chunking, embedding, indexing, and querying — into one end-to-end pipeline.

## Operational checklist

- [ ] Sized chunks and overlap based on the embedding model's token limit
- [ ] Preserved structural info (heading, page) in chunk metadata
- [ ] Applied separate chunking rules to code and tables versus prose
- [ ] Deduplicated near-identical chunks from the same document
- [ ] Tracked document ID and offset so citations remain reachable

<!-- toc:begin -->
## In this series

- [What is an embedding — converting text into vectors](./01-what-is-embedding.md)
- [HuggingFace embeddings in practice — creating your first vectors with sentence-transformers](./02-huggingface-embeddings.md)
- [Cosine similarity and vector search — computing sentence distances](./03-cosine-similarity.md)
- [FAISS fundamentals — fast approximate nearest-neighbor search](./04-faiss-fundamentals.md)
- **Chunking strategies — how to split long documents (current)**
- Vector search pipeline — from document ingestion to query (upcoming)

<!-- toc:end -->

---

## References

- [LangChain RecursiveCharacterTextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter/)
- [Chunking strategies for LLM applications — Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [sentence-transformers max sequence length](https://www.sbert.net/docs/pretrained_models.html)

Tags: Vector Search, FAISS, Embeddings, Python
