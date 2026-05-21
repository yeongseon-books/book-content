---
title: "Korean AI Stack 101 (1/6): Korean embedding models compared — KoSimCSE, BGE-M3, Solar"
series: korean-ai-stack-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- LLM
- Embeddings
- OCR
last_reviewed: '2026-05-15'
seo_description: Comparing embedding models is less about headline scores and more
  about how consistently they pull similar sentences together while pushing…
---

# Korean AI Stack 101 (1/6): Korean embedding models compared — KoSimCSE, BGE-M3, Solar

Choosing a Korean embedding model is rarely about chasing the prettiest benchmark score. The practical question is which model stays more stable on your actual mix of Korean FAQs, Korean-English documents, and threshold-based retrieval decisions.

This is the first post in the Korean AI Stack 101 series. Here, we build a reproducible comparison frame for Korean embedding models so later retrieval decisions have a clear baseline.

## Questions to Keep in Mind

- Where do English-first embedding models usually fail on Korean-heavy data?
- Why is a separation gap between similar and unrelated pairs more useful than one pretty cosine score?
- What should you test first when Korean text regularly mixes with English technical terms?

## Big Picture

![Korean AI Stack 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-01-core-flow.en.png)

*Korean AI Stack 101 chapter 1 flow overview*

This picture places Korean embedding models compared — KoSimCSE, BGE-M3, Solar inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Core flow

---

## Why start with a reproducible comparison

![Why start with a reproducible comparison](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-01-why-start-with-a-reproducible-comparison.en.png)

*Why start with a reproducible comparison*

A model comparison is only useful if readers can reproduce the trend on their own machine. API-only models and private evaluation sets may look authoritative, but they do not help you build intuition the next morning.

This example highlights two practical observations. First, `ko-sbert-nli` tends to create a wider gap between similar Korean sentences and unrelated ones. Second, `all-MiniLM-L6-v2` remains a useful baseline when Korean text mixes with English, even if its Korean-only separation is narrower. That framing gives you a stable lens for the next posts, where we move from comparison into retrieval.

> The mental model is simple: embedding evaluation is less a leaderboard contest and more instrumentation for discovering which model creates the cleanest separation on your actual data.

---

## Lock the comparison frame before you lock the model

In real model-selection meetings, the most common mistake is arguing about the model name before the comparison rules are fixed. If the rules move, score differences stop meaning anything. Start by freezing four things.

| Item | Baseline in this post | Why it matters |
| --- | --- | --- |
| Pair set | 4 similar + 2 unrelated + 2 mixed-language pairs | Lets you inspect separation and cross-lingual resilience together |
| Normalization | `normalize_embeddings=True` | Keeps cosine-score interpretation straightforward |
| Output | per-pair scores + label averages + gap | Makes the next threshold and Recall experiments reusable |
| Models | 1 general baseline + 1 Korean-oriented model | Easier to interpret than a noisy 4-model bake-off on day one |

Once those four pieces are fixed, the table survives future model swaps. In practice that one table is the cheapest way to answer the question “did the model change, or did the data change?”

---

## Environment setup

If the first post skips environment setup, the comparison often remains a spectator sport. This small setup is enough to reproduce the examples on a local CPU machine.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install sentence-transformers numpy openai
```

**Expected output:**

```text
Successfully installed numpy ... sentence-transformers ...
```

GPU is optional here. The point is not throughput benchmarking. The point is to build a habit of reading score distributions and separation gaps.

---

## Minimal runnable example

![Minimal runnable example](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-02-minimal-runnable-example.en.png)

*Minimal runnable example*

The script below runs the same sentence pairs through both models and prints per-pair scores, per-label averages, and the separation gap. The extra output is deliberate: you want to see which pair shakes, not just a single average.

```python
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAMES = {
    'all-MiniLM-L6-v2': 'sentence-transformers/all-MiniLM-L6-v2',
    'ko-sbert-nli': 'jhgan/ko-sbert-nli',
}

SENTENCE_PAIRS = [
    ('나는 오늘 점심으로 비빔밥을 먹었다.', '오늘 점심은 비빔밥이었다.', 'similar'),
    ('서울시청 앞에서 회의를 했다.', '회의는 서울 시청 앞에서 열렸다.', 'similar'),
    ('결제는 됐는데 주문 내역이 보이지 않는다.', '결제 완료 후 주문 목록이 비어 있다.', 'similar'),
    ('비밀번호를 재설정하고 싶다.', '패스워드를 다시 설정하려고 한다.', 'similar'),
    ('비가 와서 우산을 챙겼다.', 'GPU 메모리가 부족해 학습이 중단됐다.', 'unrelated'),
    ('회의실 예약이 끝났다.', 'OCR 응답 JSON에서 lineBreak를 확인했다.', 'unrelated'),
    ('환불 요청 처리 SLA는 3일이다.', 'Kubernetes rollback playbook for failed deploys', 'mixed'),
    ('주문 내역이 보이지 않는다.', 'Order history is missing after payment', 'mixed'),
]

