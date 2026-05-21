---
episode: 1
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
title: "Vector Search 101 (1/6): 임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기"
seo_description: 임베딩이 의미 기반 검색을 가능하게 하는 원리와 첫 벡터 실습을 설명합니다.
---

# Vector Search 101 (1/6): 임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기

검색 엔진은 오랫동안 키워드를 비교해 왔지만, 표현이 달라도 의미가 같은 문장을 연결하는 일에는 한계가 있습니다. 예를 들어 "Python async programming"과 "handling concurrency in Python"은 같은 뜻이지만, 키워드 기반 검색만으로는 두 문장을 자연스럽게 이어 주기 어렵습니다.

임베딩은 이 문제를 다른 방식으로 풉니다. 텍스트를 숫자 벡터로 바꿔서 의미가 비슷한 문장이 고차원 공간에서 가깝게 놓이도록 만듭니다. 즉, 벡터 사이의 거리를 의미의 대리 지표로 사용하는 것입니다. 이 성질 덕분에 정확히 같은 단어가 없어도 의미 기반 검색이 가능해집니다.

이 글은 Vector Search 101 시리즈의 첫 번째 글입니다.

여기서는 임베딩의 개념과 직관을 잡는 데 집중합니다. 코드는 최소한만 사용하되, 실제로 벡터를 만들고 점수를 읽는 첫 실습까지 연결합니다.

![Keyword search and embedding search contrast](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-01-what-is-an-embedding-converting-text-int.ko.png)
*키워드 검색과 임베딩 검색의 대비*
> 임베딩은 텍스트를 저장하는 형식이 아니라, 의미를 거리로 비교할 수 있게 만드는 표현 방식입니다.

## 먼저 던지는 질문

- 키워드가 같은데도 검색 결과가 빗나가거나, 표현만 달라서 결과를 놓칠 때 무엇이 부족한 걸까요?
- 임베딩 벡터의 “가깝다”는 말은 실제로 무엇을 비교한다는 뜻일까요?
- 첫 모델을 고를 때 차원 수, 언어, 토큰 한도 중 무엇을 먼저 확인해야 할까요?

## 키워드 검색의 한계

![Keyword search and embedding search contrast](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-01-the-ceiling-of-keyword-search.ko.png)

*키워드 검색과 임베딩 검색의 대비*
전통적인 검색은 단어 빈도와 위치를 기준으로 결과를 정렬합니다. TF-IDF와 BM25가 대표적인 예입니다. 이런 방식은 쿼리와 문서가 같은 어휘를 공유할 때 빠르고 해석 가능하며 정확합니다.

문제는 언어가 그렇게 고정되어 있지 않다는 점입니다. 같은 개념도 여러 표현으로 나타납니다.

- "store it" — "persist it" — "write to DB" — "make it durable"
- "fast" — "low-latency" — "sub-millisecond response"
- "an error occurred" — "an exception was raised" — "the service crashed"

키워드 검색은 인덱스에 없는 표현을 놓칩니다. 동의어 사전이나 형태 변형 처리는 어느 정도 도움이 되지만, 자연어의 모든 변형을 수동으로 커버하는 일은 확장되지 않습니다.

임베딩은 질문 자체를 바꿉니다. "이 문서에 이 단어가 있나?"가 아니라, "이 문서가 쿼리와 의미 공간에서 얼마나 가까운가?"를 묻는 방식입니다.

---

## 벡터 공간 직관

![Text entering vector space flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-02-vector-space-intuition.ko.png)

*텍스트가 벡터 공간으로 들어가는 흐름*
임베딩 모델은 텍스트를 고정 길이의 부동소수점 배열로 바꿉니다. `sentence-transformers/all-MiniLM-L6-v2`를 사용하면 입력 길이와 무관하게 모든 문장이 384차원 벡터가 됩니다. 768차원이나 1536차원 모델도 흔히 사용됩니다.

