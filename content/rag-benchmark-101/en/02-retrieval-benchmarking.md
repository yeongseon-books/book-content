---
title: 'Measuring retrieval performance'
series: rag-benchmark-101
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
- VectorDB
- Benchmarking
- LLM
last_reviewed: '2026-05-01'
---

# Measuring retrieval performance

> RAG Benchmark 101 (2/6)

A good RAG retriever surfaces relevant documents at the top. This post runs a systematic benchmark across a query set, aggregates results into a system-level retrieval report, and compares chunking strategies using the same evaluation harness.

The companion code lives in [`yeongseon-books/rag-benchmark-101/en/02-retrieval-benchmarking`](https://github.com/yeongseon-books/rag-benchmark-101/tree/main/en/02-retrieval-benchmarking).

---

## Benchmark design

Measuring retrieval performance requires three things.

- **Query set**: questions that reflect realistic usage patterns
- **Ground truth**: the set of relevant document IDs for each query
- **Retriever**: the system under test

If ground truth labels do not exist yet, an LLM can generate them from your corpus.

---

## Test corpus and query set

```python
import json
import os
from dataclasses import dataclass, field

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

CORPUS = [
    Document(page_content="A vector database stores embedding vectors and supports similarity search.", metadata={"id": "d01", "topic": "vectordb"}),
    Document(page_content="FAISS is a vector similarity search library developed by Facebook AI Research.", metadata={"id": "d02", "topic": "faiss"}),
    Document(page_content="FAISS IndexFlatL2 provides exact L2 distance-based search.", metadata={"id": "d03", "topic": "faiss"}),
    Document(page_content="Cosine similarity measures the directional similarity between two vectors.", metadata={"id": "d04", "topic": "similarity"}),
    Document(page_content="HNSW is a fast ANN search algorithm based on hierarchical navigable graphs.", metadata={"id": "d05", "topic": "ann"}),
    Document(page_content="Embedding models transform text into high-dimensional vector representations.", metadata={"id": "d06", "topic": "embedding"}),
    Document(page_content="all-MiniLM-L6-v2 is a lightweight model producing 384-dimensional embeddings.", metadata={"id": "d07", "topic": "embedding"}),
    Document(page_content="Smaller chunk sizes improve precision but reduce available context.", metadata={"id": "d08", "topic": "chunking"}),
    Document(page_content="Hybrid search combines keyword and vector search for better coverage.", metadata={"id": "d09", "topic": "hybrid"}),
    Document(page_content="Re-ranking reorders initial retrieval results to improve precision.", metadata={"id": "d10", "topic": "reranking"}),
]

@dataclass
class QueryGroundTruth:
    query: str
    relevant_ids: set[str]
    topic: str = ""

QUERIES: list[QueryGroundTruth] = [
    QueryGroundTruth("What is FAISS?", {"d02", "d03"}, "faiss"),
    QueryGroundTruth("How do embedding models work?", {"d06", "d07"}, "embedding"),
    QueryGroundTruth("What is the difference between cosine similarity and L2 distance?", {"d03", "d04"}, "similarity"),
    QueryGroundTruth("What is an ANN search algorithm?", {"d05"}, "ann"),
    QueryGroundTruth("How does chunk size affect retrieval?", {"d08"}, "chunking"),
    QueryGroundTruth("What is hybrid search?", {"d09"}, "hybrid"),
]
```

---

## Retrieval benchmark runner

```python
from collections import defaultdict

def _precision_recall_mrr(retrieved_ids: list[str], relevant_ids: set[str], k: int):
    top_k = retrieved_ids[:k]
    hits = [d for d in top_k if d in relevant_ids]
    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    mrr = next((1.0 / (i + 1) for i, d in enumerate(top_k) if d in relevant_ids), 0.0)
    return precision, recall, f1, mrr

def run_retrieval_benchmark(
    queries: list[QueryGroundTruth],
    vectorstore: FAISS,
    k_values: list[int] = [1, 3, 5],
) -> dict:
    retriever = vectorstore.as_retriever(search_kwargs={"k": max(k_values)})
    all_metrics: list[dict] = []

    for qt in queries:
        retrieved_docs = retriever.invoke(qt.query)
        retrieved_ids = [d.metadata["id"] for d in retrieved_docs]

        query_metrics = {"query": qt.query, "topic": qt.topic}
        for k in k_values:
            p, r, f1, mrr = _precision_recall_mrr(retrieved_ids, qt.relevant_ids, k)
            query_metrics.update({f"precision@{k}": p, f"recall@{k}": r, f"f1@{k}": f1})
        query_metrics["mrr"] = _precision_recall_mrr(retrieved_ids, qt.relevant_ids, k_values[0])[3]
        all_metrics.append(query_metrics)

    def avg(key: str) -> float:
        vals = [x[key] for x in all_metrics if key in x]
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    keys = [f"precision@{k}" for k in k_values] + [f"recall@{k}" for k in k_values] + \
           [f"f1@{k}" for k in k_values] + ["mrr"]
    return {"summary": {k: avg(k) for k in keys} | {"total_queries": len(queries)}, "details": all_metrics}
```

---

## Chunking strategy comparison

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

def build_vectorstore(docs: list[Document], chunk_size: int, chunk_overlap: int) -> FAISS:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )
    split_docs = splitter.split_documents(docs)
    for i, doc in enumerate(split_docs):
        if "id" not in doc.metadata:
            doc.metadata["id"] = f"chunk_{i}"

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return FAISS.from_documents(split_docs, embedding)

def compare_chunking_strategies(corpus, queries, configs):
    results = {}
    for cfg in configs:
        label = f"chunk={cfg['chunk_size']}_overlap={cfg['chunk_overlap']}"
        vs = build_vectorstore(corpus, cfg["chunk_size"], cfg["chunk_overlap"])
        results[label] = run_retrieval_benchmark(queries, vs)["summary"]
    return results

if __name__ == "__main__":
    configs = [
        {"chunk_size": 200, "chunk_overlap": 20},
        {"chunk_size": 400, "chunk_overlap": 80},
        {"chunk_size": 800, "chunk_overlap": 160},
    ]
    comparison = compare_chunking_strategies(CORPUS, QUERIES, configs)
    for label, metrics in comparison.items():
        print(f"\n{label}")
        print(json.dumps(metrics, indent=2))
```

---

## Interpreting results

Start with Recall@K. Low recall means relevant documents are missing from results entirely. If recall stays flat as K increases, the problem is likely embedding quality rather than K.

Precision@1 is the user-facing number — it measures whether the first result is relevant. Re-ranking after initial retrieval is the most effective lever for improving Precision@1 without reindexing.

When MRR is low, the retriever finds relevant documents eventually but ranks them poorly. This is a re-ranker problem, not an embedding problem.

<!-- blog-only:start -->
Next: [Comparing embedding models](./03-embedding-comparison.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- **Measuring retrieval performance (current)**
- Comparing embedding models (upcoming)
- VectorDB selection criteria (upcoming)
- End-to-end RAG pipeline evaluation (upcoming)
- Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [BEIR retrieval benchmark](https://github.com/beir-cellar/beir)
- [FAISS index guide](https://faiss.ai/cpp_api/struct/faiss__IndexFlat.html)
- [LangChain retriever documentation](https://python.langchain.com/docs/modules/data_connection/retrievers/)

Tags: RAG, VectorDB, Benchmarking, LLM
