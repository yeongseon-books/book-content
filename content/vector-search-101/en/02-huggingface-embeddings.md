---
episode: 2
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
title: "Vector Search 101 (2/6): HuggingFace embeddings in practice — creating your first vectors with sentence-transformers"
seo_description: Learn to use HuggingFace sentence-transformers locally to generate text vectors, manage batches, and save embeddings for semantic search applications.
---

# Vector Search 101 (2/6): HuggingFace embeddings in practice — creating your first vectors with sentence-transformers

Post 1 covered the concept. This post is about running real code. Moving from theory to working embeddings surfaces a set of practical questions that conceptual explanations skip: how to reduce model loading time, how to structure batches, how to save vectors to disk and reload them efficiently.

`HuggingFaceEmbeddings` from `langchain-huggingface` wraps `sentence-transformers` behind a LangChain-compatible interface. Even if you are not building a LangChain pipeline, the wrapper pattern itself is worth understanding — it shows how embedding models are typically integrated into larger application stacks.

This is the 2nd post in the Vector Search 101 series.

Here we turn local embeddings into a reusable workflow: initialize once, encode in batch, persist the vectors, and reload them safely.

![Single query embedding call flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-01-huggingface-embeddings-in-practice-creat.en.png)
*Single query embedding call flow*
> The core of HuggingFace embedding practice is not just learning to call one model well. It is learning a repeatable flow that produces the same vectors and lets you reuse them.

## Questions to Keep in Mind

- Where do you verify that vectors from sentence-transformers are actually usable for search?
- What changes in production when you move from one-by-one encoding to batch encoding?
- What metadata must travel with saved vectors so the result can be reproduced later?

## Installation

Three packages are needed.

```bash
pip install langchain-huggingface sentence-transformers numpy
```

`langchain-huggingface` provides `HuggingFaceEmbeddings`. `sentence-transformers` handles model loading and encoding. `numpy` handles vector storage and arithmetic.

---

## First embedding

![From sentence to 384-dim vector](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-01-first-embedding.en.png)

*From sentence to 384-dim vector*
Initialize the model and encode a single sentence.

```python
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
```

`model_kwargs={"device": "cpu"}` makes the CPU target explicit. Switch to `"cuda"` if a GPU is available.

`encode_kwargs={"normalize_embeddings": True}` matters. With L2 normalization applied, cosine similarity simplifies to a dot product. This keeps behavior consistent when you connect the model to FAISS or any other library that assumes unit vectors.

```python
text = "Vector search is the foundation of semantic retrieval."
vector = embedding_model.embed_query(text)

print(f"type: {type(vector)}")
print(f"dimension: {len(vector)}")
print(f"first 5 values: {vector[:5]}")
```

`embed_query()` handles a single input and returns a plain Python list. Convert to `np.array()` when you need NumPy operations.

---

## Batch embedding

![Single call and batch call contrast](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-02-batch-embedding.en.png)

*Single call and batch call contrast*
For multiple documents, a single `embed_documents()` call outperforms a loop of `embed_query()` calls. The model processes inputs in batches internally, and the overhead of repeated setup adds up fast.

```python
import time

import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS is a vector search library from Facebook AI Research.",
    "Cosine similarity measures the angle between two vectors.",
    "Higher embedding dimensions can capture more information.",
    "sentence-transformers specializes in sentence-level embeddings.",
    "Chunk size affects both embedding quality and retrieval accuracy.",
]

start = time.perf_counter()
vectors = embedding_model.embed_documents(documents)
elapsed = time.perf_counter() - start

vectors_np = np.array(vectors)
print(f"matrix shape: {vectors_np.shape}")  # (5, 384)
print(f"elapsed: {elapsed:.3f}s")
```

The gap between batch and loop grows with document count. For large corpora, always prefer `embed_documents()`.

---

## Saving and reloading vectors

![Vector and document save flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-03-saving-and-reloading-vectors.en.png)

*Vector and document save flow*
Recomputing embeddings for the same documents on every run wastes time. Save the matrix once and reload it.

