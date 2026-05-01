---
title: 'Measuring retrieval performance'
series: rag-benchmark-101
episode: 2
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

# Measuring retrieval performance

## Questions this post answers
- How do you attach hit rate and MRR to a FAISS retriever?
- Where should retrieval latency be measured, and in what unit?
- Can you start a benchmark with only a small gold query set?

> The core of retrieval benchmarking is not FAISS itself; it is the repeatable loop of query, gold document, and metric collection.

The second post moves the hand-written metrics onto a real retriever. Even with a tiny corpus and three questions, you can collect hit rate, MRR, and average latency together. Once that loop exists, you can reuse it for later embedding and index comparisons.

![Questions this post answers](../../../assets/rag-benchmark-101/02/02-01-questions-this-post-answers.en.png)
## Minimal runnable example

### Benchmark loop for queries and latency

![Benchmark loop for queries and latency](../../../assets/rag-benchmark-101/02/02-01-benchmark-loop-for-queries-and-latency.en.png)
The runnable code lives in `rag-benchmark-101/en/02-retrieval-benchmarking/main.py`. Episodes 05 and 06 require `GROQ_API_KEY`.

```bash
cd /root/Github/rag-benchmark-101/en/02-retrieval-benchmarking
python3 main.py
```

```python
retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
for question, relevant_ids in QUERIES:
    started_at = time.perf_counter()
    docs = retriever.invoke(question)
    ranked_ids = [doc.metadata['id'] for doc in docs]
    latencies_ms.append((time.perf_counter() - started_at) * 1000)
```

## What to notice in this code

### Retrieval quality axes with hit rate and MRR

![Retrieval quality axes with hit rate and MRR](../../../assets/rag-benchmark-101/02/02-02-retrieval-quality-axes-with-hit-rate-and.en.png)
- Latency is measured around `retriever.invoke()`, which isolates retrieval instead of document setup.
- Normalizing results to `metadata["id"]` makes later benchmarks reuse the same scoring logic.
- Hit rate is a fast sanity check for whether top-k returns anything usable at all.

## Where engineers get confused

### High hit rate with weak ranking

![High hit rate with weak ranking](../../../assets/rag-benchmark-101/02/02-03-high-hit-rate-with-weak-ranking.en.png)
- A hit rate of 1.0 can still hide poor ranking if relevant documents always appear late.
- If you mix embedding time into retrieval latency, you lose the signal for the retriever itself.
- A tiny corpus is enough to validate the benchmark loop, but not enough to claim production readiness.

## Checklist

### Benchmark record with gold IDs and logs

![Benchmark record with gold IDs and logs](../../../assets/rag-benchmark-101/02/02-04-benchmark-record-with-gold-ids-and-logs.en.png)
- [ ] Prepare gold relevant document IDs for each query.
- [ ] Measure retrieval quality and latency in the same loop.
- [ ] Keep the ranked IDs in the output, not just the average.

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- **Measuring retrieval performance (current)**
- Comparing embedding models (upcoming)
- VectorDB selection criteria (upcoming)
- End-to-end RAG pipeline evaluation (upcoming)
- Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [LangChain FAISS integration](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [FAISS documentation](https://faiss.ai/)

Tags: RAG, VectorDB, Benchmarking, LLM
