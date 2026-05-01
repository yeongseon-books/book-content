---
episode: 2
language: ko
last_reviewed: '2026-05-01'
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
  tistory: true
title: HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기
---

# HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기

> 벡터 검색 101 시리즈 (2/6)

예제 코드: [github.com/yeongseon-books/vector-search-101](https://github.com/yeongseon-books/vector-search-101/tree/main/ko/02-huggingface-embeddings)

지난 글에서 임베딩의 개념을 잡았다면, 이번 글은 실제로 벡터를 만들고 다루는 방법에 집중합니다. 이론을 코드로 옮기는 과정에서 자주 막히는 부분이 있습니다. 모델 로딩 시간을 어떻게 줄일지, 배치를 어떻게 구성할지, 벡터를 디스크에 저장했다가 재사용하는 방법은 무엇인지 같은 실용적인 질문들입니다.

`langchain-community`의 `HuggingFaceEmbeddings`는 `sentence-transformers`를 LangChain 호환 인터페이스로 감싼 클래스입니다. LangChain 생태계와 연동하지 않더라도, 임베딩 래퍼 패턴 자체가 실제 앱에서 어떻게 쓰이는지 이해하는 데 좋은 출발점이 됩니다.

이번 글에서 다룰 내용은 다음과 같습니다.

- `HuggingFaceEmbeddings` 설치와 초기화
- 단일 문장과 배치 임베딩의 차이
- 벡터를 NumPy 파일로 저장하고 불러오기
- 임베딩 속도를 높이는 실용 팁
- GPU가 없는 환경에서 CPU로 처리하기

```mermaid
flowchart LR
    A[문장 또는 문서 목록] --> B[HuggingFaceEmbeddings 초기화]
    B --> C[SentenceTransformer 모델 로딩]
    C --> D[encode 실행]
    D --> E[정규화된 벡터 출력]
    E --> F[NumPy 저장 또는 후속 검색]
```

<!-- ebook-only:start -->

이 장의 핵심: **HuggingFace 임베딩은 로컬에서 무료로 실행된다.** `sentence-transformers`가 모델을 내려받고 벡터를 반환한다.

## 이 장의 위치

이 글은 시리즈 6편 중 2번째 장입니다.
앞 장에서는 **임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기**을 다뤘습니다.
이 장을 마치면 다음 장에서 **코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기**으로 이어집니다.
<!-- ebook-only:end -->

---

## 설치

필요한 패키지는 세 가지입니다.

```bash
pip install langchain-community sentence-transformers numpy
```

`langchain-community`가 `HuggingFaceEmbeddings`를 제공하고, `sentence-transformers`가 실제 모델 로딩과 인코딩을 담당합니다. `numpy`는 벡터 저장과 연산에 씁니다.

---

## 첫 임베딩

`HuggingFaceEmbeddings`를 초기화하는 코드부터 보겠습니다.

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
```

`model_kwargs={"device": "cpu"}`는 CPU를 명시합니다. GPU가 있다면 `"cuda"`로 바꾸면 됩니다.

`encode_kwargs={"normalize_embeddings": True}`는 중요합니다. 정규화(L2-norm=1)를 켜면 코사인 유사도 계산이 내적(dot product)으로 단순화됩니다. FAISS 같은 라이브러리와 연동할 때 일관성 유지에 도움이 됩니다.

단일 문장 임베딩입니다.

```python
text = "벡터 검색은 의미 기반 검색의 핵심입니다."
vector = embedding_model.embed_query(text)

print(f"타입: {type(vector)}")
print(f"차원: {len(vector)}")
print(f"앞 5개 값: {vector[:5]}")
```

```
타입: <class 'list'>
차원: 384
앞 5개 값: [0.0523, -0.1847, 0.3012, 0.0934, -0.0721]
```

`embed_query()`는 쿼리 한 건을 처리하는 메서드입니다. 내부적으로 리스트를 반환합니다. FAISS나 NumPy와 연동할 때는 `np.array(vector)`로 변환하면 됩니다.

---

## 배치 임베딩

문서가 여러 개면 루프보다 배치가 훨씬 효율적입니다. `embed_documents()`는 리스트를 받아 리스트를 반환합니다.

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
    "FAISS는 Facebook AI Research에서 만든 벡터 검색 라이브러리입니다.",
    "코사인 유사도는 벡터 방향의 유사성을 측정합니다.",
    "임베딩 차원이 높을수록 더 많은 정보를 담을 수 있습니다.",
    "sentence-transformers는 문장 임베딩에 특화된 라이브러리입니다.",
    "청크 크기는 임베딩 품질과 검색 정확도에 영향을 줍니다.",
]

start = time.perf_counter()
vectors = embedding_model.embed_documents(documents)
elapsed = time.perf_counter() - start

vectors_np = np.array(vectors)
print(f"벡터 행렬 크기: {vectors_np.shape}")  # (5, 384)
print(f"소요 시간: {elapsed:.3f}초")
```

`embed_documents()`는 배치 단위로 모델을 호출하기 때문에, 같은 수의 문장을 루프로 `embed_query()` 5번 부르는 것보다 빠릅니다. 문서 수가 많을수록 차이가 커집니다.

---

## 벡터 저장과 불러오기

임베딩은 한 번 계산하면 재사용하는 편이 좋습니다. 같은 문서 집합을 매번 다시 인코딩하면 시간과 비용이 낭비됩니다. NumPy의 `.npy` 형식으로 저장하는 방법이 가장 단순합니다.

```python
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

documents = [
    "FAISS는 고속 벡터 검색 라이브러리입니다.",
    "임베딩 벡터를 디스크에 저장하면 재사용이 편합니다.",
    "NumPy는 배열 연산에 최적화된 라이브러리입니다.",
]

vectors = np.array(embedding_model.embed_documents(documents))

# 저장
np.save("embeddings.npy", vectors)
print(f"저장 완료: {vectors.shape}")

# 불러오기
loaded = np.load("embeddings.npy")
print(f"불러오기 완료: {loaded.shape}")
print(f"동일 여부: {np.allclose(vectors, loaded)}")
```

```
저장 완료: (3, 384)
불러오기 완료: (3, 384)
동일 여부: True
```

문서 원문도 함께 보관해야 합니다. 벡터 인덱스와 원문 텍스트를 같이 저장하면 검색 결과를 사람이 읽는 형태로 반환할 수 있습니다.

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
    "FAISS는 고속 벡터 검색 라이브러리입니다.",
    "임베딩 벡터를 디스크에 저장하면 재사용이 편합니다.",
    "NumPy는 배열 연산에 최적화된 라이브러리입니다.",
]

