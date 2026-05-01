---
title: 'RAG 평가 지표 이해'
series: rag-benchmark-101
episode: 1
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

# RAG 평가 지표 이해

> RAG 벤치마크 101 (1/6)

RAG 파이프라인은 검색과 생성 두 단계로 구성됩니다. 두 단계를 각각 측정하지 않으면 품질 문제의 원인을 파악할 수 없습니다. 검색이 나쁜 건지, 생성이 나쁜 건지, 아니면 둘 다인지 알아야 개선할 수 있습니다. 이 포스트에서는 RAG 평가에 쓰이는 핵심 지표를 구현과 함께 설명합니다.

예제 코드는 [`yeongseon-books/rag-benchmark-101`의 `ko/01-evaluation-metrics`](https://github.com/yeongseon-books/rag-benchmark-101/tree/main/ko/01-evaluation-metrics)에서 확인할 수 있습니다.

---

## RAG 평가의 두 축

RAG 평가는 크게 두 레이어로 나뉩니다.

**검색 품질**: 올바른 문서를 충분히 찾아오는가
- Precision@K: 검색한 K개 중 관련 문서 비율
- Recall@K: 전체 관련 문서 중 검색된 비율
- MRR(Mean Reciprocal Rank): 첫 번째 관련 문서의 순위

**생성 품질**: 찾아온 문서를 잘 활용해서 답하는가
- Faithfulness: 답변이 컨텍스트에 근거하는가
- Answer Relevance: 질문에 직접 답하는가
- Context Precision: 실제로 쓰인 컨텍스트의 비율

---

## 검색 지표 구현

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float
    f1_at_k: float
    mrr: float
    k: int

    def summary(self) -> dict:
        return {
            f"precision@{self.k}": round(self.precision_at_k, 4),
            f"recall@{self.k}": round(self.recall_at_k, 4),
            f"f1@{self.k}": round(self.f1_at_k, 4),
            "mrr": round(self.mrr, 4),
        }

def compute_retrieval_metrics(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int,
) -> RetrievalMetrics:
    """
    retrieved_ids: 검색 결과 (순서 있음)
    relevant_ids: 정답 문서 집합
    k: 평가할 상위 K개
    """
    top_k = retrieved_ids[:k]
    hits = [doc_id for doc_id in top_k if doc_id in relevant_ids]

    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    # MRR: 첫 번째 관련 문서의 역순위
    mrr = 0.0
    for rank, doc_id in enumerate(top_k, start=1):
        if doc_id in relevant_ids:
            mrr = 1.0 / rank
            break

    return RetrievalMetrics(
        precision_at_k=precision,
        recall_at_k=recall,
        f1_at_k=f1,
        mrr=mrr,
        k=k,
    )

# ── 예시 ──────────────────────────────────────────────────────────────────
retrieved = ["doc_3", "doc_1", "doc_5", "doc_2", "doc_7"]
relevant = {"doc_1", "doc_3", "doc_6"}

for k in [1, 3, 5]:
    metrics = compute_retrieval_metrics(retrieved, relevant, k)
    print(f"K={k}: {metrics.summary()}")
```

---

## 생성 지표 구현 (LLM-as-judge)

```python
import json
import os
import re

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

FAITHFULNESS_PROMPT = """주어진 컨텍스트와 답변을 보고 faithfulness를 평가하세요.

Faithfulness: 답변의 모든 주장이 컨텍스트에서 직접 뒷받침되는가?
- 1: 컨텍스트와 무관하거나 반대되는 주장 포함
- 3: 일부만 컨텍스트에 근거
- 5: 모든 주장이 컨텍스트에 기반

컨텍스트: {context}
답변: {answer}

JSON으로 응답: {{"score": <1-5>, "reason": "<이유>"}}"""

RELEVANCE_PROMPT = """주어진 질문과 답변을 보고 answer relevance를 평가하세요.

Answer Relevance: 답변이 질문에 직접적으로 답하는가?
- 1: 질문과 무관
- 3: 부분적으로 답변
- 5: 질문에 완전히 답변

질문: {question}
답변: {answer}

JSON으로 응답: {{"score": <1-5>, "reason": "<이유>"}}"""

@dataclass
class GenerationMetrics:
    faithfulness: float
    answer_relevance: float
    faithfulness_reason: str = ""
    answer_relevance_reason: str = ""

    @property
    def average(self) -> float:
        return (self.faithfulness + self.answer_relevance) / 2

    def summary(self) -> dict:
        return {
            "faithfulness": round(self.faithfulness, 2),
            "answer_relevance": round(self.answer_relevance, 2),
            "average": round(self.average, 2),
        }

def _parse_score(raw: str, default: float = 3.0) -> tuple[float, str]:
    try:
        match = re.search(r"\{[^}]+\}", raw, re.DOTALL)
        if not match:
            return default, ""
        data = json.loads(match.group())
        return float(data.get("score", default)), data.get("reason", "")
    except Exception:
        return default, ""

def evaluate_generation(
    question: str,
    context: str,
    answer: str,
    llm: Optional[ChatGroq] = None,
) -> GenerationMetrics:
    if llm is None:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.environ["GROQ_API_KEY"],
            temperature=0.0,
        )

    # Faithfulness 평가
    f_prompt = FAITHFULNESS_PROMPT.format(context=context, answer=answer)
    f_raw = llm.invoke([HumanMessage(content=f_prompt)]).content
    f_score, f_reason = _parse_score(f_raw)

    # Answer Relevance 평가
    r_prompt = RELEVANCE_PROMPT.format(question=question, answer=answer)
    r_raw = llm.invoke([HumanMessage(content=r_prompt)]).content
    r_score, r_reason = _parse_score(r_raw)

    return GenerationMetrics(
        faithfulness=f_score,
        answer_relevance=r_score,
        faithfulness_reason=f_reason,
        answer_relevance_reason=r_reason,
    )
