---
title: "Korean AI Stack 101 (3/6): BGE-M3 multilingual embedding in practice"
series: korean-ai-stack-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- BGE-M3
- Multilingual
- FAISS
- Embeddings
- Python
last_reviewed: '2026-05-01'
seo_description: Implement multilingual search with BGE-M3. Learn to create a dense-only baseline for mixed Korean-English corpora using FAISS and normalization.
---

# Korean AI Stack 101 (3/6): BGE-M3 multilingual embedding in practice

Many Korean teams search across a corpus where the query is Korean but half the documents are English. That is the point where a Korean-only retrieval baseline starts to look clean in tests and brittle in production.

This is the third post in the Korean AI Stack 101 series. Here, we use BGE-M3 to measure a dense multilingual baseline over mixed Korean-English corpora before adding more complex retrieval signals.

![Korean AI Stack 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/03/03-01-core-flow.en.png)
*Korean AI Stack 101 chapter 3 flow overview*

> BGE-M3 is interesting not because it is multilingual but because it is multi-functional and multi-granular in one model — dense, sparse, and ColBERT-style scoring from the same encoder, which collapses three retrieval pipelines into one.

## Questions to Keep in Mind

- Where does BGE-M3 outperform KoSimCSE on a corpus mixing Korean and English?
- What does it mean for a single model to emit dense, sparse, and multi-vector representations at once?
- Why is the dense-only baseline often enough for the first version of multilingual search?

## Why this matters

This post moves into a Korean retrieval scenario that is the daily reality at Korean companies: queries arrive in Korean, but a large fraction of the document corpus is written in English. The previous post used KoSimCSE on Korean-only short sentences. Here we use BGE-M3 on a mixed Korean-English corpus.

BGE-M3 deserves its own stage for two reasons. First, internal documentation search at Korean companies is almost impossible without a multilingual encoder — manuals and incident postmortems are in English while user queries are in Korean. Second, BGE-M3 is the first widely available open model that emits dense, sparse, and multi-vector representations at once, which means later hybrid retrieval can fuse scores from the same backbone. This post focuses on the dense baseline; sparse and multi-vector are deferred to the next stage.

## Mental Model

Multilingual dense retrieval decomposes into four steps.

```text
[multilingual corpus (ko+en)]      [Korean query]
        |                                |
        v                                v
[BGE-M3 encode -> 1024d]      [BGE-M3 encode -> 1024d]
        |                                |
        v                                v
[FAISS IndexFlatIP] <-------- search ----+
        |
        v
[top-k (language-agnostic)]
```

Three things matter most:

- **Model absorbs the language asymmetry**: the corpus may be English while the query is Korean, but both end up in the same vector space. KoSimCSE does not align languages well.
- **Normalization is still required**: BGE-M3 dense outputs are not unit length by default. Always set `normalize_embeddings=True`.
- **Dense alone is meaningful**: a multilingual encoder has already learned to fold some keyword signal into its dense vectors, so the dense baseline already shows a clear lift over KoSimCSE on mixed corpora.

Two more facts:

- BGE-M3 dense vectors are 1024-dimensional. KoSimCSE is 768. FAISS memory grows by about 1.3x.
- Model load time is longer than KoSimCSE, adding 5-10 seconds to cold starts. Caching matters more.

## Core concepts

| Item | Meaning |
| --- | --- |
| BGE-M3 | A multilingual embedding model from BAAI supporting around 100 languages |
| `BAAI/bge-m3` | Hugging Face model id, loadable via `SentenceTransformer` |
| Dense vector | Standard 1024-dim embedding. Default for semantic retrieval |
| Sparse vector | Token-weighted representation, similar to BM25 but with learned weights |
| Multi-vector (ColBERT-style) | One small vector per token for late interaction |
| `normalize_embeddings=True` | L2 normalization, makes inner product equivalent to cosine similarity |
| `IndexFlatIP` | FAISS inner-product index; pairs naturally with normalized dense vectors |

## Before vs. After

**Before** — A KoSimCSE-only search returns only Korean documents for the Korean query "Kubernetes rollback procedure." English-language internal runbooks are invisible.

