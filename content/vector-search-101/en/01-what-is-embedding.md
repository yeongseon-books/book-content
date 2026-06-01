---
episode: 1
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
title: "Vector Search 101 (1/6): What is an embedding — converting text into vectors"
seo_description: Learn how text embeddings transform natural language into numeric vectors to enable semantic search, machine-readable meaning, and vector similarity.
---

# Vector Search 101 (1/6): What is an embedding — converting text into vectors

Search engines have compared keywords for decades. A user types "python async", and the engine checks how often those words appear in each document and where. This works well when the query and the document share exact terms, but it breaks down when meaning is preserved while wording changes. "Handling concurrency in Python" and "Python async programming" mean the same thing, but a keyword engine may not connect them.

Embeddings approach the problem differently. They convert text into numeric vectors so that semantically similar sentences end up geometrically close in a high-dimensional space. The distance between those vectors becomes a proxy for meaning. That property makes keyword-free, meaning-based retrieval possible.

This is the first post in the Vector Search 101 series.

This post focuses on the concept and intuition behind embeddings. Code stays minimal, but we still build real vectors and read real similarity scores.

![Keyword search and embedding search contrast](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-01-what-is-an-embedding-converting-text-int.en.png)
*Keyword search and embedding search contrast*
> An embedding is not a format for storing text. It is a representation that makes meaning comparable by distance.

## Questions to Keep in Mind

- When keyword search misses documents with the same meaning but different wording, what is missing?
- What does it actually mean for two embedding vectors to be close?
- When choosing a first embedding model, which limits should you check before tuning anything else?

## The ceiling of keyword search

![Where exact keyword matching breaks down](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-01-the-ceiling-of-keyword-search.en.png)

*Where exact keyword matching breaks down*
Traditional search ranks results by term frequency and position. TF-IDF and BM25 are the canonical examples. These methods are fast, interpretable, and accurate when the query shares vocabulary with the document.

The problem is that language does not stay still. The same concept surfaces in many forms.

- "store it" — "persist it" — "write to DB" — "make it durable"
- "fast" — "low-latency" — "sub-millisecond response"
- "an error occurred" — "an exception was raised" — "the service crashed"

Keyword search misses every variant that is not in the index. Synonym dictionaries and stemming help at the margins, but manually covering the full surface of natural language variation does not scale.

Embeddings reframe the problem. Instead of asking "does this document contain these words?", they ask "how close is this document to the query in meaning space?".

---

## Vector space intuition

![Text entering vector space flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-02-vector-space-intuition.en.png)

*Text entering vector space flow*
An embedding model converts text into a fixed-length array of floating-point numbers. With `sentence-transformers/all-MiniLM-L6-v2`, every input — regardless of length — becomes a 384-dimensional vector. Models with 768 or 1536 dimensions are also common.

```text
"Python async programming"       → [0.12, -0.34, 0.87, ..., 0.05]  (384 numbers)
"handling concurrency in Python" → [0.14, -0.31, 0.85, ..., 0.07]  (384 numbers)
"homemade dog treats recipe"     → [-0.63, 0.77, -0.12, ..., 0.44] (384 numbers)
```

Think of these numbers as coordinates in a high-dimensional space. Sentences with similar meaning land near each other; unrelated sentences land far apart. Retrieval becomes a nearest-neighbor search in that space.

The most common distance measure is cosine similarity. It ignores vector magnitude and compares direction only, which makes it relatively stable across inputs of different lengths.

```text
cosine similarity = (A · B) / (|A| × |B|)
```

The value ranges from -1 to 1. Closer to 1 means more similar; 0 means unrelated; -1 means opposite in meaning. In practice, real sentence pairs tend to land between 0.2 and 0.95.

---

## How embedding models learn

![Positive and negative pair training structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-03-how-embedding-models-learn.en.png)

*Positive and negative pair training structure*
An embedding model is trained to place semantically similar sentence pairs close together and unrelated pairs far apart. The dominant training paradigm is contrastive learning.

Training data is typically structured like this:

- positive pairs: different passages from the same document, question-answer pairs, translation pairs
- negative pairs: randomly sampled unrelated sentences

The model updates its parameters to reduce the vector distance between positive pairs and increase it between negative pairs. After repeating this across hundreds of millions of sentence pairs, the model learns to project the semantic structure of language into a vector space.

`all-MiniLM-L6-v2` was trained on more than 1 billion sentence pairs. Its small size — about 22 MB — makes it fast enough to run on CPU, and its quality is sufficient for the retrieval tasks in this series.

---

## Creating your first vectors

![Three sentence encoding execution path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-04-creating-your-first-vectors.en.png)

*Three sentence encoding execution path*
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