```text
"Python async programming"       → [0.12, -0.34, 0.87, ..., 0.05]  (384 numbers)
"handling concurrency in Python" → [0.14, -0.31, 0.85, ..., 0.07]  (384 numbers)
"homemade dog treats recipe"     → [-0.63, 0.77, -0.12, ..., 0.44] (384 numbers)
```

이 숫자들을 고차원 공간의 좌표라고 생각하면 됩니다. 의미가 비슷한 문장은 서로 가까이 놓이고, 관련 없는 문장은 멀리 떨어집니다. 검색은 결국 이 공간에서 최근접 이웃을 찾는 작업이 됩니다.

가장 널리 쓰이는 거리 척도는 코사인 유사도입니다. 코사인 유사도는 벡터의 크기보다 방향을 비교하므로, 길이가 다른 입력끼리 비교할 때도 비교적 안정적입니다.

```text
cosine similarity = (A · B) / (|A| × |B|)
```

값 범위는 -1에서 1입니다. 1에 가까울수록 더 유사하고, 0이면 무관하며, -1이면 의미가 반대라는 뜻입니다. 실제 문장 쌍은 대체로 0.2에서 0.95 사이에 위치합니다.

---

## 임베딩 모델은 어떻게 학습하는가

![Positive and negative pair training structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-03-how-embedding-models-learn.ko.png)

*긍정 쌍과 부정 쌍의 학습 구조*
임베딩 모델은 의미가 비슷한 문장 쌍은 가깝게, 관련 없는 문장 쌍은 멀게 배치하도록 학습됩니다. 가장 지배적인 학습 방식은 대조 학습입니다.

학습 데이터는 보통 아래처럼 구성됩니다.

- 긍정 쌍: 같은 문서의 서로 다른 단락, 질문-답변 쌍, 번역 쌍
- 부정 쌍: 무작위로 뽑은 서로 관련 없는 문장

모델은 긍정 쌍 사이의 벡터 거리는 줄이고, 부정 쌍 사이의 벡터 거리는 늘리도록 파라미터를 업데이트합니다. 이런 과정을 수억 개 문장 쌍에 반복하면, 언어의 의미 구조를 벡터 공간에 투영하는 법을 배우게 됩니다.

`all-MiniLM-L6-v2`는 10억 개가 넘는 문장 쌍으로 학습되었습니다. 모델 크기가 약 22MB로 작아서 CPU에서도 빠르게 실행되며, 이 시리즈에서 다루는 검색 작업에는 품질도 충분합니다.

---

## 첫 번째 벡터 만들어 보기

![Three sentence encoding execution path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-04-creating-your-first-vectors.ko.png)

*세 문장을 인코딩하는 실행 경로*
이론을 다시 읽는 것보다 코드를 한 번 실행하는 편이 더 빠릅니다. `sentence-transformers`를 설치한 뒤 세 문장을 인코딩해 보겠습니다.

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

<!-- injected-output:start -->
**출력 결과**

    number of vectors: 3
    vector dimension: 384
    first vector (first 5 values): [-0.09979379  0.00370044 -0.10362536  0.14163396 -0.04871269]

<!-- injected-output:end -->

이제 세 쌍의 코사인 유사도를 직접 계산해 보겠습니다.

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

<!-- injected-output:start -->
**출력 결과**

    [0] vs [1] (similar meaning): 0.6201
    [0] vs [2] (unrelated):       0.0056

<!-- injected-output:end -->

"Python async programming"과 "handling concurrency in Python"은 공통 단어가 없어도 높은 유사도를 보입니다. 반면 "homemade dog treats recipe"는 거의 0에 가깝습니다. 이 숫자가 벡터 검색의 토대입니다. 쿼리 벡터와 문서 벡터의 코사인 유사도를 기준으로 문서를 정렬하면 의미 기반 검색이 됩니다.

---

## 작은 코퍼스에서 랭킹이 어떻게 바뀌는가

벡터 숫자를 하나 보는 것만으로는 아직 감이 부족할 수 있습니다. 같은 쿼리에 대해 키워드 겹침 기반 점수와 임베딩 기반 점수를 나란히 놓아 보겠습니다. 이 실험은 "왜 의미 기반 검색이 필요한가"를 가장 짧게 확인하는 방법입니다.

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

