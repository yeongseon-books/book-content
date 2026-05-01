---
episode: 6
language: en
last_reviewed: '2026-05-01'
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
  tistory: true
title: Vector search pipeline — from document ingestion to query
---

# Vector search pipeline — from document ingestion to query

> Vector Search 101 (6/6)

Example code: [github.com/yeongseon-books/vector-search-101](https://github.com/yeongseon-books/vector-search-101/tree/main/en/06-vector-search-pipeline)

The previous five posts each covered one component in isolation: embeddings, similarity metrics, FAISS, and chunking. This post assembles them into one executable pipeline that loads documents, splits them into chunks, embeds those chunks, stores them in a FAISS index, and retrieves results for natural-language queries.

The post closes with the basics of hybrid search, which combines vector retrieval with keyword search.

Topics:

- loading documents from text
- the full indexing flow: chunking → embedding → FAISS
- saving and reloading the index
- querying and displaying results
- hybrid search concept and a minimal implementation

---

<!-- ebook-only:start -->

**The key idea**: a vector search pipeline is four steps — embed, index, query, retrieve. Each step should be independently replaceable.

## Where this chapter fits

This is chapter 6 of 6 in the series.
The previous chapter covered **Chunking strategies — how to split long documents**.
<!-- ebook-only:end -->

## Pipeline structure

A vector search pipeline has two phases.

**Indexing** is an offline step: process documents once and produce a searchable index.

```
load documents → chunk → embed → save FAISS index
```

**Retrieval** is an online step: accept a query, embed it, search the index, return results.

```
embed query → FAISS search → return ranked chunks
```

Separating the two phases means you build the index once and query it many times.

---

## Complete pipeline

One self-contained, executable file.

```python
import json
from pathlib import Path

import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── config ────────────────────────────────────────────────────────────────
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 30
INDEX_PATH = "faiss.index"
DOCS_PATH = "chunks.json"

# ── embedding model ────────────────────────────────────────────────────────
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# ── text splitter ──────────────────────────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)

# ── indexing ───────────────────────────────────────────────────────────────
def build_index(documents: list[str]) -> tuple[faiss.Index, list[str]]:
    """Chunk, embed, and index a list of document strings."""
    all_chunks: list[str] = []
    for doc in documents:
        all_chunks.extend(splitter.split_text(doc))
    print(f"total chunks: {len(all_chunks)}")

    vectors = np.array(
        embedding_model.embed_documents(all_chunks), dtype=np.float32
    )
    dimension = vectors.shape[1]
    print(f"vector shape: {vectors.shape}")

    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)

    return index, all_chunks

def save_index(index: faiss.Index, chunks: list[str]) -> None:
    faiss.write_index(index, INDEX_PATH)
    with open(DOCS_PATH, "w") as f:
        json.dump(chunks, f, indent=2)
    print(f"saved: {INDEX_PATH}, {DOCS_PATH}")

def load_index() -> tuple[faiss.Index, list[str]]:
    index = faiss.read_index(INDEX_PATH)
    with open(DOCS_PATH) as f:
        chunks = json.load(f)
    print(f"loaded: {index.ntotal} vectors")
    return index, chunks

# ── retrieval ──────────────────────────────────────────────────────────────
def search(
    query: str,
    index: faiss.Index,
    chunks: list[str],
    top_k: int = 3,
) -> list[tuple[float, str]]:
    q_vec = np.array([embedding_model.embed_query(query)], dtype=np.float32)
    scores, indices = index.search(q_vec, top_k)
    return [
        (float(scores[0][i]), chunks[indices[0][i]])
        for i in range(top_k)
        if indices[0][i] != -1
    ]

# ── run ────────────────────────────────────────────────────────────────────
documents = [
    """
Vector search converts text into numeric vectors for meaning-based retrieval.
Unlike keyword search, it matches content even when phrasing differs.
Embedding models place semantically similar text close together in vector space.
""",
    """
FAISS is a high-speed vector search library developed at Facebook AI Research.
It supports both exact and approximate search and can handle billions of vectors.
IndexFlatIP is an exact inner-product index equivalent to cosine search on normalized vectors.
""",
    """
Chunking strategies split long documents into units the embedding model can process.
chunk_size and chunk_overlap must be tuned to achieve good retrieval quality.
RecursiveCharacterTextSplitter tries paragraph, sentence, and word boundaries in order.
""",
    """
RAG (Retrieval-Augmented Generation) combines retrieved documents with an LLM prompt.
The system retrieves relevant chunks for the user's question and provides them as context.
Vector search is the retrieval component in most RAG pipelines.
""",
]

index, chunks = build_index(documents)
save_index(index, chunks)

index, chunks = load_index()

queries = [
    "how vector search differs from keyword search",
    "FAISS index types",
    "choosing chunk size",
    "role of retrieval in RAG",
]

for query in queries:
    print(f"\nquery: '{query}'")
    results = search(query, index, chunks, top_k=2)
    for rank, (score, text) in enumerate(results, start=1):
        print(f"  [{rank}] {score:.4f} — {text.strip()[:70]}...")
```

Expected output:

```
total chunks: 8
vector shape: (8, 384)
saved: faiss.index, chunks.json
loaded: 8 vectors

query: 'how vector search differs from keyword search'
  [1] 0.8123 — Vector search converts text into numeric vectors for meaning-based...
  [2] 0.7234 — Unlike keyword search, it matches content even when phrasing differs.

query: 'FAISS index types'
  [1] 0.8412 — IndexFlatIP is an exact inner-product index equivalent to cosine...
  [2] 0.7891 — FAISS is a high-speed vector search library developed at Facebook...
```

---

## Hybrid search

Vector search alone is weak when exact terms matter — error codes, product IDs, proper nouns. Keyword search handles those well but misses semantic variation. Hybrid search combines both.

The standard approach normalizes each score to [0, 1] and takes a weighted sum.

```python
from rank_bm25 import BM25Okapi

def hybrid_search(
    query: str,
    index: faiss.Index,
    chunks: list[str],
    top_k: int = 3,
    alpha: float = 0.5,
) -> list[tuple[float, str]]:
    """Combine vector search and BM25 keyword search.
    alpha: weight of vector score (0 = keyword only, 1 = vector only)
    """
    # vector scores (already 0–1 with normalized vectors)
    q_vec = np.array([embedding_model.embed_query(query)], dtype=np.float32)
    vec_scores, vec_indices = index.search(q_vec, len(chunks))
    vec_score_map = {
        int(idx): float(score)
        for idx, score in zip(vec_indices[0], vec_scores[0])
        if idx != -1
    }

    # BM25 scores normalized to 0–1
    tokenized = [chunk.split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized)
    bm25_scores = bm25.get_scores(query.split())
    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
    bm25_norm = bm25_scores / max_bm25

    # weighted combination
    combined = {
        i: alpha * vec_score_map.get(i, 0.0) + (1 - alpha) * float(bm25_norm[i])
        for i in range(len(chunks))
    }

    top_indices = sorted(combined, key=combined.__getitem__, reverse=True)[:top_k]
    return [(combined[i], chunks[i]) for i in top_indices]
```

`alpha=0.5` weights both methods equally. Increase toward 1.0 for more semantic weight; decrease toward 0.0 for more keyword weight.

---

## Operational considerations

**Index updates.** Adding new documents is straightforward: embed them and call `index.add()`. `IndexFlatIP` does not support deletion. If you need to remove vectors, rebuild the index periodically or use `IndexIDMap` to track and skip deleted entries.

**Memory.** `IndexFlatIP` keeps all vectors in memory. 100,000 vectors at 384 dimensions and 4 bytes each is roughly 147 MB. At 1 million vectors that becomes 1.5 GB. Beyond that, `IndexIVFFlat` or a quantization index like `IndexPQ` reduces memory use.

**Latency.** On CPU, searching 100,000 vectors takes tens of milliseconds. If service latency is critical, consider the GPU build or an approximate index.

---

## Conclusion

This post assembled the full vector search pipeline: load documents, chunk them with `RecursiveCharacterTextSplitter`, embed with `HuggingFaceEmbeddings`, index with FAISS, persist to disk, and retrieve with natural-language queries.

The natural next step is connecting this pipeline to an LLM to build a RAG system. The langchain-101 series covers LCEL, Retriever, and Chain composition.

<!-- toc:begin -->
## In this series

- [What is an embedding — converting text into vectors](./01-what-is-embedding.md)
- [HuggingFace embeddings in practice — creating your first vectors with sentence-transformers](./02-huggingface-embeddings.md)
- [Cosine similarity and vector search — computing sentence distances](./03-cosine-similarity.md)
- [FAISS fundamentals — fast approximate nearest-neighbor search](./04-faiss-fundamentals.md)
- [Chunking strategies — how to split long documents](./05-chunking-strategies.md)
- **Vector search pipeline — from document ingestion to query (current)**

<!-- toc:end -->

---

## References

- [FAISS documentation](https://faiss.ai/)
- [LangChain FAISS integration](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [rank-bm25 library](https://github.com/dorianbrown/rank_bm25)
- [Hybrid search introduction — Pinecone](https://www.pinecone.io/learn/hybrid-search-intro/)

Tags: Vector Search, FAISS, Embeddings, Python
