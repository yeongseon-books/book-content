---
title: "RAG Evaluation and Benchmarking 101 (4/6): VectorDB selection criteria"
series: rag-benchmark-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
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
seo_description: Compare VectorDB indexes fairly. Learn to balance accuracy, latency, and memory by benchmarking flat vs. approximate nearest neighbor indexes.
---

# RAG Evaluation and Benchmarking 101 (4/6): VectorDB selection criteria

VectorDB comparison is really a comparison of index behavior under the same vectors and the same queries. Hold that frame steady and the trade-offs across accuracy, latency, and memory become hard to ignore.

This is the 4th post in the RAG Evaluation and Benchmarking 101 series.

![same vectors compared across flat and IVF indexes](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/04/04-01-same-vector-flat-and-ivf-comparison-stru.en.png)
*same vectors compared across flat and IVF indexes*
> Choosing a vector database is **not a brand comparison**. It is an experiment that measures how the same embedding vectors behave when placed inside different index structures.

## Questions to Keep in Mind

- Which operating conditions should compare VectorDBs beyond feature lists?
- What must stay fixed when changing only the VectorDB over the same embeddings and corpus?
- How should you decide when accuracy, latency, filtering, and operational complexity conflict?

## Why this matters

The cost of vector search explodes with corpus size. Up to ~10k documents the index choice barely matters. Past 100k, brute-force flat search starts pushing past 100 ms. At a million documents it is unusable.

This is where **approximate nearest neighbor (ANN) indexes** like IVF and HNSW come in. They trade a bit of accuracy for 10–100x faster search. The catch: "a bit" depends on data distribution and parameters — it can be 0.99 recall or 0.7.

That is why you have to measure on your own corpus. The comparison in this post is small, but enough to align the decision axes (accuracy vs speed vs memory).

## Mental model

The skeleton of a VectorDB comparison:

```text
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

```text
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

The runnable code lives in `rag-benchmark-101/en/04-vectordb-selection/main.py`. Episodes 05 and 06 require `GROQ_API_KEY`.

```bash
cd en/04-vectordb-selection
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

![Boundary between embedding and search time](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/04/04-02-boundary-between-embedding-and-search-ti.en.png)

*Boundary between embedding and search time*

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

![nprobe trade-off between speed and accuracy](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/04/04-03-nprobe-trade-off-between-speed-and-accur.en.png)

*nprobe trade-off between speed and accuracy*

Vary `nprobe` across 1, 2, 4, 8, 16 and plot recall and latency. There is almost always a visible sweet spot.

## Common mistakes

- **Mixing embedding time into search latency** — embedding is often slower than search and will mask the index difference.
- **Single-shot timing** — the first call is slow. Use `repeats >= 20` and the median.
- **Generalizing from a toy corpus** — recall 0.99 at 1k documents does not guarantee the same at 1M.
- **Setting `nprobe` on an untrained IVF** — calling `add()` without `train()` raises an error.
- **Ignoring HNSW memory** — HNSW is fast but uses 2–3x the memory of flat. IVF is the right choice in tight memory budgets.

## In production

![Index decision axes for real workloads](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/04/04-04-index-decision-axes-for-real-workloads.en.png)

*Index decision axes for real workloads*

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

## Evaluating VectorDB candidates under equal conditions

Performance numbers are meaningless if the operating conditions differ between candidates. Lock down the following variables before any comparison run.

| Variable | Must be identical across candidates |
| --- | --- |
| Vector dimension | Same embedding model (e.g. 384d) |
| Distance function | cosine or inner-product — pick one |
| top-k | The value your product actually uses |
| Filter clause | Same metadata `where` condition |
| Hardware | vCPU, RAM, disk type all matched |

If the distance function differs, result interpretation changes entirely — state it on the first line of every report.

### Benchmark collection script

The script below collects P50/P95 latency and recall@k for each candidate with minimal library dependencies.

```python
import numpy as np
import time

def benchmark_search(index, queries, exact_results, k=5):
    latencies = []
    recalls = []

    for q_vec, exact_ids in zip(queries, exact_results):
        t0 = time.perf_counter()
        _, approx_ids = index.search(q_vec.reshape(1, -1), k)
        latencies.append((time.perf_counter() - t0) * 1000)
        recalls.append(len(set(approx_ids[0]) & set(exact_ids)) / k)

    return {
        "p50_ms": float(np.percentile(latencies, 50)),
        "p95_ms": float(np.percentile(latencies, 95)),
        "recall@k": float(np.mean(recalls)),
    }
```

This function works with FAISS, HNSW wrappers, and server-backed VectorDB adapters because the output format is identical.

### Why filtered search needs separate measurement

RAG services frequently filter by date, product line, or customer. Measuring unfiltered performance alone diverges from production reality.

| Scenario | Example filter | Observed metrics |
| --- | --- | --- |
| Baseline | None | recall@k, p95 |
| Date filter | `year >= 2024` | recall@k, p95 |
| Multi-condition | `team == "ml" AND severity >= 2` | recall@k, p95, error rate |

Some engines see recall drop or latency spike under filters. Report filtered scenarios in a separate table.

### Server-mode VectorDB configuration example

In production, network and replication settings affect quality alongside index algorithm parameters.

```yaml
vectordb:
  engine: qdrant
  collection: rag_docs_v2
  vector_size: 384
  distance: cosine
  hnsw:
    m: 32
    ef_construct: 128
    ef_search: 64
  replication:
    factor: 2
  write_consistency: majority
  read_timeout_ms: 500
