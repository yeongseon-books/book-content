---
title: 'What is an embedding — converting text into vectors'
series: vector-search-101
episode: 1
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

# What is an embedding — converting text into vectors

> Vector Search 101 (1/6)

Example code: [github.com/yeongseon-books/vector-search-101](https://github.com/yeongseon-books/vector-search-101/tree/main/en/01-what-is-embedding)

Search engines have compared keywords for decades. A user types "python async", and the engine checks how often those words appear in each document and where. This works well when the query and the document share exact terms, but it breaks down when meaning is preserved while wording changes. "Handling concurrency in Python" and "Python async programming" mean the same thing, but a keyword engine may not connect them.

Embeddings approach the problem differently. They convert text into numeric vectors so that semantically similar sentences end up geometrically close in a high-dimensional space. The distance between those vectors becomes a proxy for meaning. That property makes keyword-free, meaning-based retrieval possible.

This post focuses on the concept and intuition behind embeddings. Code is minimal. We will cover five things:

- what embeddings are and why they emerged
- how meaning is represented as distance in vector space
- how embedding models learn that representation
- a first hands-on example that produces real vectors
- where embeddings fall short and what to watch for

---

## The ceiling of keyword search

Traditional search ranks results by term frequency and position. TF-IDF and BM25 are the canonical examples. These methods are fast, interpretable, and accurate when the query shares vocabulary with the document.

The problem is that language does not stay still. The same concept surfaces in many forms.

- "store it" — "persist it" — "write to DB" — "make it durable"
- "fast" — "low-latency" — "sub-millisecond response"
- "an error occurred" — "an exception was raised" — "the service crashed"

Keyword search misses every variant that is not in the index. Synonym dictionaries and stemming help at the margins, but manually covering the full surface of natural language variation does not scale.

Embeddings reframe the problem. Instead of asking "does this document contain these words?", they ask "how close is this document to the query in meaning space?".

---

## Vector space intuition

An embedding model converts text into a fixed-length array of floating-point numbers. With `sentence-transformers/all-MiniLM-L6-v2`, every input — regardless of length — becomes a 384-dimensional vector. Models with 768 or 1536 dimensions are also common.

```
"Python async programming"       → [0.12, -0.34, 0.87, ..., 0.05]  (384 numbers)
"handling concurrency in Python" → [0.14, -0.31, 0.85, ..., 0.07]  (384 numbers)
"homemade dog treats recipe"     → [-0.63, 0.77, -0.12, ..., 0.44] (384 numbers)
```

Think of these numbers as coordinates in a high-dimensional space. Sentences with similar meaning land near each other; unrelated sentences land far apart. Retrieval becomes a nearest-neighbor search in that space.

The most common distance measure is cosine similarity. It ignores vector magnitude and compares direction only, which makes it relatively stable across inputs of different lengths.

```
cosine similarity = (A · B) / (|A| × |B|)
```

The value ranges from -1 to 1. Closer to 1 means more similar; 0 means unrelated; -1 means opposite in meaning. In practice, real sentence pairs tend to land between 0.2 and 0.95.

---

## How embedding models learn

An embedding model is trained to place semantically similar sentence pairs close together and unrelated pairs far apart. The dominant training paradigm is contrastive learning.

Training data is typically structured like this:

- positive pairs: different passages from the same document, question-answer pairs, translation pairs
- negative pairs: randomly sampled unrelated sentences

The model updates its parameters to reduce the vector distance between positive pairs and increase it between negative pairs. After repeating this across hundreds of millions of sentence pairs, the model learns to project the semantic structure of language into a vector space.

`all-MiniLM-L6-v2` was trained on more than 1 billion sentence pairs. Its small size — about 22 MB — makes it fast enough to run on CPU, and its quality is sufficient for the retrieval tasks in this series.

---

## Creating your first vectors

Running the code once is faster than re-reading the theory. Install `sentence-transformers` and encode three sentences.

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "Python async programming",
    "handling concurrency in Python",
    "homemade dog treats recipe",
]

embeddings = model.encode(sentences)