<!-- injected-output:start -->
**출력 결과**

    keyword=3 cosine=0.8551 | Python async programming patterns for web APIs
    keyword=1 cosine=0.6934 | Handling concurrency in Python with asyncio tasks
    keyword=0 cosine=0.0848 | Distributed tracing for Java microservices
    keyword=0 cosine=0.0124 | Beginner recipe for homemade dog treats

<!-- injected-output:end -->

두 번째 문서는 쿼리와 단어를 거의 공유하지 않지만, 임베딩 점수는 높게 나옵니다. 이 차이가 바로 의미 기반 검색의 실전 가치입니다. 사용자 표현과 문서 표현이 다를수록 이런 효과는 더 커집니다.

## 임베딩 품질을 빠르게 점검하는 방법

처음 모델을 붙였을 때는 "점수가 0.69면 높은가?" 같은 질문이 바로 나옵니다. 이때는 추상적인 평균값보다, 실제 서비스에서 자주 나오는 질의를 몇 개 골라 손으로 확인하는 편이 빠릅니다.

- 같은 뜻인데 표현만 다른 질의-문서 쌍을 5~10개 고릅니다.
- 정확 문자열이 중요한 질의도 따로 5개 정도 고릅니다.
- 관련 없는 문장 쌍의 점수가 충분히 낮은지 확인합니다.
- 상위 3개 결과를 사람이 읽고 "정말 관련 있는가"를 표시합니다.

이 정도만 해도 모델 선택이 완전히 잘못되었는지, 아니면 청킹과 인덱스 튜닝 단계로 넘어가도 되는지 빠르게 판단할 수 있습니다.

---

## 임베딩이 잘 작동하지 않는 경우

![Limits with exact strings and long documents](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/01/01-05-where-embeddings-fall-short.ko.png)

*정확 문자열과 긴 문서에서 드러나는 한계*
임베딩은 키워드 검색을 완전히 대체하는 만능 도구가 아닙니다. 몇몇 상황에서는 오히려 전통적인 방식이 더 낫습니다.

**정확한 식별자와 코드.** `ERR_CONNECTION_REFUSED`나 `CVE-2024-12345` 같은 문자열은 키워드 검색이 더 잘 찾습니다. 임베딩 모델은 의미를 추상화하는 과정에서 기호 수준의 정확한 정보를 흐릴 수 있습니다.

**도메인 특화 언어.** 웹 텍스트 중심으로 학습된 범용 영어 모델은 한국어 의료 기록이나 법률 계약서에서 품질이 낮을 수 있습니다. 이런 경우에는 도메인 특화 파인튜닝이나 전용 모델이 필요합니다.

**긴 문서.** `all-MiniLM-L6-v2`는 최대 256 서브워드 토큰만 처리합니다. 그 이상은 잘립니다. 긴 문서는 임베딩 전에 청크로 나눠야 합니다. 청크 전략은 이 시리즈 5편에서 다룹니다.

**다국어 콘텐츠.** 여러 언어가 섞인 문서는 단일 언어 모델보다 `paraphrase-multilingual-MiniLM-L12-v2` 같은 다국어 모델이 더 적합합니다.

실무에서는 대부분 키워드 검색과 임베딩 검색을 결합한 하이브리드 검색을 사용합니다. 서로의 약점을 보완하기 위해서입니다. 이 패턴은 시리즈 마지막 글에서 간단히 다룹니다.

---

## 모델 선택 기준

어떤 임베딩 모델을 선택해야 할까요? 첫 번째 프로젝트에서는 아래 기준만으로도 후보를 많이 줄일 수 있습니다.

**속도와 크기.** CPU에서 실행한다면 경량 모델이 중요합니다. `all-MiniLM-L6-v2`는 약 22MB이며, 최신 CPU에서는 초당 수백 문장을 인코딩할 수 있습니다. 정확도가 더 중요하면 약 420MB 크기의 `all-mpnet-base-v2`가 흔한 상위 선택지입니다.

