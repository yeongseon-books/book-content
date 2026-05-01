---
title: '청크 전략 — 긴 문서를 어떻게 나눌 것인가'
series: vector-search-101
episode: 5
language: ko
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

# 청크 전략 — 긴 문서를 어떻게 나눌 것인가

> 벡터 검색 101 시리즈 (5/6)

임베딩 모델은 처리할 수 있는 토큰 수에 한계가 있습니다. `all-MiniLM-L6-v2`는 최대 256 서브워드 토큰입니다. PDF 한 페이지만 해도 이 한계를 금방 넘습니다. 긴 문서를 통째로 임베딩하면 잘려서 중요한 내용이 날아가거나, 너무 많은 정보가 한 벡터에 압축되어 검색 정확도가 떨어집니다.

청크(chunk)는 긴 문서를 임베딩 가능한 크기의 단위로 나눈 것입니다. 어떻게 나누느냐가 검색 품질에 직접 영향을 줍니다. 청크가 너무 작으면 문맥이 끊기고, 너무 크면 관련 없는 내용이 섞입니다.

이번 글에서 다룰 내용은 다음과 같습니다.

- 청크 크기와 오버랩의 기본 개념
- 고정 크기 청킹 직접 구현
- LangChain `RecursiveCharacterTextSplitter` 사용
- 청크 경계가 검색 품질에 미치는 영향
- 상황별 청킹 전략 선택 기준

---

## 청크 크기와 오버랩

청킹의 두 핵심 파라미터는 `chunk_size`와 `chunk_overlap`입니다.

**chunk_size**: 청크 하나의 최대 길이입니다. 문자 수나 토큰 수로 측정합니다. 일반적으로 200~500 토큰 범위에서 시작합니다.

**chunk_overlap**: 인접한 청크 사이에 공유하는 길이입니다. 오버랩이 없으면 문장이 청크 경계에서 뚝 잘릴 수 있습니다. 오버랩을 주면 같은 내용이 두 청크에 걸쳐 나타나서 경계 근처 내용도 검색에 걸립니다.

```
원본 텍스트: A B C D E F G H I J (각 문자가 하나의 단어라고 가정)

chunk_size=4, chunk_overlap=1 이면:
청크 1: A B C D
청크 2: D E F G   ← D가 겹침
청크 3: G H I J   ← G가 겹침
```

오버랩은 chunk_size의 10~20% 수준이 일반적입니다. 너무 크면 중복이 많아져서 인덱스 크기가 불필요하게 커집니다.

---

## 고정 크기 청킹 직접 구현

개념을 직접 코드로 구현해 봅니다.

```python
def chunk_text(
    text: str,
    chunk_size: int = 200,
    chunk_overlap: int = 20,
) -> list[str]:
    """문자 수 기준 고정 크기 청킹."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk:
            chunks.append(chunk)
        start += chunk_size - chunk_overlap
    return chunks

sample_text = (
    "벡터 검색은 텍스트를 수치 벡터로 변환해 의미 기반으로 검색하는 방법입니다. "
    "임베딩 모델은 유사한 의미의 텍스트를 벡터 공간에서 가깝게 배치합니다. "
    "FAISS는 Facebook AI Research에서 개발한 고속 벡터 검색 라이브러리입니다. "
    "청크 전략은 긴 문서를 임베딩 모델이 처리할 수 있는 단위로 나누는 방법입니다. "
    "적절한 청크 크기를 선택하면 검색 정확도를 높일 수 있습니다. "
    "오버랩을 설정하면 청크 경계에서 문맥이 끊기는 문제를 줄일 수 있습니다."
)

chunks = chunk_text(sample_text, chunk_size=100, chunk_overlap=20)

print(f"전체 텍스트 길이: {len(sample_text)}자")
print(f"청크 수: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"\n[{i}] {len(chunk)}자: {chunk[:60]}...")
```

이 구현은 개념 이해용입니다. 문장 중간을 잘라버릴 수 있기 때문에 실제 앱에서는 쓰기 어렵습니다.

---

## RecursiveCharacterTextSplitter

LangChain의 `RecursiveCharacterTextSplitter`는 더 정교합니다. 문단, 문장, 단어 경계 순서로 나누려고 시도해서 문장이 중간에 잘리는 일을 줄입니다.

```bash
pip install langchain-text-splitters
```

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)

document = """
벡터 검색은 텍스트를 수치 벡터로 변환해 의미 기반으로 검색하는 방법입니다.
키워드 검색과 달리 표현이 달라도 의미가 같으면 검색 결과에 포함됩니다.

임베딩 모델은 유사한 의미의 텍스트를 벡터 공간에서 가깝게 배치합니다.
sentence-transformers 라이브러리는 문장 수준 임베딩에 특화된 모델을 제공합니다.
all-MiniLM-L6-v2는 빠르고 가벼운 모델로 CPU 환경에서도 실용적입니다.

FAISS는 Facebook AI Research에서 개발한 고속 벡터 검색 라이브러리입니다.
정확 검색과 근사 검색 모두 지원하며, 수십억 개의 벡터도 처리할 수 있습니다.
IndexFlatIP는 내적 기반 정확 검색 인덱스로, 정규화된 벡터에서 코사인 검색과 동일합니다.
"""

