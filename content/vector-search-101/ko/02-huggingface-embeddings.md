---
episode: 2
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
title: HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기
seo_description: HuggingFace 임베딩을 로컬에서 만들고 저장하고 다시 불러오는 실습을 다룹니다.
---

# HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기

1편에서 개념을 다뤘다면, 이번 글은 실제 코드를 실행하는 단계입니다. 이론에서 실제 임베딩으로 넘어가면 모델 로딩 시간을 어떻게 줄일지, 배치를 어떻게 구성할지, 벡터를 디스크에 저장하고 효율적으로 다시 불러오려면 어떻게 해야 할지 같은 실무 질문이 바로 등장합니다.

`langchain-huggingface`의 `HuggingFaceEmbeddings`는 `sentence-transformers`를 LangChain 호환 인터페이스 뒤에 감싼 래퍼입니다. LangChain 파이프라인을 직접 만들지 않더라도 이 래퍼 패턴은 이해할 가치가 있습니다. 실제 애플리케이션에서 임베딩 모델이 더 큰 스택 안에 어떻게 통합되는지를 보여 주기 때문입니다.

이 글은 Vector Search 101 시리즈의 2번째 글입니다.

여기서는 로컬 임베딩을 만들고, 배치로 처리하고, 저장 후 다시 불러오는 흐름까지 한 번에 묶어 봅니다. 다음 다섯 가지를 다룹니다.

- `HuggingFaceEmbeddings` 설치와 초기화
- 단일 쿼리 임베딩과 배치 임베딩의 차이
- 벡터를 NumPy 파일로 저장하고 다시 불러오는 방법
- CPU 환경에서 인코딩 속도를 높이는 실용 팁
- 래퍼와 원시 `SentenceTransformer` API 비교

![Single query embedding call flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-01-huggingface-embeddings-in-practice-creat.ko.png)

*단일 쿼리 임베딩 호출 흐름*
<!-- ebook-only:start -->

**핵심 아이디어**: HuggingFace 임베딩은 로컬에서 무료로 실행됩니다. `sentence-transformers`가 모델을 내려받고 벡터를 반환합니다.

## 이 장의 위치

이 글은 시리즈 6편 중 2편입니다.
이전 글에서는 **임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기**를 다뤘습니다.
이 글 다음에는 **코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기**로 이어집니다.
<!-- ebook-only:end -->

---

> HuggingFace 임베딩 실습의 핵심은 모델 하나를 잘 호출하는 법보다, 같은 벡터를 반복 가능하게 만들고 재사용하는 흐름을 익히는 데 있습니다.

## 이 글에서 다룰 문제

- Hugging Face `sentence-transformers`와 OpenAI Embeddings API 사이에는 실제로 어떤 트레이드오프가 있을까요?
- GPU 없이 로컬 임베딩 모델을 실행할 때 어떤 성능 함정이 생길까요?
- 다국어 모델과 영어 전용 모델은 한국어 검색 품질에서 어떻게 갈릴까요?
- 배치 임베딩에서는 메모리, 배치 크기, 토큰 한계를 어떻게 균형 있게 맞출까요?
- 임베딩 모델 버전이 바뀌면 기존 인덱스를 어떻게 마이그레이션해야 할까요?

## 설치

필요한 패키지는 세 가지입니다.

```bash
pip install langchain-huggingface sentence-transformers numpy
```

`langchain-huggingface`는 `HuggingFaceEmbeddings`를 제공하고, `sentence-transformers`는 실제 모델 로딩과 인코딩을 담당합니다. `numpy`는 벡터 저장과 산술 연산에 사용됩니다.

---

## 첫 번째 임베딩

![Single query embedding call flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-01-first-embedding.ko.png)

*단일 쿼리 임베딩 호출 흐름*
모델을 초기화하고 문장 하나를 인코딩해 보겠습니다.

```python
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
```

`model_kwargs={"device": "cpu"}`는 CPU 실행을 명시합니다. GPU가 있다면 `"cuda"`로 바꾸면 됩니다.

`encode_kwargs={"normalize_embeddings": True}`도 중요합니다. L2 정규화를 적용하면 코사인 유사도 계산이 내적으로 단순화됩니다. FAISS 같은 라이브러리와 연결할 때도 단위 벡터를 가정하는 동작과 일관성을 유지할 수 있습니다.

```python
text = "Vector search is the foundation of semantic retrieval."
vector = embedding_model.embed_query(text)

print(f"type: {type(vector)}")
print(f"dimension: {len(vector)}")
print(f"first 5 values: {vector[:5]}")
```

<!-- injected-output:start -->
**출력 결과**

    type: <class 'list'>
    dimension: 384
    first 5 values: [0.04267469793558121, 0.00979855377227068, -0.031552139669656754, -0.033105991780757904, 0.04774016514420509]

<!-- injected-output:end -->

`embed_query()`는 입력 하나를 처리하고 일반 Python 리스트를 반환합니다. NumPy 연산이 필요할 때는 `np.array()`로 바꿔 쓰면 됩니다.

---

