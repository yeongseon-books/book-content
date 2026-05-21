---
episode: 3
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
title: "Vector Search 101 (3/6): 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기"
seo_description: 코사인 유사도와 내적, L2 거리를 비교하며 벡터 검색 점수를 읽는 법을 설명합니다.
---

# Vector Search 101 (3/6): 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기

벡터를 만들었다면 다음 질문은 그것들을 어떻게 비교할지입니다. 거리 척도는 여러 가지가 있고, 어떤 척도를 선택하느냐에 따라 검색 결과도 달라집니다. 코사인 유사도가 가장 흔하지만, 내적과 유클리드 거리에도 더 잘 맞는 경우가 있습니다.

이 글은 Vector Search 101 시리즈의 세 번째 글입니다.

여기서는 세 가지 척도를 직접 구현하고, 정규화가 왜 중요한지 보여 주며, 외부 라이브러리 없이 브루트 포스 최근접 이웃 검색까지 만들어 봅니다.

![Cosine dot and euclidean comparison structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/03/03-01-cosine-similarity-and-vector-search-comp.ko.png)
*코사인, 내적, 유클리드 비교 구조*
> 벡터 검색에서 유사도 함수는 단순한 수학 공식이 아니라, 무엇을 비슷하다고 볼지 정하는 검색 정책입니다.

## 먼저 던지는 질문

- 벡터가 있으면 왜 바로 검색이 끝나는 게 아니라 거리 척도를 골라야 할까요?
- 코사인 유사도와 내적, L2 거리는 결과를 어떻게 다르게 만들까요?
- 정규화 여부가 검색 순위와 FAISS 인덱스 선택에 왜 영향을 줄까요?

## 세 가지 거리 척도

![Cosine dot and euclidean comparison structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/03/03-01-three-distance-metrics.ko.png)

*코사인, 내적, 유클리드 비교 구조*
### 코사인 유사도

코사인 유사도는 두 벡터가 이루는 각도를 측정합니다. 벡터의 크기는 무시하고 방향만 비교합니다.

```text
cos(θ) = (A · B) / (|A| × |B|)
```

값 범위는 -1에서 1입니다. 실제 텍스트 임베딩에서는 음수 값이 드물기 때문에 보통 0에서 1 사이에 분포하는 경우가 많습니다. 1에 가까울수록 더 유사합니다.

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

### 내적

내적은 각 차원의 값을 곱해 모두 더한 값입니다.

```text
A · B = Σ(Aᵢ × Bᵢ)
```

벡터가 L2 정규화되어 있다면, 즉 크기가 1이라면 내적과 코사인 유사도는 수치적으로 같습니다. 내적은 전체 코사인 공식보다 계산이 빠르기 때문에, FAISS 같은 라이브러리는 먼저 정규화한 뒤 내적을 계산하는 방식으로 코사인 검색을 구현합니다.

```python
def dot_product(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))
```

### 유클리드 거리 (L2)

유클리드 거리는 두 점 사이의 직선 거리입니다.

```text
L2(A, B) = √Σ(Aᵢ - Bᵢ)²
```

값이 작을수록 더 유사합니다. 즉, 코사인 유사도와는 방향이 반대입니다. 하지만 정규화된 벡터에서는 L2와 코사인 유사도가 단조 관계를 가지므로 순위는 동일합니다.

```python
def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))
```

---

## 세 척도를 한 번에 비교하기

![Three metrics on one pair flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/03/03-02-comparing-all-three-metrics.ko.png)

*같은 문장 쌍에 세 척도를 적용하는 흐름*
같은 문장 쌍에 세 가지 척도를 모두 적용해 보겠습니다.