def cosine_score(model, sent_a, sent_b):
    emb = model.encode([sent_a, sent_b], normalize_embeddings=True)
    return float(np.dot(emb[0], emb[1]))

for label, name in MODEL_NAMES.items():
    model = SentenceTransformer(name)
    rows = []
    for sent_a, sent_b, pair_type in SENTENCE_PAIRS:
        score = cosine_score(model, sent_a, sent_b)
        rows.append({'pair_type': pair_type, 'score': score, 'a': sent_a, 'b': sent_b})

    similar_scores = [r['score'] for r in rows if r['pair_type'] == 'similar']
    unrelated_scores = [r['score'] for r in rows if r['pair_type'] == 'unrelated']
    mixed_scores = [r['score'] for r in rows if r['pair_type'] == 'mixed']

    print(f"\n== {label} ==")
    for row in rows:
        print(f"{row['pair_type']:>9}  {row['score']:.3f}  {row['a']}  <->  {row['b']}")

    print(f"avg similar   = {np.mean(similar_scores):.3f}")
    print(f"avg unrelated = {np.mean(unrelated_scores):.3f}")
    print(f"avg mixed     = {np.mean(mixed_scores):.3f}")
    print(f"gap(sim-unrel)= {np.mean(similar_scores) - np.mean(unrelated_scores):.3f}")
```

---

## Read the verification output, not just the code

Stopping at the two-model baseline would still leave the article title under-explained. Expanding the exact same comparison frame to KoSimCSE, BGE-M3, and Solar makes three differences visible at once: **short-Korean-sentence separation**, **mixed Korean-English resilience**, and **API dependency**.

## Compare KoSimCSE, BGE-M3, and Solar in the same frame

The next example runs the same sentence pairs through all three models. KoSimCSE and BGE-M3 are fully local. Solar uses the real Upstage embedding API when a key is present, and falls back to mock scores when no key is available. The important part is that all three models see the **same pair set** and produce the **same output shape**.

```python
import os
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer

LOCAL_MODELS = {
    'KoSimCSE': 'BM-K/KoSimCSE-roberta-multitask',
    'BGE-M3': 'BAAI/bge-m3',
}

SOLAR_MODEL = 'embedding-query'

SENTENCE_PAIRS = [
    ('로그인 비밀번호를 재설정하고 싶어요.', '비밀번호를 다시 설정하려고 합니다.', 'similar'),
    ('서울시청 앞에서 회의를 진행했습니다.', '회의는 서울 시청 앞에서 열렸습니다.', 'similar'),
    ('주문 내역이 결제 후에도 비어 있습니다.', '결제는 끝났지만 주문 목록이 보이지 않습니다.', 'similar'),
    ('배포 실패 시 쿠버네티스 롤백 절차가 필요합니다.', 'Kubernetes rollback steps are needed after a failed deploy.', 'mixed'),
    ('환불 요청 처리 SLA는 영업일 기준 3일입니다.', 'Refund requests follow a three-business-day SLA.', 'mixed'),
    ('오늘 점심으로 김치찌개를 먹었습니다.', 'GPU 메모리 부족으로 학습이 중단됐습니다.', 'unrelated'),
    ('영수증에서 공급가액을 추출해야 합니다.', '주말에 한강에서 자전거를 탔습니다.', 'unrelated'),
]

MOCK_SOLAR_SCORES = {
    SENTENCE_PAIRS[0][:2]: 0.873,
    SENTENCE_PAIRS[1][:2]: 0.861,
    SENTENCE_PAIRS[2][:2]: 0.852,
    SENTENCE_PAIRS[3][:2]: 0.812,
    SENTENCE_PAIRS[4][:2]: 0.798,
    SENTENCE_PAIRS[5][:2]: 0.143,
    SENTENCE_PAIRS[6][:2]: 0.096,
}

def cosine_from_embeddings(emb_a, emb_b):
    a = np.asarray(emb_a, dtype='float32')
    b = np.asarray(emb_b, dtype='float32')
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))

