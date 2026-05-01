---
title: 'Completing the RAG benchmark'
series: rag-benchmark-101
episode: 6
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

# Completing the RAG benchmark

## Questions this post answers
- How do you package dataset, retrieval, generation, and evaluation into one executable benchmark?
- How should retrieval metrics and RAGAS scores be separated in one report?
- Which experiment settings must be fixed first in a full pipeline benchmark?

> A complete RAG benchmark is not one magic score; it is a reproducible pipeline that reports retrieval and generation separately under fixed conditions.

The final post connects all the earlier pieces. A FAISS retriever finds the evidence, Groq generates the answer from that context, and the script aggregates both retrieval metrics and RAGAS scores. That gives you one run log where you can separate search failures from answer-generation failures.

![Questions this post answers](../../../assets/rag-benchmark-101/06/06-01-questions-this-post-answers.en.png)
## Minimal runnable example

The runnable code lives in `rag-benchmark-101/en/06-benchmark-complete/main.py`. Episodes 05 and 06 require `GROQ_API_KEY`.

```bash
cd /root/Github/rag-benchmark-101/en/06-benchmark-complete
export GROQ_API_KEY=... && python3 main.py
```

```python
for case in TEST_CASES:
    docs = retriever.invoke(case['question'])
    answer = chain.invoke({'question': case['question'], 'context': context})
    rows.append({'question': case['question'], 'answer': answer, 'contexts': [doc.page_content for doc in docs]})

ragas_result = evaluate(dataset=Dataset.from_list(rows), ...)
```

## What to notice in this code
- Keep retrieval and generation in separate report sections so bottlenecks remain obvious.
- Logging retrieved IDs together with the final answer makes failure analysis much faster.
- A full pipeline benchmark is only meaningful when corpus, embedding model, top-k, and LLM are fixed.

## Where engineers get confused
- Low faithfulness does not always mean the LLM failed; the retriever may have supplied the wrong evidence.
- Strong retrieval can still produce low answer relevancy if the generation step ignores the question intent.
- Sorting everything by one overall number hides which layer actually needs work.

## Checklist
- [ ] Run retrieval, generation, and evaluation in one script.
- [ ] Report retrieval metrics separately from generation metrics.
- [ ] Keep both per-question logs and a final summary report.

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

- [RAGAS documentation](https://docs.ragas.io/)
- [LangChain retrieval overview](https://python.langchain.com/docs/concepts/retrieval/)
- [FAISS documentation](https://faiss.ai/)

Tags: RAG, VectorDB, Benchmarking, LLM
