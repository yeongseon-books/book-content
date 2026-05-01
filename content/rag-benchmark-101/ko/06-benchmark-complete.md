---
title: 'RAG 벤치마크 완성'
series: rag-benchmark-101
episode: 6
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

# RAG 벤치마크 완성

> RAG 벤치마크 101 (6/6)

이 시리즈에서 다룬 평가 지표, 검색 벤치마크, 임베딩 비교, VectorDB 선택, 종단 간 평가를 하나의 완전한 벤치마크 파이프라인으로 통합합니다. 서로 다른 RAG 구성을 체계적으로 비교하고 최적 설정을 찾는 프레임워크를 만듭니다.

예제 코드는 [`yeongseon-books/rag-benchmark-101`의 `ko/06-benchmark-complete`](https://github.com/yeongseon-books/rag-benchmark-101/tree/main/ko/06-benchmark-complete)에서 확인할 수 있습니다.

---

## 완전한 RAG 벤치마크 프레임워크

```python
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Optional

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── 설정 ──────────────────────────────────────────────────────────────────
@dataclass
class RAGConfig:
    name: str
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 400
    chunk_overlap: int = 80
    k: int = 3
    temperature: float = 0.0
    llm_model: str = "llama-3.1-8b-instant"

# ── 지표 ──────────────────────────────────────────────────────────────────
@dataclass
class BenchmarkResult:
    config_name: str
    precision_at_k: float
    recall_at_k: float
    mrr: float
    faithfulness: float
    answer_relevance: float
    avg_latency_ms: float
    total_queries: int

    @property
    def retrieval_score(self) -> float:
        return (self.precision_at_k + self.recall_at_k + self.mrr) / 3

    @property
    def generation_score(self) -> float:
        return (self.faithfulness + self.answer_relevance) / 2

    @property
    def overall_score(self) -> float:
        return (self.retrieval_score + self.generation_score) / 2

    def summary(self) -> dict:
        return {
            "config": self.config_name,
            "overall_score": round(self.overall_score, 3),
            "retrieval_score": round(self.retrieval_score, 3),
            "generation_score": round(self.generation_score, 3),
            "precision@k": round(self.precision_at_k, 3),
            "recall@k": round(self.recall_at_k, 3),
            "mrr": round(self.mrr, 3),
            "faithfulness": round(self.faithfulness, 3),
            "answer_relevance": round(self.answer_relevance, 3),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "total_queries": self.total_queries,
        }

# ── 유틸 ──────────────────────────────────────────────────────────────────
def _prm(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> tuple[float, float, float]:
    top_k = retrieved_ids[:k]
    hits = [d for d in top_k if d in relevant_ids]
    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    mrr = next((1.0 / (i + 1) for i, d in enumerate(top_k) if d in relevant_ids), 0.0)
    return precision, recall, mrr

def _judge(llm: ChatGroq, prompt: str) -> float:
    raw = llm.invoke([HumanMessage(content=prompt)]).content
    try:
        m = re.search(r'"score"\s*:\s*(\d+(?:\.\d+)?)', raw)
        return float(m.group(1)) if m else 3.0
    except Exception:
        return 3.0

# ── 메인 벤치마크 ──────────────────────────────────────────────────────────
class RAGBenchmark:
    FAITHFULNESS_TMPL = "Context: {context}\nAnswer: {answer}\n\nRate faithfulness 1-5 (grounded in context?)\nJSON only: {{\"score\": <1-5>}}"
    RELEVANCE_TMPL = "Question: {question}\nAnswer: {answer}\n\nRate answer relevance 1-5 (directly answers?)\nJSON only: {{\"score\": <1-5>}}"
    RAG_TMPL = "Answer using only the context below. If absent, say so.\n\nContext: {context}\n\nQuestion: {question}"

    def __init__(self, corpus: list[Document], test_cases: list[dict]):
        self.corpus = corpus
        self.test_cases = test_cases

    def _build_vectorstore(self, config: RAGConfig) -> FAISS:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " "],
        )
        chunks = splitter.split_documents(self.corpus)
        for i, doc in enumerate(chunks):
            if "id" not in doc.metadata:
                doc.metadata["id"] = f"chunk_{i}"

        embedding = HuggingFaceEmbeddings(
            model_name=config.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        return FAISS.from_documents(chunks, embedding)

    def run(self, config: RAGConfig) -> BenchmarkResult:
        vectorstore = self._build_vectorstore(config)
        retriever = vectorstore.as_retriever(search_kwargs={"k": config.k})
        llm = ChatGroq(
            model=config.llm_model,
            api_key=os.environ["GROQ_API_KEY"],
            temperature=config.temperature,
        )

        precisions, recalls, mrrs = [], [], []
        faithfulness_scores, relevance_scores = [], []
        latencies = []

        for tc in self.test_cases:
            question = tc["question"]
            relevant_ids = tc["relevant_ids"]

            t0 = time.perf_counter()
            retrieved_docs = retriever.invoke(question)
            retrieved_ids = [d.metadata.get("id", "") for d in retrieved_docs]
            context = "\n\n".join(d.page_content for d in retrieved_docs)
            answer = llm.invoke([HumanMessage(content=self.RAG_TMPL.format(context=context, question=question))]).content
            latencies.append((time.perf_counter() - t0) * 1000)

            p, r, m = _prm(retrieved_ids, relevant_ids, config.k)
            precisions.append(p)
            recalls.append(r)
            mrrs.append(m)

            faithfulness_scores.append(_judge(llm, self.FAITHFULNESS_TMPL.format(context=context, answer=answer)))
            relevance_scores.append(_judge(llm, self.RELEVANCE_TMPL.format(question=question, answer=answer)))

        def avg(lst): return sum(lst) / len(lst) if lst else 0.0

        return BenchmarkResult(
            config_name=config.name,
            precision_at_k=avg(precisions),
            recall_at_k=avg(recalls),
            mrr=avg(mrrs),
            faithfulness=avg(faithfulness_scores),
            answer_relevance=avg(relevance_scores),
            avg_latency_ms=avg(latencies),
            total_queries=len(self.test_cases),
        )

    def compare(self, configs: list[RAGConfig]) -> list[dict]:
        results = []
        for config in configs:
            print(f"평가 중: {config.name} ...")
            result = self.run(config)
            results.append(result.summary())
        return sorted(results, key=lambda x: x["overall_score"], reverse=True)
```

---

## 실행 예시

```python
from rag_benchmark_post2 import CORPUS, QUERIES

TEST_CASES = [
    {"question": "What is FAISS?", "relevant_ids": {"d02", "d03"}},
    {"question": "How do embedding models work?", "relevant_ids": {"d06", "d07"}},
    {"question": "What is hybrid search?", "relevant_ids": {"d09"}},
    {"question": "What is cosine similarity?", "relevant_ids": {"d04"}},
]

CONFIGS = [
    RAGConfig("baseline", chunk_size=400, chunk_overlap=80, k=3),
    RAGConfig("small-chunks", chunk_size=200, chunk_overlap=20, k=3),
    RAGConfig("large-k", chunk_size=400, chunk_overlap=80, k=5),
    RAGConfig("mpnet", embedding_model="sentence-transformers/all-mpnet-base-v2", chunk_size=400, k=3),
]

if __name__ == "__main__":
    bench = RAGBenchmark(CORPUS, TEST_CASES)
    results = bench.compare(CONFIGS)

    print("\n=== RAG 벤치마크 결과 (overall_score 기준 내림차순) ===")
    for i, r in enumerate(results, 1):
        print(f"\n{i}위: {r['config']}")
        print(json.dumps(r, indent=2, ensure_ascii=False))
```

---

## 시리즈 마무리

이 시리즈에서 구축한 평가 체계는 세 레이어로 구성됩니다.

- **지표 레이어**: Precision, Recall, MRR, Faithfulness, Answer Relevance
- **구성 요소 레이어**: 임베딩 모델 비교, VectorDB 선택, 청킹 전략
- **파이프라인 레이어**: 종단 간 평가와 설정 비교

이 프레임워크를 쓰면 모델 교체, 청킹 변경, 프롬프트 수정 중 어느 것이 가장 효과적인지 데이터로 결정할 수 있습니다. RAG 품질 개선은 직관이 아니라 측정에서 시작합니다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [검색 성능 측정](./02-retrieval-benchmarking.md)
- [임베딩 모델 비교](./03-embedding-comparison.md)
- [VectorDB 선택 기준](./04-vectordb-selection.md)
- [종단 간 RAG 파이프라인 평가](./05-e2e-evaluation.md)
- **RAG 벤치마크 완성 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [RAGAS 프레임워크](https://docs.ragas.io/)
- [BEIR 벤치마크](https://github.com/beir-cellar/beir)
- [LangChain 평가 모듈](https://python.langchain.com/docs/guides/evaluation/)

Tags: RAG, VectorDB, Benchmarking, LLM