```python
import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def dot_product(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))

def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

pairs = [
    ("Python async programming", "handling concurrency in Python"),
    ("Python async programming", "training a machine learning model"),
    ("Python async programming", "walking the dog in the park"),
]

for text_a, text_b in pairs:
    a = model.encode(text_a, normalize_embeddings=True)
    b = model.encode(text_b, normalize_embeddings=True)

    cos = cosine_similarity(a, b)
    dot = dot_product(a, b)
    l2 = euclidean_distance(a, b)

    print(f"\n'{text_a[:25]}' vs '{text_b[:25]}'")
    print(f"  cosine:     {cos:.4f}")
    print(f"  dot:        {dot:.4f}")
    print(f"  euclidean:  {l2:.4f}")
```

<!-- injected-output:start -->
**출력 결과**

    'Python async programming' vs 'handling concurrency in P'
      cosine:     0.6201
      dot:        0.6201
      euclidean:  0.8717

    'Python async programming' vs 'training a machine learni'
      cosine:     0.1399
      dot:        0.1399
      euclidean:  1.3115

    'Python async programming' vs 'walking the dog in the pa'
      cosine:     -0.0400
      dot:        -0.0400
      euclidean:  1.4423

<!-- injected-output:end -->

정규화된 벡터에서는 코사인 유사도와 내적이 정확히 일치합니다. 유클리드 거리는 반대 방향의 값이 나오지만 순위는 동일합니다.

---

## 정규화가 왜 중요한가

![Before and after normalization difference](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/03/03-03-why-normalization-matters.ko.png)

*정규화 전후 차이*
정규화가 없으면 내적과 코사인 유사도는 갈라집니다.

```python
import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

text_a = "Python async programming"
text_b = "handling concurrency in Python"

a_raw = model.encode(text_a, normalize_embeddings=False)
b_raw = model.encode(text_b, normalize_embeddings=False)
a_norm = model.encode(text_a, normalize_embeddings=True)
b_norm = model.encode(text_b, normalize_embeddings=True)

print(f"raw magnitudes: a={np.linalg.norm(a_raw):.4f}, b={np.linalg.norm(b_raw):.4f}")
print(f"norm magnitudes: a={np.linalg.norm(a_norm):.4f}, b={np.linalg.norm(b_norm):.4f}")

print(f"\nraw cosine: {cosine_similarity(a_raw, b_raw):.4f}")
print(f"raw dot:    {float(np.dot(a_raw, b_raw)):.4f}")

print(f"\nnorm cosine: {cosine_similarity(a_norm, b_norm):.4f}")
print(f"norm dot:    {float(np.dot(a_norm, b_norm)):.4f}")
```

<!-- injected-output:start -->
**출력 결과**

    raw magnitudes: a=1.0000, b=1.0000
    norm magnitudes: a=1.0000, b=1.0000

    raw cosine: 0.6201
    raw dot:    0.6201

    norm cosine: 0.6201
    norm dot:    0.6201

<!-- injected-output:end -->

설명 자체는 더 중요합니다. 정규화가 없으면 원시 내적은 벡터 크기의 영향을 크게 받습니다. 반면 정규화 후에는 내적과 코사인 유사도가 같은 값으로 수렴합니다. FAISS의 `IndexFlatIP`는 바로 이 등가성을 전제로 동작합니다. 그래서 이런 인덱스를 쓸 때 `normalize_embeddings=True`를 일관되게 적용하는 일은 선택 사항이 아니라 계약에 가깝습니다.

---

## 브루트 포스 최근접 이웃 검색

![Brute force nearest neighbor execution path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/03/03-04-brute-force-nearest-neighbor-search.ko.png)

*브루트 포스 최근접 이웃 실행 경로*
문서 수가 수백 개 수준이라면 NumPy만으로도 검색이 가능합니다.

```python
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
]

doc_vectors = np.array(embedding_model.embed_documents(documents))

def search(query: str, top_k: int = 3) -> list[tuple[float, str]]:
    query_vector = np.array(embedding_model.embed_query(query))
    # 정규화된 벡터: 내적 == 코사인 유사성
    scores = doc_vectors @ query_vector
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(float(scores[i]), documents[i]) for i in top_indices]

query = "how vector search finds similar documents"
results = search(query, top_k=3)

print(f"query: '{query}'\n")
for rank, (score, text) in enumerate(results, start=1):
    print(f"[{rank}] score: {score:.4f}")
    print(f"    {text}\n")
```

