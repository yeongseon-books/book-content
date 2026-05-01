---
title: 'Understanding RAG evaluation metrics'
series: rag-benchmark-101
episode: 1
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

# Understanding RAG evaluation metrics

> RAG Benchmark 101 (1/6)

A RAG pipeline has two distinct stages: retrieval and generation. Without measuring each stage separately, you cannot diagnose quality problems. Is retrieval returning the wrong documents? Is the model ignoring what it retrieved? You need to know before you can fix anything. This post covers the core RAG evaluation metrics and implements them from scratch.

The companion code lives in [`yeongseon-books/rag-benchmark-101/en/01-evaluation-metrics`](https://github.com/yeongseon-books/rag-benchmark-101/tree/main/en/01-evaluation-metrics).

---

## Two evaluation layers

RAG evaluation splits across two layers.

**Retrieval quality**: does the system fetch the right documents?
- Precision@K: fraction of the top-K results that are relevant
- Recall@K: fraction of all relevant documents that appear in the top K
- MRR (Mean Reciprocal Rank): rank of the first relevant result

**Generation quality**: does the model use retrieved context correctly?
- Faithfulness: are all claims in the answer grounded in the retrieved context?
- Answer relevance: does the answer directly address the question?
- Context precision: what fraction of retrieved context was actually used?

---

## Retrieval metrics

```python
from dataclasses import dataclass

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
    top_k = retrieved_ids[:k]
    hits = [doc_id for doc_id in top_k if doc_id in relevant_ids]

    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    mrr = 0.0
    for rank, doc_id in enumerate(top_k, start=1):
        if doc_id in relevant_ids:
            mrr = 1.0 / rank
            break

    return RetrievalMetrics(precision_at_k=precision, recall_at_k=recall, f1_at_k=f1, mrr=mrr, k=k)

# example
retrieved = ["doc_3", "doc_1", "doc_5", "doc_2", "doc_7"]
relevant = {"doc_1", "doc_3", "doc_6"}

for k in [1, 3, 5]:
    metrics = compute_retrieval_metrics(retrieved, relevant, k)
    print(f"K={k}: {metrics.summary()}")
```

---

## Generation metrics (LLM-as-judge)

```python
import json
import os
import re
from typing import Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

FAITHFULNESS_PROMPT = """Evaluate faithfulness for the given context and answer.

Faithfulness: are all claims in the answer directly supported by the context?
- 1: contains claims contradicted by or absent from the context
- 3: some claims are grounded, others are not
- 5: every claim is directly supported by the context

Context: {context}
Answer: {answer}

Respond with JSON only: {{"score": <1-5>, "reason": "<one sentence>"}}"""

RELEVANCE_PROMPT = """Evaluate answer relevance for the given question and answer.

Answer Relevance: does the answer directly address the question?
- 1: unrelated to the question
- 3: partially answers
- 5: fully and directly answers the question

Question: {question}
Answer: {answer}

Respond with JSON only: {{"score": <1-5>, "reason": "<one sentence>"}}"""

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
        llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)

    f_raw = llm.invoke([HumanMessage(content=FAITHFULNESS_PROMPT.format(context=context, answer=answer))]).content
    f_score, f_reason = _parse_score(f_raw)

    r_raw = llm.invoke([HumanMessage(content=RELEVANCE_PROMPT.format(question=question, answer=answer))]).content
    r_score, r_reason = _parse_score(r_raw)

    return GenerationMetrics(faithfulness=f_score, answer_relevance=r_score,
                             faithfulness_reason=f_reason, answer_relevance_reason=r_reason)
```

---

## End-to-end evaluation demo

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

def run_rag_eval_demo():
    docs = [
        Document(page_content="FAISS is a high-density vector search library developed by Facebook AI.", metadata={"id": "doc_1"}),
        Document(page_content="FAISS can search billions of vectors in milliseconds.", metadata={"id": "doc_2"}),
        Document(page_content="Chroma is an open-source vector database for embedding-based document retrieval.", metadata={"id": "doc_3"}),
        Document(page_content="Vector indexes use ANN (approximate nearest neighbor) algorithms.", metadata={"id": "doc_4"}),
    ]

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(docs, embedding)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    question = "What is FAISS?"
    relevant_ids = {"doc_1", "doc_2"}

    retrieved_docs = retriever.invoke(question)
    retrieved_ids = [d.metadata["id"] for d in retrieved_docs]
    context = "\n".join(d.page_content for d in retrieved_docs)

    retrieval = compute_retrieval_metrics(retrieved_ids, relevant_ids, k=3)
    print("=== retrieval metrics ===")
    print(json.dumps(retrieval.summary(), indent=2))

    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"], temperature=0.0)
    answer = llm.invoke([HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}")]).content

    generation = evaluate_generation(question, context, answer, llm)
    print("\n=== generation metrics ===")
    print(json.dumps(generation.summary(), indent=2))

if __name__ == "__main__":
    run_rag_eval_demo()
```

---

## Interpreting results

Tracking retrieval and generation metrics separately surfaces bottlenecks fast. High Precision@K with low Faithfulness points to a prompting or model problem. Low Precision@K with high Faithfulness means retrieval is the bottleneck. Fixing the wrong layer wastes time.

MRR captures ranking quality: a relevant document at rank 1 scores 1.0; at rank 3 it scores 0.33. When MRR is low, adding a re-ranker after initial retrieval is usually the highest-ROI intervention.

<!-- blog-only:start -->
Next: [Measuring retrieval performance](./02-retrieval-benchmarking.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- **Understanding RAG evaluation metrics (current)**
- Measuring retrieval performance (upcoming)
- Comparing embedding models (upcoming)
- VectorDB selection criteria (upcoming)
- End-to-end RAG pipeline evaluation (upcoming)
- Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [RAGAS evaluation framework](https://docs.ragas.io/)
- [BEIR benchmark](https://github.com/beir-cellar/beir)
- [TREC evaluation metrics](https://trec.nist.gov/)

Tags: RAG, VectorDB, Benchmarking, LLM
