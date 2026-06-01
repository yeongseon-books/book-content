---
episode: 4
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
title: "Vector Search 101 (4/6): FAISS fundamentals — fast approximate nearest-neighbor search"
seo_description: Implement fast approximate nearest-neighbor search with FAISS to handle large-scale vector collections with high accuracy and low latency.
---

# Vector Search 101 (4/6): FAISS fundamentals — fast approximate nearest-neighbor search

Once documents number in the thousands or tens of thousands, NumPy brute-force search slows down. Comparing a query against 100,000 vectors of dimension 384 requires 38.4 million multiplications per query. At that scale, search latency climbs into the hundreds of milliseconds or higher, which is too slow for interactive applications.

FAISS (Facebook AI Similarity Search) was built for this problem. It supports approximate nearest-neighbor (ANN) search that trades a small accuracy cost for a large speed gain. It handles billion-scale vector collections and runs fast on both CPU and GPU.

This is the 4th post in the Vector Search 101 series.

This post covers the baseline FAISS workflow you need before tuning larger ANN deployments.

![FAISS index type comparison structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-01-faiss-fundamentals-fast-approximate-near.en.png)
*FAISS index type comparison structure*
> The best way to understand FAISS is not as a smarter database, but as a compute engine dedicated to vector search.

## Questions to Keep in Mind

- Where does a simple loop over vectors stop being good enough?
- What assumption should decide between IndexFlatIP and IndexFlatL2?
- When saving and reloading an index, how do vectors and metadata stay aligned?

## Installation

CPU-only version:

```bash
pip install faiss-cpu sentence-transformers numpy
```

Replace `faiss-cpu` with `faiss-gpu` if a compatible GPU is available.

---

## Understanding index types

![Flat, IVF, and HNSW index trade-offs](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-01-understanding-index-types.en.png)

*Flat, IVF, and HNSW index trade-offs*
FAISS supports many index types, each with different speed-accuracy tradeoffs. Two are essential at the start.

**IndexFlatL2**: exact search using Euclidean distance. Compares every vector without skipping. Accuracy is 100%, but search time scales linearly with the number of vectors.

**IndexFlatIP**: exact search using inner product. With normalized vectors, inner product equals cosine similarity. Text retrieval typically uses this index with pre-normalized vectors.

Larger deployments use approximate indexes like `IndexIVFFlat` or `IndexHNSWFlat`. This post focuses on Flat indexes to establish the baseline pattern.

---

## Exact search with IndexFlatIP

![Flow from embeddings to index creation](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-02-exact-search-with-indexflatip.en.png)

*Flow from embeddings to index creation*
The standard pattern for text retrieval: normalized vectors plus inner-product index.

```python
import json

import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS is a high-speed vector search library from Facebook AI Research.",
    "Cosine similarity measures the directional similarity between two vectors.",
    "Embedding models project text into a high-dimensional vector space.",
    "sentence-transformers specializes in sentence-level embeddings.",
    "Vector search captures semantic similarity that keyword search misses.",
    "Chunking strategies split long documents into searchable units.",
    "RAG combines retrieved documents with an LLM prompt.",
    "HNSW indexes use graph-based approximate nearest-neighbor search.",
    "Higher embedding dimensions can capture more information.",
    "With normalized vectors, inner product equals cosine similarity.",
]

doc_vectors = np.array(embedding_model.embed_documents(documents), dtype=np.float32)
dimension = doc_vectors.shape[1]  # 384

index = faiss.IndexFlatIP(dimension)
index.add(doc_vectors)

print(f"total vectors in index: {index.ntotal}")
print(f"vector dimension: {dimension}")
```

FAISS requires `float32` arrays. Without the explicit `dtype=np.float32` cast, NumPy defaults to `float64` and FAISS raises an error.

---

## Running queries

![Query to FAISS result path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-03-running-queries.en.png)

*Query to FAISS result path*
```python
def search(query: str, top_k: int = 3) -> list[tuple[float, str]]:
    query_vector = np.array(
        [embedding_model.embed_query(query)], dtype=np.float32
    )  # (1, 384) — FAISS expects a 2D array
    scores, indices = index.search(query_vector, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:  # -1 means no result found
            results.append((float(score), documents[idx]))
    return results

queries = [
    "how vector search finds similar content",
    "what embedding models do",
    "splitting documents into pieces",
]

for query in queries:
    print(f"\nquery: '{query}'")
    results = search(query, top_k=3)
    for rank, (score, text) in enumerate(results, start=1):
        print(f"  [{rank}] {score:.4f} — {text[:60]}")
```

