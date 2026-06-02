---
title: "Korean AI Stack 101 (2/6): Building sentence similarity search with KoSimCSE"
series: korean-ai-stack-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- KoSimCSE
- FAISS
- SemanticSearch
- Embeddings
- Python
last_reviewed: '2026-05-01'
seo_description: Build a Korean sentence similarity search using KoSimCSE and FAISS. Learn about embedding normalization, indexing, and retrieval metrics.
---

# Korean AI Stack 101 (2/6): Building sentence similarity search with KoSimCSE

The first working retrieval loop should be small enough to inspect with your own eyes. In Korean FAQ search, a single bad choice around normalization or indexing is enough to make every later LLM step look smarter than it really is.

This is the second post in the Korean AI Stack 101 series. Here, we build a minimal Korean sentence-similarity search flow with KoSimCSE and make the retrieval mechanics explicit.

![Korean AI Stack 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-01-core-flow.en.png)
*Korean AI Stack 101 chapter 2 flow overview*

> Sentence similarity in Korean is not 'cosine of two embeddings' — it is the question of which encoder was trained on text that looks like yours, and KoSimCSE exists because multilingual models routinely miss the meaning that Korean speakers actually share.

## Questions to Keep in Mind

- Where does KoSimCSE usually pay off first in Korean retrieval work?
- Why is indexing FAQ questions alone a clean first version of search?
- Why do normalized embeddings pair so well with `IndexFlatIP`?

## Why this matters

This post moves from model comparison into an actual Korean retrieval loop. The task is intentionally narrow: encode FAQ questions, index them with FAISS, and retrieve the closest match for a new Korean query.

Sentence similarity deserves its own stage because many Korean RAG systems collapse at this very step. If embedding quality, normalization, or index choice is wrong, no amount of LLM polish will recover the wrong document. Practicing the smallest retrieval loop with a proven model like KoSimCSE gives you a reference point for everything that follows — BGE-M3, multi-vector search, hybrid retrieval.

## Mental Model

Sentence similarity search decomposes into four steps.

```text
[corpus]                         [query]
   |                                |
   v                                v
[encode -> vector]            [encode -> vector]
   |                                |
   v                                v
[FAISS index] <----- search -----+
   |
   v
[top-k results]
```

Two things matter most:

- **Encode with the same model**: the corpus and the query must share the model and the normalization scheme. Mixing models destroys distance semantics.
- **Match the distance and the index**: normalized vectors + `IndexFlatIP` (inner product) is mathematically equivalent to cosine similarity. Inner product on unnormalized vectors gets dominated by length.

Two more facts:

- KoSimCSE is a BERT-family encoder fine-tuned with contrastive learning. It is strong on short Korean sentences.
- FAISS `IndexFlatIP` is brute-force. Up to 10K items it is fast enough; beyond that switch to IVF or HNSW.

## Core concepts

| Item | Meaning |
| --- | --- |
| KoSimCSE | A Korean sentence-embedding model adapting the SimCSE contrastive learning recipe |
| `SentenceTransformer` | A library for loading and using embedding models with one line |
| `normalize_embeddings=True` | L2 normalization. Sets vector length to 1 to simplify cosine similarity |
| `IndexFlatIP` | FAISS inner-product brute-force index. Pairs with normalized vectors |
| `IndexFlatL2` | FAISS L2-distance brute-force index. For unnormalized vectors |
| top-k | Top k retrieval results. k=2~3 is suitable for debugging |
| Recall@k | Fraction of queries where the correct answer appears in the top k. Basic retrieval metric |

## Before vs. After

**Before** — When a user searches "I forgot my password" on the FAQ page, keyword matching may surface "password change policy" instead of "password reset."

**After** — KoSimCSE-based retrieval behaves as follows:

```python
query = '로그인 비밀번호를 다시 설정하고 싶어요.'  # "I want to reset my login password."
# top-1: '비밀번호나 패스워드를 재설정하고 싶어요.' (score 0.91)
# top-2: '결제는 됐는데 주문 내역이 보이지 않습니다.' (score 0.32)
```

What matters is (1) queries without the exact keyword "재설정" still match, (2) there is a large score gap between top-1 and top-2, and (3) you can manually inspect candidate meanings.

## Why index only the questions first

If you embed both questions and answers on day one, debugging becomes harder. A bad match may come from the query text, the answer wording, or the fact that long answer sentences drift semantically. Start with questions only and join the answer at display time.

## Step-by-step practice

### Step 1 — Prepare model and data

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
```

### Step 2 — Embed and index

```python
embeddings = model.encode(
    [item['question'] for item in FAQS],
    normalize_embeddings=True,
).astype('float32')

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)
```

`normalize_embeddings=True` and `IndexFlatIP` are a pair. Drop either and scores become misleading.

### Step 3 — Search a query

![Minimal runnable example](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-01-minimal-runnable-example.en.png)

*Minimal runnable example*

```python
query = '로그인 비밀번호를 다시 설정하고 싶어요.'
query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
distances, indices = index.search(query_vec, 2)
print(distances, indices)
```

### Step 4 — Interpret the result

```python
for score, idx in zip(distances[0], indices[0]):
    print(f"{score:.3f}  {FAQS[idx]['question']}")
```

Look at the top 2-3 instead of just the top 1. The score distribution shows whether the result is trustworthy at a glance.

### Step 5 — Measure Recall@k (optional)

```python
test_cases = [
    ('비밀번호 변경 어떻게 해요?', 0),  # gold: FAQ #0
    ('주문이 안 보여요', 1),
    ('택배 어디까지 왔나요?', 2),
]

hits = 0
for query, gold_idx in test_cases:
    vec = model.encode([query], normalize_embeddings=True).astype('float32')
    _, idx = index.search(vec, 1)
    if idx[0][0] == gold_idx:
        hits += 1