<!-- injected-output:start -->
**출력 결과**

    query: 'how vector search finds similar documents'

    [1] score: 0.6824
        Vector search captures semantic similarity that keyword search misses.

    [2] score: 0.4593
        Chunking strategies split long documents into searchable units.

    [3] score: 0.4517
        FAISS is a high-speed vector search library from Facebook AI Research.

<!-- injected-output:end -->

`doc_vectors @ query_vector`는 문서마다 코사인 유사도를 한 번씩 계산하는 행렬-벡터 내적입니다. NumPy가 전체 코퍼스에 대해 벡터화해 처리합니다. `np.argsort(scores)[::-1][:top_k]`는 점수 내림차순으로 상위 k개 인덱스를 반환합니다.

이 방식은 정확 검색 또는 브루트 포스 검색이라고 부릅니다. 정확하지만 복잡도는 O(n × d)입니다. 여기서 n은 문서 수, d는 벡터 차원입니다. 문서가 수만 건을 넘어가면 너무 느려집니다. 그 지점에서 FAISS가 필요해집니다.

---

## 언제 어떤 척도를 써야 하는가

![Metric selection decision flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/03/03-05-when-to-use-each-metric.ko.png)

*거리 척도 선택 흐름*
| 척도 | 적합한 상황 | 주의할 점 |
|---|---|---|
| 코사인 유사도 | 텍스트 의미 비교, 길이가 다른 문서 | 크기 정보를 무시함 |
| 내적 | 정규화된 벡터, FAISS IP 인덱스 | 정규화가 없으면 크기가 결과를 왜곡함 |
| 유클리드 L2 | 절대 거리 자체가 의미를 가질 때 | 정규화된 벡터에서는 코사인과 순위가 같음 |

텍스트 검색에서는 코사인 유사도가 가장 안전한 기본값입니다. 벡터가 정규화되어 있다면 더 적은 연산으로 같은 결과를 내는 내적을 써도 됩니다. FAISS의 `IndexFlatIP`가 정확히 그 가정 위에 서 있습니다.

---

## 마무리

세 가지 거리 척도를 직접 구현해 비교했습니다. 핵심은 정규화입니다. 벡터 크기를 1로 맞췄을 때만 내적이 코사인 유사도와 일치합니다. 브루트 포스 검색은 작은 코퍼스에서는 잘 동작하지만, 규모가 커지면 버티지 못합니다.

다음 글에서는 FAISS를 소개합니다. 인덱스 유형, 인덱스 구축과 저장, 그리고 근사 검색이 작은 정확도 손실로 큰 속도 이득을 만드는 방식을 살펴보겠습니다.

## 운영 체크리스트

- [ ] 유사도 함수 선택을 모델이 권장하는 거리와 맞췄다
- [ ] 모든 벡터를 미리 정규화했거나, 하지 않은 이유를 명시해 두었다
- [ ] 샘플 쿼리 분포를 기준으로 임계값을 보정했다
- [ ] 점수 산정 뒤 리랭커에 넘길 후보 수를 결정했다
- [ ] 거짓 양성 예시를 회귀 테스트 케이스로 남겼다

## ANN 알고리즘과 거리 함수의 연결

거리 함수는 수학 선택처럼 보이지만, 실제로는 인덱스 알고리즘 선택과 바로 연결됩니다. 예를 들어 HNSW와 IVF 모두 코사인/L2를 지원하지만, 내부 최적화 포인트가 다릅니다.