chunks = splitter.split_text(document)

print(f"청크 수: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"\n[{i}] {len(chunk)}자:")
    print(f"  {chunk[:80]}...")
```

`separators` 리스트는 우선순위 순서입니다. 먼저 `\n\n`(문단 경계)로 나누려 하고, 실패하면 `\n`, `. `, ` `, 마지막으로 문자 단위까지 내려갑니다. 이 덕분에 자연스러운 문장 경계에서 잘릴 가능성이 높아집니다.

---

## 청킹과 임베딩을 연결하기

청크를 만들고 바로 임베딩해서 FAISS 인덱스에 넣는 전체 흐름입니다.

```python
import json

import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30,
    separators=["\n\n", "\n", ". ", " ", ""],
)

document = """
벡터 검색은 텍스트를 수치 벡터로 변환해 의미 기반으로 검색하는 방법입니다.
키워드 검색과 달리 표현이 달라도 의미가 같으면 검색 결과에 포함됩니다.

임베딩 모델은 유사한 의미의 텍스트를 벡터 공간에서 가깝게 배치합니다.
sentence-transformers 라이브러리는 문장 수준 임베딩에 특화된 모델을 제공합니다.

FAISS는 Facebook AI Research에서 개발한 고속 벡터 검색 라이브러리입니다.
정확 검색과 근사 검색 모두 지원하며, 수십억 개의 벡터도 처리할 수 있습니다.

청크 전략은 긴 문서를 임베딩 모델이 처리할 수 있는 단위로 나누는 방법입니다.
chunk_size와 chunk_overlap을 잘 조정해야 검색 품질이 좋아집니다.
"""

# 청킹
chunks = splitter.split_text(document)
print(f"청크 수: {len(chunks)}")

# 임베딩
vectors = np.array(embedding_model.embed_documents(chunks), dtype=np.float32)
dimension = vectors.shape[1]

# FAISS 인덱스
index = faiss.IndexFlatIP(dimension)
index.add(vectors)

# 검색 함수
def search(query: str, top_k: int = 3) -> list[tuple[float, str]]:
    q_vec = np.array([embedding_model.embed_query(query)], dtype=np.float32)
    scores, indices = index.search(q_vec, top_k)
    return [
        (float(scores[0][i]), chunks[indices[0][i]])
        for i in range(top_k)
        if indices[0][i] != -1
    ]

# 쿼리 테스트
for query in ["벡터 검색 원리", "FAISS 라이브러리 특징", "청크 크기 설정"]:
    print(f"\n쿼리: '{query}'")
    for rank, (score, text) in enumerate(search(query, top_k=2), start=1):
        print(f"  [{rank}] {score:.4f} — {text[:60]}...")
```

---

## 청크 크기가 검색 품질에 미치는 영향

청크가 너무 작으면 단일 청크에 충분한 문맥이 없어서 쿼리와 매칭이 잘 안 됩니다. 너무 크면 관련 없는 내용이 섞여 검색 정확도가 떨어집니다.

일반적인 시작값은 다음과 같습니다.

| 문서 유형 | chunk_size | chunk_overlap |
|---|---|---|
| 짧은 문단, 뉴스 기사 | 200~300 | 20~30 |
| 기술 문서, 매뉴얼 | 300~500 | 30~50 |
| 법률 문서, 학술 논문 | 500~800 | 50~100 |

시작값으로 시작해서 실제 데이터로 검색 품질을 측정하고 조정하는 것이 정석입니다. 청킹 파라미터는 경험적으로 결정하는 편이 많습니다.

---

## 마무리

청킹은 벡터 검색 파이프라인에서 가장 설정하기 까다로운 부분 중 하나입니다. 임베딩 모델보다 청킹 전략이 검색 품질에 더 큰 영향을 주는 경우도 있습니다.

다음 글에서는 문서 수집부터 FAISS 인덱스 구축, 쿼리까지 전체 파이프라인을 하나로 연결해 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기](./01-what-is-embedding.md)
- [HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기](./02-huggingface-embeddings.md)
- [코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기](./03-cosine-similarity.md)
- [FAISS 입문 — 고속 근사 최근접 이웃 검색](./04-faiss-fundamentals.md)
- **청크 전략 — 긴 문서를 어떻게 나눌 것인가 (현재 글)**
- 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain RecursiveCharacterTextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter/)
- [Chunking Strategies for LLM Applications — Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [sentence-transformers 최대 시퀀스 길이](https://www.sbert.net/docs/pretrained_models.html)

Tags: Vector Search, FAISS, Embeddings, Python