vectors = np.array(embedding_model.embed_documents(documents))

np.save("embeddings.npy", vectors)
with open("documents.json", "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)

print("저장 완료")
```

나중에 검색할 때는 두 파일을 같이 불러와서 인덱스를 연결합니다. 이 패턴은 4편(FAISS)에서 실제 검색 시스템을 만들 때 그대로 사용합니다.

---

## 속도를 높이는 실용 팁

CPU 환경에서 임베딩 속도를 높이는 방법이 몇 가지 있습니다.

**배치 크기 조정.** `encode_kwargs={"batch_size": 64}`로 배치 크기를 명시할 수 있습니다. 기본값은 32입니다. 메모리가 충분하다면 64나 128로 늘리면 처리 속도가 개선됩니다.

```python
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True, "batch_size": 64},
)
```

**모델 재사용.** `HuggingFaceEmbeddings` 객체를 함수마다 새로 만들지 말고, 모듈 수준에서 한 번만 초기화해서 재사용합니다. 모델 가중치 로딩에 수 초가 걸리기 때문입니다.

```python
# 좋은 패턴: 모듈 수준에서 한 번
_embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

def get_embedding_model() -> HuggingFaceEmbeddings:
    return _embedding_model
```

**캐싱.** 같은 텍스트를 반복 인코딩하는 경우라면 결과를 딕셔너리에 캐시해두는 것도 방법입니다. 문서 수가 수십만 건 이상이면 `diskcache` 같은 라이브러리를 고려할 수 있습니다.

---

## 직접 SentenceTransformer와 비교하기

`HuggingFaceEmbeddings`는 `SentenceTransformer`를 감싼 래퍼입니다. 두 방식의 결과는 동일합니다.

```python
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

text = "두 라이브러리의 출력이 같은지 확인합니다."

# HuggingFaceEmbeddings
hf_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
hf_vector = np.array(hf_model.embed_query(text))

# SentenceTransformer 직접
st_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
st_vector = st_model.encode(text, normalize_embeddings=True)

print(f"HuggingFaceEmbeddings 차원: {hf_vector.shape}")
print(f"SentenceTransformer 차원: {st_vector.shape}")
print(f"최대 오차: {np.max(np.abs(hf_vector - st_vector)):.6f}")
```

```
HuggingFaceEmbeddings 차원: (384,)
SentenceTransformer 차원: (384,)
최대 오차: 0.000001
```

부동소수점 오차 수준의 미세한 차이만 있을 뿐 결과는 동일합니다. LangChain 체인과 연동하려면 `HuggingFaceEmbeddings`를 쓰고, 단독으로 쓸 때는 `SentenceTransformer`를 직접 써도 무방합니다.

---

## 마무리

`HuggingFaceEmbeddings`로 벡터를 만들고, NumPy로 저장하고 불러오는 방법까지 익혔습니다. 배치 임베딩과 모델 재사용 패턴은 실제 앱에서도 그대로 쓸 수 있는 구조입니다.

다음 글에서는 벡터 간 유사도를 제대로 계산하는 방법을 다룹니다. 코사인 유사도 외에 내적과 유클리드 거리가 언제 유리한지, 정규화가 왜 중요한지, 그리고 직접 최근접 이웃 검색을 만들어 보겠습니다.

<!-- blog-only:start -->
다음 글: [코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기](./03-cosine-similarity.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기](./01-what-is-embedding.md)
- **HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기 (현재 글)**
- 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기 (예정)
- FAISS 입문 — 고속 근사 최근접 이웃 검색 (예정)
- 청크 전략 — 긴 문서를 어떻게 나눌 것인가 (예정)
- 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 (예정)

<!-- toc:end -->

---

## 참고 자료

- [langchain-community HuggingFaceEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/huggingfacehub/)
- [sentence-transformers encode API](https://www.sbert.net/docs/package_reference/SentenceTransformer.html)
- [all-MiniLM-L6-v2 모델 카드](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

Tags: Vector Search, FAISS, Embeddings, Python