**After** — With BGE-M3 dense retrieval the behavior changes:

```python
query = '배포 실패 시 쿠버네티스 롤백 절차를 찾고 싶습니다.'
# top-1: 'Kubernetes rollback playbook for failed deploys' (score 0.78, en)
# top-2: '배포 실패 시 롤백 체크리스트' (score 0.74, ko)
# top-3: 'CI 파이프라인 실패 알림 정책' (score 0.41, ko)
```

What matters: (1) a Korean query lifts an English runbook to top-1, (2) the equivalent Korean document still ranks closely as top-2, and (3) the score gap to top-3 is wide enough to make a cutoff threshold meaningful.

## Why start from a dense-only baseline

![Minimal runnable example](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/03/03-01-minimal-runnable-example.en.png)

*Minimal runnable example*

The fact that BGE-M3 emits dense, sparse, and multi-vector signals at once does not mean you should fuse all three on day one. If you never measure how the dense baseline alone compares to KoSimCSE, you will not know whether a later improvement comes from sparse, dense, or the fusion weights. The simplest dense + IndexFlatIP combination, with Recall@5 captured once, becomes the reference point for every subsequent experiment.

## Step-by-step practice

### Step 1 — Prepare the model and a multilingual corpus

```python
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'BAAI/bge-m3'
DOCS = [
    {'lang': 'en', 'text': 'Kubernetes rollback playbook for failed deploys: kubectl rollout undo'},
    {'lang': 'en', 'text': 'Customer support label taxonomy for refund and cancellation tickets'},
    {'lang': 'ko', 'text': '배포 실패 시 롤백 체크리스트: 헬스체크, 트래픽 회수, 알림 순서'},
    {'lang': 'ko', 'text': 'CI 파이프라인 실패 시 슬랙 알림 정책과 담당자 매트릭스'},
    {'lang': 'ko', 'text': '환불 요청 처리 SLA와 cancellation 사유 코드 관리'},
]

model = SentenceTransformer(MODEL_NAME)
```

### Step 2 — Embed and index

```python
embeddings = model.encode(
    [doc['text'] for doc in DOCS],
    normalize_embeddings=True,
).astype('float32')

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)
print('dim =', embeddings.shape[1])  # 1024
```

Confirm the dimension once. It helps later when sizing IVF training data.

### Step 3 — Search English+Korean documents with a Korean query

![What to notice in this code](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/03/03-02-what-to-notice-in-this-code.en.png)

*What to notice in this code*

```python
query = '배포 실패 시 쿠버네티스 롤백 절차를 찾고 싶습니다.'
query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
distances, indices = index.search(query_vec, 3)

for score, idx in zip(distances[0], indices[0]):
    print(f"{score:.3f}  [{DOCS[idx]['lang']}]  {DOCS[idx]['text']}")
```

Printing the language code makes the cross-lingual mapping visible at a glance.

### Step 4 — Recall by language

```python
test_cases = [
    ('배포 실패 시 쿠버네티스 롤백 절차', 0),     # gold: English runbook
    ('환불 요청 SLA 알려 주세요', 4),              # gold: Korean refund policy
    ('CI 실패 알림은 누구에게 가나요', 3),         # gold: Korean CI policy
]

hits = 0
for query, gold_idx in test_cases:
    vec = model.encode([query], normalize_embeddings=True).astype('float32')
    _, idx = index.search(vec, 1)
    if idx[0][0] == gold_idx:
        hits += 1
print(f"Recall@1 (ko query) = {hits / len(test_cases):.2f}")
```

Holding the query language fixed (Korean) while varying the gold language is the key. If Recall on English-gold cases drops below 0.6, dense alone is not enough.

### Step 5 — Compare with the same query in English (optional)

```python
en_query = 'kubernetes rollback procedure for failed deployment'
en_vec = model.encode([en_query], normalize_embeddings=True).astype('float32')
en_dist, en_idx = index.search(en_vec, 3)

for score, idx in zip(en_dist[0], en_idx[0]):
    print(f"{score:.3f}  [{DOCS[idx]['lang']}]  {DOCS[idx]['text']}")
```

