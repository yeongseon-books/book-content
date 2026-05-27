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

![Single query embedding call flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-01-first-embedding.en.png)

*Single query embedding call flow*
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

<!-- injected-output:start -->
**Output**

    type: <class 'list'>
    dimension: 384
    first 5 values: [0.04267469793558121, 0.00979855377227068, -0.031552139669656754, -0.033105991780757904, 0.04774016514420509]

<!-- injected-output:end -->

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

<!-- injected-output:start -->
**Output**

    matrix shape: (5, 384)
    elapsed: 0.101s

<!-- injected-output:end -->

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

<!-- injected-output:start -->
**Output**

    saved: (3, 384)
    reloaded: (3, 384)
    identical: True

<!-- injected-output:end -->

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

<!-- injected-output:start -->
**Output**

    saved embeddings and documents

<!-- injected-output:end -->

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

<!-- injected-output:start -->
**Output**

    HuggingFaceEmbeddings shape: (384,)
    SentenceTransformer shape:   (384,)
    max difference: 0.000000

<!-- injected-output:end -->

Floating-point rounding aside, the results are the same. Use `HuggingFaceEmbeddings` when building LangChain pipelines. Use `SentenceTransformer` directly when you do not need the abstraction.

---

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
