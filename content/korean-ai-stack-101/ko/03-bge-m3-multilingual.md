---
title: 'BGE-M3 다국어 임베딩 실전'
series: korean-ai-stack-101
episode: 3
language: ko
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

# BGE-M3 다국어 임베딩 실전

> 한국어 AI 스택 101 시리즈 (3/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/ko/03-bge-m3-multilingual)

기술 문서, 논문, API 레퍼런스는 한국어 본문에 영어 용어가 섞인 경우가 많습니다. "트랜스포머(Transformer) 아키텍처의 어텐션(Attention) 메커니즘"처럼요. KoSimCSE는 한국어에 최적화되어 있지만, 이런 코드스위칭 텍스트에서는 BGE-M3가 더 강합니다. BGE-M3는 100개 이상의 언어를 지원하며, Dense + Sparse 두 가지 검색 방식을 하나의 모델에서 모두 제공합니다.

다룰 내용은 다음과 같습니다.

- BGE-M3의 Dense / Sparse / ColBERT 세 가지 출력
- 한국어-영어 혼용 문서에서 BGE-M3 성능 확인
- Dense + BM25 스타일 하이브리드 검색
- LangChain과 통합

---

<!-- ebook-only:start -->

이 장의 핵심: **BGE-M3는 한 모델로 다국어 임베딩을 처리한다.** 한국어와 영어를 같은 벡터 공간에 표현해 크로스링구얼 검색이 가능하다.

## 이 장의 위치

이 글은 시리즈 6편 중 3번째 장입니다.
앞 장에서는 **KoSimCSE로 문장 유사도 구현하기**을 다뤘습니다.
이 장을 마치면 다음 장에서 **CLOVA OCR API로 문서 텍스트 추출**으로 이어집니다.
<!-- ebook-only:end -->

## BGE-M3의 세 가지 출력

BGE-M3는 동일한 입력에 대해 세 가지 다른 형태의 임베딩을 출력합니다.

**Dense**: 일반적인 고차원 벡터(1024차원). FAISS 같은 ANN 인덱스와 함께 사용합니다.

**Sparse (Lexical Weight)**: 각 토큰에 가중치를 부여한 희소 벡터. BM25와 유사한 방식으로 정확한 키워드 매칭에 강합니다.

**ColBERT (Multi-vector)**: 각 토큰별로 별도의 벡터를 생성해 Late Interaction 방식으로 점수를 계산합니다. 가장 정확하지만 저장 공간과 계산 비용이 큽니다.

실제 서비스에서는 Dense + Sparse 하이브리드가 비용 대비 효과가 좋습니다.

---

## Dense 임베딩 기본 사용

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")

# 한국어-영어 혼용 문서
mixed_docs = [
    "트랜스포머(Transformer) 모델의 어텐션(Attention) 메커니즘은 시퀀스의 각 위치가 다른 위치에 얼마나 집중할지를 학습합니다.",
    "FAISS는 Facebook AI Research에서 개발한 벡터 유사도 검색 라이브러리입니다.",
    "파이썬의 asyncio 모듈을 사용하면 비동기 I/O 작업을 효율적으로 처리할 수 있습니다.",
    "LangChain의 LCEL(LangChain Expression Language)은 체인을 선언적으로 구성하는 방법입니다.",
    "RAG(Retrieval-Augmented Generation)는 검색과 생성을 결합해 LLM의 지식 한계를 보완합니다.",
    "Docker 컨테이너를 Kubernetes 클러스터에 배포하는 방법을 알아봅니다.",
]

# Dense 임베딩
embeddings = model.encode(mixed_docs, normalize_embeddings=True)
print(f"Dense 임베딩 형태: {embeddings.shape}")  # (6, 1024)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))

# 한국어와 영어 혼용 쿼리 테스트
queries = [
    "Attention mechanism이 어떻게 작동하나요?",     # 영어 키워드 + 한국어 문장
    "벡터 검색 라이브러리",                          # 순수 한국어 쿼리
    "async I/O 처리 방법",                           # 영어 + 한국어 혼용
]

for query in queries:
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    sims = [(cosine_sim(query_vec, emb), doc) for emb, doc in zip(embeddings, mixed_docs)]
    sims.sort(reverse=True)

    print(f"\n쿼리: {query}")
    for score, doc in sims[:3]:
        print(f"  [{score:.3f}] {doc[:60]}...")
```

---

## Sparse 가중치 추출

BGE-M3의 Sparse 출력은 토큰별 가중치 딕셔너리 형태입니다. 중요한 토큰에 높은 가중치가 부여됩니다.

```python
from FlagEmbedding import BGEM3FlagModel

# FlagEmbedding 라이브러리로 Sparse 출력 사용
# pip install FlagEmbedding
flag_model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)

docs = [
    "파이썬 비동기 프로그래밍과 asyncio 사용법",
    "딥러닝 모델 훈련과 최적화 기법",
]