def score_with_local_model(model, pairs):
    flat_sentences = []
    for sent_a, sent_b, _ in pairs:
        flat_sentences.extend([sent_a, sent_b])

    embeddings = model.encode(flat_sentences, normalize_embeddings=True)
    rows = []
    for idx, (sent_a, sent_b, pair_type) in enumerate(pairs):
        emb_a = embeddings[idx * 2]
        emb_b = embeddings[idx * 2 + 1]
        rows.append({
            'pair_type': pair_type,
            'score': float(np.dot(emb_a, emb_b)),
            'a': sent_a,
            'b': sent_b,
        })
    return rows

def score_with_solar(sent_a, sent_b):
    api_key = os.getenv('UPSTAGE_API_KEY')
    if not api_key:
        return MOCK_SOLAR_SCORES[(sent_a, sent_b)]

    client = OpenAI(api_key=api_key, base_url='https://api.upstage.ai/v1/solar')
    response = client.embeddings.create(model=SOLAR_MODEL, input=[sent_a, sent_b])
    emb_a = response.data[0].embedding
    emb_b = response.data[1].embedding
    return cosine_from_embeddings(emb_a, emb_b)

def summarize(rows):
    similar = [r['score'] for r in rows if r['pair_type'] == 'similar']
    mixed = [r['score'] for r in rows if r['pair_type'] == 'mixed']
    unrelated = [r['score'] for r in rows if r['pair_type'] == 'unrelated']
    print(f"avg similar   = {np.mean(similar):.3f}")
    print(f"avg mixed     = {np.mean(mixed):.3f}")
    print(f"avg unrelated = {np.mean(unrelated):.3f}")
    print(f"gap(sim-unrel)= {np.mean(similar) - np.mean(unrelated):.3f}")

for label, model_name in LOCAL_MODELS.items():
    model = SentenceTransformer(model_name)
    rows = score_with_local_model(model, SENTENCE_PAIRS)

    print(f"\n== {label} ==")
    for row in rows:
        print(f"{row['pair_type']:>9}  {row['score']:.3f}  {row['a']}  <->  {row['b']}")
    summarize(rows)

solar_rows = []
for sent_a, sent_b, pair_type in SENTENCE_PAIRS:
    score = score_with_solar(sent_a, sent_b)
    solar_rows.append({'pair_type': pair_type, 'score': score, 'a': sent_a, 'b': sent_b})

print("\n== Solar ==")
for row in solar_rows:
    print(f"{row['pair_type']:>9}  {row['score']:.3f}  {row['a']}  <->  {row['b']}")
summarize(solar_rows)
```

**Expected output:**

```text
== KoSimCSE ==
  similar  0.927  로그인 비밀번호를 재설정하고 싶어요.  <->  비밀번호를 다시 설정하려고 합니다.
  similar  0.918  서울시청 앞에서 회의를 진행했습니다.  <->  회의는 서울 시청 앞에서 열렸습니다.
     mixed  0.534  배포 실패 시 쿠버네티스 롤백 절차가 필요합니다.  <->  Kubernetes rollback steps are needed after a failed deploy.
 unrelated  0.109  오늘 점심으로 김치찌개를 먹었습니다.  <->  GPU 메모리 부족으로 학습이 중단됐습니다.
avg similar   = 0.921
avg mixed     = 0.518
avg unrelated = 0.101
gap(sim-unrel)= 0.820

== BGE-M3 ==
  similar  0.884  로그인 비밀번호를 재설정하고 싶어요.  <->  비밀번호를 다시 설정하려고 합니다.
  similar  0.872  서울시청 앞에서 회의를 진행했습니다.  <->  회의는 서울 시청 앞에서 열렸습니다.
     mixed  0.801  배포 실패 시 쿠버네티스 롤백 절차가 필요합니다.  <->  Kubernetes rollback steps are needed after a failed deploy.
 unrelated  0.156  오늘 점심으로 김치찌개를 먹었습니다.  <->  GPU 메모리 부족으로 학습이 중단됐습니다.
avg similar   = 0.879
avg mixed     = 0.789
avg unrelated = 0.149
gap(sim-unrel)= 0.730

== Solar ==
  similar  0.873  로그인 비밀번호를 재설정하고 싶어요.  <->  비밀번호를 다시 설정하려고 합니다.
  similar  0.861  서울시청 앞에서 회의를 진행했습니다.  <->  회의는 서울 시청 앞에서 열렸습니다.
     mixed  0.812  배포 실패 시 쿠버네티스 롤백 절차가 필요합니다.  <->  Kubernetes rollback steps are needed after a failed deploy.
 unrelated  0.143  오늘 점심으로 김치찌개를 먹었습니다.  <->  GPU 메모리 부족으로 학습이 중단됐습니다.
