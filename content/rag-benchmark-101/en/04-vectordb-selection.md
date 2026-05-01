---
title: 'VectorDB selection criteria'
series: rag-benchmark-101
episode: 4
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

# VectorDB selection criteria

## Questions this post answers
- How can you compare FAISS flat and IVF when Annoy is unavailable?
- Which accuracy and latency signals do you need to describe a search trade-off?
- How do you expose approximate-search behavior even in a compact benchmark?

> VectorDB selection is not a logo comparison; it is an experiment in how different index structures change speed and accuracy on the same vectors.

The fourth post focuses on the algorithm layer inside the vector store. Annoy is not installed in this environment, so the runnable example compares a FAISS flat index against IVF. The key is to hold the vectors constant and change only the search strategy.

![Questions this post answers](../../../assets/rag-benchmark-101/04/04-01-questions-this-post-answers.en.png)
## Minimal runnable example

The runnable code lives in `rag-benchmark-101/en/04-vectordb-selection/main.py`. Episodes 05 and 06 require `GROQ_API_KEY`.

```bash
cd /root/Github/rag-benchmark-101/en/04-vectordb-selection
python3 main.py
```

```python
flat_index = faiss.IndexFlatIP(dimension)
flat_index.add(doc_vectors)

ivf_index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
ivf_index.train(doc_vectors)
ivf_index.add(doc_vectors)
ivf_index.nprobe = 1
```

## What to notice in this code
- Document and query embeddings are precomputed so the loop measures pure `index.search()` latency.
- `nprobe` is the main IVF control for trading recall against speed.
- The fallback to flat vs IVF keeps the benchmark useful even without Annoy installed.

## Where engineers get confused
- If embedding time dominates the benchmark, index differences disappear into noise.
- Approximate search does not always reduce quality in a visible way; the effect depends on the data and `nprobe`.
- A tie on a toy corpus does not guarantee a tie on a much larger production collection.

## Checklist
- [ ] Benchmark the same vectors across both indexes.
- [ ] Measure search latency separately from embedding time.
- [ ] Choose the index with both speed and accuracy in view.

<!-- toc:begin -->
## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [Comparing embedding models](./03-embedding-comparison.md)
- **VectorDB selection criteria (current)**
- End-to-end RAG pipeline evaluation (upcoming)
- Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [FAISS indexes wiki](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)

Tags: RAG, VectorDB, Benchmarking, LLM
