---
title: VectorDB selection criteria
series: rag-benchmark-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- VectorDB
- FAISS
- IVF
- Recall
- ANN
last_reviewed: '2026-05-01'
seo_description: 'The skeleton of a VectorDB comparison:'
---

# VectorDB selection criteria

## Questions this post answers

![Questions this post answers](../../../assets/rag-benchmark-101/04/04-01-questions-this-post-answers.en.png)

- How do you compare a FAISS flat index against an IVF index fairly?
- What do you have to record alongside accuracy to talk about a real trade-off?
- How do you surface the trade-offs of approximate nearest neighbor (ANN) search even on a small example?
- What needs to be fixed to compare candidate vector databases (FAISS, Chroma, pgvector, Qdrant) on equal footing?

> Choosing a vector database is **not a brand comparison**. It is an experiment that measures how the same embedding vectors behave when placed inside different index structures.

## Why this matters

The cost of vector search explodes with corpus size. Up to ~10k documents the index choice barely matters. Past 100k, brute-force flat search starts pushing past 100 ms. At a million documents it is unusable.

This is where **approximate nearest neighbor (ANN) indexes** like IVF and HNSW come in. They trade a bit of accuracy for 10–100x faster search. The catch: "a bit" depends on data distribution and parameters — it can be 0.99 recall or 0.7.

That is why you have to measure on your own corpus. The comparison in this post is small, but enough to align the decision axes (accuracy vs speed vs memory).

## Mental model

The skeleton of a VectorDB comparison:

```
[fixed] embedding model + corpus embeddings (doc_vectors)
                  │
                  ▼
        [variable] index structure
        ┌─────────┴─────────┐
        ▼                   ▼
   IndexFlatIP           IndexIVFFlat (nprobe=N)
   (exact, slow)         (approximate, fast)
        │                   │
        ▼                   ▼
   recall=1.0            recall<=1.0
   search_lat = X        search_lat = X / k
```

You do not regenerate vectors. Embed once and feed the same vectors into both indexes. Only then can you attribute the difference to the index structure.

## Core concepts

| Term | Meaning |
| --- | --- |
| Flat index | Computes distance against every vector. Exact, but O(N) |
| IVF (Inverted File) | Splits the corpus into nlist clusters and only searches the nprobe nearest ones |
| HNSW | Graph-based ANN. High recall and fast, but heavy on memory |
| Recall@k | How many of flat's top-k results the ANN index also returned |
| nprobe | Number of clusters IVF searches. Higher = more accurate, lower = faster |
| nlist | Total number of clusters (typically √N) |

Recall is not the same as hit rate. **Hit rate** asks if the gold doc made it into the top-k. **Recall** asks how closely the ANN result matches flat.

## Before vs. after

**Before**: "Chroma is convenient, let's use it." At 100k documents search slows down and you scramble to migrate to FAISS. After the migration you lose days debugging "why are answers different now?".

**After**: same embedding vectors, two indexes side by side.

```
index               recall@5  search_ms  memory_mb
IndexFlatIP         1.00      18.3       384
IndexIVFFlat (n=1)  0.72       2.1       386
IndexIVFFlat (n=4)  0.95       4.7       386
IndexIVFFlat (n=8)  0.99       7.9       386
```

`nprobe=4` is the sweet spot. The table is something you can drop straight into a meeting deck.

## Step-by-step walkthrough

### Step 1 — Embed once

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
doc_vectors = model.encode(DOC_TEXTS, normalize_embeddings=True).astype("float32")
query_vectors = model.encode(QUERY_TEXTS, normalize_embeddings=True).astype("float32")
dimension = doc_vectors.shape[1]
```

### Step 2 — Build the flat index

![same vectors compared across flat and IVF indexes](../../../assets/rag-benchmark-101/04/04-01-same-vector-flat-and-ivf-comparison-stru.en.png)

The runnable code lives in `rag-benchmark-101/en/04-vectordb-selection/main.py`. Episodes 05 and 06 require `GROQ_API_KEY`.

```bash
cd /root/Github/rag-benchmark-101/en/04-vectordb-selection
python3 main.py
```

```python
import faiss

