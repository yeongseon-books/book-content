---
title: 'Chunking strategies — how to split long documents'
series: vector-search-101
episode: 5
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Vector Search
- FAISS
- Embeddings
- Python
last_reviewed: '2026-05-01'
---

# Chunking strategies — how to split long documents

> Vector Search 101 (5/6)

Example code: [github.com/yeongseon-books/vector-search-101](https://github.com/yeongseon-books/vector-search-101/tree/main/en/05-chunking-strategies)

Embedding models have a hard token limit. `all-MiniLM-L6-v2` processes at most 256 subword tokens. A single page of a PDF often exceeds that. Feeding a long document as one input either truncates it — losing content at the boundary — or compresses too much information into one vector, which dilutes retrieval precision.

Chunking is the process of splitting a long document into embedding-sized pieces. How you split directly affects retrieval quality. Chunks that are too small lose context; chunks that are too large mix unrelated content.

This post covers five things:

- the core parameters: chunk size and overlap
- implementing fixed-size chunking from scratch
- using LangChain's `RecursiveCharacterTextSplitter`
- how chunk boundaries affect retrieval quality
- choosing a chunking strategy for different document types

---

## Chunk size and overlap

Two parameters control chunking: `chunk_size` and `chunk_overlap`.

**chunk_size**: the maximum length of one chunk, measured in characters or tokens. A common starting range is 200–500 tokens.

**chunk_overlap**: the number of characters shared between adjacent chunks. Without overlap, a sentence may land exactly on a chunk boundary and be split in half. With overlap, the same content appears in two consecutive chunks, so content near any boundary is still retrievable.

```
original: A B C D E F G H I J (each letter represents one word)

chunk_size=4, chunk_overlap=1:
chunk 0: A B C D
chunk 1: D E F G   ← D repeats
chunk 2: G H I J   ← G repeats
```

A common rule of thumb sets overlap at 10–20% of chunk size. Too much overlap inflates index size without proportional benefit.

---

## Fixed-size chunking from scratch

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

This version is for illustration only. Splitting by raw character count often cuts sentences in the middle. For production use, the approach below works better.

---

## RecursiveCharacterTextSplitter

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

The `separators` list is tried in order. If `\n\n` produces a piece within `chunk_size`, that split is used. Otherwise the splitter tries the next separator. The result is chunks that usually end at paragraph or sentence boundaries.

---

## Full pipeline: chunking to FAISS

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

---

## How chunk size affects retrieval

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