print(f"number of vectors: {len(embeddings)}")
print(f"vector dimension: {embeddings[0].shape[0]}")
print(f"first vector (first 5 values): {embeddings[0][:5]}")
```

Running this gives output similar to:

```
number of vectors: 3
vector dimension: 384
first vector (first 5 values): [ 0.0812 -0.2193  0.3471  0.1034 -0.0657]
```

Now compute cosine similarity between all three pairs.

```python
import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "Python async programming",
    "handling concurrency in Python",
    "homemade dog treats recipe",
]

embeddings = model.encode(sentences)

print(f"[0] vs [1] (similar meaning): {cosine_similarity(embeddings[0], embeddings[1]):.4f}")
print(f"[0] vs [2] (unrelated):       {cosine_similarity(embeddings[0], embeddings[2]):.4f}")
```

Expected output:

```
[0] vs [1] (similar meaning): 0.8134
[0] vs [2] (unrelated):       0.0471
```

"Python async programming" and "handling concurrency in Python" score 0.81 despite sharing no common words. "Homemade dog treats" scores 0.05. These numbers are the foundation of vector search: rank documents by their cosine similarity to the query vector and return the top results.

---

## Where embeddings fall short

Embeddings are not a universal replacement for keyword search. Several situations favor the older approach.

**Exact identifiers and codes.** Searching for `ERR_CONNECTION_REFUSED` or `CVE-2024-12345` works better with keyword search. Embedding models abstract meaning, and in doing so they can blur precise symbolic information.

**Domain-specific language.** A general-purpose English model trained on web text may perform poorly on Korean medical records or legal contracts. Those cases call for domain-specific fine-tuning or a purpose-built model.

**Long documents.** `all-MiniLM-L6-v2` processes a maximum of 256 subword tokens. Text beyond that limit is truncated. Long documents must be split into chunks before embedding. Chunking strategy is the subject of post 5 in this series.

**Multilingual content.** Documents that mix languages are better served by a multilingual model like `paraphrase-multilingual-MiniLM-L12-v2` than by a single-language model.

In production, most systems combine keyword search with embedding-based retrieval — commonly called hybrid search — to compensate for the weaknesses of each approach. That pattern is touched on briefly in the final post of this series.

---

## Choosing a model

Which embedding model should you use? For a first project, these criteria narrow the field quickly.

**Speed and size.** If you are running on CPU, a lightweight model is essential. `all-MiniLM-L6-v2` is about 22 MB and encodes hundreds of sentences per second on a modern CPU. If accuracy matters more than speed, `all-mpnet-base-v2` at around 420 MB is a common step up.

**Language.** If Korean text is involved, a multilingual model or a Korean-specific model performs more reliably than an English-only one. Korean embeddings are covered in depth in the Korean AI Stack 101 series.

**Task.** Sentence similarity models and retrieval models are trained with slightly different objectives. Retrieval models are optimized for the case where query and document come from different distributions, which is common in search. The MTEB leaderboard's Retrieval section is a practical reference for comparing models on that task.

This series uses `all-MiniLM-L6-v2` throughout for consistency.

---

## Conclusion

Embeddings convert text into numeric vectors where semantic similarity becomes spatial proximity. Cosine similarity measures that proximity and makes keyword-free retrieval possible. The intuition is simple: similar meaning, smaller distance.

The next post moves from concept to practice. We will use `HuggingFaceEmbeddings` to produce, save, and reload embeddings, and speed up the encoding step with batch processing.

<!-- blog-only:start -->
Next: [HuggingFace embeddings in practice — creating your first vectors with sentence-transformers](./02-huggingface-embeddings.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- **What is an embedding — converting text into vectors (current)**
- HuggingFace embeddings in practice — creating your first vectors with sentence-transformers (upcoming)
- Cosine similarity and vector search — computing sentence distances (upcoming)
- FAISS fundamentals — fast approximate nearest-neighbor search (upcoming)
- Chunking strategies — how to split long documents (upcoming)
- Vector search pipeline — from document ingestion to query (upcoming)

<!-- toc:end -->

---

## References

- [sentence-transformers documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [The Illustrated Word2Vec — Jay Alammar](https://jalammar.github.io/illustrated-word2vec/)

Tags: Vector Search, FAISS, Embeddings, Python