**언어.** 한국어 텍스트가 포함된다면 영어 전용 모델보다 다국어 모델이나 한국어 특화 모델이 더 안정적입니다. 한국어 임베딩은 별도 한국어 AI 시리즈에서 더 깊게 다룹니다.

**태스크.** 문장 유사도 모델과 검색 모델은 학습 목표가 조금 다릅니다. 검색 모델은 쿼리와 문서가 서로 다른 분포를 가지는 상황에 더 최적화되어 있습니다. MTEB 리더보드의 Retrieval 섹션은 이런 비교에 실용적인 기준입니다.

이 시리즈에서는 일관성을 위해 `all-MiniLM-L6-v2`를 계속 사용합니다.

---

## 마무리

임베딩은 텍스트를 숫자 벡터로 바꾸고, 의미적 유사성을 공간적 근접성으로 표현합니다. 코사인 유사도는 그 근접성을 측정하는 도구이며, 이 덕분에 키워드 없는 검색이 가능해집니다. 직관은 단순합니다. 의미가 비슷할수록 거리가 가깝습니다.

다음 글에서는 개념에서 실습으로 넘어갑니다. `HuggingFaceEmbeddings`를 사용해 임베딩을 만들고 저장하고 다시 불러오는 방법, 그리고 배치 처리로 인코딩 속도를 높이는 방법을 살펴보겠습니다.

## 운영 체크리스트

- [ ] 사용 모델의 차원 수와 토큰 한도를 문서에 기록했다
- [ ] 정규화 여부를 한 번 정하고 모든 벡터에 일관되게 적용했다
- [ ] 임베딩 캐시 키에 모델, 버전, 입력 해시를 포함했다
- [ ] 직접 고른 몇 개의 문장 쌍으로 유사도를 계산해 품질을 기본 점검했다
- [ ] 임베딩 모델이 바뀔 때를 위한 재인덱싱 절차를 작성했다

## 임베딩 생성 계약을 코드로 고정하기

개념을 이해한 뒤 실제 서비스에 붙일 때 가장 먼저 해야 할 일은 임베딩 생성 계약을 코드로 고정하는 것입니다. 여기서 계약이란 `모델 이름`, `차원 수`, `정규화 여부`, `입력 전처리`, `출력 dtype`을 명시하고, 실행마다 같은 규칙을 강제하는 것을 뜻합니다. 이 계약이 느슨하면 같은 문장을 다른 조건으로 임베딩해 점수가 흔들리고, 인덱스 재현이 깨집니다.

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

이 패턴의 장점은 단순합니다. 이후 FAISS, Chroma, Qdrant, Pinecone으로 저장소를 바꿔도 임베딩 생성 규칙은 변하지 않습니다. 즉, 인덱스 계층을 바꿔도 점수 의미가 유지됩니다.

## 벡터 저장소별 최소 연결 예시

임베딩이 무엇인지 이해한 뒤에는 "어디에 넣을 것인가"가 자연스럽게 따라옵니다. 아래 예시는 개념 비교용으로 최소 코드만 남긴 형태입니다.

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
# 솔방울(관리형 서비스)
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

세 저장소 모두 API 모양은 다르지만 공통 원칙은 같습니다. `dimension`, `metric`, `metadata schema`가 임베딩 계약과 일치해야 합니다.

## HNSW와 IVF를 처음 볼 때의 기준

ANN 인덱스 알고리즘은 복잡해 보이지만 초반 기준은 간단하게 잡을 수 있습니다.

| 항목 | HNSW | IVF |
|---|---|---|
| 핵심 아이디어 | 그래프를 따라 근접 후보 탐색 | 군집 중심을 먼저 찾고 일부 버킷만 탐색 |
| 장점 | 높은 recall, 온라인 업데이트에 비교적 강함 | 메모리 효율, 대규모에서 예측 가능한 튜닝 |
| 단점 | 메모리 사용량 증가 | nlist/nprobe 튜닝 없으면 recall 급락 가능 |
| 주요 파라미터 | `M`, `efConstruction`, `efSearch` | `nlist`, `nprobe` |