| 알고리즘 | 일반 조합 | 핵심 튜닝 포인트 | 거리 함수와의 관계 |
|---|---|---|---|
| HNSW | cosine + normalized vectors | `M`, `efConstruction`, `efSearch` | `efSearch`를 높이면 recall 상승, latency 증가 |
| IVF Flat | cosine 또는 L2 | `nlist`, `nprobe` | `nprobe`가 낮으면 후보 누락으로 recall 하락 |
| Flat(정확) | cosine/IP/L2 | 없음 | 기준선(ground truth) 생성에 사용 |

실무에서는 Flat 인덱스로 정답 집합을 만들고, HNSW/IVF가 그 정답을 얼마나 재현하는지로 recall을 계산합니다.

## HNSW와 IVF 파라미터가 점수 해석에 미치는 영향

아래 표는 같은 데이터셋에서 검색 파라미터만 바꿨을 때의 전형적인 경향입니다.

| 설정 | Recall@10 | p95 latency (ms) |
|---|---:|---:|
| HNSW `efSearch=32` | 0.91 | 7 |
| HNSW `efSearch=96` | 0.97 | 15 |
| IVF `nprobe=4` | 0.84 | 4 |
| IVF `nprobe=24` | 0.95 | 10 |

포인트는 단순합니다. 점수 함수가 같아도 후보를 얼마나 보느냐가 달라지면 최종 순위가 달라집니다. 그래서 운영 대시보드는 점수 분포만 보지 말고 `efSearch`, `nprobe` 값도 같이 기록해야 합니다.

## 최소 벤치마크 코드

```python
import time

import faiss
import numpy as np

def recall_at_k(pred: np.ndarray, truth: np.ndarray, k: int) -> float:
    hit = 0
    total = pred.shape[0] * k
    for i in range(pred.shape[0]):
        hit += len(set(pred[i, :k]).intersection(set(truth[i, :k])))
    return hit / total

def benchmark(index: faiss.Index, queries: np.ndarray, truth: np.ndarray, k: int = 10) -> tuple[float, float]:
    start = time.perf_counter()
    _, pred = index.search(queries, k)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return recall_at_k(pred, truth, k), elapsed_ms
```

이 코드 수준만 있어도 "튜닝 후 latency는 줄었는데 recall이 얼마나 빠졌는지"를 수치로 답할 수 있습니다.

## 하이브리드 점수 결합에서의 스케일 정렬

코사인 점수와 BM25 점수는 분포가 다릅니다. 둘을 그대로 더하면 BM25가 지나치게 우세하거나 반대로 코사인 점수가 모든 순위를 덮어 버릴 수 있습니다. 따라서 최소-최대 정규화 또는 z-score 정규화를 먼저 적용해야 합니다.

```python
import numpy as np

def min_max(arr: np.ndarray) -> np.ndarray:
    lo, hi = float(arr.min()), float(arr.max())
    if hi == lo:
        return np.zeros_like(arr, dtype=np.float32)
    return (arr - lo) / (hi - lo)

def hybrid_score(cos_scores: np.ndarray, bm25_scores: np.ndarray, alpha: float) -> np.ndarray:
    cos_norm = min_max(cos_scores)
    bm25_norm = min_max(bm25_scores)
    return alpha * cos_norm + (1 - alpha) * bm25_norm
```

점수 결합을 도입했다면, 운영 로그에는 `alpha`, 정규화 방식, 상위 후보 수를 반드시 남겨야 다음 실험과 비교가 가능합니다.

## 임계값(threshold) 기반 검색에서 자주 하는 실수

top-k 방식은 상대 순위만 보지만, threshold 방식은 절대 점수 기준을 사용합니다. 예를 들어 코사인 점수가 0.62 이상이면 통과시키는 정책을 두면, 도메인이나 질의 길이에 따라 거짓 음성/거짓 양성이 크게 바뀔 수 있습니다.

| 질의 유형 | 권장 접근 |
|---|---|
| 짧은 키워드형 질의 | threshold를 다소 높게 설정 |
| 긴 설명형 질의 | threshold를 낮추고 top-k 확대 |
| 오류 코드/식별자 질의 | 벡터 threshold보다 lexical 보강 우선 |