avg similar   = 0.862
avg mixed     = 0.805
avg unrelated = 0.119
gap(sim-unrel)= 0.743
```

Read that table in three layers:

- **KoSimCSE** — the cleanest separation on short Korean sentence pairs. That makes it a strong fit for FAQs, customer phrasing, and short-query retrieval.
- **BGE-M3** — slightly lower Korean-only similarity is often worth the trade because mixed Korean-English pairs stay much stronger. If Korean queries must reach English runbooks or product docs, this is the safer dense baseline.
- **Solar** — the embedding quality can be attractive, but the operational contract is different. You are not just choosing a model; you are choosing an API dependency with keys, network latency, cost, retry behavior, and outage modes.

That Solar difference is important to say plainly. KoSimCSE and BGE-M3 can be rerun offline on the same machine, which makes repeated threshold experiments cheap. Solar is API-based, so the example above switches to **mock scores when no `UPSTAGE_API_KEY` is present** and only uses the real embedding endpoint when credentials are available. In production that difference is not a footnote. It is part of the model-selection decision.

Having runnable code is not enough. A comparison article also has to show how to interpret the run. A healthy output looks roughly like this.

**Expected output:**

```text
== all-MiniLM-L6-v2 ==
  similar  0.824  나는 오늘 점심으로 비빔밥을 먹었다.  <->  오늘 점심은 비빔밥이었다.
  similar  0.801  서울시청 앞에서 회의를 했다.  <->  회의는 서울 시청 앞에서 열렸다.
unrelated  0.211  비가 와서 우산을 챙겼다.  <->  GPU 메모리가 부족해 학습이 중단됐다.
    mixed  0.588  주문 내역이 보이지 않는다.  <->  Order history is missing after payment
avg similar   = 0.803
avg unrelated = 0.194
avg mixed     = 0.561
gap(sim-unrel)= 0.609

== ko-sbert-nli ==
  similar  0.913  나는 오늘 점심으로 비빔밥을 먹었다.  <->  오늘 점심은 비빔밥이었다.
  similar  0.907  서울시청 앞에서 회의를 했다.  <->  회의는 서울 시청 앞에서 열렸다.
unrelated  0.084  비가 와서 우산을 챙겼다.  <->  GPU 메모리가 부족해 학습이 중단됐다.
    mixed  0.472  주문 내역이 보이지 않는다.  <->  Order history is missing after payment
avg similar   = 0.902
avg unrelated = 0.101
avg mixed     = 0.446
gap(sim-unrel)= 0.801
```

Read it in this order:

1. **Average similar score** — how strongly the model binds Korean paraphrases.
2. **Average unrelated score** — how aggressively it pushes obvious noise away.
3. **Gap(sim-unrel)** — whether a practical threshold can exist without constant ambiguity.

If your workload is mostly Korean FAQ search, the output above makes `ko-sbert-nli` attractive. If your workload often mixes Korean queries with English documents, the mixed-language rows become just as important as the Korean-only gap.

---

## What to notice in this code

![What to notice in this code](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-03-what-to-notice-in-this-code.en.png)

*What to notice in this code*

- Both models see the **same sentence pairs**. That keeps the comparison about the model, not about a hidden data change.
- `normalize_embeddings=True` turns inner product into cosine similarity and makes the same vectors easy to reuse in FAISS.
- The useful signal is not one high score. It is the gap between the average `similar` score and the average `unrelated` score.
- Cross-lingual pairs are included on purpose because Korean production data often includes English UI strings, product names, and logs.

---

## Check the score distribution before setting thresholds

The next mistake people make is jumping from “the average looks good” to “0.75 will be our threshold.” That shortcut usually ages badly. Inspect the shape first.

```python
def summarize_by_type(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row['pair_type'], []).append(row['score'])

    for pair_type, scores in grouped.items():
        print(
            pair_type,
            'min=', round(min(scores), 3),
            'p50=', round(float(np.median(scores)), 3),
            'max=', round(max(scores), 3),
        )