print(f"Recall@1 = {hits / len(test_cases):.2f}")
```

## What to notice in this code

![What to notice in this code](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-02-what-to-notice-in-this-code.en.png)

*What to notice in this code*

- The index stores the **question strings**, not the full answers.
- `normalize_embeddings=True` makes inner product equivalent to cosine similarity.
- The test queries paraphrase the indexed questions instead of repeating them exactly.
- The full script prints the top two hits because ranking errors are easier to diagnose when you can inspect near misses.

## Common mistakes

![Where engineers get confused](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/02/02-03-where-engineers-get-confused.en.png)

*Where engineers get confused*

- **Skipping normalization** — using `IndexFlatIP` without `normalize_embeddings=True` lets long sentences score unfairly high.
- **Encoding with different models** — corpus on KoSimCSE, query on BGE-M3 makes distances meaningless. Always use the same model.
- **Trusting the top-1 only** — a 0.92 score can still be wrong. The gap between candidates (0.92 vs 0.91 vs 0.45) is what reveals confidence.
- **Reusing FAQ settings on long documents** — long documents need chunking and different distance metrics. KoSimCSE is optimized for short sentences.
- **Including test data in the index** — Recall becomes unrealistically high. Always separate them.
- **Reusing score thresholds across model changes** — when the model changes, the score distribution changes. Recalibrate thresholds per model.

## Production application

- **Two-stage retrieval**: pull 100 candidates with KoSimCSE, then re-rank with a cross-encoder (`bongsoo/kpf-cross-encoder` etc.). Accuracy improves significantly.
- **Category filter**: filter by category before searching to shrink the candidate set, improving both accuracy and speed.
- **Cache embeddings**: FAQ corpora rarely change. Persist embeddings to disk and load on app startup to reduce cold start.
- **Choose the right index**: ≤10K items → `IndexFlatIP`. ≥100K → `IndexIVFFlat`. ≥1M → `IndexHNSWFlat`.
- **Hybrid retrieval**: weighted combination of BM25 (keyword) and KoSimCSE (semantic) scores catches both domain jargon and general paraphrasing.
- **Recall monitoring**: weekly, sample 50 new user queries, label gold answers, measure Recall@5. Below 80% triggers a model review.

## Checklist

- [ ] Decide whether the index should store questions, answers, or both.
- [ ] Test multiple paraphrases for the same intent.
- [ ] Print at least the top two or three results while tuning.
- [ ] Validate retrieval by itself before adding an LLM layer.
- [ ] Have measured Recall@k at least once.

## Exercises

1. Grow the FAQ corpus to 10 items and intentionally add 2 entries with similar meanings. Observe the top-1 score gap between them.
2. Switch to `normalize_embeddings=False`, search the same query, and compare how the rankings change.
3. Replace KoSimCSE with `jhgan/ko-sroberta-multitask` and compare the score distribution on the same query. Which model shows clearer gaps?

## Summary · Next article

The KoSimCSE example is valuable because it keeps the retrieval loop visible. That visibility becomes your reference point when you later add multilingual embeddings or generation on top. Three small habits — normalization, index choice, top-k printout — make a workable first version of Korean retrieval.

The next article (episode 3) covers BGE-M3. We will see where it surpasses KoSimCSE on mixed Korean-English corpora, and what dense + sparse multi-vector retrieval means in code.

## How Tokenizer Characteristics Affect Search Scores

A frequently overlooked point when using KoSimCSE in production is the tokenizer. Even sentences with identical meaning produce different token fragments depending on spacing, particles, and loanword spelling—and these differences propagate into embedding distributions. In operations, record tokenizer characteristics alongside the model name.

| Item | KoSimCSE (RoBERTa family) | BGE-M3 (XLM-R family) | Operational Implication |
| --- | --- | --- | --- |
| Base tokenizer | SentencePiece/BPE | SentencePiece multilingual | If Korean+English mix ratio is high, maintain a BGE-M3 baseline too |
| Korean particle handling | Frequent splits at particle boundaries | Relatively smoother decomposition | KoSimCSE advantage may be stronger on short queries |
| English abbreviation handling | High variance on abbreviations/version strings | More stable on abbreviations | If `API v2`, `SLA`, `OCR` are common, verify multilingual model |
| Typo/spacing tolerance | Medium | Medium-high | Input normalization pipeline is mandatory |

```python
from transformers import AutoTokenizer

samples = [
    '결제는 됐는데 주문 내역이 보이지 않습니다.',
    '결제는됬는데 주문내역이 안보여요',
    'Payment succeeded but order history is missing',
]

tok_kosimcse = AutoTokenizer.from_pretrained('BM-K/KoSimCSE-roberta-multitask')
tok_bgem3 = AutoTokenizer.from_pretrained('BAAI/bge-m3')

for text in samples:
    print('\n[TEXT]', text)
    print('KoSimCSE:', tok_kosimcse.tokenize(text)[:18])
    print('BGE-M3  :', tok_bgem3.tokenize(text)[:18])
```

The purpose of token comparison is not to dissect model internals. It is a diagnostic tool for quickly checking "how was the query decomposed" on days when scores fluctuate.

## Measuring Recall and MRR Together with a Small Benchmark Set

In practice, Recall@k alone cannot fully explain ranking quality. Even if the correct answer lands in the top-3, it being consistently third means low user-perceived quality. For a KoSimCSE baseline, measuring Recall@k and MRR (Mean Reciprocal Rank) together is better.

```python
def evaluate_retrieval_metrics(index, model, cases, top_k=3):
    recall_hits = 0
    reciprocal_ranks = []

    for query, gold_idx in cases:
        vec = model.encode([query], normalize_embeddings=True).astype('float32')
        _, idx = index.search(vec, top_k)
        ranked = idx[0].tolist()

        if gold_idx in ranked:
            recall_hits += 1
            rank = ranked.index(gold_idx) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    recall = recall_hits / len(cases)
    mrr = sum(reciprocal_ranks) / len(cases)
    return {'recall_at_k': round(recall, 3), 'mrr_at_k': round(mrr, 3)}