---

## Saving and reloading the index

Persisting the index avoids re-embedding documents on every startup.

```python
import json

import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS is a high-speed vector search library from Facebook AI Research.",
    "Cosine similarity measures the directional similarity between two vectors.",
    "Embedding models project text into a high-dimensional vector space.",
]

doc_vectors = np.array(embedding_model.embed_documents(documents), dtype=np.float32)
dimension = doc_vectors.shape[1]

index = faiss.IndexFlatIP(dimension)
index.add(doc_vectors)

# save
faiss.write_index(index, "faiss.index")
with open("documents.json", "w") as f:
    json.dump(documents, f, indent=2)

print(f"saved: {index.ntotal} vectors")

# reload
loaded_index = faiss.read_index("faiss.index")
with open("documents.json") as f:
    loaded_documents = json.load(f)

print(f"reloaded: {loaded_index.ntotal} vectors")

# verify with a query
query_vector = np.array(
    [embedding_model.embed_query("vector search speed")], dtype=np.float32
)
scores, indices = loaded_index.search(query_vector, 2)

print("\nresults:")
for score, idx in zip(scores[0], indices[0]):
    print(f"  {score:.4f} — {loaded_documents[idx]}")
```

`faiss.write_index()` and `faiss.read_index()` use FAISS's own binary format, which loads faster than NumPy `.npy` files at scale.

---

## IndexFlatL2 versus IndexFlatIP

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "Python async programming",
    "handling concurrency in Python",
    "training a machine learning model",
    "walking the dog in the park",
]

vectors_norm = model.encode(sentences, normalize_embeddings=True).astype(np.float32)
vectors_raw = model.encode(sentences, normalize_embeddings=False).astype(np.float32)

query = "Python concurrency"
query_norm = model.encode(query, normalize_embeddings=True).reshape(1, -1).astype(np.float32)
query_raw = model.encode(query, normalize_embeddings=False).reshape(1, -1).astype(np.float32)

dim = vectors_norm.shape[1]

idx_ip = faiss.IndexFlatIP(dim)
idx_ip.add(vectors_norm)
scores_ip, indices_ip = idx_ip.search(query_norm, 2)

idx_l2 = faiss.IndexFlatL2(dim)
idx_l2.add(vectors_raw)
scores_l2, indices_l2 = idx_l2.search(query_raw, 2)

print("IndexFlatIP (higher = more similar):")
for score, idx in zip(scores_ip[0], indices_ip[0]):
    print(f"  {score:.4f} — {sentences[idx]}")

print("\nIndexFlatL2 (lower = more similar):")
for score, idx in zip(scores_l2[0], indices_l2[0]):
    print(f"  {score:.4f} — {sentences[idx]}")
```

Both indexes return the correct ranking. For text retrieval, `IndexFlatIP` with normalized vectors is the standard choice.

---

## Choosing an index

![float64 input error path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-04-choosing-an-index.en.png)

*float64 input error path*
| Index | Accuracy | Speed | Memory | Typical scale |
|---|---|---|---|---|
| IndexFlatL2 / IP | 100% | O(n) | n × d × 4B | up to ~100K |
| IndexIVFFlat | 99%+ | O(n/nlist) | n × d × 4B | 100K–1M |
| IndexHNSWFlat | 98%+ | O(log n) | n × d × 4B + graph | any |

Start with `IndexFlatIP`. When search latency becomes a problem, move to `IndexIVFFlat` or `IndexHNSWFlat`.

---

## Scaling to HNSW and IVF

Flat indexes set the baseline, but traffic growth hits their limits fast. The two most common next steps are HNSW and IVF.

| Aspect | HNSW (`IndexHNSWFlat`) | IVF (`IndexIVFFlat`) |
|---|---|---|
| Search complexity | Graph traversal, very fast in practice | Coarse quantizer narrows candidates |
| Build characteristics | Build time/memory increases with graph | Requires a `train()` step |
| Online additions | Relatively natural | Possible, but distribution shift may require retraining |
| Key parameters | `M`, `efConstruction`, `efSearch` | `nlist`, `nprobe` |

HNSW gives more intuitive tuning feedback early on. IVF offers more predictable cost modeling at very large scale.

## HNSW creation example

```python
import faiss
import numpy as np