If the top-1 stays the same across the Korean and English version of the same query, the model has absorbed the language asymmetry well — at least qualitatively.

## What to notice in this code

- Korean and English documents are encoded with **one model** into one index. The old per-language index pattern is unnecessary with BGE-M3.
- Mixing the gold language inside the test cases reveals the real multilingual performance.
- 1024 dimensions cost more memory and time than KoSimCSE. Caching and batched encoding matter more.
- If dense Recall is good enough, do not add sparse or multi-vector yet.

## Common mistakes

![Where engineers get confused](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/03/03-03-where-engineers-get-confused.en.png)

*Where engineers get confused*

- **Skipping normalization** — without `normalize_embeddings=True`, dense vector length dominates the score under `IndexFlatIP`.
- **Per-language indexes** — splitting by language defeats BGE-M3's cross-lingual alignment. Put both languages into the same index.
- **Comparing absolute scores across models** — KoSimCSE's 0.91 and BGE-M3's 0.78 are not on the same scale. Different models, different distributions.
- **Enabling dense, sparse, and multi-vector all at once** — you lose the ability to attribute improvements. Add them one at a time: dense → sparse → multi-vector.
- **Ignoring query length** — BGE-M3 supports up to 8K tokens, but very long queries dilute meaning and flatten scores. Aim for around 200 tokens.
- **Running the model in fp32 on GPU** — BGE-M3 is safe and fast in fp16. `model.half()` halves memory in one line.

## Production application

- **Multilingual internal search**: put English manuals and Korean operational guides into one index and accept Korean queries — a usable first version of internal search emerges quickly.
- **Hybrid retrieval (dense axis)**: fuse BM25 (sparse, keyword) with BGE-M3 dense via weighted sum. Domain acronyms and general paraphrases both get covered. Start with weights between 0.3 and 0.7.
- **Cross-encoder rerank**: pull top-50 candidates with BGE-M3 and rerank with `bge-reranker-large`. Multilingual queries see a clear accuracy bump.
- **Embedding caching**: 1024 dims times tens of thousands of documents is non-trivial memory. Disk caching and mmap matter.
- **Choose the right index**: ≤10K → `IndexFlatIP`. ≥100K → `IndexIVFFlat` (nlist≈√N), train with at least 10K samples. ≥1M → `IndexHNSWFlat`.
- **Per-language monitoring**: weekly, split Recall@5 into Korean-query/English-gold and Korean-query/Korean-gold groups. A drop on one side signals corpus-mix or model-change pressure.

## Checklist

- [ ] Both Korean and English documents live in the same index.
- [ ] Dense baseline Recall@5 has been measured once and recorded.
- [ ] Normalization and IndexFlatIP are paired.
- [ ] Same-meaning Korean and English queries have been spot-checked for consistent top-1.
- [ ] Dense-only limitations are written down before sparse or multi-vector are added.

## Exercises

1. Grow the corpus to 6 English and 6 Korean documents, then measure Recall@1 over 5 Korean queries. Split the Recall by gold language and compare.
2. Switch to `normalize_embeddings=False` and observe how long English documents distort the scores.
3. Index the same corpus with KoSimCSE and compare Recall@5 on Korean-gold vs English-gold cases against BGE-M3. What pattern emerges?

## Summary · Next article

The value of the BGE-M3 dense example is that it draws a clear baseline for multilingual retrieval. Lifting an English runbook to top-1 from a Korean query is already a significant step, and only on top of that baseline can the additional gain from sparse or multi-vector be measured. One commitment — encoding Korean and English into the same space with one model — is what makes a usable internal-search v1 possible.

The next article (episode 4) covers the CLOVA OCR API. We will reliably pull text out of Korean document images and shape the result into the form a BGE-M3 corpus expects, with code.

## How to Build a Multilingual Benchmark Table

What matters in multilingual search is not a single number but failure locations by case. Recording Korean-query-to-English-document cases and Korean-query-to-Korean-document cases separately reveals improvement directions.

