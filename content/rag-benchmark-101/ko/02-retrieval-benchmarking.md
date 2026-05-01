---
title: '검색 성능 측정'
series: rag-benchmark-101
episode: 2
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- VectorDB
- Benchmarking
- LLM
last_reviewed: '2026-05-01'
---

# 검색 성능 측정

> RAG 벤치마크 101 (2/6)

좋은 RAG 시스템은 관련 문서를 높은 순위에 배치합니다. 이 포스트에서는 FAISS 기반 검색기의 성능을 쿼리 집합으로 체계적으로 측정하고, 결과를 집계해 시스템 수준의 검색 성능 리포트를 만드는 방법을 다룹니다.

예제 코드는 [`yeongseon-books/rag-benchmark-101`의 `ko/02-retrieval-benchmarking`](https://github.com/yeongseon-books/rag-benchmark-101/tree/main/ko/02-retrieval-benchmarking)에서 확인할 수 있습니다.

---

## 검색 성능 벤치마크 설계

검색 성능을 측정하려면 세 가지가 필요합니다.

- **쿼리 집합**: 실제 사용 패턴을 반영한 질문 목록
- **정답 집합**: 각 쿼리에 대한 관련 문서 ID 목록 (ground truth)
- **검색기**: 비교 대상 시스템

정답 집합이 없다면 LLM을 사용해 자동으로 생성할 수 있습니다.

---

## 테스트 코퍼스와 쿼리 생성

```python
import json
import os
from dataclasses import dataclass, field
from typing import Optional

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

# ── 테스트 코퍼스 ─────────────────────────────────────────────────────────
CORPUS = [
    Document(page_content="벡터 데이터베이스는 임베딩 벡터를 저장하고 유사도 검색을 지원합니다.", metadata={"id": "d01", "topic": "vectordb"}),
    Document(page_content="FAISS는 Facebook AI Research에서 개발한 벡터 유사도 검색 라이브러리입니다.", metadata={"id": "d02", "topic": "faiss"}),
    Document(page_content="FAISS의 IndexFlatL2는 정확한 L2 거리 기반 검색을 지원합니다.", metadata={"id": "d03", "topic": "faiss"}),
    Document(page_content="코사인 유사도는 두 벡터의 방향 유사성을 측정합니다.", metadata={"id": "d04", "topic": "similarity"}),
    Document(page_content="HNSW 알고리즘은 계층적 그래프를 사용한 빠른 ANN 검색입니다.", metadata={"id": "d05", "topic": "ann"}),
    Document(page_content="임베딩 모델은 텍스트를 고차원 벡터로 변환합니다.", metadata={"id": "d06", "topic": "embedding"}),
    Document(page_content="all-MiniLM-L6-v2는 384차원 임베딩을 생성하는 경량 모델입니다.", metadata={"id": "d07", "topic": "embedding"}),
    Document(page_content="청킹 크기가 작을수록 정밀도가 높아지지만 컨텍스트가 줄어듭니다.", metadata={"id": "d08", "topic": "chunking"}),
    Document(page_content="하이브리드 검색은 키워드 검색과 벡터 검색을 결합합니다.", metadata={"id": "d09", "topic": "hybrid"}),
    Document(page_content="리랭킹은 초기 검색 결과를 재정렬해 정밀도를 높입니다.", metadata={"id": "d10", "topic": "reranking"}),
]

@dataclass
class QueryGroundTruth:
    query: str
    relevant_ids: set[str]
    topic: str = ""

# ── 쿼리 집합 정의 ────────────────────────────────────────────────────────
QUERIES: list[QueryGroundTruth] = [
    QueryGroundTruth("FAISS란 무엇인가요?", {"d02", "d03"}, "faiss"),
    QueryGroundTruth("임베딩 모델은 어떻게 동작하나요?", {"d06", "d07"}, "embedding"),
    QueryGroundTruth("코사인 유사도와 L2 거리의 차이는?", {"d03", "d04"}, "similarity"),
    QueryGroundTruth("ANN 검색 알고리즘이란?", {"d05"}, "ann"),
    QueryGroundTruth("청킹 크기가 검색에 미치는 영향은?", {"d08"}, "chunking"),
    QueryGroundTruth("하이브리드 검색이란?", {"d09"}, "hybrid"),
]
```

---

## 검색기 벤치마크 실행

```python
from collections import defaultdict

def run_retrieval_benchmark(
    queries: list[QueryGroundTruth],
    vectorstore: FAISS,
    k_values: list[int] = [1, 3, 5],
) -> dict:
    """쿼리 집합 전체에 대해 검색 성능을 측정합니다."""

    retriever_k = max(k_values)
    retriever = vectorstore.as_retriever(search_kwargs={"k": retriever_k})

    all_metrics: list[dict] = []
    per_topic: dict[str, list[dict]] = defaultdict(list)

    for qt in queries:
        retrieved_docs = retriever.invoke(qt.query)
        retrieved_ids = [d.metadata["id"] for d in retrieved_docs]

        query_metrics = {"query": qt.query, "topic": qt.topic}
        for k in k_values:
            m = compute_retrieval_metrics(retrieved_ids, qt.relevant_ids, k)
            query_metrics.update({
                f"precision@{k}": m.precision_at_k,
                f"recall@{k}": m.recall_at_k,
                f"f1@{k}": m.f1_at_k,
            })
            if k == k_values[0]:
                query_metrics["mrr"] = m.mrr

        all_metrics.append(query_metrics)
        per_topic[qt.topic].append(query_metrics)

    # 집계
    def avg(lst: list, key: str) -> float:
        vals = [x[key] for x in lst if key in x]
        return sum(vals) / len(vals) if vals else 0.0

    aggregate_keys = [f"precision@{k}" for k in k_values] + \
                     [f"recall@{k}" for k in k_values] + \
                     [f"f1@{k}" for k in k_values] + ["mrr"]

    summary = {key: round(avg(all_metrics, key), 4) for key in aggregate_keys}
    summary["total_queries"] = len(queries)

    return {"summary": summary, "details": all_metrics}

def compute_retrieval_metrics(retrieved_ids, relevant_ids, k):
    top_k = retrieved_ids[:k]
    hits = [d for d in top_k if d in relevant_ids]
    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    mrr = next((1.0 / (i + 1) for i, d in enumerate(top_k) if d in relevant_ids), 0.0)
    from dataclasses import dataclass
    @dataclass
    class _M:
        precision_at_k: float
        recall_at_k: float
        f1_at_k: float
        mrr: float
    return _M(precision, recall, f1, mrr)
```

---

## 청킹 전략 비교

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

def build_vectorstore(docs: list[Document], chunk_size: int, chunk_overlap: int) -> FAISS:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )
    split_docs = splitter.split_documents(docs)
    # 메타데이터 ID 보존
    for i, doc in enumerate(split_docs):
        if "id" not in doc.metadata:
            doc.metadata["id"] = f"chunk_{i}"

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return FAISS.from_documents(split_docs, embedding)