"Python async programming" and "handling concurrency in Python" score highly despite sharing no exact words. "Homemade dog treats" lands near zero. These numbers are the foundation of vector search: rank documents by their cosine similarity to the query vector and return the top results.

---

## How ranking changes on a tiny corpus

One similarity score is useful, but ranking behavior is what matters in practice. Put keyword overlap next to embedding similarity for the same query, and the reason vector search matters becomes easier to see.

```python
import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def keyword_overlap_score(query: str, document: str) -> int:
    query_terms = set(query.lower().split())
    doc_terms = set(document.lower().split())
    return len(query_terms & doc_terms)

query = "python async programming"
documents = [
    "Python async programming patterns for web APIs",
    "Handling concurrency in Python with asyncio tasks",
    "Beginner recipe for homemade dog treats",
    "Distributed tracing for Java microservices",
]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
query_vector = model.encode(query)
doc_vectors = model.encode(documents)

results = []
for document, vector in zip(documents, doc_vectors):
    results.append(
        {
            "document": document,
            "keyword_overlap": keyword_overlap_score(query, document),
            "cosine": cosine_similarity(query_vector, vector),
        }
    )

for item in sorted(results, key=lambda x: (-x["keyword_overlap"], -x["cosine"])):
    print(
        f"keyword={item['keyword_overlap']} cosine={item['cosine']:.4f} | {item['document']}"
    )
```

The second document shares almost none of the query vocabulary, yet the embedding score is still strong. That is the practical value of semantic retrieval: useful matches survive wording changes.

## A fast sanity check for embedding quality

Once a model is wired in, the next question is usually "is 0.69 good or bad?" The fastest answer is not a benchmark suite. It is a small hand-built evaluation set drawn from the actual product vocabulary.

- Pick 5–10 query-document pairs that mean the same thing with different wording.
- Add 5 exact-string queries where identifiers must survive intact.
- Add a few clearly unrelated pairs and verify their scores stay low.
- Read the top 3 results for each query and mark whether they are genuinely useful.

That small pass tells you whether the model is directionally right or whether you should stop and rethink model choice before tuning chunking and indexing.

---

## Where embeddings fall short

![Limits with exact strings and long documents](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-05-where-embeddings-fall-short.en.png)

*Limits with exact strings and long documents*
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

## Locking the embedding contract in code

Once you understand the concept and are ready to wire embeddings into a service, the first step is to codify the embedding contract. By contract I mean explicitly declaring and enforcing the model name, dimensionality, normalization flag, input pre-processing, and output dtype. If this contract is loose, the same sentence can be embedded under different conditions across runs, scores drift unpredictably, and index reproducibility breaks.

```python
from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

@dataclass(frozen=True)
class EmbeddingSpec:
    model_name: str
    dimension: int
    normalize: bool
    dtype: str

SPEC = EmbeddingSpec(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    dimension=384,
    normalize=True,
    dtype="float32",
)

_model = SentenceTransformer(SPEC.model_name)

def embed_texts(texts: list[str]) -> np.ndarray:
    vectors = _model.encode(texts, normalize_embeddings=SPEC.normalize)
    vectors = np.asarray(vectors, dtype=np.float32)
    if vectors.shape[1] != SPEC.dimension:
        raise ValueError(f"dimension mismatch: got {vectors.shape[1]}, expected {SPEC.dimension}")
    return vectors
```

The advantage is straightforward. When you later swap the storage layer — FAISS, Chroma, Qdrant, Pinecone — the embedding generation rules stay unchanged. Score semantics survive infrastructure changes.

## Minimal wiring for common vector stores

After you know what an embedding is, the natural follow-up is "where do I put them?" The examples below are concept-comparison code, stripped to the minimum.

```python
# Chroma
from chromadb import PersistentClient

client = PersistentClient(path="./chroma-data")
collection = client.get_or_create_collection(name="docs-mini")
collection.add(
    ids=["d1", "d2"],
    documents=["Vector search introduction", "ANN indexing basics"],
    embeddings=embed_texts(["Vector search introduction", "ANN indexing basics"]).tolist(),
)
```

```python
# Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

qdrant = QdrantClient(path="./qdrant-local")
qdrant.recreate_collection(
    collection_name="docs-mini",
    vectors_config=VectorParams(size=SPEC.dimension, distance=Distance.COSINE),
)
vectors = embed_texts(["Vector search introduction", "ANN indexing basics"])
qdrant.upsert(
    collection_name="docs-mini",
    points=[
        PointStruct(id=1, vector=vectors[0].tolist(), payload={"text": "Vector search introduction"}),
        PointStruct(id=2, vector=vectors[1].tolist(), payload={"text": "ANN indexing basics"}),
    ],
)
```

