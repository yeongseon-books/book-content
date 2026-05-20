---
title: "Korean AI Stack 101 (6/6): Assembling a Korean RAG pipeline"
series: korean-ai-stack-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- RAG
- Pipeline
- Retrieval
- LLM
- Python
last_reviewed: '2026-05-15'
seo_description: Assemble a minimal Korean RAG pipeline by connecting embedding, OCR, and generation. Learn chunking, retrieval metrics, and prompt engineering.
---

# Korean AI Stack 101 (6/6): Assembling a Korean RAG pipeline

RAG stops feeling mystical once you can see where each failure comes from. In Korean workflows, chunking, retrieval, and generation each introduce their own class of mistakes, so the only sane approach is to wire them together in a way you can inspect stage by stage.

This is the final post in the Korean AI Stack 101 series. Here, we connect the earlier embedding, OCR, and generation pieces into one minimal Korean RAG pipeline.

## Questions to Keep in Mind

- What stages are non-negotiable in a minimal Korean RAG pipeline?
- Which stage most often becomes the quality bottleneck — chunking, embedding, retrieval, or generation?
- How should retrieved context be formatted before it reaches the LLM?

## Big Picture

![Korean AI Stack 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/06/06-01-core-flow.en.png)

*Korean AI Stack 101 chapter 6 flow overview*

This picture places Assembling a Korean RAG pipeline inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Assembling a Korean RAG pipeline is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What you will learn

This final post connects every piece introduced earlier in the series. You will split Korean documents into chunks, embed them with KoSimCSE or BGE-M3, retrieve top chunks with FAISS, and then call a Groq model (or Solar / HyperCLOVA X) using only the retrieved context — a minimum viable Korean RAG pipeline.

Concretely, you will pick up four habits.

1. **Four-stage decomposition** — keep Ingest, Index, Retrieve, and Generate as separate functions so you can isolate which stage is the quality bottleneck.
2. **Chunk boundary design** — understand the difference between paragraph, fixed-token, and sentence chunking, and the failure patterns that show up in Korean text.
3. **Separate retrieval from generation evaluation** — learn why Recall@k and Faithfulness must be measured independently, with minimal evaluation code.
4. **Anti-speculation prompting** — explicitly instruct the LLM to say "I don't know" when the answer is not in the context, and force a citation line.

By the end you will have enough fundamentals to build a small internal-wiki RAG over 30–50 documents and debug retrieval failures and hallucination separately.

---

## Why this matters

The difference between a bare LLM call and RAG is **provenance**. When a user asks "the payment went through but the order is missing — what should I check?", a standalone LLM may fabricate plausible-looking advice that contradicts your actual internal policy. Operations teams cannot rely on answers without traceable sources.

RAG is hard not because there are many stages, but because **responsibility separation** between stages is hard. When an answer looks wrong, you must first determine whether the chunking was off, the embedding missed the meaning, top-k was insufficient, or the LLM ignored the context. A single end-to-end call makes that diagnosis nearly impossible.

The code in this post deliberately prints intermediate state and logs retrieval scores alongside selected chunk IDs. In Korean RAG, chunking is an especially common failure point because tokenizers differ in how they treat whitespace versus morphemes — visually inspecting which chunk was selected dramatically shortens debugging time.

---

## Mental Model — the four-stage pipeline

RAG decomposes into four independent stages.

| Stage | Input | Output | Quality metric |
|---|---|---|---|
| **Ingest** | Raw documents (PDF, HTML, OCR output) | Chunk list | Chunk length distribution, boundary placement |
| **Index** | Chunks + embedding model | FAISS index | Vector dimension, index size |
| **Retrieve** | Question embedding + index | Top-k chunks + scores | Recall@k |
| **Generate** | Question + retrieved chunks | Answer + citations | Faithfulness, speculation rate |

Each stage can be replaced, measured, and debugged independently. Changing only the chunk boundary in Ingest can swing Recall@k significantly; changing only the prompt in Generate can change the hallucination rate. This separation is the central mental model of the entire post.

