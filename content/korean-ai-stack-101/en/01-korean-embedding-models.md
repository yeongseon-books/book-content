---
title: 'Korean embedding models compared — KoSimCSE, BGE-M3, Solar'
series: korean-ai-stack-101
episode: 1
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- LLM
- Embeddings
- OCR
last_reviewed: '2026-05-01'
---

# Korean embedding models compared — KoSimCSE, BGE-M3, Solar

> Korean AI Stack 101 (1/6)

Example code: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/01-korean-embedding-models)

Embedding models designed around English corpora do not reliably capture the meaning of Korean sentences. Understanding that "나는 밥을 먹었다" and "I had a meal" are semantically equivalent requires a model that has learned Korean morphology. This post compares three embedding models suited for Korean NLP work.

Topics:

- why Korean-specific embedding models matter
- characteristics of KoSimCSE, BGE-M3, and Solar Embedding
- side-by-side similarity scores on the same sentence pairs
- a practical guide to choosing between them

---

## Why Korean-specific models matter

A multilingual model like `sentence-transformers/all-MiniLM-L6-v2` can process Korean text, but its training corpus is English-dominant. It is not sensitive to Korean particles, verb endings, or the way meaning is packed into suffixes. As a result, "서울시청" and "서울 시청" — the same place, written with and without a space — can end up far apart in embedding space. Korean-specific models trained on morpheme-tokenized data reduce these errors.

---

## Three models at a glance

**KoSimCSE-RoBERTa** (`BM-K/KoSimCSE-roberta-multitask`): A Korean SimCSE model from the open-source community. Strong on Korean sentence similarity benchmarks. Outputs 768-dimensional vectors. Free on HuggingFace.

**BGE-M3** (`BAAI/bge-m3`): A multilingual model from BAAI supporting 100-plus languages, with solid Korean performance. Supports dense, sparse, and multi-vector retrieval in the same model, making it well suited for hybrid search. Outputs 1024-dimensional vectors.

**Solar Embedding** (`upstage/solar-embedding-1-large-query`): A bilingual Korean/English model from Upstage optimized for Korean RAG. Delivered as an API. Uses 4096-dimensional vectors to capture fine semantic distinctions.

---

## Side-by-side comparison

```python
import numpy as np
from sentence_transformers import SentenceTransformer

print("loading models...")

kosimcse = SentenceTransformer("BM-K/KoSimCSE-roberta-multitask")
bge_m3 = SentenceTransformer("BAAI/bge-m3")

print("models loaded")

# Korean sentence pairs with expected similarity label
sentence_pairs = [
    ("나는 오늘 밥을 먹었다.", "나는 오늘 식사를 했다.", "similar"),
    ("서울 날씨가 맑다.", "부산 날씨가 흐리다.", "unrelated"),
    ("파이썬으로 웹 서버를 만들었다.", "Python을 이용해 웹 앱을 개발했다.", "similar"),
    ("고양이가 쥐를 잡았다.", "주식 시장이 하락했다.", "unrelated"),
    ("인공지능이 의료 진단을 돕는다.", "AI가 병원에서 환자 진단을 지원한다.", "similar"),
]

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def compare_models(pairs: list[tuple]) -> None:
    print(f"\n{'Sentence A':<32} {'Sentence B':<32} {'Expected':^8} {'KoSimCSE':^10} {'BGE-M3':^10}")
    print("-" * 96)

    for sent_a, sent_b, expected in pairs:
        vec_a = kosimcse.encode(sent_a, normalize_embeddings=True)
        vec_b = kosimcse.encode(sent_b, normalize_embeddings=True)
        ko_sim = cosine_similarity(vec_a, vec_b)

        vec_a = bge_m3.encode(sent_a, normalize_embeddings=True)
        vec_b = bge_m3.encode(sent_b, normalize_embeddings=True)
        bge_sim = cosine_similarity(vec_a, vec_b)

        a_display = sent_a[:30] + ".." if len(sent_a) > 32 else sent_a
        b_display = sent_b[:30] + ".." if len(sent_b) > 32 else sent_b
        print(f"{a_display:<32} {b_display:<32} {expected:^8} {ko_sim:^10.3f} {bge_sim:^10.3f}")

compare_models(sentence_pairs)
```

---

## Dimensionality and retrieval performance

Higher embedding dimensionality can encode finer semantic distinctions, but it increases storage and search time proportionally.

```python
import time

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# KoSimCSE: 768 dims
# BGE-M3:   1024 dims
# Solar:    4096 dims (API only)

bge_m3 = SentenceTransformer("BAAI/bge-m3")

documents = [
    "Comparing Python web development frameworks",
    "Training machine learning models step by step",
    "Korean natural language processing techniques",
    "Database index optimization strategies",
    "Cloud service architecture design",
    "Deep learning image classification models",
    "API security and authentication methods",
    "Docker container deployment strategies",
] * 100  # 800 documents

print(f"document count: {len(documents)}")

start = time.time()
embeddings = bge_m3.encode(documents, normalize_embeddings=True, show_progress_bar=True)
embed_time = time.time() - start
print(f"embedding time: {embed_time:.2f}s")
print(f"embedding dims: {embeddings.shape[1]}")
print(f"storage size: {embeddings.nbytes / 1024:.1f} KB")

embeddings_f32 = embeddings.astype(np.float32)
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings_f32)

query = "deep learning models for natural language processing"
query_vec = bge_m3.encode([query], normalize_embeddings=True).astype(np.float32)

start = time.time()
for _ in range(100):
    distances, indices = index.search(query_vec, k=5)
search_time = (time.time() - start) / 100 * 1000
print(f"\nsearch latency: {search_time:.3f}ms (100-run average)")
print("top 5 results:")
for i, idx in enumerate(indices[0]):
    print(f"  {i + 1}. [{distances[0][i]:.3f}] {documents[idx]}")
```

---

## Choosing between models

**Korean-only, free, lightweight**: KoSimCSE. At 768 dimensions it is storage-efficient and available directly from HuggingFace. It has been validated on Korean sentence similarity benchmarks.

**Mixed Korean/English documents**: BGE-M3. Technical documentation and academic papers often mix English terms into Korean sentences. BGE-M3 handles this well and also supports hybrid dense+sparse retrieval.

**Highest quality Korean RAG, API budget available**: Solar Embedding. The 4096-dimensional vectors distinguish fine-grained semantic differences, and Upstage has specifically optimized it for Korean.

---

## Conclusion

No single model is best for every scenario. For zero-cost experimentation, start with KoSimCSE or BGE-M3. The next post builds a sentence similarity search system using KoSimCSE, walking through each step from encoding to retrieval.

<!-- blog-only:start -->
Next: [Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- **Korean embedding models compared — KoSimCSE, BGE-M3, Solar (current)**
- Building sentence similarity search with KoSimCSE (upcoming)
- BGE-M3 multilingual embedding in practice (upcoming)
- Document text extraction with CLOVA OCR API (upcoming)
- Using HyperCLOVA X and Solar API (upcoming)
- Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [KoSimCSE paper (Kim et al., 2021)](https://arxiv.org/abs/2109.12145)
- [BGE-M3 on HuggingFace](https://huggingface.co/BAAI/bge-m3)
- [Upstage Solar Embedding](https://developers.upstage.ai/docs/apis/embeddings)
- [SentenceTransformers library](https://www.sbert.net/)

Tags: Korean NLP, LLM, Embeddings, OCR