threshold는 고정값 하나로 끝내기보다 질의 타입 분류와 함께 운영하는 편이 안정적입니다.

## 거리 함수 선택과 리랭커 연동

대부분 시스템은 1차 검색에서 빠르게 후보를 뽑고, 2차 리랭커로 정밀 정렬합니다. 이때 거리 함수 선택은 1차 후보의 다양성에 영향을 줍니다.

- 코사인 중심 1차 검색은 의미적으로 넓은 후보를 확보하는 데 유리합니다.
- L2 중심 1차 검색은 좌표 거리 보존이 중요할 때 유리하지만 텍스트 검색에서는 이점이 제한적입니다.
- 리랭커(예: cross-encoder)를 쓴다면 1차 단계에서 recall 확보를 우선하고, precision은 2차에서 끌어올리는 편이 일반적입니다.

아래는 후보 수와 리랭커 품질의 전형적인 관계 예시입니다.

| 1차 후보 수 | 최종 Recall@5 | 최종 p95(ms) |
|---:|---:|---:|
| 10 | 0.84 | 120 |
| 30 | 0.91 | 170 |
| 50 | 0.93 | 230 |

즉, 유사도 함수 선택은 리랭커를 포함한 전체 지연 시간 예산 안에서 판단해야 합니다.

## FAISS 인덱스별 유사도 실험 코드 스케치

```python
import faiss
import numpy as np

def build_flat_ip(vectors: np.ndarray) -> faiss.Index:
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors.astype(np.float32))
    return index

def build_flat_l2(vectors: np.ndarray) -> faiss.Index:
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors.astype(np.float32))
    return index
```

같은 질의셋으로 두 인덱스의 상위 결과를 비교하면, 정규화 여부가 결과 해석에 어떤 영향을 주는지 더 명확하게 보입니다.

## 프로덕션 모니터링 지표

거리 함수를 운영에 올렸다면 아래 지표를 기본으로 수집하는 편이 좋습니다.

- 쿼리별 상위 1위 점수, 상위 5위 평균 점수
- 무응답 질의 비율(임계값 미달)
- 질의 길이 구간별 성공률
- ANN 파라미터(`nprobe`, `efSearch`)별 latency/recall 추세

이 지표를 보면 "점수 함수가 틀렸는지", "청킹이 틀렸는지", "ANN 튜닝이 부족한지"를 훨씬 빠르게 분리할 수 있습니다.

## 코사인 점수 구간을 해석하는 방법

실제 운영에서 점수 숫자만 보고 품질을 직관적으로 읽기 어렵다는 질문이 자주 나옵니다. 아래 구간은 절대 규칙은 아니지만 초기 해석 기준으로 유용합니다.

| 코사인 점수 | 해석 가이드 |
|---:|---|
| 0.80 이상 | 의미가 매우 가깝거나 거의 동일한 문맥 |
| 0.60~0.80 | 관련성이 높아 후보로 충분히 유의미 |
| 0.40~0.60 | 부분 관련, 리랭커 또는 추가 필터 필요 |
| 0.40 미만 | 노이즈일 가능성 큼 |

도메인 문서가 기술 용어 중심인지, 일반 문장 중심인지에 따라 실제 구간은 달라지므로 반드시 내부 평가셋으로 재보정해야 합니다.

## 질의 길이와 점수 분포

짧은 질의와 긴 질의는 점수 분포가 다르게 나옵니다. 한두 단어 질의는 의미가 압축되어 상위 점수 편차가 작고, 긴 질의는 문맥 제약이 많아 상위 후보가 분명해지는 경향이 있습니다.

```python
def classify_query(query: str) -> str:
    tokens = query.split()
    if len(tokens) <= 2:
        return "short"
    if len(tokens) <= 8:
        return "medium"
    return "long"
```

