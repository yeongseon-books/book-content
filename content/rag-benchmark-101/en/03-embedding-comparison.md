# Comparing embedding models

> RAG Benchmark 101 (3/6)

The embedding model is the foundation of a RAG pipeline. Swap it out while keeping everything else constant and retrieval quality shifts significantly. This post benchmarks three common models against the same query set to establish a model selection framework.

---

## Models under comparison

Three models commonly found in production RAG systems.

| Model | Dimensions | Size | Notes |
|-------|-----------|------|-------|
| all-MiniLM-L6-v2 | 384 | 80 MB | lightweight, fast |
| all-mpnet-base-v2 | 768 | 420 MB | higher quality |
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | 120 MB | multilingual |

---

## Embedding model benchmark

```python
import time
from dataclasses import dataclass

import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

@dataclass
class EmbeddingBenchResult:
    model_name: str
    index_time_s: float
    query_time_ms: float
    precision_at_3: float
    recall_at_3: float
    mrr: float

    def summary(self) -> dict:
        return {
            "model": self.model_name.split("/")[-1],
            "index_time_s": round(self.index_time_s, 2),
            "query_time_ms": round(self.query_time_ms, 1),
            "precision@3": round(self.precision_at_3, 4),
            "recall@3": round(self.recall_at_3, 4),
            "mrr": round(self.mrr, 4),
        }

def _prm(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> tuple[float, float, float]:
    top_k = retrieved_ids[:k]
    hits = [d for d in top_k if d in relevant_ids]
    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    mrr = next((1.0 / (i + 1) for i, d in enumerate(top_k) if d in relevant_ids), 0.0)
    return precision, recall, mrr

def benchmark_embedding_model(
    model_name: str,
    corpus: list[Document],
    queries: list,
    k: int = 3,
) -> EmbeddingBenchResult:
    embedding = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    t0 = time.perf_counter()
    vectorstore = FAISS.from_documents(corpus, embedding)
    index_time = time.perf_counter() - t0

    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    precisions, recalls, mrrs, query_times = [], [], [], []

    for qt in queries:
        t0 = time.perf_counter()
        retrieved_docs = retriever.invoke(qt.query)
        query_times.append((time.perf_counter() - t0) * 1000)

        retrieved_ids = [d.metadata.get("id", "") for d in retrieved_docs]
        p, r, m = _prm(retrieved_ids, qt.relevant_ids, k)
        precisions.append(p)
        recalls.append(r)
        mrrs.append(m)

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    return EmbeddingBenchResult(
        model_name=model_name,
        index_time_s=index_time,
        query_time_ms=avg(query_times),
        precision_at_3=avg(precisions),
        recall_at_3=avg(recalls),
        mrr=avg(mrrs),
    )
```

---

## Similarity distribution analysis

```python
def analyze_similarity_distribution(
    model_name: str,
    corpus: list[Document],
    queries: list,
    k: int = 5,
) -> dict:
    embedding = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(corpus, embedding)

    relevant_scores, irrelevant_scores = [], []
    for qt in queries:
        results = vectorstore.similarity_search_with_score(qt.query, k=k)
        for doc, score in results:
            doc_id = doc.metadata.get("id", "")
            (relevant_scores if doc_id in qt.relevant_ids else irrelevant_scores).append(float(score))

    def stats(scores: list[float]) -> dict:
        if not scores:
            return {}
        arr = np.array(scores)
        return {"mean": round(float(arr.mean()), 4), "std": round(float(arr.std()), 4),
                "min": round(float(arr.min()), 4), "max": round(float(arr.max()), 4)}

    return {
        "model": model_name.split("/")[-1],
        "relevant": stats(relevant_scores),
        "irrelevant": stats(irrelevant_scores),
        "gap": round(
            abs(np.mean(relevant_scores) - np.mean(irrelevant_scores))
            if (relevant_scores and irrelevant_scores) else 0, 4
        ),
    }
```

---

## Running the comparison

```python
import json

MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/all-mpnet-base-v2",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
]

if __name__ == "__main__":
    from rag_benchmark_post2 import CORPUS, QUERIES  # reuse from post 2

    print("=== embedding model comparison ===")
    for model_name in MODELS:
        print(f"\nbenchmarking {model_name.split('/')[-1]} ...")
        result = benchmark_embedding_model(model_name, CORPUS, QUERIES)
        print(json.dumps(result.summary(), indent=2))

    print("\n=== similarity distribution ===")
    for model_name in MODELS:
        dist = analyze_similarity_distribution(model_name, CORPUS, QUERIES)
        print(json.dumps(dist, indent=2))
```

---

## Model selection criteria

No single metric determines the best embedding model. Match the model to the use case.

- **Throughput-constrained**: `all-MiniLM-L6-v2` — best when query speed and memory matter more than absolute quality.
- **Quality-first**: `all-mpnet-base-v2` — worth the larger footprint when retrieval precision is the primary concern.
- **Multilingual corpus**: `paraphrase-multilingual-MiniLM-L12-v2` — required when documents mix languages.

The similarity gap between relevant and irrelevant documents measures discriminability. A small gap means the model cannot reliably separate good from bad results, which makes threshold-based filtering unreliable and pollutes the context window.

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [Measuring retrieval performance](./02-retrieval-benchmarking.md)
- **Comparing embedding models (current)**
- VectorDB selection criteria (upcoming)
- End-to-end RAG pipeline evaluation (upcoming)
- Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [MTEB embedding benchmark](https://huggingface.co/spaces/mteb/leaderboard)
- [Sentence Transformers model hub](https://www.sbert.net/docs/pretrained_models.html)
- [FAISS index type guide](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)

Tags: RAG, VectorDB, Benchmarking, LLM
