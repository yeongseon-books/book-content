---
title: 'HuggingFace embeddings in practice — creating your first vectors with sentence-transformers'
series: vector-search-101
episode: 2
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

# HuggingFace embeddings in practice — creating your first vectors with sentence-transformers

> Vector Search 101 (2/6)

Post 1 covered the concept. This post is about running real code. Moving from theory to working embeddings surfaces a set of practical questions that conceptual explanations skip: how to reduce model loading time, how to structure batches, how to save vectors to disk and reload them efficiently.

`HuggingFaceEmbeddings` from `langchain-community` wraps `sentence-transformers` behind a LangChain-compatible interface. Even if you are not building a LangChain pipeline, the wrapper pattern itself is worth understanding — it shows how embedding models are typically integrated into larger application stacks.

This post covers five things:

- installing and initializing `HuggingFaceEmbeddings`
- the difference between single-query and batch embedding
- saving vectors to NumPy files and reloading them
- practical tips for speeding up encoding on CPU
- comparing the wrapper to the raw `SentenceTransformer` API

---

## Installation

Three packages are needed.

```bash
pip install langchain-community sentence-transformers numpy
```

`langchain-community` provides `HuggingFaceEmbeddings`. `sentence-transformers` handles model loading and encoding. `numpy` handles vector storage and arithmetic.

---

## First embedding

Initialize the model and encode a single sentence.

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

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

```
type: <class 'list'>
dimension: 384
first 5 values: [0.0523, -0.1847, 0.3012, 0.0934, -0.0721]
```

`embed_query()` handles a single input and returns a plain Python list. Convert to `np.array()` when you need NumPy operations.

---

## Batch embedding

For multiple documents, a single `embed_documents()` call outperforms a loop of `embed_query()` calls. The model processes inputs in batches internally, and the overhead of repeated setup adds up fast.

```python
import time

import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings

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

Recomputing embeddings for the same documents on every run wastes time. Save the matrix once and reload it.

```python
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings

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

```
saved: (3, 384)
reloaded: (3, 384)
identical: True
```

Save the source texts alongside the vectors. Without the original text, search results are just index positions.

```python
import json
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings

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

`HuggingFaceEmbeddings` wraps `SentenceTransformer`. Their outputs are numerically identical.

```python
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
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

```
HuggingFaceEmbeddings shape: (384,)
SentenceTransformer shape:   (384,)
max difference: 0.000001
```

Floating-point rounding aside, the results are the same. Use `HuggingFaceEmbeddings` when building LangChain pipelines. Use `SentenceTransformer` directly when you do not need the abstraction.

---

## Conclusion

You can now produce, save, and reload embeddings with a few lines of code. The batch encoding pattern and module-level initialization are production-ready habits worth keeping from the start.

The next post moves to similarity computation. We will look at when cosine similarity, dot product, and Euclidean distance each make sense, why normalization changes the arithmetic, and how to build a brute-force nearest-neighbor search from scratch.

<!-- toc:begin -->
## In this series

- [What is an embedding — converting text into vectors](./01-what-is-embedding.md)
- **HuggingFace embeddings in practice — creating your first vectors with sentence-transformers (current)**
- Cosine similarity and vector search — computing sentence distances (upcoming)
- FAISS fundamentals — fast approximate nearest-neighbor search (upcoming)
- Chunking strategies — how to split long documents (upcoming)
- Vector search pipeline — from document ingestion to query (upcoming)

<!-- toc:end -->

---

## References

- [langchain-community HuggingFaceEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/huggingfacehub/)
- [sentence-transformers encode API](https://www.sbert.net/docs/package_reference/SentenceTransformer.html)
- [all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

Tags: Vector Search, FAISS, Embeddings, Python