output = flag_model.encode(docs, return_sparse=True)
sparse_weights = output["lexical_weights"]

# 첫 번째 문서의 상위 가중치 토큰 출력
print("문서 1의 중요 토큰:")
weights = sparse_weights[0]
sorted_tokens = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:10]
for token_id, weight in sorted_tokens:
    print(f"  토큰 ID {token_id}: {weight:.4f}")
```

---

## Dense + Sparse 하이브리드 검색

Dense는 의미 유사도에 강하고, Sparse는 정확한 키워드 매칭에 강합니다. 두 점수를 가중 합산하면 두 장점을 모두 얻습니다.

```python
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")

tech_docs = [
    "Python asyncio를 사용한 비동기 HTTP 요청 처리",
    "FAISS IndexIVFFlat으로 대규모 벡터 검색 최적화",
    "Kubernetes Pod 스케줄링과 리소스 제한 설정",
    "LangChain Retriever와 FAISS 벡터스토어 통합",
    "트랜스포머 모델의 Self-Attention 구현",
    "Redis를 이용한 API 응답 캐싱 전략",
    "PostgreSQL 인덱스 최적화와 쿼리 플랜 분석",
    "Docker multi-stage build로 이미지 크기 줄이기",
]

# Dense 임베딩 구성
dense_embeddings = model.encode(tech_docs, normalize_embeddings=True).astype(np.float32)
dim = dense_embeddings.shape[1]
dense_index = faiss.IndexFlatIP(dim)
dense_index.add(dense_embeddings)

def sparse_sim(query: str, doc: str) -> float:
    """단순 단어 오버랩 기반 Sparse 유사도 (BM25 근사)."""
    query_tokens = set(query.lower().split())
    doc_tokens = set(doc.lower().split())
    overlap = query_tokens & doc_tokens
    if not query_tokens:
        return 0.0
    return len(overlap) / len(query_tokens)

def hybrid_search(query: str, alpha: float = 0.7, k: int = 3) -> list[dict]:
    """
    하이브리드 검색: alpha * dense_score + (1 - alpha) * sparse_score
    alpha=1.0이면 pure dense, alpha=0.0이면 pure sparse.
    """
    # Dense 점수
    query_vec = model.encode([query], normalize_embeddings=True).astype(np.float32)
    distances, indices = dense_index.search(query_vec, len(tech_docs))
    dense_scores = {int(idx): float(dist) for idx, dist in zip(indices[0], distances[0])}

    # Sparse 점수 (모든 문서)
    sparse_scores = {i: sparse_sim(query, doc) for i, doc in enumerate(tech_docs)}

    # 점수 정규화 및 합산
    results = []
    for i, doc in enumerate(tech_docs):
        d_score = dense_scores.get(i, 0.0)
        s_score = sparse_scores.get(i, 0.0)
        combined = alpha * d_score + (1 - alpha) * s_score
        results.append({"score": combined, "dense": d_score, "sparse": s_score, "doc": doc})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:k]

queries = [
    "FAISS 벡터 인덱스 구성 방법",
    "asyncio HTTP",
    "Kubernetes 리소스 관리",
]

for query in queries:
    print(f"\n쿼리: {query}")
    results = hybrid_search(query, alpha=0.7)
    for r in results:
        print(f"  [{r['score']:.3f}] dense={r['dense']:.3f} sparse={r['sparse']:.3f}")
        print(f"       {r['doc']}")
```

---

## LangChain과 통합

```python
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

vectorstore = FAISS.from_texts(texts=tech_docs, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "아래 기술 문서를 참고해서 질문에 답하세요.\n\n"
        "문서:\n{context}",
    ),
    ("human", "{question}"),
])

def format_docs(docs: list) -> str:
    return "\n".join(doc.page_content for doc in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = chain.invoke("FAISS로 벡터 검색을 최적화하는 방법은?")
print(f"답변: {answer}")
```

---

## 마무리

BGE-M3는 한국어-영어 혼용 문서를 다루는 기술 서비스에 적합합니다. Dense만 써도 충분한 경우가 많지만, 정확한 키워드 매칭이 중요하다면 Sparse와 하이브리드 검색을 고려하세요. 다음 글에서는 CLOVA OCR API로 이미지나 PDF에서 텍스트를 추출하는 방법을 다룹니다.

<!-- blog-only:start -->
다음 글: [CLOVA OCR API로 문서 텍스트 추출](./04-clova-ocr.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
- **BGE-M3 다국어 임베딩 실전 (현재 글)**
- CLOVA OCR API로 문서 텍스트 추출 (예정)
- HyperCLOVA X와 Solar API 사용하기 (예정)
- 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [BGE-M3 논문](https://arxiv.org/abs/2309.07597)
- [FlagEmbedding 라이브러리](https://github.com/FlagOpen/FlagEmbedding)
- [하이브리드 검색 전략](https://www.pinecone.io/learn/hybrid-search-intro/)

Tags: Korean NLP, LLM, Embeddings, OCR
