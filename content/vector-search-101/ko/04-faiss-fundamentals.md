---
episode: 4
language: ko
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
  medium: false
  mkdocs: true
  tistory: true
title: FAISS 입문 — 고속 근사 최근접 이웃 검색
seo_description: FAISS로 벡터 인덱스를 만들고 저장하고 검색하는 기본 패턴을 설명합니다.
---

# FAISS 입문 — 고속 근사 최근접 이웃 검색

문서 수가 수천, 수만 건으로 늘어나면 NumPy 기반 브루트 포스 검색은 금방 느려집니다. 차원이 384인 벡터 10만 개를 쿼리 하나와 비교하려면 쿼리마다 3,840만 번의 곱셈이 필요합니다. 이 정도 규모에서는 검색 지연이 수백 밀리초 이상으로 올라가며, 대화형 애플리케이션에는 너무 느립니다.

FAISS(Facebook AI Similarity Search)는 바로 이 문제를 풀기 위해 만들어졌습니다. 작은 정확도 손실과 큰 속도 향상을 맞바꾸는 근사 최근접 이웃 검색을 지원하고, 수십억 개 규모의 벡터도 처리할 수 있으며, CPU와 GPU 모두에서 빠르게 동작합니다.

이 글은 Vector Search 101 시리즈의 4번째 글입니다.

여기서는 검색 속도를 올릴 때 가장 먼저 만나는 FAISS의 기본 패턴을 정리합니다. 다음 다섯 가지를 다룹니다.

- FAISS 설치와 인덱스 유형 선택
- `IndexFlatL2`와 `IndexFlatIP`를 사용한 정확 검색
- 인덱스를 디스크에 저장하고 다시 불러오기
- 작은 코퍼스에 실제 쿼리를 날려 보기
- 인덱스 유형을 선택하는 기준

