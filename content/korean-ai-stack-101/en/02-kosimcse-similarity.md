---
title: 'Building sentence similarity search with KoSimCSE'
series: korean-ai-stack-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- LLM
- Embeddings
- OCR
last_reviewed: '2026-05-01'
---

# Building sentence similarity search with KoSimCSE

## Questions this post answers

- Where does KoSimCSE usually pay off first in Korean retrieval work?
- Why is indexing FAQ questions alone a clean first version of search?
- Why do normalized embeddings pair so well with `IndexFlatIP`?
- How can a high similarity score still return the wrong result?

> The first useful sentence-similarity system comes from clean embeddings plus a transparent index, not from a complicated orchestration layer.

> Korean AI Stack 101 (2/6)

Example code: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/02-kosimcse-similarity)

This post moves from model comparison into an actual Korean retrieval loop. The task is intentionally narrow: encode FAQ questions, index them with FAISS, and retrieve the closest match for a new Korean query.

---

## Core flow

![Core flow](../../../assets/korean-ai-stack-101/02/02-01-core-flow.en.png)
---

## Why index only the questions first

If you embed both questions and answers on day one, debugging becomes harder. A bad match may come from the query text, the answer wording, or the fact that long answer sentences drift semantically.

---

## Minimal runnable example

```python
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'BM-K/KoSimCSE-roberta-multitask'
FAQS = [
    {'category': 'account', 'question': '비밀번호나 패스워드를 재설정하고 싶어요.'},
    {'category': 'billing', 'question': '결제는 됐는데 주문 내역이 보이지 않습니다.'},
    {'category': 'shipping', 'question': '배송 상태는 어디에서 확인하나요?'},
]

model = SentenceTransformer(MODEL_NAME)
embeddings = model.encode([item['question'] for item in FAQS], normalize_embeddings=True).astype('float32')
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

query = '로그인 비밀번호를 다시 설정하고 싶어요.'
query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
distances, indices = index.search(query_vec, 2)
print(distances, indices)
```

~~~
Output
[[0.92722106 0.27328622]] [[0 1]]
~~~

---

## What to notice in this code

- The index stores the **question strings**, not the full answers.
- `normalize_embeddings=True` makes inner product equivalent to cosine similarity.
- The test queries paraphrase the indexed questions instead of repeating them exactly.
- The full script prints the top two hits because ranking errors are easier to diagnose when you can inspect near misses.

---

## Where engineers get confused

- Sentence similarity search is retrieval, not generation.
- A score above 0.9 is not automatically correct.
- Settings that work for short FAQ questions do not transfer directly to long document chunks.

---

## Checklist

- [ ] Decide whether the index should store questions, answers, or both.
- [ ] Test multiple paraphrases for the same intent.
- [ ] Print at least the top two or three results while tuning.
- [ ] Validate retrieval by itself before adding an LLM layer.

---

## Summary

The KoSimCSE example is valuable because it keeps the retrieval loop visible. That visibility becomes your reference point when you later add multilingual embeddings or generation on top.

<!-- toc:begin -->
## In this series

- [Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- **Building sentence similarity search with KoSimCSE (current)**
- BGE-M3 multilingual embedding in practice (upcoming)
- Document text extraction with CLOVA OCR API (upcoming)
- Using HyperCLOVA X and Solar API (upcoming)
- Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [SentenceTransformers semantic search examples](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)

Tags: Korean NLP, LLM, Embeddings, OCR