benchmark_cases = [
    ('패스워드 초기화 방법 알려 주세요', 0),
    ('결제 후 주문 목록이 비어 있어요', 1),
    ('배송 조회는 어디에서 하나요', 2),
    ('송장 번호 확인하는 방법', 2),
    ('주문이 사라졌어요', 1),
]

print(evaluate_retrieval_metrics(index, model, benchmark_cases, top_k=3))
```

**Expected output:**

```text
{'recall_at_k': 1.0, 'mrr_at_k': 0.9}
```

These numbers show "does it find the answer" and "does it rank the answer high" simultaneously. In Korean FAQ search, stable improvement in support-diversion rates typically appears when both metrics rise together.

## Production Configuration Example: KoSimCSE Retrieval Service

When moving to a production service, configuration drifts before code does. If model version, index file path, rebuild schedule, and timeout vary across environments, the same query can behave differently.

```yaml
service:
  name: korean-faq-retriever
  env: prod
  host: 0.0.0.0
  port: 8080

embedding:
  model_id: BM-K/KoSimCSE-roberta-multitask
  normalize: true
  batch_size: 128
  cache_dir: /var/lib/app/embeddings

index:
  type: faiss-flat-ip
  path: /var/lib/app/index/faqs.index
  metadata_path: /var/lib/app/index/faqs.meta.json
  rebuild_cron: '0 3 * * *'

retrieval:
  top_k: 3
  min_score: 0.42
  timeout_ms: 120

observability:
  log_level: INFO
  metrics_enabled: true
  trace_sample_ratio: 0.05
```

Configuration files look simple but greatly reduce operational incidents. Model swaps, threshold adjustments, and index rebuild schedule changes remain as recorded changes without code modifications.

## Operational Logging from a Failure-Response Perspective

Search failures often appear as "wrong answers" but the real cause is frequently a retrieval candidate miss. Logging the following per request is advisable.

```python
import json
from datetime import datetime, timezone

def log_retrieval_event(query, hits, model_name):
    event = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'model': model_name,
        'query': query,
        'top_hits': [
            {
                'idx': int(hit['idx']),
                'score': round(float(hit['score']), 4),
                'category': hit['category'],
            }
            for hit in hits
        ],
    }
    print(json.dumps(event, ensure_ascii=False))
```

With this log, vague claims like "the model got worse" transform into actionable problems like "delivery-category query score tail dropped."

## Data Cleanup Tips for Raising Korean Search Quality

Corpus cleanup is as important as model selection. Korean FAQ has diverse spacing variants, honorific/informal forms, and abbreviations—same meaning appears in many surface forms.

- When collecting question sentences, keep actual user expressions intact and add a normalized version in a separate field.
- Manage proper nouns and domain terms in a dictionary to unify spelling variants.
- For excessively long questions, store a summary version that preserves core intent alongside the original to improve retrieval stability.

These cleanups accumulate value regardless of model changes. Whether using KoSimCSE or another embedding, data design raises the floor of retrieval-based quality.

## Offline Regression Test Example for Korean FAQ Search

Search quality can be largely caught by offline regression tests before deployment. The following pattern fixes a test set including query-expression variants and blocks deployment if performance drops below baseline.

```python
BASELINE = {
    'recall_at_3': 0.94,
    'mrr_at_3': 0.82,
}

def assert_regression_guard(metrics):
    if metrics['recall_at_k'] < BASELINE['recall_at_3']:
        raise AssertionError(
            f"Recall regression: {metrics['recall_at_k']} < {BASELINE['recall_at_3']}"
        )
    if metrics['mrr_at_k'] < BASELINE['mrr_at_3']:
        raise AssertionError(
            f"MRR regression: {metrics['mrr_at_k']} < {BASELINE['mrr_at_3']}"
        )