여기서 중요한 메시지는 "지금 1편에서 인덱스를 확정하지 말라"입니다. 임베딩과 점수 의미를 먼저 고정하고, 데이터가 커질 때 ANN으로 넘어가도 늦지 않습니다.

## 초기 벤치마크 표를 남겨야 하는 이유

처음부터 복잡한 평가 파이프라인을 만들 필요는 없습니다. 하지만 최소한 아래 두 축은 기록해야 합니다.

| 설정 | top-5 recall(샘플 50개) | p95 latency (ms) |
|---|---:|---:|
| 브루트 포스(NumPy) | 1.00 | 82 |
| FAISS IndexFlatIP | 1.00 | 27 |
| HNSW(efSearch=64) | 0.98 | 11 |
| IVF(nlist=256, nprobe=16) | 0.95 | 8 |

수치 자체보다 중요한 것은 같은 질의셋으로 추이를 비교할 수 있는 기준선을 남기는 것입니다. 이 표가 없으면 "빨라졌는데 품질이 떨어졌는지"를 누구도 증명할 수 없습니다.

또 하나의 실전 팁은 임베딩 스키마를 문서화해 두는 것입니다. 예를 들어 `embedding_model`, `dimension`, `normalized`, `distance_metric` 네 항목을 인덱스 메타데이터에 넣어 두면, 팀원이 바뀌거나 배포 환경이 바뀌어도 "이 인덱스가 어떤 가정 위에서 만들어졌는지"를 바로 확인할 수 있습니다.

## 처음 질문으로 돌아가기

- **키워드가 같은데도 검색 결과가 빗나가거나, 표현만 달라서 결과를 놓칠 때 무엇이 부족한 걸까요?**
  부족한 것은 단어 일치가 아니라 의미를 비교할 표현입니다. 임베딩은 문장을 벡터로 바꿔 표현이 달라도 가까운 의미를 찾을 수 있게 합니다.

- **임베딩 벡터의 “가깝다”는 말은 실제로 무엇을 비교한다는 뜻일까요?**
  “가깝다”는 말은 벡터 공간에서 방향이나 거리 같은 수치 기준으로 두 텍스트의 의미적 근접성을 비교한다는 뜻입니다.

- **첫 모델을 고를 때 차원 수, 언어, 토큰 한도 중 무엇을 먼저 확인해야 할까요?**
  차원 수, 토큰 한도, 언어 지원, 모델 버전을 먼저 확인해야 합니다. 이 값들이 검색 품질과 재인덱싱 비용의 기본 제약이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- **Vector Search 101 (1/6): 임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기 (현재 글)**
- Vector Search 101 (2/6): HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기 (예정)
- Vector Search 101 (3/6): 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기 (예정)
- Vector Search 101 (4/6): FAISS 입문 — 고속 근사 최근접 이웃 검색 (예정)
- Vector Search 101 (5/6): 청크 전략 — 긴 문서를 어떻게 나눌 것인가 (예정)
- Vector Search 101 (6/6): 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 (예정)

<!-- toc:end -->

---

## 참고 자료

- [sentence-transformers documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Sentence Transformers pretrained models](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)
- [The Illustrated Word2Vec — Jay Alammar](https://jalammar.github.io/illustrated-word2vec/)

### 관련 시리즈

- [RAG Deep Dive](../../rag-deep-dive/ko/01-document-loading-and-chunking.md) — 이 시리즈가 다루는 임베딩과 ANN 인덱스를 RAG 파이프라인에서 어떻게 조립해 쓰는지 보여줍니다. 검색 엔진 자체보다 "문서 → 청크 → 검색 → 응답" 흐름이 궁금하다면 다음 단계로 권장합니다.

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/vector-search-101/ko/01-what-is-embedding)

Tags: Vector Search, FAISS, Embeddings, Python