```python
def evaluate_by_target_language(index, model, docs, eval_cases, top_k=5):
    buckets = {
        'ko_target': {'n': 0, 'hits': 0},
        'en_target': {'n': 0, 'hits': 0},
    }

    for case in eval_cases:
        q = case['query']
        gold = case['gold_idx']
        target_lang = docs[gold]['lang']

        vec = model.encode([q], normalize_embeddings=True).astype('float32')
        _, idx = index.search(vec, top_k)
        retrieved = idx[0].tolist()

        key = 'ko_target' if target_lang == 'ko' else 'en_target'
        buckets[key]['n'] += 1
        buckets[key]['hits'] += int(gold in retrieved)

    for key, row in buckets.items():
        recall = row['hits'] / row['n'] if row['n'] else 0.0
        print(key, f"Recall@{top_k}={recall:.3f}")
```

**Expected output:**

```text
ko_target Recall@5=0.920
en_target Recall@5=0.860
```

This level of separation is highly practical in operations. For example, if only English-target Recall drops, you can start checking whether corpus updates were skewed toward English documents or whether query preprocessing over-reduced Korean expressions.

## Dense + Sparse + Rerank Extension Order

With BGE-M3, the temptation is to use dense, sparse, and multi-vector all at once. But in practice, an order that enables root-cause tracing matters more.

| Stage | Configuration | Metric | Criterion to advance |
| --- | --- | --- | --- |
| 1 | Dense only (`IndexFlatIP`) | Recall@5, MRR@5 | Korean-query/English-target Recall ≥ 0.8 |
| 2 | Dense + BM25 (RRF) | Recall@5, NDCG@10 | False positive reduction on abbreviation/proper-noun queries |
| 3 | Dense top-50 + Reranker | Recall@5, Precision@1 | Consistent top-1 accuracy improvement |
| 4 | Sparse/multi-vector addition | Latency, Cost, Quality | Meaningful gain within latency budget |

Following this order lets you explain "why it improved" and keeps rollback cost low when regressions occur.

## Production Configuration Example: Multilingual Search API

Multilingual search services depend on index operation policies as much as model performance. Below is an operational configuration example based on BGE-M3.

```yaml
service:
  name: multilingual-retriever
  env: prod
  region: ap-northeast-2

embedding:
  model_id: BAAI/bge-m3
  normalize: true
  device: cuda
  dtype: float16
  batch_size: 96

index:
  backend: faiss
  type: ivf-flat-ip
  nlist: 4096
  nprobe: 24
  index_path: /data/index/docs.ivf
  metadata_path: /data/index/docs.meta.parquet

retrieval:
  top_k: 5
  min_score: 0.35
  reranker_enabled: true
  reranker_model: BAAI/bge-reranker-v2-m3

runtime:
  request_timeout_ms: 250
  max_qps_per_pod: 35
  warmup_queries:
    - 쿠버네티스 롤백 절차
    - 환불 SLA 정책
```

In operations, managing `nprobe` and `top_k` together is essential. Raising `nprobe` improves Recall but increases latency, so profiling by request characteristic is advisable.

## Comparison Logs Useful During Incidents

Multilingual search incidents often manifest in only one language. Logging query language, target language (in evaluation), and top-candidate language distribution per request speeds up root-cause isolation.

```python
import json

def log_multilingual_retrieval(query, hits, query_lang='ko'):
    event = {
        'query': query,
        'query_lang': query_lang,
        'top_k': len(hits),
        'scores': [round(float(h['score']), 4) for h in hits],
        'langs': [h['lang'] for h in hits],
        'doc_ids': [h['id'] for h in hits],
    }
    print(json.dumps(event, ensure_ascii=False))
```

For example, if Korean queries increasingly return only English documents in the top-5, suspect corpus supply imbalance or topic bias.

## Tokenizer Length Statistics as Multilingual Input Health Indicator

In BGE-M3, token length distributions can shift significantly when query language changes. Ignoring this shift can lead to mistaking latency increases for model problems. Aggregating query token lengths daily simplifies operational judgments.

```python
from transformers import AutoTokenizer
import numpy as np

tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-m3')

def token_length_stats(queries):
    lengths = [len(tokenizer.encode(q, add_special_tokens=True)) for q in queries]
    return {
        'count': len(lengths),
        'p50': int(np.percentile(lengths, 50)),
        'p90': int(np.percentile(lengths, 90)),
        'p99': int(np.percentile(lengths, 99)),
        'max': max(lengths),
    }
```