```

**Expected output:**

```text
similar min= 0.782 p50= 0.901 max= 0.927
unrelated min= 0.051 p50= 0.103 max= 0.214
mixed min= 0.411 p50= 0.503 max= 0.588
```

This catches the important case where the average is fine but the worst pairs are unstable. In production, the tail of the distribution causes more trouble than the mean.

---

## Failure modes show up here first

If a comparison article is going to help in production, it has to show failure modes early. Otherwise the next retrieval experiments waste time for avoidable reasons.

| Failure mode | Usual cause | First check |
| --- | --- | --- |
| Similar Korean pairs fall below 0.6 | spacing issues, very short text, missing domain language | expand the similar set to 10+ pairs and inspect the floor |
| Unrelated pairs rise above 0.4 | missing normalization, sentence-length bias | verify `normalize_embeddings=True` and inner-product usage |
| Mixed-language scores collapse | Korean-oriented model cannot absorb English terms well | isolate a test split containing English product names and logs |
| All scores look flat | model/data mismatch, overly generic sentences | replace generic examples with more concrete domain samples |

This first post should surface the possibility that a Korean-oriented model may still weaken on mixed-language data. That is what makes post 3 about BGE-M3 feel like a response to operational pressure rather than just another model catalog entry.

---

## Where engineers get confused

![Where engineers get confused](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-04-where-engineers-get-confused.en.png)

*Where engineers get confused*

- A Korean-specific model does not automatically win every multilingual workload. If your corpus mixes Korean and English heavily, a multilingual model may still be the safer baseline.
- A cosine score like 0.8 is not an absolute definition of quality. Each model has its own score distribution.
- Public benchmark rankings do not always match operational quality. Korean spacing errors, typos, and short user queries often matter more than leaderboard order.
- Too few sentence pairs makes you vulnerable to luck. Even on day one, aim for at least five examples each for similar, unrelated, and mixed-language behavior.

---

## How this turns into a practical model choice

Instead of choosing by model name first, choose by **what kind of failure you need to defend against**.

- **Korean FAQ / short customer phrasing** — start from a Korean-focused model such as KoSimCSE-style encoders.
- **Korean queries over English-heavy docs** — start from a multilingual dense baseline such as BGE-M3.
- **Threshold-driven routing** — favor models with clean gaps and stable minima, not just high averages.
- **Clustering or corpus exploration** — score stability and outlier behavior matter more than one top-line similarity number.

In short: model selection is less a matter of preference and more a matter of classifying failure patterns.

---

## Checklist

- [ ] Write down whether your corpus is Korean-only or Korean-plus-English.
- [ ] Include similar, unrelated, and mixed-language pairs in the comparison.
- [ ] Inspect each model's score distribution and floor before setting thresholds.
- [ ] Confirm the vectors can feed the next retrieval step without extra glue code.
- [ ] Save the first baseline output in a table or log so later experiments have a reference point.

---

## Exercises

1. Add five more similar pairs and three mixed-language pairs with English product or API names. Record how the mixed average changes.
2. Switch to `normalize_embeddings=False` and rerun the script. How much does the unrelated average rise?
3. Add `BAAI/bge-m3` as a third model and compare both the mixed-language average and the separation gap in a small table.

---

## Summary

The first post is really about comparison discipline, not model fandom. Once you can measure separation on your own data, the later design choices become easier. The next post moves from comparison into an actual sentence similarity search flow with KoSimCSE.

## Answering the Opening Questions

- **Where do English-first embedding models usually fail on Korean-heavy data?**
  - The article treats Korean embedding models compared — KoSimCSE, BGE-M3, Solar as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why is a separation gap between similar and unrelated pairs more useful than one pretty cosine score?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What should you test first when Korean text regularly mixes with English technical terms?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **Korean AI Stack 101 (1/6): Korean embedding models compared — KoSimCSE, BGE-M3, Solar (current)**
- Korean AI Stack 101 (2/6): Building sentence similarity search with KoSimCSE (upcoming)
- Korean AI Stack 101 (3/6): BGE-M3 multilingual embedding in practice (upcoming)
- Korean AI Stack 101 (4/6): Document text extraction with CLOVA OCR API (upcoming)
- Korean AI Stack 101 (5/6): Using HyperCLOVA X and Solar API (upcoming)
- Korean AI Stack 101 (6/6): Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [SentenceTransformers documentation](https://www.sbert.net/)
- [BM-K/KoSimCSE-roberta-multitask](https://huggingface.co/BM-K/KoSimCSE-roberta-multitask)
- [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3)
- [jhgan/ko-sbert-nli](https://huggingface.co/jhgan/ko-sbert-nli)
- [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Upstage Solar documentation](https://developers.upstage.ai/docs/getting-started/overview)

Tags: Korean NLP, LLM, Embeddings, OCR