```python
# Pinecone (managed service)
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="${PINECONE_API_KEY}")
index_name = "docs-mini"
if index_name not in [idx["name"] for idx in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=SPEC.dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
index = pc.Index(index_name)
vectors = embed_texts(["Vector search introduction", "ANN indexing basics"])
index.upsert(
    vectors=[
        ("d1", vectors[0].tolist(), {"text": "Vector search introduction"}),
        ("d2", vectors[1].tolist(), {"text": "ANN indexing basics"}),
    ]
)
```

All three stores have different API shapes but share one principle: `dimension`, `metric`, and `metadata schema` must align with the embedding contract.

## HNSW vs IVF — first-encounter criteria

ANN index algorithms look complex, but the early-stage decision criteria are simple.

| Aspect | HNSW | IVF |
|---|---|---|
| Core idea | Traverse a graph toward nearest candidates | Find the closest cluster center, scan only that bucket |
| Strength | High recall, relatively friendly to online updates | Memory efficient, predictable tuning at scale |
| Weakness | Higher memory consumption | Recall drops sharply without nlist/nprobe tuning |
| Key params | `M`, `efConstruction`, `efSearch` | `nlist`, `nprobe` |

The important message here is: do not commit to an index type in post 1. Lock the embedding and score semantics first. When data grows large enough to need ANN, switching is straightforward because the contract layer above stays unchanged.

## Why you need a baseline benchmark table early

You do not need a complex evaluation pipeline on day one. But you must record at least two axes from the start.

| Setup | top-5 recall (50 samples) | p95 latency (ms) |
|---|---:|---:|
| Brute force (NumPy) | 1.00 | 82 |
| FAISS IndexFlatIP | 1.00 | 27 |
| HNSW (efSearch=64) | 0.98 | 11 |
| IVF (nlist=256, nprobe=16) | 0.95 | 8 |

The numbers themselves matter less than having a fixed query set that lets you compare trends. Without this table, no one can prove whether a change made retrieval faster at the cost of quality or genuinely improved both.

One more practical tip: document the embedding schema in your index metadata. For example, storing `embedding_model`, `dimension`, `normalized`, and `distance_metric` as index-level metadata means that when team members rotate or the deployment environment changes, anyone can immediately verify what assumptions the index was built on.

## Conclusion

Embeddings convert text into numeric vectors where semantic similarity becomes spatial proximity. Cosine similarity measures that proximity and makes keyword-free retrieval possible. The intuition is simple: similar meaning, smaller distance.

The next post moves from concept to practice. We will use `HuggingFaceEmbeddings` to produce, save, and reload embeddings, and speed up the encoding step with batch processing.

## Operational checklist

- [ ] Recorded the model's dimensionality and token limit in your docs
- [ ] Decided on normalization once and applied it to every vector
- [ ] Keyed the embedding cache on model, version, and input hash
- [ ] Sanity-checked quality by computing similarity on a few hand-picked pairs
- [ ] Wrote a reindex procedure for when the embedding model changes

## Answering the Opening Questions

- **When keyword search misses documents with the same meaning but different wording, what is missing?**
  What is missing is a representation of meaning, not another keyword rule. Embeddings provide that representation by mapping text into vectors that can be compared geometrically.

- **What does it actually mean for two embedding vectors to be close?**
  Close means the vectors have a small distance or similar direction under the chosen metric, which the system treats as a proxy for semantic similarity.

- **When choosing a first embedding model, which limits should you check before tuning anything else?**
  Check dimensionality, token limit, language support, and model version first because those values define quality limits and reindexing cost.

<!-- toc:begin -->
## In this series

- **Vector Search 101 (1/6): What is an embedding — converting text into vectors (current)**
- Vector Search 101 (2/6): HuggingFace embeddings in practice — creating your first vectors with sentence-transformers (upcoming)
- Vector Search 101 (3/6): Cosine similarity and vector search — computing sentence distances (upcoming)
- Vector Search 101 (4/6): FAISS fundamentals — fast approximate nearest-neighbor search (upcoming)
- Vector Search 101 (5/6): Chunking strategies — how to split long documents (upcoming)
- Vector Search 101 (6/6): Vector search pipeline — from document ingestion to query (upcoming)

<!-- toc:end -->

---

## References

- [sentence-transformers documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Sentence Transformers pretrained models](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)
- [The Illustrated Word2Vec — Jay Alammar](https://jalammar.github.io/illustrated-word2vec/)

### Related Series

- [RAG Deep Dive](../../rag-deep-dive/en/01-document-loading-and-chunking.md) — shows how the embeddings and ANN indexes from this series get assembled inside a full RAG pipeline. Read it next if you care more about the "documents → chunks → retrieval → answer" flow than the search engine itself.

Tags: Vector Search, FAISS, Embeddings, Python