dimension = 384
vectors = np.random.rand(50000, dimension).astype(np.float32)
faiss.normalize_L2(vectors)

index_hnsw = faiss.IndexHNSWFlat(dimension, 32)  # M=32
index_hnsw.hnsw.efConstruction = 200
index_hnsw.hnsw.efSearch = 64
index_hnsw.add(vectors)

print(index_hnsw.ntotal)
```

Increasing `efSearch` improves recall but also increases latency. In production, it is common to vary `efSearch` by query type.

## IVF creation example

```python
import faiss
import numpy as np

dimension = 384
nlist = 1024
vectors = np.random.rand(50000, dimension).astype(np.float32)
faiss.normalize_L2(vectors)

quantizer = faiss.IndexFlatIP(dimension)
index_ivf = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
index_ivf.train(vectors)
index_ivf.add(vectors)
index_ivf.nprobe = 24

print(index_ivf.is_trained, index_ivf.ntotal)
```

IVF without `train()` cannot search. Training data must reflect the actual distribution. Random samples lead to noticeably lower recall.

## Why tuning logs matter

Recording tuning results in a table speeds up team decision-making.

| Index | Parameters | Recall@10 | p95 (ms) | Memory (GB) |
|---|---|---:|---:|---:|
| FlatIP | - | 1.00 | 78 | 1.5 |
| HNSW | M=32, efSearch=64 | 0.97 | 18 | 2.2 |
| HNSW | M=32, efSearch=128 | 0.99 | 29 | 2.2 |
| IVF | nlist=1024, nprobe=12 | 0.92 | 11 | 1.6 |
| IVF | nlist=1024, nprobe=32 | 0.97 | 22 | 1.6 |

With this record, tradeoff discussions ("accept lower recall for budget savings" vs "maintain accuracy at all costs") happen with numbers, not opinions.

## Production scaling patterns

When deploying FAISS to production, plan for these patterns:

- Scale read traffic horizontally via index replicas
- Separate index build from serving index; deploy via atomic swap
- Log `index_version` and `embedding_version` together
- Periodically evaluate whether batch rebuild is more stable than incremental adds

These patterns reduce not only search latency but also incident recovery time.

## IVF parameter tuning workflow

For IVF in production, tune `nlist` and `nprobe` separately. `nlist` defines index structure; `nprobe` controls query-time search breadth.

1. Choose ~3 `nlist` candidates based on data size.
2. For each `nlist`, sweep `nprobe` upward measuring recall/latency.
3. Adopt the minimum `nprobe` that meets the SLA.

```python
def sweep_nprobe(index_ivf, queries, truths, nprobe_values):
    rows = []
    for nprobe in nprobe_values:
        index_ivf.nprobe = nprobe
        recall, elapsed = benchmark(index_ivf, queries, truths, k=10)
        rows.append((nprobe, recall, elapsed))
    return rows
```

| nprobe | Recall@10 | p95 (ms) |
|---:|---:|---:|
| 4 | 0.83 | 7 |
| 8 | 0.89 | 10 |
| 16 | 0.94 | 16 |
| 32 | 0.97 | 28 |

The balance point is typically around 16 for most workloads.

## HNSW parameter interpretation

In HNSW, `M` controls graph connectivity and `efSearch` controls search-time candidate breadth. Higher `M` increases memory and build time; higher `efSearch` increases query latency.

| M | efSearch | Recall@10 | p95 (ms) | Memory multiplier |
|---:|---:|---:|---:|---:|
| 16 | 32 | 0.90 | 8 | 1.0x |
| 32 | 64 | 0.96 | 14 | 1.5x |
| 48 | 96 | 0.98 | 23 | 2.0x |

Decide first whether the service is more sensitive to memory or latency, then select parameters accordingly.

## Delete and update strategy

FAISS Flat indexes do not natively support frequent deletions. The standard workaround:

- Maintain a tombstone table of deleted document IDs
- Post-filter tombstone IDs from query results
- Apply tombstones during periodic batch rebuilds

```python
def filter_deleted(results, deleted_ids: set[str]):
    return [r for r in results if r["doc_id"] not in deleted_ids]
