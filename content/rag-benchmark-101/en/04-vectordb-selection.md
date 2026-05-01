---
title: 'VectorDB selection criteria'
series: rag-benchmark-101
episode: 4
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- VectorDB
- Benchmarking
- LLM
last_reviewed: '2026-05-01'
---

# VectorDB selection criteria

> RAG Benchmark 101 (4/6)

FAISS, Chroma, Qdrant — every vector database makes different trade-offs. This post benchmarks FAISS and Chroma head-to-head on indexing speed, query latency, memory footprint, and metadata filtering support, then establishes clear selection criteria.

The companion code lives in [`yeongseon-books/rag-benchmark-101/en/04-vectordb-selection`](https://github.com/yeongseon-books/rag-benchmark-101/tree/main/en/04-vectordb-selection).

---

## Evaluation axes

Four dimensions drive vector database selection.

- **Indexing speed**: how fast can documents be added?
- **Query latency**: time per similarity search
- **Memory efficiency**: RAM footprint relative to corpus size
- **Filter support**: metadata-conditioned retrieval

---

## FAISS vs Chroma benchmark

```python
import json
import time
import tempfile
from dataclasses import dataclass

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma

@dataclass
class VectorDBBenchResult:
    name: str
    index_time_s: float
    query_time_ms: float
    precision_at_3: float
    recall_at_3: float
    supports_filter: bool
    notes: str = ""

    def summary(self) -> dict:
        return {
            "db": self.name,
            "index_time_s": round(self.index_time_s, 2),
            "query_time_ms": round(self.query_time_ms, 1),
            "precision@3": round(self.precision_at_3, 4),
            "recall@3": round(self.recall_at_3, 4),
            "supports_filter": self.supports_filter,
            "notes": self.notes,
        }

def _get_embedding():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

def _prm(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> tuple[float, float, float]:
    top_k = retrieved_ids[:k]
    hits = [d for d in top_k if d in relevant_ids]
    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    mrr = next((1.0 / (i + 1) for i, d in enumerate(top_k) if d in relevant_ids), 0.0)
    return precision, recall, mrr

def benchmark_faiss(corpus: list[Document], queries: list, k: int = 3) -> VectorDBBenchResult:
    embedding = _get_embedding()
    t0 = time.perf_counter()
    vs = FAISS.from_documents(corpus, embedding)
    index_time = time.perf_counter() - t0

    retriever = vs.as_retriever(search_kwargs={"k": k})
    precisions, recalls, qtimes = [], [], []
    for qt in queries:
        t0 = time.perf_counter()
        docs = retriever.invoke(qt.query)
        qtimes.append((time.perf_counter() - t0) * 1000)
        p, r, _ = _prm([d.metadata.get("id", "") for d in docs], qt.relevant_ids, k)
        precisions.append(p)
        recalls.append(r)

    avg = lambda lst: sum(lst) / len(lst) if lst else 0.0
    return VectorDBBenchResult("FAISS", index_time, avg(qtimes), avg(precisions), avg(recalls),
                               False, "in-memory; serialization required for persistence")

def benchmark_chroma(corpus: list[Document], queries: list, k: int = 3) -> VectorDBBenchResult:
    embedding = _get_embedding()
    with tempfile.TemporaryDirectory() as tmpdir:
        t0 = time.perf_counter()
        vs = Chroma.from_documents(corpus, embedding, persist_directory=tmpdir, collection_name="bench")
        index_time = time.perf_counter() - t0

        retriever = vs.as_retriever(search_kwargs={"k": k})
        precisions, recalls, qtimes = [], [], []
        for qt in queries:
            t0 = time.perf_counter()
            docs = retriever.invoke(qt.query)
            qtimes.append((time.perf_counter() - t0) * 1000)
            p, r, _ = _prm([d.metadata.get("id", "") for d in docs], qt.relevant_ids, k)
            precisions.append(p)
            recalls.append(r)

        avg = lambda lst: sum(lst) / len(lst) if lst else 0.0
        return VectorDBBenchResult("Chroma", index_time, avg(qtimes), avg(precisions), avg(recalls),
                                   True, "SQLite-backed persistence, native metadata filters")
```

---

## Metadata filter comparison

```python
def demo_metadata_filter(corpus: list[Document]):
    embedding = _get_embedding()
    query = "what is vector search?"

    # Chroma: native filter
    with tempfile.TemporaryDirectory() as tmpdir:
        chroma_vs = Chroma.from_documents(corpus, embedding, persist_directory=tmpdir)
        retriever = chroma_vs.as_retriever(search_kwargs={"k": 3, "filter": {"topic": "faiss"}})
        results = retriever.invoke(query)
        print("Chroma native filter (topic=faiss):")
        for doc in results:
            print(f"  [{doc.metadata.get('id')}] {doc.page_content[:60]}")

    # FAISS: post-hoc filter
    faiss_vs = FAISS.from_documents(corpus, embedding)
    all_results = faiss_vs.similarity_search(query, k=len(corpus))
    filtered = [d for d in all_results if d.metadata.get("topic") == "faiss"][:3]
    print("\nFAISS post-hoc filter (topic=faiss):")
    for doc in filtered:
        print(f"  [{doc.metadata.get('id')}] {doc.page_content[:60]}")
```

---

## Selection guide

**Choose FAISS when:**
- In-memory processing is acceptable and persistence is not required
- Metadata filters are not needed
- Corpus is up to a few million vectors

**Choose Chroma when:**
- Metadata-conditioned retrieval is required
- Persistence and index reload across restarts is needed
- Corpus is up to hundreds of thousands of documents

**Consider Qdrant or Weaviate when:**
- Hundreds of millions of vectors or more
- Distributed deployment and horizontal scaling
- Complex payload filtering and hybrid search

```python
if __name__ == "__main__":
    from rag_benchmark_post2 import CORPUS, QUERIES

    for result in [benchmark_faiss(CORPUS, QUERIES), benchmark_chroma(CORPUS, QUERIES)]:
        print(json.dumps(result.summary(), indent=2))

    demo_metadata_filter(CORPUS)
```

<!-- blog-only:start -->
Next: [End-to-end RAG pipeline evaluation](./05-e2e-evaluation.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [Comparing embedding models](./03-embedding-comparison.md)
- **VectorDB selection criteria (current)**
- End-to-end RAG pipeline evaluation (upcoming)
- Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [FAISS wiki](https://github.com/facebookresearch/faiss/wiki)
- [Chroma documentation](https://docs.trychroma.com/)
- [ANN benchmarks](https://ann-benchmarks.com/)

Tags: RAG, VectorDB, Benchmarking, LLM