If token length p99 suddenly spikes, check first whether raw log text leaked into prompt input or OCR line breaks collapsed.

## Bilingual Benchmark Example Results Table

To aid interpretation of multilingual baselines, recording small-scale experiment results in documentation is helpful.

| Model | ko→ko Recall@5 | ko→en Recall@5 | MRR@5 | p95 latency (ms) |
| --- | --- | --- | --- | --- |
| KoSimCSE | 0.94 | 0.51 | 0.73 | 34 |
| BGE-M3 dense | 0.92 | 0.86 | 0.79 | 51 |
| BGE-M3 dense + rerank | 0.95 | 0.89 | 0.84 | 89 |

This table shows "what improvement was gained at what cost" rather than "which model is unconditionally superior." It effectively gets operations and product teams looking at the same picture.

## Index Rebuild and Deployment Strategy

Multilingual corpora grow quickly, so define an index rebuild strategy first. Typically both patterns are used together:

1. **Weekly full rebuild**: Clears accumulated drift and omissions.
2. **Hourly incremental updates**: Quickly makes new documents searchable.

```python
def should_trigger_full_rebuild(last_full_rebuild_hours, drift_ratio):
    if last_full_rebuild_hours >= 24 * 7:
        return True
    if drift_ratio >= 0.12:
        return True
    return False
```

Here `drift_ratio` is the proportion of documents existing only in the incremental index but not in the main index. When this value grows, search results start skewing toward stale documents.

## Team Operations Checkpoint: Reducing Multilingual Search Regressions

Multilingual search wobbles more from operational procedures than model quality. Fixing a simple weekly review routine significantly reduces unnecessary regressions.

1. **Corpus increment check**: Record per-language document growth rate versus last week.
2. **Evaluation set re-run**: Re-measure ko→ko, ko→en Recall@5 with the same seed.
3. **Latency budget check**: Confirm p95 latency and GPU memory usage together.
4. **Top failure case logging**: Fix 10 failed queries into the next regression set.

Documenting this procedure lets the entire team interpret results against the same criteria when experimenting with new models or index options.

## Answering the Opening Questions

- **Where is BGE-M3 stronger than KoSimCSE on a Korean-English mixed corpus?**
  - The advantage is clearest when a Korean query must find an English runbook or English product document. In this article's examples, a Korean question pulled an English rollback doc to top-1, and ko→en Recall was measured separately to confirm the gap. BGE-M3's first value is bridging Korean meaning into English document space reliably.
- **What does it mean that one model produces dense, sparse, and multi-vector representations simultaneously?**
  - The same backbone can emit a semantic vector (dense), token-weight-based signals (sparse), and per-token interaction representations (multi-vector) together. This article fixes only dense first to measure a multilingual baseline. The reason: when you later add sparse or rerank, you can isolate where the improvement came from.
- **Why is dense alone often sufficient for a first multilingual retrieval version?**
  - Dense alone already lets you compare Korean queries and English documents in the same vector space, so the initial improvement margin is large. Measuring Recall@5 first gives you a clear baseline before adding sparse or multi-vector. Not turning on complex signals all at once keeps quality gains and latency increases explainable.

<!-- toc:begin -->
## In this series

- [Korean AI Stack 101 (1/6): Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Korean AI Stack 101 (2/6): Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- **Korean AI Stack 101 (3/6): BGE-M3 multilingual embedding in practice (current)**
- Korean AI Stack 101 (4/6): Document text extraction with CLOVA OCR API (upcoming)
- Korean AI Stack 101 (5/6): Using HyperCLOVA X and Solar API (upcoming)
- Korean AI Stack 101 (6/6): Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [BAAI/bge-m3 model card](https://huggingface.co/BAAI/bge-m3)
- [BGE-M3 paper (M3-Embedding)](https://arxiv.org/abs/2402.03216)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [SentenceTransformers semantic search examples](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)

Tags: Korean NLP, LLM, Embeddings, OCR