---

## Core concepts

### Chunking

Splits long documents into search units. For Korean, three strategies are common.

- **Paragraph** — split on `\n\n`. Simplest, preserves semantic boundaries well.
- **Fixed token** — 256–512 tokens per chunk with 50–100 token overlap. Predictable size, stable indexing.
- **Sentence** — split with KSS or kiwi. Suitable for short FAQs, but each chunk may lack context.

### Embedding

Turns chunks into vectors. For Korean-only corpora, KoSimCSE (post 2) is a typical pick; for multilingual corpora, BGE-M3 (post 3). Set `normalize_embeddings=True` and use `IndexFlatIP` (inner product) — the result equals cosine similarity.

### Retrieval

Pulls the top-k chunks closest to the question vector. Start with k = 3–5 and adjust based on the LLM's context window. Always log the score (distance) so you can audit retrieval quality afterwards.

### Generation

Injects only the retrieved chunks into the system message. Two non-negotiables: (1) explicitly say "if the answer is not in the context, say you don't know"; (2) force the model to cite chunk numbers.

---

## Before / After

### Before — bare LLM call

```python
client.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{'role': 'user', 'content': 'Payment succeeded but no order — what to check?'}],
)
```

The LLM produces a generic-sounding answer. It may contradict your internal policy, and there is no source.

### After — RAG pipeline

```python
chunks = retrieve(question, top_k=3)        # internal-doc chunks
answer = generate(question, chunks)         # answer grounded only in chunks
print('sources:', [c['id'] for c in chunks])
```

The answer is grounded in your documents, and you can trace exactly which chunks were used.

---

## Step-by-step walkthrough

### Step 1 — chunking and indexing

```python
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')

chunks = [
    '결제는 성공했지만 주문이 생성되지 않은 경우에는 주문 동기화 지연 여부를 먼저 확인합니다.',
    '결제 실패 문의는 카드 승인 실패와 주문 저장 실패를 분리해서 대응해야 합니다.',
    '환불 요청은 결제 채널별로 처리 시간이 다르며, 카드사 환불은 영업일 기준 3~5일이 소요됩니다.',
    '쿠폰이 적용되지 않을 때는 적용 조건(최소 주문 금액, 카테고리 제한, 만료일)을 먼저 확인합니다.',
]

vectors = model.encode(chunks, normalize_embeddings=True).astype('float32')
index = faiss.IndexFlatIP(vectors.shape[1])
index.add(vectors)
```

### Step 2 — retrieval

![Minimal runnable example](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/06/06-01-minimal-runnable-example.en.png)

*Minimal runnable example*

```python
def retrieve(question: str, top_k: int = 2) -> list[dict]:
    query_vec = model.encode([question], normalize_embeddings=True).astype('float32')
    distances, indices = index.search(query_vec, top_k)
    return [
        {'id': int(idx), 'score': float(score), 'text': chunks[idx]}
        for score, idx in zip(distances[0], indices[0])
    ]

question = '결제는 됐는데 주문 내역이 없을 때 어떤 순서로 점검해야 하나요?'
hits = retrieve(question, top_k=2)
for h in hits:
    print(f"[{h['id']}] score={h['score']:.3f}  {h['text'][:40]}...")
```

### Step 3 — generation

![What to notice in this code](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/06/06-02-what-to-notice-in-this-code.en.png)

*What to notice in this code*

```python
from groq import Groq

client = Groq()

def generate(question: str, hits: list[dict]) -> str:
    context = '\n\n'.join(f"[{h['id']}] {h['text']}" for h in hits)
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {
                'role': 'system',
                'content': (
                    'Answer ONLY using the provided context. '
                    'If the answer is not in the context, reply '
                    '"I could not find a relevant policy" and do not speculate. '
                    'End the answer with a citation in the form [sources: 0,1].'
                ),
            },
            {'role': 'user', 'content': f'Context:\n{context}\n\nQuestion: {question}'},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content

answer = generate(question, hits)
print(answer)
```