```python
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS is a high-speed vector search library.",
    "Saving embeddings to disk makes reuse straightforward.",
    "NumPy is optimized for array operations.",
]

vectors = np.array(embedding_model.embed_documents(documents))

# save
np.save("embeddings.npy", vectors)
print(f"saved: {vectors.shape}")

# reload
loaded = np.load("embeddings.npy")
print(f"reloaded: {loaded.shape}")
print(f"identical: {np.allclose(vectors, loaded)}")
```

Save the source texts alongside the vectors. Without the original text, search results are just index positions.

```python
import json
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS is a high-speed vector search library.",
    "Saving embeddings to disk makes reuse straightforward.",
    "NumPy is optimized for array operations.",
]

vectors = np.array(embedding_model.embed_documents(documents))

np.save("embeddings.npy", vectors)
with open("documents.json", "w") as f:
    json.dump(documents, f, indent=2)

print("saved embeddings and documents")
```

Post 4 uses exactly this pattern to build a working FAISS search system.

---

## Practical speed tips

![Model reuse and batch size path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-04-practical-speed-tips.en.png)

*Model reuse and batch size path*
CPU encoding is slow at scale. Several adjustments help.

**Increase batch size.** The default is 32. If memory allows, bumping to 64 or 128 reduces overhead.

```python
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True, "batch_size": 64},
)
```

**Initialize once.** Model weight loading takes a few seconds. Create the `HuggingFaceEmbeddings` object once at the module level and reuse it.

```python
# module level — initialize once
_embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

def get_embedding_model() -> HuggingFaceEmbeddings:
    return _embedding_model
```

**Cache repeated inputs.** If the same texts are encoded repeatedly, cache the results in a dictionary. For large workloads, `diskcache` or `joblib.Memory` handle persistence automatically.

---

## Comparing wrapper and raw API

![Wrapper and raw API comparison structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-05-comparing-wrapper-and-raw-api.en.png)

*Wrapper and raw API comparison structure*
`HuggingFaceEmbeddings` wraps `SentenceTransformer`. Their outputs are numerically identical.

```python
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

text = "Checking that both libraries produce the same output."

hf_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
hf_vector = np.array(hf_model.embed_query(text))

st_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
st_vector = st_model.encode(text, normalize_embeddings=True)

print(f"HuggingFaceEmbeddings shape: {hf_vector.shape}")
print(f"SentenceTransformer shape:   {st_vector.shape}")
print(f"max difference: {np.max(np.abs(hf_vector - st_vector)):.6f}")
```

Floating-point rounding aside, the results are the same. Use `HuggingFaceEmbeddings` when building LangChain pipelines. Use `SentenceTransformer` directly when you do not need the abstraction.

---

## Batch size tuning experiment template

The most common production question is "what batch size should I use?" The answer varies by hardware, but the experiment template is universal. The key is measuring throughput (docs/sec) and p95 latency together.

```python
import statistics
import time

from langchain_huggingface import HuggingFaceEmbeddings

texts = [f"sample document {i}" for i in range(2000)]

def run_batch_test(batch_size: int) -> tuple[float, float]:
    model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True, "batch_size": batch_size},
    )
    timings = []
    chunk = 200
    for i in range(0, len(texts), chunk):
        window = texts[i : i + chunk]
        start = time.perf_counter()
        model.embed_documents(window)
        timings.append((time.perf_counter() - start) * 1000)
    mean_ms = sum(timings) / len(timings)
    p95_ms = statistics.quantiles(timings, n=20)[18]
    return mean_ms, p95_ms
```

| batch_size | mean batch time (ms) | p95 (ms) |
|---:|---:|---:|
| 16 | 72 | 89 |
| 32 | 54 | 67 |
| 64 | 43 | 58 |
| 128 | 40 | 77 |

When batch 128 improves the mean but spikes p95, batch 64 may be the safer production choice.

## Separating embedding generation from indexing

Embedding generation inside the search API makes operations harder. The standard pattern separates generation from indexing.

```python
from dataclasses import dataclass

import numpy as np

@dataclass
class EmbeddingArtifact:
    vectors: np.ndarray
    doc_ids: list[str]
    model_name: str
    normalized: bool

def build_embedding_artifact(doc_ids: list[str], docs: list[str]) -> EmbeddingArtifact:
    vectors = np.asarray(embedding_model.embed_documents(docs), dtype=np.float32)
    return EmbeddingArtifact(
        vectors=vectors,
        doc_ids=doc_ids,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        normalized=True,
    )
```

