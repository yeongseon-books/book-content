---
title: 'Understanding RAG evaluation metrics'
series: rag-benchmark-101
episode: 1
language: en
status: publish-ready
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

## Questions this post answers
- What does each of Precision@k, Recall@k, and MRR reveal?
- How should you read per-query scores versus benchmark averages?
- Why does calculating the metrics by hand make RAG debugging easier?

> RAG evaluation is not about memorizing metric names; it is about dissecting where ranking failed on each query.

The first post starts with the smallest retrieval unit. Before jumping to LLM-based evaluation, you need to be able to compute Precision@k, Recall@k, and MRR from a ranked list and a gold set. The companion example does exactly that with plain Python.

```mermaid
flowchart LR
    Q[Query set] --> R[Ranked results]
    G[Gold relevant documents] --> C[Metric calculation]
    R --> C
    C --> P[Precision@k]
    C --> RC[Recall@k]
    C --> M[MRR]
```

## Minimal runnable example

The runnable code lives in `rag-benchmark-101/en/01-evaluation-metrics/main.py`. Episodes 05 and 06 require `GROQ_API_KEY`.

```bash
cd /root/Github/rag-benchmark-101/en/01-evaluation-metrics
python3 main.py
```

```python
from dataclasses import dataclass

@dataclass
class QueryCase:
    question: str
    retrieved_ids: list[str]
    relevant_ids: set[str]

for case in cases:
    metrics = evaluate_case(case, k=3)
    print(case.question, metrics.as_dict())
```

## What to notice in this code
- The script evaluates only `retrieved_ids[:k]`, which keeps the metric definition honest.
- Separating Precision@k from Recall@k helps you distinguish “too broad” from “too narrow” retrieval.
- MRR tracks how early the first relevant hit appears, so it maps well to first-page retrieval UX.

## Where engineers get confused
- A high Precision@k can still hide poor Recall@k if the retriever finds only one of many relevant passages.
- MRR ignores what happens after the first relevant hit, so it cannot stand in for overall top-k quality.
- With only a few queries, an average can hide a catastrophic miss. Keep the per-query printout.

## Checklist
- [ ] Define a gold relevant-document set for each query.
- [ ] Use the same k in both the code and the report.
- [ ] Review per-query outputs alongside the benchmark average.

<!-- blog-only:start -->

## Summary

Now the retrieval metrics are grounded in actual numbers. The next post attaches the same metrics to a real FAISS retriever and measures hit rate and MRR.

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

- [Wikipedia: Mean reciprocal rank](https://en.wikipedia.org/wiki/Mean_reciprocal_rank)
- [Stanford IR book: Evaluation in information retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)

Tags: RAG, VectorDB, Benchmarking, LLM