### Step 4 — a minimal evaluation set

```python
eval_set = [
    {'q': 'Payment succeeded but no order — steps to check?', 'expected_chunk': 0},
    {'q': 'How long does a refund take?', 'expected_chunk': 2},
    {'q': 'What to verify when a coupon is not applied?', 'expected_chunk': 3},
]

recall_hits = sum(
    1 for case in eval_set
    if case['expected_chunk'] in [h['id'] for h in retrieve(case['q'], top_k=3)]
)
print(f'Recall@3 = {recall_hits}/{len(eval_set)}')
```

Even ten cases are enough for the impact of chunking and embedding changes to show up as numbers.

### Step 5 — wrap everything in one runnable function

RAG turns abstract the moment each stage makes sense separately but the full path no longer shows what to print or inspect. Even a small tutorial benefits from a single `run_pipeline()` that preserves intermediate state.

```python
import json
import re

def mask_pii(text: str) -> str:
    text = re.sub(r'\b\d{6}-\d{7}\b', '[RRN]', text)
    text = re.sub(r'\b\d{2,3}-\d{3,4}-\d{4}\b', '[PHONE]', text)
    return text

def run_pipeline(question: str) -> dict:
    masked_question = mask_pii(question)
    hits = retrieve(masked_question, top_k=2)
    answer = generate(masked_question, hits)
    result = {
        'question': masked_question,
        'hit_ids': [h['id'] for h in hits],
        'hit_scores': [round(h['score'], 3) for h in hits],
        'answer': answer,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

run_pipeline('결제는 됐는데 주문 내역이 없을 때 어떤 순서로 점검해야 하나요?')
```

**Expected output:**

```json
{
  "question": "결제는 됐는데 주문 내역이 없을 때 어떤 순서로 점검해야 하나요?",
  "hit_ids": [0, 1],
  "hit_scores": [0.873, 0.522],
  "answer": "먼저 주문 동기화 지연 여부를 확인하고, 그다음 결제 성공과 주문 저장 실패가 분리된 상황인지 점검해야 합니다. [sources: 0,1]"
}
```

That output matters for two reasons. First, the answer is logged together with the selected chunks and scores. Second, the log line is enough to reopen the case later and ask whether retrieval failed or generation failed.

### Step 6 — force a failure case on purpose

One validation step is easy to skip: ask a question the corpus cannot answer. That is the only honest way to verify that the no-speculation prompt really works.

```python
unknown_question = '우리 회사 포인트 만료 정책은 몇 개월인가요?'
unknown_result = run_pipeline(unknown_question)
print(unknown_result['answer'])
```

**Expected output:**

```text
I could not find a relevant policy [sources: 1,3]
```

If you skip this test, it is easy to ship a pipeline whose retrieval is weak but whose answers still sound confident.

---

## A fast way to locate the bottleneck

When debugging RAG, it is usually faster to map symptoms to a first check than to write a long description of the problem.

| Symptom | Usual cause | First log to inspect |
| --- | --- | --- |
| Answer sounds fluent but factually wrong | retrieve failure or generation speculation | `hit_ids`, `hit_scores`, citation line |
| Retrieval scores are all close together | chunks are too short or too generic | chunk-length distribution, top-5 scores |
| top-1 chunk is right but answer is still off | weak context formatting | `Context:` string, system prompt |
| Only some questions keep failing | eval-set bias or missing corpus content | whether the gold chunk exists at all |
| Long documents fail more often | chunk boundaries cut through meaning | paragraph vs fixed-token comparison |

This table is simple enough to paste into an internal wiki. It turns “the LLM feels weird” into a concrete first-check sequence.

---

## Context-format rules for Korean RAG

One frequent generation mistake is pasting retrieved chunks together with no structure. In Korean workflows, these three rules help a lot.

