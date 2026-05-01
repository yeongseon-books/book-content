---
title: 'Completing the RAG benchmark'
series: rag-benchmark-101
episode: 6
language: en
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

# Completing the RAG benchmark

> RAG Benchmark 101 (6/6)

This post assembles the evaluation metrics, retrieval benchmark, embedding comparison, VectorDB selection, and end-to-end evaluation from across the series into one complete benchmark pipeline. The result is a framework for systematically comparing RAG configurations and finding the optimal setup.

The companion code lives in [`yeongseon-books/rag-benchmark-101/en/06-benchmark-complete`](https://github.com/yeongseon-books/rag-benchmark-101/tree/main/en/06-benchmark-complete).

---

<!-- ebook-only:start -->

**The key idea**: benchmarks must be reproducible. Fix the dataset, model versions, and parameters, and automate the experiment so comparisons are meaningful.

## Where this chapter fits

This is chapter 6 of 6 in the series.
The previous chapter covered **End-to-end RAG pipeline evaluation**.
<!-- ebook-only:end -->

## Complete RAG benchmark framework

```python
import json
import os
import re
import time
from dataclasses import dataclass

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── config ─────────────────────────────────────────────────────────────────
@dataclass
class RAGConfig:
    name: str
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 400
    chunk_overlap: int = 80
    k: int = 3
    temperature: float = 0.0
    llm_model: str = "llama-3.1-8b-instant"

# ── result ─────────────────────────────────────────────────────────────────
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

# ── helpers ─────────────────────────────────────────────────────────────────
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

# ── benchmark ───────────────────────────────────────────────────────────────
class RAGBenchmark:
    FAITHFULNESS = "Context: {context}\nAnswer: {answer}\n\nRate faithfulness 1-5. JSON only: {{\"score\": <1-5>}}"
    RELEVANCE = "Question: {question}\nAnswer: {answer}\n\nRate answer relevance 1-5. JSON only: {{\"score\": <1-5>}}"
    RAG = "Answer using only the context below. If absent, say so.\n\nContext: {context}\n\nQuestion: {question}"

    def __init__(self, corpus: list[Document], test_cases: list[dict]):
        self.corpus = corpus
        self.test_cases = test_cases

    def _build_vectorstore(self, config: RAGConfig) -> FAISS:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap,
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
        llm = ChatGroq(model=config.llm_model, api_key=os.environ["GROQ_API_KEY"], temperature=config.temperature)

        precisions, recalls, mrrs, faiths, rels, lats = [], [], [], [], [], []
        for tc in self.test_cases:
            q, rel_ids = tc["question"], tc["relevant_ids"]
            t0 = time.perf_counter()
            docs = retriever.invoke(q)
            context = "\n\n".join(d.page_content for d in docs)
            answer = llm.invoke([HumanMessage(content=self.RAG.format(context=context, question=q))]).content
            lats.append((time.perf_counter() - t0) * 1000)

            p, r, m = _prm([d.metadata.get("id", "") for d in docs], rel_ids, config.k)
            precisions.append(p); recalls.append(r); mrrs.append(m)
            faiths.append(_judge(llm, self.FAITHFULNESS.format(context=context, answer=answer)))
            rels.append(_judge(llm, self.RELEVANCE.format(question=q, answer=answer)))

        avg = lambda lst: sum(lst) / len(lst) if lst else 0.0
        return BenchmarkResult(
            config_name=config.name, precision_at_k=avg(precisions), recall_at_k=avg(recalls),
            mrr=avg(mrrs), faithfulness=avg(faiths), answer_relevance=avg(rels),
            avg_latency_ms=avg(lats), total_queries=len(self.test_cases),
        )

    def compare(self, configs: list[RAGConfig]) -> list[dict]:
        results = []
        for config in configs:
            print(f"evaluating {config.name} ...")
            results.append(self.run(config).summary())
        return sorted(results, key=lambda x: x["overall_score"], reverse=True)
```

---

## Example run

```python
from rag_benchmark_post2 import CORPUS

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
    RAGConfig("mpnet", embedding_model="sentence-transformers/all-mpnet-base-v2", k=3),
]

if __name__ == "__main__":
    bench = RAGBenchmark(CORPUS, TEST_CASES)
    results = bench.compare(CONFIGS)
    print("\n=== RAG benchmark results (ranked by overall score) ===")
    for i, r in enumerate(results, 1):
        print(f"\n#{i}: {r['config']}")
        print(json.dumps(r, indent=2))
```

---

## Series summary

The evaluation framework built across this series has three layers.

The **metrics layer** defines what to measure: Precision, Recall, MRR for retrieval; Faithfulness and Answer Relevance for generation.

The **component layer** benchmarks individual pieces in isolation: embedding model comparison, VectorDB selection, chunking strategy.

The **pipeline layer** ties it together: end-to-end evaluation and multi-config comparison surface which change delivers the highest overall score improvement.

With this framework, decisions about model swaps, chunking changes, and prompt revisions are driven by data, not intuition.

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [Comparing embedding models](./03-embedding-comparison.md)
- [VectorDB selection criteria](./04-vectordb-selection.md)
- [End-to-end RAG pipeline evaluation](./05-e2e-evaluation.md)
- **Completing the RAG benchmark (current)**

<!-- toc:end -->

---

## References

- [RAGAS framework](https://docs.ragas.io/)
- [BEIR benchmark](https://github.com/beir-cellar/beir)
- [LangChain evaluation module](https://python.langchain.com/docs/guides/evaluation/)

Tags: RAG, VectorDB, Benchmarking, LLM
