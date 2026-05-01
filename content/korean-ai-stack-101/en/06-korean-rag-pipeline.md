---
title: 'Assembling a Korean RAG pipeline'
series: korean-ai-stack-101
episode: 6
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

# Assembling a Korean RAG pipeline

## Questions this post answers

- What stages are non-negotiable in a minimal Korean RAG pipeline?
- Which stage most often becomes the quality bottleneck: chunking, embedding, retrieval, or generation?
- How should retrieved context be formatted before it reaches the LLM?
- How do the earlier pieces connect into one working pipeline?

> RAG quality is not produced by one magical call. It emerges from the combined behavior of chunk boundaries, retrieval candidates, and how context is handed to the model.

> Korean AI Stack 101 (6/6)

Example code: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/06-korean-rag-pipeline)

The final post connects the earlier pieces. Korean documents are split into small chunks, embedded with KoSimCSE, searched with FAISS, and then passed to a Groq model only after retrieval has selected the top context.

---

## Core flow

![Core flow](../../../assets/korean-ai-stack-101/06/06-01-core-flow.en.png)
---

## Why a simpler pipeline teaches more

A simpler implementation makes failure visible sooner. When the question is about a successful payment with no order record, you should inspect the retrieved context before judging the answer.

---

## Minimal runnable example

```python
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')
chunks = [
    '결제는 성공했지만 주문이 생성되지 않은 경우에는 주문 동기화 지연 여부를 먼저 확인합니다.',
    '결제 실패 문의는 카드 승인 실패와 주문 저장 실패를 분리해서 대응해야 합니다.',
]
vectors = model.encode(chunks, normalize_embeddings=True).astype('float32')
index = faiss.IndexFlatIP(vectors.shape[1])
index.add(vectors)

question = '결제는 됐는데 주문 내역이 없을 때 어떤 순서로 점검해야 하나요?'
query_vec = model.encode([question], normalize_embeddings=True).astype('float32')
distances, indices = index.search(query_vec, 2)
print(distances, indices)
```

---

## What to notice in this code

- The documents are broken into **chunks** before indexing.
- Retrieved chunks are printed with scores.
- The full script forbids unsupported speculation in the system prompt.
- The full `main.py` shows both the evidence and the generated answer.

---

## Where engineers get confused

- A better LLM does not rescue weak retrieval.
- Chunking strategy matters almost as much as model choice.
- Sensitive documents may need masking before context is sent to an external API.

---

## Checklist

- [ ] Choose chunk boundaries before tuning the prompt.
- [ ] Log retrieval scores and selected sources together.
- [ ] Tell the LLM not to guess beyond the provided context.
- [ ] Add masking rules before external generation when the corpus is sensitive.

---

## Summary

The deeper lesson of the series is not a specific tool choice but the habit of separating each Korean document-processing stage clearly. Once you can inspect those stages independently, the pipeline becomes much easier to improve safely.

<!-- blog-only:start -->
This is the final post in the series. Return to episode 1, rebuild the comparison on your own corpus, and then swap that model into this pipeline.
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- [BGE-M3 multilingual embedding in practice](./03-bge-m3-multilingual.md)
- [Document text extraction with CLOVA OCR API](./04-clova-ocr.md)
- [Using HyperCLOVA X and Solar API](./05-hyperclova-solar-api.md)
- **Assembling a Korean RAG pipeline (current)**

<!-- toc:end -->

---

## References

- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [Groq API reference](https://console.groq.com/docs/api-reference)

Tags: Korean NLP, LLM, Embeddings, OCR