With this structure in place, connecting to FAISS, HNSW, IVF, or an external vector DB becomes straightforward.

## Loading into Chroma, Qdrant, and Pinecone

The same `HuggingFaceEmbeddings` output flows into different stores with minimal adaptation.

```python
# Chroma
from chromadb import PersistentClient

artifact = build_embedding_artifact(["doc-1", "doc-2"], ["Chunk A", "Chunk B"])
chroma = PersistentClient(path="./chroma")
col = chroma.get_or_create_collection("vs101")
col.add(ids=artifact.doc_ids, documents=["Chunk A", "Chunk B"], embeddings=artifact.vectors.tolist())
```

```python
# Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

qdrant = QdrantClient(path="./qdrant")
qdrant.recreate_collection("vs101", vectors_config=VectorParams(size=384, distance=Distance.COSINE))
qdrant.upsert(
    "vs101",
    points=[
        PointStruct(id=1, vector=artifact.vectors[0].tolist(), payload={"doc_id": "doc-1"}),
        PointStruct(id=2, vector=artifact.vectors[1].tolist(), payload={"doc_id": "doc-2"}),
    ],
)
```

```python
# Pinecone
from pinecone import Pinecone

pc = Pinecone(api_key="${PINECONE_API_KEY}")
index = pc.Index("vs101")
index.upsert(vectors=[("doc-1", artifact.vectors[0].tolist()), ("doc-2", artifact.vectors[1].tolist())])
```

## Operational failure patterns and pre-flight validation

Embedding-layer outages follow recurring patterns:

- Model changed but index not rebuilt — score distributions shift silently
- Multilingual input on an English-only model — recall drops
- Normalization flag inconsistent between indexing and query paths
- float64 vectors stored, then FAISS raises a dtype error on load

Production indexing jobs validate these checks before starting:

| Check | Action on failure |
|---|---|
| Embedding dimension == index dimension | Abort immediately |
| Normalization setting matches | Abort immediately |
| Model version tag present | Abort immediately |
| Sample query recall passes threshold | Hold deployment |

## Reproducible embedding artifact

Sharing embeddings across teams requires more than a bare `.npy` file. At minimum, store these fields alongside the vectors to enable reproducibility.

```python
import hashlib
import json
from pathlib import Path

import numpy as np

def sha256_texts(texts: list[str]) -> str:
    h = hashlib.sha256()
    for item in texts:
        h.update(item.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()

def persist_artifact(texts: list[str], vectors: np.ndarray, out_dir: str = "artifact") -> None:
    path = Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)

    np.save(path / "vectors.npy", vectors)
    (path / "documents.json").write_text(json.dumps(texts, ensure_ascii=False, indent=2))

    manifest = {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "dimension": int(vectors.shape[1]),
        "dtype": str(vectors.dtype),
        "normalized": True,
        "document_count": len(texts),
        "input_hash": sha256_texts(texts),
    }
    (path / "manifest.json").write_text(json.dumps(manifest, indent=2))
```

With this pattern, when an index incident occurs you can quickly isolate whether the inputs changed or the model changed.

## Mixed-language corpus considerations

When a corpus contains both Korean and English, vector distributions often diverge. An English-centric model may lose distance resolution for Korean queries. Run these checks early to catch the signal:

- Compute Recall@k separately for 20 Korean queries and 20 English queries
- Compare cosine score distributions for semantically equivalent Korean/English sentence pairs
- Check top-result error rate for Korean proper nouns (service names, error codes)

| Model | Korean Recall@5 | English Recall@5 | Notes |
|---|---:|---:|---|
| all-MiniLM-L6-v2 | 0.74 | 0.90 | Strong on English, weak on Korean |
| paraphrase-multilingual-MiniLM-L12-v2 | 0.86 | 0.87 | Balanced |

When the gap is this large, either switch models or implement language-detection routing.

## Dimension migration strategy

Changing the embedding model may change dimensionality. Moving from 384 to 768 dimensions, for example, requires a full reindex — partial updates are not possible.