1. **Prefix chunk ids.** Citations and debugging become easy.
2. **Separate chunks with blank lines.** Chunk boundaries stay visible.
3. **Make the model read context before question semantics.** The system prompt should enforce that priority.

```python
def build_context(hits: list[dict]) -> str:
    return '\n\n'.join(
        f"[chunk:{hit['id']}]\n{hit['text']}"
        for hit in hits
    )
```

It looks like a tiny helper, but without a stable format, both citation quality and debugging speed degrade quickly.

---

## A tiny evaluation loop before production

Even the first version needs around ten labeled questions. The goal is not an impressive evaluation framework. The goal is a tiny loop that catches regressions quickly.

```python
def evaluate_retrieval(eval_set):
    failures = []
    hits = 0

    for case in eval_set:
        result = retrieve(case['q'], top_k=3)
        hit_ids = [item['id'] for item in result]
        ok = case['expected_chunk'] in hit_ids
        hits += int(ok)
        if not ok:
            failures.append({'question': case['q'], 'hit_ids': hit_ids})

    recall = hits / len(eval_set)
    return recall, failures

recall, failures = evaluate_retrieval(eval_set)
print('Recall@3 =', round(recall, 2))
print('Failures =', failures)
```

**Expected output:**

```text
Recall@3 = 1.0
Failures = []
```

Whenever a failure appears, promote that question into the permanent regression set. Strong RAG teams do not start with huge eval suites. They start with small ones that keep accumulating.

---

## Common mistakes

![Where engineers get confused](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/06/06-03-where-engineers-get-confused.en.png)

*Where engineers get confused*

1. **Believing a stronger LLM rescues RAG.** If retrieval pulls the wrong chunk, GPT-4o or Claude Opus will still answer wrong. Measure Recall@k first.
2. **Not logging retrieval scores.** Looking at answers alone hides which stage broke. Always log retrieval results, scores, and selected chunk IDs together.
3. **Setting top-k too high.** k = 20 only adds noise and crowds out the relevant chunks. Start at k = 3–5.
4. **Skipping citations.** Without citations, neither users nor operators can verify answers. Force them in the system prompt.
5. **Chunks that are too long or too short.** Over 1000 tokens lets the LLM focus on irrelevant parts; under 50 tokens loses context. Aim for 200–500 tokens.
6. **Sending sensitive data unmasked.** Mask resident registration numbers, card numbers, and account IDs before calling an external LLM API.
7. **Tuning without an eval set.** "It feels better" invites regressions. Write ten cases and measure on every change.

---

## How this usually expands in production

The first features that get added to a tutorial-sized RAG pipeline are usually these three:

1. **Input-path separation** — HTML, PDF, and OCR output all land in the same `chunks` structure.
2. **Post-retrieval reranking** — fetch top-20, then use a cross-encoder to choose top-3.
3. **Answer audit logging** — write question, chunk ids, scores, citations, and user feedback as one JSON line.

Even a tiny audit record already pays off.

```python
audit_log = {
    'question': question,
    'retrieved': hits,
    'answer': answer,
    'citations_present': '[sources:' in answer,
}
print(json.dumps(audit_log, ensure_ascii=False))
```

This is not just for analytics. It is the difference between guessing why an answer failed and reopening the exact retrieval path.

---

## Production application — internal wiki RAG

In real deployments you typically add the following:

- **Metadata filtering** — attach fields like `{'team': 'payments', 'updated_at': '2026-04-01'}` to each chunk so you can scope searches by team or date. FAISS alone is not enough; vector databases such as Qdrant, Weaviate, or Milvus are commonly used.
- **Hybrid search** — combine BM25 (keyword) and dense (embedding) scores via Reciprocal Rank Fusion. This significantly improves Korean retrieval for proper nouns and abbreviations.
- **Reranking** — retrieve top-20, then rescore with a cross-encoder (for example `BAAI/bge-reranker-v2-m3`) and pass only top-3 to the LLM.
- **OCR ingestion** — for PDF/image documents, run them through CLOVA OCR (post 4) and merge the output into the chunking stage.
- **Model swap** — when external APIs are restricted, swap the LLM for Solar or HyperCLOVA X (post 5). With separate `retrieve` / `generate` interfaces, model replacement is nearly free.
- **Logging and operations** — write one JSON line per request: question, retrieved chunk IDs, scores, answer, user feedback. A few days of data already produces the next eval set and chunking improvement ideas.

