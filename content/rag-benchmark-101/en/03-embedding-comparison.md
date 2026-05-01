---
title: 'Comparing embedding models'
series: rag-benchmark-101
episode: 3
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

# Comparing embedding models

## Questions this post answers
- What do you learn by benchmarking all-MiniLM-L6-v2 and paraphrase-MiniLM-L3-v2 on the same queries?
- Why is hit rate alone insufficient for embedding comparisons?
- How should you read the speed-versus-quality trade-off?

> An embedding comparison is not about which model feels smarter; it is about which one ranks relevant evidence earlier in the same pipeline.

The third post keeps the retriever structure fixed and swaps only the embedding model. That isolates quality differences to the embedding layer. The example benchmarks two sentence-transformers models on the same corpus, query set, and k value.

![Questions this post answers](../../../assets/rag-benchmark-101/03/03-01-questions-this-post-answers.en.png)
## Minimal runnable example

### Fixed-corpus embedding comparison structure

![Fixed-corpus embedding comparison structure](../../../assets/rag-benchmark-101/03/03-01-fixed-corpus-embedding-comparison-struct.en.png)
The runnable code lives in `rag-benchmark-101/en/03-embedding-comparison/main.py`. Episodes 05 and 06 require `GROQ_API_KEY`.

```bash
cd /root/Github/rag-benchmark-101/en/03-embedding-comparison
python3 main.py
```

```python
MODELS = [
    'sentence-transformers/all-MiniLM-L6-v2',
    'sentence-transformers/paraphrase-MiniLM-L3-v2',
]
results = [benchmark_model(model_name) for model_name in MODELS]
print(json.dumps(results, indent=2))
```

## What to notice in this code

### Quality and latency comparison axes

![Quality and latency comparison axes](../../../assets/rag-benchmark-101/03/03-02-quality-and-latency-comparison-axes.en.png)
- Fixing the corpus and query set is what makes the model comparison fair.
- MRR adds rank sensitivity, so you can see whether a model finds the right passage earlier.
- Keeping latency in the report helps you judge whether the extra quality is worth the runtime cost.

## Where engineers get confused

### One-variable-at-a-time experiment boundary

![One-variable-at-a-time experiment boundary](../../../assets/rag-benchmark-101/03/03-03-one-variable-at-a-time-experiment-bounda.en.png)
- If you change chunking and embeddings at the same time, you lose causal clarity.
- The same hit rate can still produce different downstream answers when MRR differs a lot.
- A win on a tiny toy benchmark is only a directional signal, not a production conclusion.

## Checklist

### Speed quality and cost selection flow

![Speed quality and cost selection flow](../../../assets/rag-benchmark-101/03/03-04-speed-quality-and-cost-selection-flow.en.png)
- [ ] Benchmark both models on the same corpus and query set.
- [ ] Compare hit rate and MRR together.
- [ ] Include latency so the runtime cost stays visible.

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [Measuring retrieval performance](./02-retrieval-benchmarking.md)
- **Comparing embedding models (current)**
- VectorDB selection criteria (upcoming)
- End-to-end RAG pipeline evaluation (upcoming)
- Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [Sentence Transformers model catalog](https://www.sbert.net/docs/pretrained_models.html)
- [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)

Tags: RAG, VectorDB, Benchmarking, LLM