```python
def requires_full_reindex(old_manifest: dict, new_manifest: dict) -> bool:
    keys = ["model_name", "dimension", "normalized"]
    return any(old_manifest.get(k) != new_manifest.get(k) for k in keys)
```

The recommended 3-step production process:

1. Build a parallel index (`index_v2`) in the background with the new model.
2. Evaluate `index_v1` vs `index_v2` on the test set for quality and latency.
3. Shift traffic gradually; decommission `index_v1` only after confirming no regressions.

Skipping this procedure and swapping immediately leaves you with weak rollback evidence when quality drops.

## Embedding quality regression test

The embedding layer can drift even without code changes — library upgrades, model cache corruption, or tokenizer updates all affect output. A minimal CI regression test catches this early.

```python
import numpy as np

EVAL_PAIRS = [
    ("python async programming", "handling concurrency in python", True),
    ("python async programming", "dog food recipe", False),
    ("faiss vector index", "approximate nearest neighbor", True),
]

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def run_embedding_regression(model) -> None:
    for a, b, should_be_similar in EVAL_PAIRS:
        va = np.asarray(model.embed_query(a), dtype=np.float32)
        vb = np.asarray(model.embed_query(b), dtype=np.float32)
        score = cosine(va, vb)
        if should_be_similar and score < 0.45:
            raise AssertionError(f"expected similar: {a} vs {b}, got {score:.4f}")
        if (not should_be_similar) and score > 0.35:
            raise AssertionError(f"expected dissimilar: {a} vs {b}, got {score:.4f}")
```

Thresholds vary by domain, but even this minimal harness catches model-swap mistakes before deployment.

## Encoding queue and backpressure

For large-scale document ingestion, embedding calls should not be synchronous inside the request path. A queue-based async pipeline is the standard separation:

- The ingestion stage pushes document IDs and raw text to a queue.
- Workers pull batches and generate embeddings.
- Failed batches route to a retry queue.
- The indexing stage receives only successful batches.

This architecture bounds API response latency even during traffic spikes.

## Conclusion

You can now produce, save, and reload embeddings with a few lines of code. The batch encoding pattern and module-level initialization are production-ready habits worth keeping from the start.

The next post moves to similarity computation. We will look at when cosine similarity, dot product, and Euclidean distance each make sense, why normalization changes the arithmetic, and how to build a brute-force nearest-neighbor search from scratch.

## Operational checklist

- [ ] Reviewed the model card (license, training data, dimensionality)
- [ ] Tuned batch size and tokenizer options for your CPU/GPU environment
- [ ] Validated Korean inputs against a multilingual or Korean-specialized model
- [ ] Aligned the result dimension and dtype with your index schema
- [ ] Stored the model version alongside any embedding kept long-term

## Answering the Opening Questions

- **Where do you verify that vectors from sentence-transformers are actually usable for search?**
  Verify shape, dtype, dimensionality, and a few similarity results before treating the vectors as search-ready.

- **What changes in production when you move from one-by-one encoding to batch encoding?**
  Batch encoding reduces per-call overhead and improves throughput, but production code must also manage latency, memory, and batch size.

- **What metadata must travel with saved vectors so the result can be reproduced later?**
  Store model name, model version, dimensionality, normalization choice, and input hashes with the vectors so the index can be reproduced.

<!-- toc:begin -->
## In this series

- [Vector Search 101 (1/6): What is an embedding — converting text into vectors](./01-what-is-embedding.md)
- **Vector Search 101 (2/6): HuggingFace embeddings in practice — creating your first vectors with sentence-transformers (current)**
- Vector Search 101 (3/6): Cosine similarity and vector search — computing sentence distances (upcoming)
- Vector Search 101 (4/6): FAISS fundamentals — fast approximate nearest-neighbor search (upcoming)
- Vector Search 101 (5/6): Chunking strategies — how to split long documents (upcoming)
- Vector Search 101 (6/6): Vector search pipeline — from document ingestion to query (upcoming)

<!-- toc:end -->

---

## References

- [langchain-huggingface HuggingFaceEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/huggingfacehub/)
- [sentence-transformers encode API](https://www.sbert.net/docs/package_reference/SentenceTransformer.html)
- [all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

Tags: Vector Search, FAISS, Embeddings, Python