```

If updates and deletes are very frequent, managed vector databases (Qdrant, Pinecone) often reduce operational complexity.

## Incident response playbook

Common index-layer incidents and first-response actions:

| Symptom | Common cause | First response |
|---|---|---|
| Scores uniformly low | Normalization mismatch, model swap | Compare manifests, check reindex status |
| Latency spike | nprobe/efSearch increased, vector count grew | Roll back parameters, reduce top-k |
| Quality drop | IVF train sample distribution mismatch | Retrain with fresh representative sample |

Including this table in the runbook shortens on-call response time.

## Building a search accuracy baseline

The most important ANN tuning principle: always have a ground-truth baseline. Typically built with `IndexFlatIP` or `IndexFlatL2` exact search. All HNSW/IVF recall is measured against this.

```python
def build_ground_truth(flat_index, queries, k=10):
    _, indices = flat_index.search(queries, k)
    return indices
```

Keeping the baseline explicit means performance changes can be tracked quantitatively when data or parameters change.

## Memory estimation

Estimate memory requirements before selecting an instance:

```text
memory (bytes) ≈ n (vectors) × d (dimension) × 4 (float32)
```

Example: `n=3,000,000`, `d=384` → raw vectors alone ≈ 4.3 GB. HNSW graph overhead adds significantly more. Capacity planning with headroom is mandatory before instance selection.

## Sharding and replication

When data outgrows a single index, two patterns apply:

- **Sharding**: partition indexes by document-ID hash or domain
- **Replication**: copy each shard to multiple nodes for read throughput
- **Aggregation**: collect per-shard top-k, re-rank globally

This adds complexity but maintains latency and availability under heavy traffic.

## Benchmark report template

Standardize benchmark reporting for comparability:

| Field | Example |
|---|---|
| Dataset version | `docs_2026_05_20` |
| Embedding model | `all-MiniLM-L6-v2` |
| Index type | `IndexHNSWFlat` |
| Key parameters | `M=32, efSearch=64` |
| Recall@10 | `0.968` |
| p95 latency | `18ms` |
| Memory | `2.2GB` |

When recording benchmarks, prefer distributions (p50, p95, p99) over single averages. Tail latency affects user perception disproportionately — the same mean can hide dramatically different p99 values.

## Conclusion

You can now build a FAISS index, run queries against it, and persist it to disk. The combination of `IndexFlatIP` with normalized vectors is the baseline for text retrieval.

The next post covers chunking. We will look at how chunk size, overlap, and split strategy affect retrieval quality — and why getting this wrong causes more problems than choosing the wrong embedding model.

## Operational checklist

- [ ] Picked an index type that matches your data scale and latency budget
- [ ] Trained IVF/PQ-style indexes on a representative sample
- [ ] Persisted the index and reproduced it on the same environment
- [ ] Tuned nprobe/ef from measurements, not from defaults
- [ ] Added metrics for vector count, dimension, and memory footprint

## Answering the Opening Questions

- **Where does a simple loop over vectors stop being good enough?**
  A brute-force loop becomes expensive as vector count and dimensionality grow because every query compares against every stored vector.

- **What assumption should decide between IndexFlatIP and IndexFlatL2?**
  Use IndexFlatIP when normalized vectors should behave like cosine ranking, and IndexFlatL2 when coordinate distance is the intended metric.

- **When saving and reloading an index, how do vectors and metadata stay aligned?**
  Persist the row-id mapping together with document ids, source text, and metadata so reloaded search results point to the same records.

<!-- toc:begin -->
## In this series

- [Vector Search 101 (1/6): What is an embedding — converting text into vectors](./01-what-is-embedding.md)
- [Vector Search 101 (2/6): HuggingFace embeddings in practice — creating your first vectors with sentence-transformers](./02-huggingface-embeddings.md)
- [Vector Search 101 (3/6): Cosine similarity and vector search — computing sentence distances](./03-cosine-similarity.md)
- **Vector Search 101 (4/6): FAISS fundamentals — fast approximate nearest-neighbor search (current)**
- Vector Search 101 (5/6): Chunking strategies — how to split long documents (upcoming)
- Vector Search 101 (6/6): Vector search pipeline — from document ingestion to query (upcoming)

<!-- toc:end -->

---

## References

- [FAISS documentation](https://faiss.ai/)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [FAISS index selection guide](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index)
- [faiss-cpu on PyPI](https://pypi.org/project/faiss-cpu/)

Tags: Vector Search, FAISS, Embeddings, Python
