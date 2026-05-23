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
title: "Vector Search 101 (4/6): FAISS 입문 — 고속 근사 최근접 이웃 검색"
seo_description: FAISS로 벡터 인덱스를 만들고 저장하고 검색하는 기본 패턴을 설명합니다.
---

# Vector Search 101 (4/6): FAISS 입문 — 고속 근사 최근접 이웃 검색

문서 수가 수천, 수만 건으로 늘어나면 NumPy 기반 브루트 포스 검색은 금방 느려집니다. 차원이 384인 벡터 10만 개를 쿼리 하나와 비교하려면 쿼리마다 3,840만 번의 곱셈이 필요합니다. 이 정도 규모에서는 검색 지연이 수백 밀리초 이상으로 올라가며, 대화형 애플리케이션에는 너무 느립니다.

FAISS(Facebook AI Similarity Search)는 바로 이 문제를 풀기 위해 만들어졌습니다. 작은 정확도 손실과 큰 속도 향상을 맞바꾸는 근사 최근접 이웃 검색을 지원하고, 수십억 개 규모의 벡터도 처리할 수 있으며, CPU와 GPU 모두에서 빠르게 동작합니다.

여기서는 검색 속도를 올릴 때 가장 먼저 만나는 FAISS의 기본 패턴을 정리합니다.

![FAISS index type comparison structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/04/04-01-faiss-fundamentals-fast-approximate-near.ko.png)
*FAISS 인덱스 유형 비교 구조*
> FAISS를 이해하는 가장 좋은 방법은 더 똑똑한 데이터베이스로 보는 것이 아니라, 벡터 검색 전용 계산 엔진으로 보는 것입니다.

## 먼저 던지는 질문

- 벡터가 많아질수록 단순 반복 검색은 어디서 한계가 날까요?
- IndexFlatIP와 IndexFlatL2는 어떤 전제에서 선택해야 할까요?
- 인덱스를 저장하고 다시 불러올 때 벡터와 메타데이터를 어떻게 맞춰야 할까요?

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

# 쿼리로 검증합니다
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

다음 글에서는 청킹을 다룹니다. 청크 크기, 오버랩, 분할 전략이 검색 품질에 어떤 영향을 주는지, 그리고 잘못된 청킹이 왜 잘못된 임베딩 모델 선택보다 더 큰 문제를 만들 수 있는지 봅니다.

## 운영 체크리스트

- [ ] 데이터 규모와 지연 시간 예산에 맞는 인덱스 유형을 골랐다
- [ ] IVF/PQ 계열 인덱스는 대표 샘플로 학습시켰다
- [ ] 인덱스를 영속화하고 같은 환경에서 재현해 보았다
- [ ] 기본값이 아니라 측정값을 바탕으로 nprobe/ef를 조정했다
- [ ] 벡터 수, 차원 수, 메모리 사용량 메트릭을 추가했다

## HNSW와 IVF로 확장할 때의 실전 기준

Flat 인덱스는 기준선을 만들기에는 좋지만, 트래픽이 커지면 한계가 명확합니다. 그다음 단계에서 가장 자주 검토하는 선택지는 HNSW와 IVF입니다.

| 항목 | HNSW (`IndexHNSWFlat`) | IVF (`IndexIVFFlat`) |
|---|---|---|
| 검색 복잡도 경향 | 그래프 탐색 기반, 실무에서 매우 빠름 | coarse quantizer로 후보 축소 |
| 구축 특성 | 구축 시간/메모리 증가 | 학습(train) 단계 필요 |
| 온라인 추가 | 비교적 자연스러움 | 가능하지만 분포 변화 시 재학습 고려 |
| 핵심 파라미터 | `M`, `efConstruction`, `efSearch` | `nlist`, `nprobe` |

초기 운영에서는 HNSW가 튜닝 체감이 직관적이고, IVF는 데이터가 매우 클 때 비용 예측이 좋은 경우가 많습니다.

## HNSW 생성 예시

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

`efSearch`를 높이면 recall이 좋아지지만 지연 시간도 같이 증가합니다. 그래서 서비스 단계에서는 쿼리 유형별로 `efSearch`를 다르게 주는 정책도 자주 사용합니다.

## IVF 생성 예시

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

IVF는 `train()`을 건너뛰면 검색이 불가능합니다. 학습 데이터는 실제 분포를 반영한 샘플을 써야 합니다. 임의 샘플로 학습하면 recall이 눈에 띄게 떨어집니다.

## 튜닝 로그를 남기는 이유

아래처럼 튜닝 결과를 표로 남기면 팀 의사결정이 빨라집니다.