```

---

## 종합 평가 예시

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

def run_rag_eval_demo():
    # 테스트 문서
    docs = [
        Document(page_content="FAISS는 Facebook AI가 개발한 고밀도 벡터 검색 라이브러리입니다.", metadata={"id": "doc_1"}),
        Document(page_content="FAISS는 수십억 개의 벡터를 밀리초 단위로 검색할 수 있습니다.", metadata={"id": "doc_2"}),
        Document(page_content="Chroma는 임베딩 기반 문서 저장과 검색을 위한 오픈소스 벡터 DB입니다.", metadata={"id": "doc_3"}),
        Document(page_content="벡터 인덱스는 ANN(근사 최근접 이웃) 알고리즘을 사용합니다.", metadata={"id": "doc_4"}),
    ]

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(docs, embedding)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    question = "FAISS란 무엇인가요?"
    relevant_ids = {"doc_1", "doc_2"}

    # 검색 수행
    retrieved_docs = retriever.invoke(question)
    retrieved_ids = [d.metadata["id"] for d in retrieved_docs]
    context = "\n".join(d.page_content for d in retrieved_docs)

    # 검색 지표
    retrieval = compute_retrieval_metrics(retrieved_ids, relevant_ids, k=3)
    print("=== 검색 지표 ===")
    print(json.dumps(retrieval.summary(), indent=2, ensure_ascii=False))

    # 답변 생성
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    answer = llm.invoke([
        HumanMessage(content=f"컨텍스트:\n{context}\n\n질문: {question}"),
    ]).content

    # 생성 지표
    generation = evaluate_generation(question, context, answer, llm)
    print("\n=== 생성 지표 ===")
    print(json.dumps(generation.summary(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_rag_eval_demo()
```

---

## 지표 해석 가이드

| 지표 | 낮은 경우 원인 | 개선 방법 |
|------|-------------|---------|
| Precision@K | 관련 없는 문서 검색 | 청킹 개선, 임베딩 모델 교체 |
| Recall@K | 관련 문서 누락 | K 증가, 하이브리드 검색 도입 |
| MRR | 관련 문서 순위 낮음 | 리랭킹 추가 |
| Faithfulness | 모델 환각 | 시스템 프롬프트 강화, 컨텍스트 품질 개선 |
| Answer Relevance | 질문 이탈 | 프롬프트 개선, temperature 낮춤 |

검색 지표와 생성 지표를 따로 추적하면 병목을 빠르게 찾을 수 있습니다. Precision@K가 낮은데 Faithfulness가 높다면 검색 문제입니다. 반대라면 프롬프트나 모델 문제입니다.

<!-- toc:begin -->
## 시리즈 목차

- **RAG 평가 지표 이해 (현재 글)**
- 검색 성능 측정 (예정)
- 임베딩 모델 비교 (예정)
- VectorDB 선택 기준 (예정)
- 종단 간 RAG 파이프라인 평가 (예정)
- RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [RAGAS 평가 프레임워크](https://docs.ragas.io/)
- [BEIR 벤치마크](https://github.com/beir-cellar/beir)
- [TREC 평가 메트릭](https://trec.nist.gov/)

Tags: RAG, VectorDB, Benchmarking, LLM