metrics = evaluate_retrieval_metrics(index, model, benchmark_cases, top_k=3)
assert_regression_guard(metrics)
print('Pass regression guard:', metrics)
```

This regression guard is not a perfect quality guarantee, but it quickly blocks obvious drops after model changes or preprocessing modifications.

## Korean Query Normalization Pipeline Example

KoSimCSE is strong on short sentences, but if input fluctuates too much, the score distribution flattens quickly. Query normalization does not need to be overly clever—just ensuring consistency yields large effects.

```python
import re

SPACE_RE = re.compile(r'\s+')

REPLACE_RULES = {
    '패스워드': '비밀번호',
    '로그인 불가': '로그인 안 됨',
    '주문내역': '주문 내역',
    '환불요청': '환불 요청',
}

def normalize_query(text: str) -> str:
    t = text.strip()
    for src, dst in REPLACE_RULES.items():
        t = t.replace(src, dst)
    t = SPACE_RE.sub(' ', t)
    return t
```

Normalization is not a trick to fool the model—it makes same-intent sentences arrive in the same form, making index search more stable.

## Periodically Updating the Cosine Score Threshold

Fixed thresholds go stale over time. As FAQs grow and sentence lengths change, score distributions shift. Recalculating the following statistics monthly and updating thresholds is safer.

| Range | Recommended Calculation | Operational Use |
| --- | --- | --- |
| Similar distribution lower bound | Similar-pair score p10 | Below this → trigger retraining/normalization review |
| Unrelated distribution upper bound | Unrelated-pair score p90 | Above this → false-positive risk alarm |
| Safe threshold | `(similar_p10 + unrelated_p90) / 2` | Low-confidence search result branching |

This approach is not an absolute answer, but it helps establish the principle that thresholds must move when operational data changes.

Finally, do not just record threshold numbers in documentation—include the sample count and date used in calculation. This enables quick distinction between quality changes and data composition changes next quarter.

## Answering the Opening Questions

- **Where does KoSimCSE show its effect first in Korean retrieval tasks?**
  - It shows up first on short Korean FAQ questions—password reset, missing order history—rephrased in different words. When same-intent sentences land at top-1 with a clear score gap to the second candidate (as in this article's examples), the model is ready to serve as a retrieval baseline. The first payoff comes in Korean sentence-similarity ranking, not flashy multilingual search.
- **Why is indexing only the FAQ questions a clean first version?**
  - When retrieval is wrong, you can immediately narrow the cause to question-meaning matching. If answers are mixed in, sentence length, explanation style, and extra context bleed into scores, making debugging harder. That's why the first version separates questions from answers by role.
- **Why do normalized embeddings pair so well with `IndexFlatIP`?**
  - Inner product on normalized vectors equals cosine similarity, making score interpretation straightforward. Without normalization, longer sentences or specific length biases dominate scores and blur FAQ rankings. That's why this article always treats `normalize_embeddings=True` and `IndexFlatIP` as a single unit.

<!-- toc:begin -->
## In this series

- [Korean AI Stack 101 (1/6): Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- **Korean AI Stack 101 (2/6): Building sentence similarity search with KoSimCSE (current)**
- Korean AI Stack 101 (3/6): BGE-M3 multilingual embedding in practice (upcoming)
- Korean AI Stack 101 (4/6): Document text extraction with CLOVA OCR API (upcoming)
- Korean AI Stack 101 (5/6): Using HyperCLOVA X and Solar API (upcoming)
- Korean AI Stack 101 (6/6): Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [SimCSE paper](https://arxiv.org/abs/2104.08821)
- [FAISS getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [SentenceTransformers semantic search examples](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)

Tags: Korean NLP, LLM, Embeddings, OCR