## 배치 임베딩

![Single call and batch call contrast](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-02-batch-embedding.ko.png)

*단일 호출과 배치 호출의 대비*
문서가 여러 개라면 `embed_query()`를 반복 호출하는 것보다 `embed_documents()` 한 번이 더 효율적입니다. 모델이 내부적으로 배치 처리하고, 반복 초기화 오버헤드도 줄일 수 있기 때문입니다.

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
**출력 결과**

    matrix shape: (5, 384)
    elapsed: 0.101s

<!-- injected-output:end -->

문서 수가 늘어날수록 배치 호출과 반복 호출의 차이는 더 커집니다. 코퍼스가 크다면 `embed_documents()`를 기본 선택으로 삼는 편이 좋습니다.

---

## 벡터 저장과 다시 불러오기

![Vector and document save flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-03-saving-and-reloading-vectors.ko.png)

*벡터와 문서 저장 흐름*
같은 문서에 대해 실행할 때마다 임베딩을 다시 계산하면 시간이 낭비됩니다. 한 번 계산한 행렬을 저장하고 재사용하는 편이 낫습니다.

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
**출력 결과**

    saved: (3, 384)
    reloaded: (3, 384)
    identical: True

<!-- injected-output:end -->

벡터만 저장하면 결과는 결국 인덱스 위치 번호에 불과합니다. 원문 텍스트도 함께 저장해야 검색 결과를 다시 사용자에게 읽을 수 있는 형태로 보여 줄 수 있습니다.

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
**출력 결과**

    saved embeddings and documents

<!-- injected-output:end -->

4편에서는 정확히 이 패턴을 이용해 실제 FAISS 검색 시스템을 만듭니다.

---

## 속도를 높이는 실용 팁

![Model reuse and batch size path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-04-practical-speed-tips.ko.png)

*모델 재사용과 배치 크기 조정 경로*
CPU 기반 인코딩은 규모가 커질수록 느립니다. 몇 가지 조정만으로도 꽤 개선할 수 있습니다.

**배치 크기 늘리기.** 기본값은 32입니다. 메모리가 허용한다면 64나 128로 늘려 오버헤드를 줄일 수 있습니다.

```python
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True, "batch_size": 64},
)
```

**한 번만 초기화하기.** 모델 가중치를 로드하는 데는 몇 초가 걸릴 수 있습니다. `HuggingFaceEmbeddings` 객체를 모듈 수준에서 한 번 만들고 계속 재사용하는 편이 좋습니다.

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

**반복 입력 캐시하기.** 같은 텍스트를 반복 인코딩한다면 사전에 결과를 캐시할 수 있습니다. 더 큰 워크로드에서는 `diskcache`나 `joblib.Memory` 같은 도구를 사용하면 영속 캐시를 자동으로 관리할 수 있습니다.

---

## 래퍼와 원시 API 비교

![Wrapper and raw API comparison structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/02/02-05-comparing-wrapper-and-raw-api.ko.png)

*래퍼와 원시 API 비교 구조*
`HuggingFaceEmbeddings`는 내부적으로 `SentenceTransformer`를 사용합니다. 출력은 수치적으로 동일합니다.

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
**출력 결과**

    HuggingFaceEmbeddings shape: (384,)
    SentenceTransformer shape:   (384,)
    max difference: 0.000000

<!-- injected-output:end -->

부동소수점 반올림 수준의 차이를 제외하면 결과는 같습니다. LangChain 파이프라인을 만들 때는 `HuggingFaceEmbeddings`가 편하고, 추상화가 필요 없을 때는 `SentenceTransformer`를 직접 써도 됩니다.

---

## 마무리

이제 몇 줄의 코드로 임베딩을 만들고 저장하고 다시 불러올 수 있습니다. 배치 인코딩과 모듈 수준 초기화는 처음부터 가져가면 좋은 실전 습관입니다.

다음 글에서는 유사도 계산으로 넘어갑니다. 코사인 유사도, 내적, 유클리드 거리가 각각 언제 맞는지, 정규화가 계산식을 어떻게 바꾸는지, 그리고 외부 라이브러리 없이 브루트 포스 최근접 이웃 검색을 어떻게 만드는지 살펴보겠습니다.

## 운영 체크리스트

- [ ] 모델 카드(라이선스, 학습 데이터, 차원 수)를 검토했다
- [ ] CPU/GPU 환경에 맞게 배치 크기와 토크나이저 옵션을 조정했다
- [ ] 한국어 입력은 다국어 모델이나 한국어 특화 모델로 검증했다
- [ ] 결과 차원 수와 dtype를 인덱스 스키마와 맞췄다
- [ ] 장기 보관하는 임베딩과 함께 모델 버전을 저장했다

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

- [langchain-huggingface HuggingFaceEmbeddings](https://python.langchain.com/docs/integrations/text_embedding/huggingfacehub/)
- [sentence-transformers encode API](https://www.sbert.net/docs/package_reference/SentenceTransformer.html)
- [all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

Tags: Vector Search, FAISS, Embeddings, Python