예제 코드: [github.com/yeongseon-books/vector-search-101](https://github.com/yeongseon-books/vector-search-101/tree/main/en/04-faiss-fundamentals)

![FAISS index type comparison structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-01-faiss-fundamentals-fast-approximate-near.ko.png)

*FAISS 인덱스 유형 비교 구조*
<!-- ebook-only:start -->

**핵심 아이디어**: FAISS는 벡터를 빠르게 찾습니다. 가장 단순한 선택은 IndexFlatL2이며, 데이터가 커지면 IVF나 HNSW로 넘어갑니다.

## 이 장의 위치

이 글은 시리즈 6편 중 4편입니다.
이전 글에서는 **코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기**를 다뤘습니다.
이 글 다음에는 **청크 전략 — 긴 문서를 어떻게 나눌 것인가**로 이어집니다.
<!-- ebook-only:end -->

---

> FAISS를 이해하는 가장 좋은 방법은 더 똑똑한 데이터베이스로 보는 것이 아니라, 벡터 검색 전용 계산 엔진으로 보는 것입니다.

## 이 글에서 다룰 문제

- FAISS의 IndexFlat, IVF, HNSW는 각각 언제 선택하는 것이 맞을까요?
- 정확 검색과 ANN 사이의 정확도-지연 시간 트레이드오프는 어떻게 이해해야 할까요?
- 어떤 인덱스 유형은 학습이 필요하고, 그 학습은 어떻게 진행할까요?
- FAISS 인덱스를 저장하고 다시 불러올 때 어떤 함정을 조심해야 할까요?
- 어떤 워크로드에서는 GPU FAISS가 CPU FAISS보다 유리하고, 또 어떤 경우에는 반대일까요?

## 설치

CPU 전용 버전은 아래와 같습니다.

```bash
pip install faiss-cpu sentence-transformers numpy
```

호환되는 GPU가 있다면 `faiss-cpu` 대신 `faiss-gpu`를 사용하면 됩니다.

---

## 인덱스 유형 이해하기

![FAISS index type comparison structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-01-understanding-index-types.ko.png)

*FAISS 인덱스 유형 비교 구조*
FAISS는 속도와 정확도 사이의 균형이 다른 여러 인덱스 유형을 제공합니다. 시작 단계에서는 두 가지만 확실히 이해해도 충분합니다.

**IndexFlatL2**: 유클리드 거리를 사용하는 정확 검색입니다. 모든 벡터를 하나도 건너뛰지 않고 비교합니다. 정확도는 100%지만, 검색 시간은 벡터 수에 선형으로 비례합니다.

**IndexFlatIP**: 내적을 사용하는 정확 검색입니다. 벡터가 정규화되어 있다면 내적은 코사인 유사도와 같습니다. 텍스트 검색에서는 보통 정규화된 벡터와 함께 이 인덱스를 사용합니다.

더 큰 배포에서는 `IndexIVFFlat`이나 `IndexHNSWFlat` 같은 근사 인덱스를 씁니다. 이 글은 기준선이 되는 Flat 인덱스 패턴에 집중합니다.

---

## IndexFlatIP로 정확 검색 구현하기

![Flow from embeddings to index creation](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-02-exact-search-with-indexflatip.ko.png)

*임베딩에서 인덱스 생성까지의 흐름*
텍스트 검색에서 가장 표준적인 패턴은 정규화된 벡터와 내적 인덱스를 조합하는 방식입니다.

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

<!-- injected-output:start -->
**출력 결과**

    total vectors in index: 10
    vector dimension: 384

<!-- injected-output:end -->

FAISS는 `float32` 배열을 요구합니다. `dtype=np.float32`를 명시하지 않으면 NumPy는 기본적으로 `float64`를 만들고, 그 상태로는 FAISS가 오류를 냅니다.

---

## 쿼리 실행하기

![Query to FAISS result path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-03-running-queries.ko.png)

*쿼리에서 FAISS 결과까지의 경로*
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

<!-- injected-output:start -->
**출력 결과**

    query: 'how vector search finds similar content'
      [1] 0.6746 — Vector search captures semantic similarity that keyword sear
      [2] 0.4981 — Cosine similarity measures the directional similarity betwee
      [3] 0.4782 — FAISS is a high-speed vector search library from Facebook AI

    query: 'what embedding models do'
      [1] 0.6641 — Higher embedding dimensions can capture more information.
      [2] 0.6437 — Embedding models project text into a high-dimensional vector
      [3] 0.4751 — sentence-transformers specializes in sentence-level embeddin

    query: 'splitting documents into pieces'
      [1] 0.7226 — Chunking strategies split long documents into searchable uni
      [2] 0.3137 — RAG combines retrieved documents with an LLM prompt.
      [3] 0.2652 — Embedding models project text into a high-dimensional vector

<!-- injected-output:end -->

---

## 인덱스 저장과 다시 불러오기

인덱스를 영속화하면 애플리케이션이 시작될 때마다 문서를 다시 임베딩하지 않아도 됩니다.

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

<!-- injected-output:start -->
**출력 결과**

    saved: 3 vectors
    reloaded: 3 vectors

    results:
      0.5446 — FAISS is a high-speed vector search library from Facebook AI Research.
      0.4393 — Cosine similarity measures the directional similarity between two vectors.

<!-- injected-output:end -->

`faiss.write_index()`와 `faiss.read_index()`는 FAISS 전용 바이너리 포맷을 사용합니다. 큰 규모에서는 NumPy `.npy`보다 더 빠르게 로드됩니다.

---

## IndexFlatL2와 IndexFlatIP 비교

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

<!-- injected-output:start -->
**출력 결과**

    IndexFlatIP (higher = more similar):
      0.9508 — handling concurrency in Python
      0.6413 — Python async programming

    IndexFlatL2 (lower = more similar):
      0.0984 — handling concurrency in Python
      0.7173 — Python async programming

<!-- injected-output:end -->

두 인덱스 모두 올바른 순위를 반환합니다. 텍스트 검색에서는 정규화된 벡터와 함께 `IndexFlatIP`를 쓰는 것이 표준적인 선택입니다.

---

## 인덱스 선택하기

![float64 input error path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-04-choosing-an-index.ko.png)

*float64 입력 오류 경로*
| 인덱스 | 정확도 | 속도 | 메모리 | 일반적인 규모 |
|---|---|---|---|---|
| IndexFlatL2 / IP | 100% | O(n) | n × d × 4B | 약 10만 개 이하 |
| IndexIVFFlat | 99%+ | O(n/nlist) | n × d × 4B | 10만~100만 |
| IndexHNSWFlat | 98%+ | O(log n) | n × d × 4B + graph | 폭넓은 규모 |

처음에는 `IndexFlatIP`로 시작하면 됩니다. 검색 지연이 문제가 되기 시작하면 `IndexIVFFlat`이나 `IndexHNSWFlat`으로 옮기면 됩니다.

---

## 마무리

이제 FAISS 인덱스를 만들고, 쿼리를 실행하고, 인덱스를 디스크에 저장하는 방법까지 익혔습니다. 정규화된 벡터와 `IndexFlatIP` 조합이 텍스트 검색의 기본 패턴입니다.

다음 글에서는 청킹을 다룹니다. 청크 크기, 오버랩, 분할 전략이 검색 품질에 어떤 영향을 주는지, 그리고 잘못된 청킹이 왜 잘못된 임베딩 모델 선택보다 더 큰 문제를 만들 수 있는지 살펴보겠습니다.

## 운영 체크리스트

- [ ] 데이터 규모와 지연 시간 예산에 맞는 인덱스 유형을 골랐다
- [ ] IVF/PQ 계열 인덱스는 대표 샘플로 학습시켰다
- [ ] 인덱스를 영속화하고 같은 환경에서 재현해 보았다
- [ ] 기본값이 아니라 측정값을 바탕으로 nprobe/ef를 조정했다
- [ ] 벡터 수, 차원 수, 메모리 사용량 메트릭을 추가했다

<!-- toc:begin -->
## 시리즈 목차

- [임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기](./01-what-is-embedding.md)
- [HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기](./02-huggingface-embeddings.md)
- [코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기](./03-cosine-similarity.md)
- **FAISS 입문 — 고속 근사 최근접 이웃 검색 (현재 글)**
- 청크 전략 — 긴 문서를 어떻게 나눌 것인가 (예정)
- 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 (예정)

<!-- toc:end -->

---

## 참고 자료

- [FAISS documentation](https://faiss.ai/)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [FAISS index selection guide](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index)
- [faiss-cpu on PyPI](https://pypi.org/project/faiss-cpu/)

Tags: Vector Search, FAISS, Embeddings, Python