def compare_chunking_strategies(
    corpus: list[Document],
    queries: list[QueryGroundTruth],
    configs: list[dict],
) -> dict:
    results = {}
    for cfg in configs:
        label = f"chunk={cfg['chunk_size']}_overlap={cfg['chunk_overlap']}"
        vs = build_vectorstore(corpus, cfg["chunk_size"], cfg["chunk_overlap"])
        bench = run_retrieval_benchmark(queries, vs)
        results[label] = bench["summary"]
    return results

if __name__ == "__main__":
    configs = [
        {"chunk_size": 200, "chunk_overlap": 20},
        {"chunk_size": 400, "chunk_overlap": 80},
        {"chunk_size": 800, "chunk_overlap": 160},
    ]

    print("청킹 전략 비교:")
    comparison = compare_chunking_strategies(CORPUS, QUERIES, configs)
    for label, metrics in comparison.items():
        print(f"\n{label}")
        print(json.dumps(metrics, indent=2, ensure_ascii=False))
```

---

## 결과 해석

벤치마크 결과에서 가장 먼저 볼 것은 Recall@K입니다. Recall이 낮다면 관련 문서가 검색 결과에 아예 포함되지 않는 것이고, K를 늘려도 Recall이 늘지 않는다면 임베딩 품질 문제일 가능성이 높습니다.

Precision@1이 낮다면 첫 번째 결과가 신뢰할 수 없다는 의미입니다. 사용자가 첫 번째 결과를 가장 많이 보기 때문에 이 지표가 UX에 직접적인 영향을 줍니다. 리랭킹 레이어를 추가하면 Precision@1을 가장 효과적으로 높일 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG 평가 지표 이해](./01-evaluation-metrics.md)
- **검색 성능 측정 (현재 글)**
- 임베딩 모델 비교 (예정)
- VectorDB 선택 기준 (예정)
- 종단 간 RAG 파이프라인 평가 (예정)
- RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [BEIR 검색 벤치마크](https://github.com/beir-cellar/beir)
- [FAISS 인덱스 가이드](https://faiss.ai/cpp_api/struct/faiss__IndexFlat.html)
- [LangChain 검색기 문서](https://python.langchain.com/docs/modules/data_connection/retrievers/)

Tags: RAG, VectorDB, Benchmarking, LLM
