---
episode: 6
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
title: "Vector Search 101 (6/6): Vector search pipeline — from document ingestion to query"
seo_description: Build an end-to-end vector search pipeline from document ingestion to retrieval, including hybrid search combining keywords and embeddings.
---

# Vector Search 101 (6/6): Vector search pipeline — from document ingestion to query

The previous five posts each covered one component in isolation: embeddings, similarity metrics, FAISS, and chunking. This post assembles them into one executable pipeline that loads documents, splits them into chunks, embeds those chunks, stores them in a FAISS index, and retrieves results for natural-language queries.

The post closes with the basics of hybrid search, which combines vector retrieval with keyword search.

This is the final post in the Vector Search 101 series.

The emphasis here is not on one component in isolation, but on how the whole retrieval system moves from raw documents to ranked answers.

![End to end indexing and retrieval flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-01-vector-search-pipeline-from-document-ing.en.png)
*End to end indexing and retrieval flow*
> A vector search pipeline is not one monolithic feature. It is a structure that separates indexing from retrieval so each part can be replaced independently.

## Questions to Keep in Mind

- What stages make vector search a pipeline rather than one embedding call?
- When is hybrid search safer than pure vector search?
- When documents change, what should drive reindexing and operational logs?

## Pipeline structure

![End to end indexing and retrieval flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-01-pipeline-structure.en.png)

*End to end indexing and retrieval flow*
![Pipeline component connection structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-02-pipeline-structure-2.en.png)

*Pipeline component connection structure*
A vector search pipeline has two phases.

**Indexing** is an offline step: process documents once and produce a searchable index.

```text
load documents → chunk → embed → save FAISS index
```

**Retrieval** is an online step: accept a query, embed it, search the index, return results.

```text
embed query → FAISS search → return ranked chunks
```

Separating the two phases means you build the index once and query it many times.

---

## Complete pipeline

![Build save load search execution path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-03-complete-pipeline.en.png)

*Build save load search execution path*
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

This example ends with 4 chunks because the input corpus is intentionally small. In real systems, the absolute number is not what matters. The real check is whether **document count → chunk count → index vector count** changes in the way you expect after a pipeline update.

---

## Hybrid search

![Combining vector scores with BM25 scores](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-04-hybrid-search.en.png)

*Combining vector scores with BM25 scores*
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

Running it makes the benefit clearer.

```python
bm25_ready_chunks = [
    "FAISS IndexFlatIP supports exact inner-product search on normalized vectors.",
    "Error code ERR_CONNECTION_REFUSED is usually better handled by exact keyword search.",
    "Chunking strategy changes how much context each vector carries.",
]

for query in ["IndexFlatIP cosine search", "ERR_CONNECTION_REFUSED"]:
    results = hybrid_search(query, build_index(bm25_ready_chunks)[0], bm25_ready_chunks, top_k=2, alpha=0.5)
    print(f"\nquery: {query}")
    for score, text in results:
        print(f"  {score:.4f} — {text}")
```

The first query benefits from both semantic and lexical signals pointing at the same chunk. The second depends much more on exact token matching. That contrast is exactly why hybrid search exists.

## When should reindexing run?

One common operational mistake is treating the index as a one-time artifact. In practice, you need an explicit reindex trigger whenever one of these changes:

- the embedding model name or version
- chunking rules such as `chunk_size`, `chunk_overlap`, or separators
- the source documents themselves
- metadata fields stored alongside chunks

Persisting a small manifest next to the index gives you a fast compatibility check at startup.

```python
import json

manifest = {
    "embedding_model": EMBED_MODEL,
    "chunk_size": CHUNK_SIZE,
    "chunk_overlap": CHUNK_OVERLAP,
    "document_count": len(documents),
    "index_type": "IndexFlatIP",
}

with open("index-manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print(manifest)
```

This is not glamorous infrastructure, but it gives you the first thing to compare when someone asks why retrieval quality changed after a deployment.

---

## Operational considerations

![Index update and deletion constraint path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-05-operational-considerations.en.png)

*Index update and deletion constraint path*
**Index updates.** Adding new documents is straightforward: embed them and call `index.add()`. `IndexFlatIP` does not support deletion. If you need to remove vectors, rebuild the index periodically or use `IndexIDMap` to track and skip deleted entries.

**Memory.** `IndexFlatIP` keeps all vectors in memory. 100,000 vectors at 384 dimensions and 4 bytes each is roughly 147 MB. At 1 million vectors that becomes 1.5 GB. Beyond that, `IndexIVFFlat` or a quantization index like `IndexPQ` reduces memory use.

**Latency.** On CPU, searching 100,000 vectors takes tens of milliseconds. If service latency is critical, consider the GPU build or an approximate index.

---

## Conclusion

This post assembled the full vector search pipeline: load documents, chunk them with `RecursiveCharacterTextSplitter`, embed with `HuggingFaceEmbeddings`, index with FAISS, persist to disk, and retrieve with natural-language queries.

The natural next step is connecting this pipeline to an LLM to build a RAG system. The langchain-101 series covers LCEL, Retriever, and Chain composition.

## Operational checklist

- [ ] Separated ingest, embed, index, and search into independently deployable stages
- [ ] Automated reindex triggers tied to embedding-model and index version
- [ ] Defined how lexical and vector scores fuse (weighted sum, RRF, etc.)
- [ ] Maintained an eval set and an automated quality script in production
- [ ] Surfaced latency, recall, and cost on the same dashboard

## Answering the Opening Questions

- **What stages make vector search a pipeline rather than one embedding call?**
  Ingestion, cleaning, chunking, embedding, indexing, query embedding, retrieval, and result assembly all have to work together.

- **When is hybrid search safer than pure vector search?**
  Hybrid search is safer when exact identifiers, fresh keywords, filters, or symbolic matches matter and pure semantic retrieval may blur them.

- **When documents change, what should drive reindexing and operational logs?**
  Document version, input hash, model version, and chunking settings should drive reindexing; logs should keep query, result, latency, and index version together.

<!-- toc:begin -->
## In this series

- [Vector Search 101 (1/6): What is an embedding — converting text into vectors](./01-what-is-embedding.md)
- [Vector Search 101 (2/6): HuggingFace embeddings in practice — creating your first vectors with sentence-transformers](./02-huggingface-embeddings.md)
- [Vector Search 101 (3/6): Cosine similarity and vector search — computing sentence distances](./03-cosine-similarity.md)
- [Vector Search 101 (4/6): FAISS fundamentals — fast approximate nearest-neighbor search](./04-faiss-fundamentals.md)
- [Vector Search 101 (5/6): Chunking strategies — how to split long documents](./05-chunking-strategies.md)
- **Vector Search 101 (6/6): Vector search pipeline — from document ingestion to query (current)**

<!-- toc:end -->

---

## References

- [FAISS documentation](https://faiss.ai/)
- [LangChain FAISS integration](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [rank-bm25 library](https://github.com/dorianbrown/rank_bm25)
- [Hybrid search introduction — Pinecone](https://www.pinecone.io/learn/hybrid-search-intro/)
- [Sentence Transformers pretrained models](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)

Tags: Vector Search, FAISS, Embeddings, Python