---

## Checklist

- [ ] Ingest, Index, Retrieve, and Generate are split into separate functions.
- [ ] Chunk boundaries are decided first; retrieved chunks are inspected by eye (200–500 tokens recommended).
- [ ] Retrieval scores and selected chunk IDs are always logged with the answer.
- [ ] The system prompt forbids speculation and forces citations.
- [ ] An evaluation set of at least ten question/expected-chunk pairs exists, with Recall@k measured.
- [ ] Sensitive-data masking runs immediately before `generate`.
- [ ] Top-k starts at 3–5 and is tuned against the LLM context budget.
- [ ] At least three unanswerable questions have been used to verify anti-speculation behavior.

---

## Exercises

1. **Compare chunking strategies.** Index the same document with (a) paragraph splits and (b) 300-token chunks with 50-token overlap. Measure Recall@3 over the same five questions and compare.
2. **Verify the no-speculation rule.** Add three questions to your eval set whose answers are NOT in the corpus, then compare how often the LLM speculates with vs. without the no-speculation system prompt.
3. **Hybrid search.** Add BM25 scores via `rank_bm25`, fuse them with the dense scores using RRF, and measure Recall@3 improvement over dense-only retrieval.
4. **Force citations.** Add a retry that re-calls the LLM whenever the answer does not contain a `[sources: 0,1]` line.

---

## Summary and next steps

The deeper lesson of the series is not a specific tool choice but the habit of **separating each Korean document-processing stage clearly**. By stacking embedding comparison (post 1), sentence similarity (post 2), multilingual retrieval (post 3), OCR (post 4), and generation APIs (post 5), you can design Korean RAG pipelines with much more composure.

Three habits matter most: keep retrieval and generation visible as separate stages, always log chunk ids and scores with the answer, and test unanswerable questions on purpose. Those habits alone move a small Korean RAG system much closer to something you can actually operate.

This post closes the series. Recommended next series:

- **vector-search-101** — deep dive on FAISS, Qdrant, and Milvus, covering metadata filters, hybrid search, and index tuning.
- **ai-evaluation-101** — building a RAG evaluation system using Recall@k, MRR, Faithfulness, and RAGAS.

A small evaluation set and a four-stage pipeline are the only two habits you really need to scale into much larger RAG systems with confidence.

## Answering the Opening Questions

- **What stages are non-negotiable in a minimal Korean RAG pipeline?**
  - The article treats Assembling a Korean RAG pipeline as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which stage most often becomes the quality bottleneck — chunking, embedding, retrieval, or generation?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How should retrieved context be formatted before it reaches the LLM?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Korean AI Stack 101 (1/6): Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Korean AI Stack 101 (2/6): Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- [Korean AI Stack 101 (3/6): BGE-M3 multilingual embedding in practice](./03-bge-m3-multilingual.md)
- [Korean AI Stack 101 (4/6): Document text extraction with CLOVA OCR API](./04-clova-ocr.md)
- [Korean AI Stack 101 (5/6): Using HyperCLOVA X and Solar API](./05-hyperclova-solar-api.md)
- **Korean AI Stack 101 (6/6): Assembling a Korean RAG pipeline (current)**

<!-- toc:end -->

---

## References

- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [RAGAS — RAG evaluation framework](https://github.com/explodinggradients/ragas)
- [Reciprocal Rank Fusion paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

Tags: Korean NLP, LLM, Embeddings, OCR
