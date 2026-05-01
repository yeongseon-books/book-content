---
title: 'End-to-end RAG pipeline evaluation'
series: rag-benchmark-101
episode: 5
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

# End-to-end RAG pipeline evaluation

> RAG Benchmark 101 (5/6)

The previous posts evaluated individual components — retriever, embedding model, vector database — in isolation. This post evaluates the full RAG pipeline as a single unit: one evaluation loop measures retrieval metrics and generation metrics simultaneously, from question to answer.

The companion code lives in [`yeongseon-books/rag-benchmark-101/en/05-e2e-evaluation`](https://github.com/yeongseon-books/rag-benchmark-101/tree/main/en/05-e2e-evaluation).

---

## End-to-end evaluation design

Pipeline evaluation is about localizing failure, not just measuring accuracy.

```
question → [retriever] → context → [LLM] → answer
                ↓                      ↓
         retrieval metrics       generation metrics
     (Precision, Recall, MRR)  (Faithfulness, Relevance)
```

---

## Combined evaluator

```python
import json
import os
import re
from dataclasses import dataclass
from typing import Optional

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage
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

def _judge_score(llm: ChatGroq, prompt: str, default: float = 3.0) -> float:
    raw = llm.invoke([HumanMessage(content=prompt)]).content
    try:
        match = re.search(r'"score"\s*:\s*(\d+(?:\.\d+)?)', raw)
        return float(match.group(1)) if match else default
    except Exception:
        return default

FAITHFULNESS_TMPL = """Context: {context}
Answer: {answer}

Rate faithfulness 1-5: are all claims grounded in the context?
Respond only: {{"score": <1-5>}}"""

RELEVANCE_TMPL = """Question: {question}
Answer: {answer}

Rate answer relevance 1-5: does it directly address the question?
Respond only: {{"score": <1-5>}}"""

class EndToEndEvaluator:
    def __init__(self, vectorstore: FAISS, llm: ChatGroq, judge_llm: Optional[ChatGroq] = None, k: int = 3):
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        self.llm = llm
        self.judge = judge_llm or llm
        self.k = k

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer the question using only the context below.\n\nContext: {context}"),
            ("human", "{question}"),
        ])
        self.chain = (
            {"context": self.retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
             "question": RunnablePassthrough()}
            | prompt | self.llm | StrOutputParser()
        )

    def _prm(self, retrieved_ids: list[str], relevant_ids: set[str]) -> tuple[float, float, float]:
        top_k = retrieved_ids[:self.k]
        hits = [d for d in top_k if d in relevant_ids]
        precision = len(hits) / self.k if self.k > 0 else 0.0
        recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
        mrr = next((1.0 / (i + 1) for i, d in enumerate(top_k) if d in relevant_ids), 0.0)
        return precision, recall, mrr

    def evaluate_single(self, question: str, relevant_ids: set[str]) -> EndToEndEvalResult:
        retrieved_docs = self.retriever.invoke(question)
        retrieved_ids = [d.metadata.get("id", "") for d in retrieved_docs]
        context = "\n\n".join(d.page_content for d in retrieved_docs)
        answer = self.chain.invoke(question)

        precision, recall, mrr = self._prm(retrieved_ids, relevant_ids)
        faithfulness = _judge_score(self.judge, FAITHFULNESS_TMPL.format(context=context, answer=answer))
        relevance = _judge_score(self.judge, RELEVANCE_TMPL.format(question=question, answer=answer))

        return EndToEndEvalResult(
            question=question, retrieved_ids=retrieved_ids, relevant_ids=relevant_ids,
            context=context, answer=answer, precision_at_k=precision, recall_at_k=recall,
            mrr=mrr, faithfulness=faithfulness, answer_relevance=relevance,
        )

    def evaluate_suite(self, test_cases: list[dict]) -> dict:
        results = [self.evaluate_single(tc["question"], tc["relevant_ids"]).summary() for tc in test_cases]

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

## Example run

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
    print(json.dumps(evaluator.evaluate_suite(test_cases), indent=2))

if __name__ == "__main__":
    run_e2e_eval()
```

---

## Bottleneck diagnosis

Pipeline score alone does not tell you where to intervene.

- **Low pipeline score + low retrieval score**: retrieval is the bottleneck. Try a better embedding model, increase K, or add hybrid search.
- **Low pipeline score + low generation score**: generation is the bottleneck. Strengthen the system prompt, lower temperature, or switch models.
- **High retrieval score + low faithfulness**: retrieval works but the model ignores context. Add an explicit instruction to stay within the provided context.

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [Comparing embedding models](./03-embedding-comparison.md)
- [VectorDB selection criteria](./04-vectordb-selection.md)
- **End-to-end RAG pipeline evaluation (current)**
- Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [RAGAS comprehensive evaluation](https://docs.ragas.io/en/latest/concepts/metrics/index.html)
- [LangChain RAG evaluation guide](https://python.langchain.com/docs/guides/evaluation/string/criteria_eval_chain)
- [G-Eval paper](https://arxiv.org/abs/2303.16634)

Tags: RAG, VectorDB, Benchmarking, LLM