```

Store this configuration alongside benchmark results. When someone asks "why did the score change since last month," you can answer immediately.

### Fault-condition performance matters too

Normal-state measurements underestimate operational risk. Run at least these two additional scenarios:

1. First 100 queries before index warm-up (cold-start latency)
2. Queries during a rolling index rebuild (concurrent write load)

If cold-start P95 exceeds your SLA threshold, you need a warm-up step in your deployment pipeline.

## Appendix — standard fields for a VectorDB benchmark report

Fixing report fields across teams makes retrospectives and reproduction straightforward.

### JSON schema example

```json
{
  "run_id": "20260521T021000-7d8e9f0",
  "embedding_model": "all-MiniLM-L6-v2",
  "vector_dim": 384,
  "distance": "cosine",
  "dataset_size": 100000,
  "candidate": "faiss-ivf",
  "params": {"nlist": 316, "nprobe": 8},
  "metrics": {
    "recall@5_vs_flat": 0.989,
    "p50_ms": 7.4,
    "p95_ms": 11.3,
    "memory_mb": 386
  }
}
```

With a fixed schema, adding new candidates still lands on the same dashboard.

### Filtered-scenario performance table (separate from baseline)

| candidate | scenario | recall@5 | p95_ms |
| --- | --- | ---: | ---: |
| flat | no-filter | 1.00 | 24.7 |
| ivf(nprobe=8) | no-filter | 0.99 | 11.3 |
| ivf(nprobe=8) | year>=2024 | 0.98 | 14.8 |
| hnsw(ef=64) | team=ml | 0.97 | 12.1 |

Without a separated filter table, benchmark results and production experience diverge.

### Recommended repetition counts

- Corpus < 100k: 20 repetitions per query, report median
- Corpus 100k-1M: 10 repetitions, report median + P95
- Corpus > 1M: 200+ sample queries, measure per shard independently

Too few repetitions lets transient cache effects masquerade as true performance.

### Pre-production validation checklist

1. Have you actually run a backup/restore test at least once?
2. Can you complete an index rebuild within the maintenance window?
3. Is a fallback search path (flat or previous index) ready for outages?
4. Does monitoring separately track P95, error rate, and timeouts?

VectorDB selection is not just a performance comparison — it is an operational-system choice. Keep that framing throughout.

### Load-stage performance test example

| QPS range | candidate | recall@5 | p95 (ms) | timeout rate |
| --- | --- | ---: | ---: | ---: |
| 10 | ivf(nprobe=8) | 0.99 | 10.9 | 0.0% |
| 50 | ivf(nprobe=8) | 0.99 | 14.2 | 0.1% |
| 100 | ivf(nprobe=8) | 0.98 | 28.6 | 0.9% |

Static benchmarks alone cannot reveal operational limits. Run load-stage tests alongside recall measurements.

Record the data fill ratio and index fragmentation level at measurement time. The same candidate can produce different latency and recall distributions depending on whether the index was freshly built or partially updated over time.

When changing index parameters, keep the previous configuration running in A/B shadow mode for at least 24 hours. Traffic patterns vary by time of day, and a short benchmark window cannot capture real operational variance.

### Sample benchmark results

The table below was measured on 100k document vectors (384-dim), top-k=5, same hardware. Numbers vary by environment, but the interpretation method applies everywhere.

| Candidate | Parameters | Recall@5 (vs Flat) | P50 latency (ms) | P95 latency (ms) | Memory (MB) |
| --- | --- | ---: | ---: | ---: | ---: |
| FAISS FlatIP | exact | 1.00 | 18.1 | 24.7 | 382 |
| FAISS IVFFlat | nlist=316, nprobe=4 | 0.95 | 4.8 | 7.2 | 386 |
| FAISS IVFFlat | nlist=316, nprobe=8 | 0.99 | 7.6 | 11.4 | 386 |
| HNSW | M=32, efSearch=64 | 0.98 | 3.9 | 6.0 | 514 |

This table is not for picking "the fastest candidate." It is for quickly filtering candidates that meet product requirements (e.g. recall >= 0.97 AND P95 <= 10 ms).

## Answering the Opening Questions

- **Which operating conditions should compare VectorDBs beyond feature lists?**
  Compare by data size, latency target, filter needs, update frequency, team operations capacity, and cost model.

- **What must stay fixed when changing only the VectorDB over the same embeddings and corpus?**
  Fix embeddings, chunking, query set, gold labels, metadata schema, top_k, and hardware so the VectorDB is the main variable.

- **How should you decide when accuracy, latency, filtering, and operational complexity conflict?**
  Set product-weighted tradeoffs before choosing; if filter correctness is critical, a slightly slower candidate may be better.

<!-- toc:begin -->
## In this series

- [RAG Evaluation and Benchmarking 101 (1/6): Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [RAG Evaluation and Benchmarking 101 (2/6): Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [RAG Evaluation and Benchmarking 101 (3/6): Comparing embedding models](./03-embedding-comparison.md)
- **RAG Evaluation and Benchmarking 101 (4/6): VectorDB selection criteria (current)**
- RAG Evaluation and Benchmarking 101 (5/6): End-to-end RAG pipeline evaluation (upcoming)
- RAG Evaluation and Benchmarking 101 (6/6): Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [FAISS indexes wiki](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [pgvector](https://github.com/pgvector/pgvector)
- [Qdrant benchmarks](https://qdrant.tech/benchmarks/)

Tags: RAG, VectorDB, Benchmarking, LLM