flat_index = faiss.IndexFlatIP(dimension)
flat_index.add(doc_vectors)
```

### Step 3 — Build and train the IVF index

```python
nlist = max(1, int(np.sqrt(len(doc_vectors))))
quantizer = faiss.IndexFlatIP(dimension)
ivf_index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
ivf_index.train(doc_vectors)
ivf_index.add(doc_vectors)
ivf_index.nprobe = 4
```

`train()` clusters the corpus — a cost flat does not have.

### Step 4 — Measure pure search latency

![Boundary between embedding and search time](../../../assets/rag-benchmark-101/04/04-02-boundary-between-embedding-and-search-ti.en.png)

```python
def search_only(index, query_vec, k=5, repeats=20):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        D, I = index.search(query_vec.reshape(1, -1), k)
        times.append((time.perf_counter() - t0) * 1000)
    return np.median(times), I[0]
```

The point is: time only `index.search()`, not embedding.

### Step 5 — Compute recall

```python
def recall_at_k(approx_ids, exact_ids):
    return len(set(approx_ids) & set(exact_ids)) / len(exact_ids)

flat_results = [search_only(flat_index, q)[1] for q in query_vectors]
ivf_results = [search_only(ivf_index, q)[1] for q in query_vectors]
recall = np.mean([recall_at_k(a, e) for a, e in zip(ivf_results, flat_results)])
```

### Step 6 — Sweep `nprobe`

![nprobe trade-off between speed and accuracy](../../../assets/rag-benchmark-101/04/04-03-nprobe-trade-off-between-speed-and-accur.en.png)

Vary `nprobe` across 1, 2, 4, 8, 16 and plot recall and latency. There is almost always a visible sweet spot.

## Common mistakes

- **Mixing embedding time into search latency** — embedding is often slower than search and will mask the index difference.
- **Single-shot timing** — the first call is slow. Use `repeats >= 20` and the median.
- **Generalizing from a toy corpus** — recall 0.99 at 1k documents does not guarantee the same at 1M.
- **Setting `nprobe` on an untrained IVF** — calling `add()` without `train()` raises an error.
- **Ignoring HNSW memory** — HNSW is fast but uses 2–3x the memory of flat. IVF is the right choice in tight memory budgets.

## In production

![Index decision axes for real workloads](../../../assets/rag-benchmark-101/04/04-04-index-decision-axes-for-real-workloads.en.png)

- **VectorDB candidate comparison**: FAISS (library), Chroma (embedded + REST), pgvector (Postgres extension), Qdrant/Weaviate (standalone server). Send the same queries and put latency, recall, and operational cost (install, backup, scaling) in one table.
- **Recall target**: 0.95 is enough for most RAG. Domains where missing a result is costly (legal, medical) need 0.99+.
- **Re-train cadence**: when more than 30% of the corpus changes, IVF clusters become stale. Schedule periodic re-training.
- **Production monitoring**: always record query latency distribution (p50, p95, p99) and the rate of empty-result queries.

## Checklist

- [ ] Embedded vectors once and fed both indexes simultaneously.
- [ ] Wrapped only `index.search()` to measure pure search latency.
- [ ] Used median latency, not mean.
- [ ] Computed recall@k against flat results as ground truth.
- [ ] Swept `nprobe` (or the equivalent ANN parameter) and drew the trade-off curve.

## Exercises

1. Scale corpus size to 100, 1,000, 10,000 and plot the search latency ratio of flat vs IVF. Where does the gap open?
2. Add `IndexHNSWFlat` and compare flat, IVF, and HNSW on the same table.
3. Measure recall at `nprobe=1, 4, 16` and find the smallest nprobe that satisfies recall ≥ 0.95.

## Wrap-up · what's next

This post fed identical embedding vectors into flat and IVF indexes and measured the recall vs search-latency trade-off. The keys are **don't re-embed**, **time only the search step**, and **use medians plus an nprobe sweep**.

Episode 5 evaluates the **end-to-end RAG pipeline** with the retriever wired to an LLM, measuring not just retrieval but the answer itself.

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [Comparing embedding models](./03-embedding-comparison.md)
- **VectorDB selection criteria (current)**
- End-to-end RAG pipeline evaluation (upcoming)
- Completing the RAG Benchmark (upcoming)

<!-- toc:end -->

---

## References

- [FAISS indexes wiki](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [pgvector](https://github.com/pgvector/pgvector)
- [Qdrant benchmarks](https://qdrant.tech/benchmarks/)

Tags: RAG, VectorDB, Benchmarking, LLM