| 인덱스 | 파라미터 | Recall@10 | p95(ms) | 메모리(GB) |
|---|---|---:|---:|---:|
| FlatIP | - | 1.00 | 78 | 1.5 |
| HNSW | M=32, efSearch=64 | 0.97 | 18 | 2.2 |
| HNSW | M=32, efSearch=128 | 0.99 | 29 | 2.2 |
| IVF | nlist=1024, nprobe=12 | 0.92 | 11 | 1.6 |
| IVF | nlist=1024, nprobe=32 | 0.97 | 22 | 1.6 |

이 기록이 있으면 "느려져도 정확도를 지켜야 하는가" 또는 "정확도를 조금 낮춰도 예산을 줄여야 하는가" 같은 선택을 수치로 논의할 수 있습니다.

## 프로덕션 스케일링 패턴

FAISS를 프로덕션에 올릴 때는 아래 패턴을 함께 설계하는 편이 안전합니다.

- 읽기 트래픽은 인덱스 복제(replica)로 수평 확장
- 인덱스 빌드와 서비스 인덱스를 분리하고, 원자적 스왑으로 배포
- 인덱스 버전(`index_version`)과 임베딩 버전(`embedding_version`)을 로그에 동시 기록
- 대규모 갱신은 증분 추가보다 배치 재구축이 더 안정적인지 주기적으로 검토

이 패턴을 잡아 두면 단순 검색 성능뿐 아니라 장애 복구 시간도 크게 줄어듭니다.

## IVF 파라미터 튜닝 워크플로

IVF를 운영에 올릴 때는 `nlist`와 `nprobe`를 분리해서 튜닝해야 합니다. `nlist`는 인덱스 구조를 결정하고, `nprobe`는 질의 시 탐색 폭을 조절합니다.

1. 데이터 규모를 기준으로 `nlist` 후보를 3개 정도 고릅니다.
2. 각 `nlist`에 대해 `nprobe`를 증가시키며 recall/latency를 측정합니다.
3. SLA를 만족하는 최소 `nprobe` 조합을 채택합니다.

```python
def sweep_nprobe(index_ivf, queries, truths, nprobe_values):
    rows = []
    for nprobe in nprobe_values:
        index_ivf.nprobe = nprobe
        recall, elapsed = benchmark(index_ivf, queries, truths, k=10)
        rows.append((nprobe, recall, elapsed))
    return rows
```

| nprobe | Recall@10 | p95(ms) |
|---:|---:|---:|
| 4 | 0.83 | 7 |
| 8 | 0.89 | 10 |
| 16 | 0.94 | 16 |
| 32 | 0.97 | 28 |

이 표를 보면 보통 16 부근이 균형점이 되는 경우가 많습니다.

## HNSW 파라미터 해석

HNSW에서는 `M`이 그래프 연결 수를, `efSearch`가 검색 시 후보 폭을 의미합니다. 일반적으로 `M`을 높이면 메모리 사용량과 구축 시간이 증가하고, `efSearch`를 높이면 질의 지연 시간이 증가합니다.

| M | efSearch | Recall@10 | p95(ms) | 메모리 증가율 |
|---:|---:|---:|---:|---:|
| 16 | 32 | 0.90 | 8 | 1.0x |
| 32 | 64 | 0.96 | 14 | 1.5x |
| 48 | 96 | 0.98 | 23 | 2.0x |

서비스가 메모리보다 지연 시간을 더 엄격히 보는지, 반대인지를 먼저 정한 뒤 파라미터를 선택해야 합니다.

## 삭제/업데이트 전략

FAISS Flat 인덱스는 문서 삭제가 잦은 워크로드에 바로 맞지 않습니다. 그래서 보통 아래 전략을 조합합니다.

- tombstone 테이블로 삭제 대상 ID를 별도 관리
- 조회 시 tombstone ID를 후처리에서 제외
- 배치 재구축 시 tombstone을 반영해 인덱스를 정리

```python
def filter_deleted(results, deleted_ids: set[str]):
    return [r for r in results if r["doc_id"] not in deleted_ids]
```

업데이트가 매우 잦고 삭제도 빈번하다면, Qdrant/Pinecone 같은 관리형/서버형 벡터 DB가 운영 복잡도를 낮추는 경우가 많습니다.

## 장애 대응 플레이북 요약

인덱스 계층에서 자주 발생하는 문제와 1차 대응을 짧게 정리하면 다음과 같습니다.

| 증상 | 흔한 원인 | 1차 대응 |
|---|---|---|
| 점수가 전체적으로 낮아짐 | 정규화 불일치, 모델 교체 | 매니페스트 비교, 재인덱싱 여부 확인 |
| latency 급증 | nprobe/efSearch 상승, 벡터 수 증가 | 파라미터 롤백, top-k 축소 |
| 결과 품질 급락 | IVF 학습 샘플 분포 불일치 | train 데이터 재선정 후 재학습 |

이 표를 런북에 포함해 두면 온콜 대응 속도가 크게 빨라집니다.

## 검색 정확도 기준선 구축