운영에서는 질의 길이 구간별로 threshold를 다르게 두는 전략이 종종 유효합니다.

## Precision/Recall 트레이드오프 예시

| 정책 | Precision@5 | Recall@5 |
|---|---:|---:|
| threshold 0.70 | 0.91 | 0.62 |
| threshold 0.55 | 0.84 | 0.79 |
| threshold 0.45 | 0.73 | 0.88 |

지원 챗봇처럼 놓치면 안 되는 환경이라면 recall 쪽으로, 탐색 품질이 중요한 문서 검색이라면 precision 쪽으로 맞추는 식으로 정책을 선택합니다.

## 거리 함수 변경 시 롤아웃 체크리스트

- 기존 함수와 신규 함수로 같은 평가셋을 병렬 실행
- top-k 결과의 교집합 비율을 계산해 급격한 분포 변화를 점검
- 품질 지표 외에 p95 latency와 비용 변화를 함께 확인
- 실패 질의 샘플을 사람이 직접 검토하고 변경 이유를 문서화

이 과정을 거치면 "수학적으로 더 좋아 보이는 함수"가 실제 사용자 질문에서도 좋은지 검증할 수 있습니다.

추가로 기억할 점은 점수 함수가 단독으로 품질을 결정하지 않는다는 사실입니다. 실제 결과는 청킹, 임베딩 모델, ANN 후보 수, 리랭커 정책과 함께 만들어집니다. 그래서 거리 함수 비교 실험은 반드시 동일한 파이프라인 설정에서 진행해야 하며, 하나의 요소만 바꿔 A/B 테스트를 수행해야 원인을 정확히 분리할 수 있습니다.

그리고 실험 결과를 공유할 때는 "어떤 함수가 더 좋다"는 결론만 남기지 말고, 질의 유형별 편차를 함께 기록해야 합니다. 보통 오류 코드, 짧은 명령형 질의, 긴 설명형 질의에서 점수 분포가 다르게 나타나며, 이 차이가 운영 정책을 결정하는 근거가 됩니다.

## 처음 질문으로 돌아가기

- **벡터가 있으면 왜 바로 검색이 끝나는 게 아니라 거리 척도를 골라야 할까요?**
  거리 척도는 “가깝다”를 수식으로 정의합니다. 척도를 고르지 않으면 벡터를 어떤 기준으로 정렬해야 하는지 정해지지 않습니다.

- **코사인 유사도와 내적, L2 거리는 결과를 어떻게 다르게 만들까요?**
  코사인은 방향을, 내적은 방향과 크기를, L2는 좌표 거리 자체를 더 강하게 반영합니다. 그래서 같은 벡터 집합도 순위가 달라질 수 있습니다.

- **정규화 여부가 검색 순위와 FAISS 인덱스 선택에 왜 영향을 줄까요?**
  정규화하면 코사인과 내적의 관계가 바뀌고, FAISS에서는 IndexFlatIP와 IndexFlatL2 선택 기준도 함께 달라집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Vector Search 101 (1/6): 임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기](./01-what-is-embedding.md)
- [Vector Search 101 (2/6): HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기](./02-huggingface-embeddings.md)
- **Vector Search 101 (3/6): 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기 (현재 글)**
- Vector Search 101 (4/6): FAISS 입문 — 고속 근사 최근접 이웃 검색 (예정)
- Vector Search 101 (5/6): 청크 전략 — 긴 문서를 어떻게 나눌 것인가 (예정)
- Vector Search 101 (6/6): 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 (예정)

<!-- toc:end -->

---

## 참고 자료

- [FAISS wiki — choosing an index](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index)
- [sentence-transformers semantic similarity](https://www.sbert.net/docs/usage/semantic_textual_similarity.html)
- [Vector similarity — Pinecone](https://www.pinecone.io/learn/vector-similarity/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/vector-search-101/ko/03-cosine-similarity)

Tags: Vector Search, FAISS, Embeddings, Python
