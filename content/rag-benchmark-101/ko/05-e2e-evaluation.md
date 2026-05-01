---
title: '종단 간 RAG 파이프라인 평가'
series: rag-benchmark-101
episode: 5
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

# 종단 간 RAG 파이프라인 평가

> RAG 벤치마크 101 (5/6)

지금까지 개별 구성 요소(검색기, 임베딩, VectorDB)를 각각 평가했습니다. 이 포스트에서는 전체 RAG 파이프라인을 하나의 단위로 평가하는 방법을 다룹니다. 입력(질문)부터 출력(답변)까지 한 번의 평가 루프로 검색 지표와 생성 지표를 동시에 측정합니다.

예제 코드는 [`yeongseon-books/rag-benchmark-101`의 `ko/05-e2e-evaluation`](https://github.com/yeongseon-books/rag-benchmark-101/tree/main/ko/05-e2e-evaluation)에서 확인할 수 있습니다.

---

## 종단 간 평가 설계

RAG 파이프라인 평가는 단순히 정확도를 측정하는 것이 아닙니다. 어느 단계에서 손실이 발생하는지 파악해야 합니다.

```
질문 → [검색기] → 컨텍스트 → [LLM] → 답변
         ↓                          ↓
    검색 지표                   생성 지표
(Precision, Recall, MRR)  (Faithfulness, Relevance)
```

---

## 종합 평가 클래스

```python
import json
import os
from dataclasses import dataclass, field
from typing import Optional

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

@dataclass
class EndToEndEvalResult:
    question: str
    retrieved_ids: list[str]
    relevant_ids: set[str]
    context: str
    answer: str
    precision_at_k: float
    recall_at_k: float
    mrr: float
    faithfulness: float
    answer_relevance: float

    @property
    def retrieval_score(self) -> float:
        return (self.precision_at_k + self.recall_at_k + self.mrr) / 3

    @property
    def generation_score(self) -> float:
        return (self.faithfulness + self.answer_relevance) / 2

    @property
    def pipeline_score(self) -> float:
        return (self.retrieval_score + self.generation_score) / 2

    def summary(self) -> dict:
        return {
            "question": self.question[:60],
            "retrieval": {
                "precision@k": round(self.precision_at_k, 3),
                "recall@k": round(self.recall_at_k, 3),
                "mrr": round(self.mrr, 3),
                "score": round(self.retrieval_score, 3),
            },
            "generation": {
                "faithfulness": round(self.faithfulness, 3),
                "answer_relevance": round(self.answer_relevance, 3),
                "score": round(self.generation_score, 3),
            },
            "pipeline_score": round(self.pipeline_score, 3),
        }

import re

def _judge_score(llm: ChatGroq, prompt: str, default: float = 3.0) -> float:
    raw = llm.invoke([HumanMessage(content=prompt)]).content
    try:
        match = re.search(r'"score"\s*:\s*(\d+(?:\.\d+)?)', raw)
        return float(match.group(1)) if match else default
    except Exception:
        return default

FAITHFULNESS_TMPL = """Context: {context}
Answer: {answer}

Rate faithfulness 1-5: all claims grounded in context?
Respond only: {{"score": <1-5>}}"""

RELEVANCE_TMPL = """Question: {question}
Answer: {answer}

Rate answer relevance 1-5: directly addresses the question?
Respond only: {{"score": <1-5>}}"""

class EndToEndEvaluator:
    def __init__(
        self,
        vectorstore: FAISS,
        llm: ChatGroq,
        judge_llm: Optional[ChatGroq] = None,
        k: int = 3,
    ):
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        self.llm = llm
        self.judge = judge_llm or llm
        self.k = k
        self._build_chain()

    def _build_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer the question using only the context below. If the answer is not in the context, say so.\n\nContext: {context}"),
            ("human", "{question}"),
        ])

        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)

        self.chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def _retrieval_metrics(self, retrieved_ids: list[str], relevant_ids: set[str]) -> tuple[float, float, float]:
        top_k = retrieved_ids[:self.k]
        hits = [d for d in top_k if d in relevant_ids]
        precision = len(hits) / self.k if self.k > 0 else 0.0
        recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
        mrr = next((1.0 / (i + 1) for i, d in enumerate(top_k) if d in relevant_ids), 0.0)
        return precision, recall, mrr

    def evaluate_single(self, question: str, relevant_ids: set[str]) -> EndToEndEvalResult:
        # 검색
        retrieved_docs = self.retriever.invoke(question)
        retrieved_ids = [d.metadata.get("id", "") for d in retrieved_docs]
        context = "\n\n".join(d.page_content for d in retrieved_docs)

        # 생성
        answer = self.chain.invoke(question)

        # 검색 지표
        precision, recall, mrr = self._retrieval_metrics(retrieved_ids, relevant_ids)

        # 생성 지표
        faithfulness = _judge_score(
            self.judge, FAITHFULNESS_TMPL.format(context=context, answer=answer)
        )
        relevance = _judge_score(
            self.judge, RELEVANCE_TMPL.format(question=question, answer=answer)
        )

        return EndToEndEvalResult(
            question=question,
            retrieved_ids=retrieved_ids,
            relevant_ids=relevant_ids,
            context=context,
            answer=answer,
            precision_at_k=precision,
            recall_at_k=recall,
            mrr=mrr,
            faithfulness=faithfulness,
            answer_relevance=relevance,
        )

    def evaluate_suite(self, test_cases: list[dict]) -> dict:
        results = []
        for tc in test_cases:
            result = self.evaluate_single(tc["question"], tc["relevant_ids"])
            results.append(result.summary())

        def avg(key_path: list[str]) -> float:
            vals = []
            for r in results:
                obj = r
                for k in key_path:
                    obj = obj.get(k, {})
                if isinstance(obj, (int, float)):
                    vals.append(obj)
            return round(sum(vals) / len(vals), 3) if vals else 0.0

        return {
            "total": len(results),
            "avg_pipeline_score": avg(["pipeline_score"]),
            "avg_precision": avg(["retrieval", "precision@k"]),
            "avg_recall": avg(["retrieval", "recall@k"]),
            "avg_faithfulness": avg(["generation", "faithfulness"]),
            "avg_relevance": avg(["generation", "answer_relevance"]),
            "details": results,
        }
```

---

## 실행 예시

```python
def run_e2e_eval():
    from rag_benchmark_post2 import CORPUS

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(CORPUS, embedding)
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)

    evaluator = EndToEndEvaluator(vectorstore, llm, k=3)

    test_cases = [
        {"question": "What is FAISS?", "relevant_ids": {"d02", "d03"}},
        {"question": "How do embedding models work?", "relevant_ids": {"d06", "d07"}},
        {"question": "What is hybrid search?", "relevant_ids": {"d09"}},
    ]

    report = evaluator.evaluate_suite(test_cases)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run_e2e_eval()
```

---

## 병목 진단 가이드

종단 간 평가 결과로 다음 진단을 할 수 있습니다.

- **pipeline_score 낮음 + retrieval.score 낮음**: 검색이 병목. 임베딩 모델 교체, K 증가, 하이브리드 검색 도입을 검토합니다.
- **pipeline_score 낮음 + generation.score 낮음**: 생성이 병목. 시스템 프롬프트 강화, temperature 조정, LLM 교체를 검토합니다.
- **retrieval.score 높음 + generation.faithfulness 낮음**: 검색은 잘 되지만 모델이 컨텍스트를 무시함. 프롬프트에 컨텍스트 의존성 명시가 필요합니다.

<!-- blog-only:start -->
다음 글: [RAG 벤치마크 완성](./06-benchmark-complete.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [검색 성능 측정](./02-retrieval-benchmarking.md)
- [임베딩 모델 비교](./03-embedding-comparison.md)
- [VectorDB 선택 기준](./04-vectordb-selection.md)
- **종단 간 RAG 파이프라인 평가 (현재 글)**
- RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [RAGAS 종합 평가](https://docs.ragas.io/en/latest/concepts/metrics/index.html)
- [LangChain RAG 평가 가이드](https://python.langchain.com/docs/guides/evaluation/string/criteria_eval_chain)
- [G-Eval 논문](https://arxiv.org/abs/2303.16634)

Tags: RAG, VectorDB, Benchmarking, LLM