ANN 인덱스 튜닝에서 가장 중요한 원칙은 항상 기준선이 있어야 한다는 사실입니다. 기준선은 보통 `IndexFlatIP` 또는 `IndexFlatL2`로 만든 정확 검색 결과입니다. 이후 HNSW/IVF 결과를 이 기준선과 비교해 Recall@k를 계산합니다.

```python
def build_ground_truth(flat_index, queries, k=10):
    _, indices = flat_index.search(queries, k)
    return indices
```

이렇게 기준선을 명시적으로 보관하면 데이터가 바뀌거나 파라미터를 바꿀 때 성능 변화를 정량적으로 추적할 수 있습니다.

## 메모리 계산 감각 잡기

운영 준비 단계에서는 대략적인 메모리 계산을 미리 해 두는 것이 좋습니다.

```text
메모리(바이트) ≈ 벡터 수(n) × 차원(d) × 4(float32)
```

예를 들어 `n=3,000,000`, `d=384`이면 벡터 원본만 약 4.3GB입니다. 여기에 HNSW 그래프 오버헤드가 추가되면 훨씬 커집니다. 따라서 인스턴스 선택 전에 여유 메모리를 포함한 용량 계획이 필수입니다.

## 샤딩과 복제 전략

데이터 규모가 커지면 단일 인덱스로는 운영이 어려워집니다. 이때 많이 쓰는 패턴은 샤딩과 복제입니다.

- 샤딩: 문서 ID 해시 또는 도메인별로 인덱스를 분할
- 복제: 같은 샤드를 여러 노드에 복제해 읽기 처리량 확보
- 집계: 각 샤드 top-k를 모아 글로벌 top-k 재정렬

이 구조는 복잡도가 늘지만, 대규모 트래픽에서도 지연 시간과 가용성을 유지하는 데 효과적입니다.

## 운영 벤치마크 리포트 템플릿

벤치마크를 할 때 아래 항목을 정해진 형식으로 남기면 비교가 쉬워집니다.

| 항목 | 예시 |
|---|---|
| 데이터셋 버전 | `docs_2026_05_20` |
| 임베딩 모델 | `all-MiniLM-L6-v2` |
| 인덱스 유형 | `IndexHNSWFlat` |
| 핵심 파라미터 | `M=32, efSearch=64` |
| Recall@10 | `0.968` |
| p95 latency | `18ms` |
| 메모리 | `2.2GB` |

이 템플릿을 습관화하면 실험이 늘어도 의사결정 품질이 떨어지지 않습니다.

마지막으로 벤치마크 결과를 기록할 때는 단일 평균값보다 분포를 함께 남기는 편이 좋습니다. 특히 검색 시스템은 tail latency가 사용자 체감에 큰 영향을 주므로 p50, p95, p99를 함께 비교해야 합니다. 같은 평균이라도 p99가 급격히 나빠지면 실제 서비스에서는 불안정하게 느껴집니다.

이 관점은 인덱스 선택뿐 아니라 용량 계획에서도 동일하게 적용됩니다.

## 처음 질문으로 돌아가기

- **벡터가 많아질수록 단순 반복 검색은 어디서 한계가 날까요?**
  문서 수와 벡터 차원이 커지면 모든 벡터를 매번 비교하는 방식은 지연 시간과 CPU 비용이 빠르게 커집니다.

- **IndexFlatIP와 IndexFlatL2는 어떤 전제에서 선택해야 할까요?**
  정규화된 벡터에서 코사인에 가까운 순위를 원하면 IndexFlatIP가 잘 맞고, 좌표 거리 자체를 비교하려면 IndexFlatL2를 선택합니다.

- **인덱스를 저장하고 다시 불러올 때 벡터와 메타데이터를 어떻게 맞춰야 할까요?**
  인덱스가 반환하는 row id와 문서 ID, 원문, 메타데이터 배열의 순서를 함께 저장해야 재로딩 후에도 결과가 어긋나지 않습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Vector Search 101 (1/6): 임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기](./01-what-is-embedding.md)
- [Vector Search 101 (2/6): HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기](./02-huggingface-embeddings.md)
- [Vector Search 101 (3/6): 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기](./03-cosine-similarity.md)
- **Vector Search 101 (4/6): FAISS 입문 — 고속 근사 최근접 이웃 검색 (현재 글)**
- Vector Search 101 (5/6): 청크 전략 — 긴 문서를 어떻게 나눌 것인가 (예정)
- Vector Search 101 (6/6): 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 (예정)

<!-- toc:end -->

---

## 참고 자료

- [FAISS documentation](https://faiss.ai/)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [FAISS index selection guide](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index)
- [faiss-cpu on PyPI](https://pypi.org/project/faiss-cpu/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/vector-search-101/ko/04-faiss-fundamentals)

Tags: Vector Search, FAISS, Embeddings, Python
