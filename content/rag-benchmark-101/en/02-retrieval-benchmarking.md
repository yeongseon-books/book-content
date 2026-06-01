---
title: "RAG Evaluation and Benchmarking 101 (2/6): Measuring retrieval performance"
series: rag-benchmark-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- VectorDB
- Benchmarking
- Hit-Rate
- Latency
- MRR
last_reviewed: '2026-05-15'
seo_description: Build a RAG retrieval benchmark loop. Measure hit rate, MRR, and latency to quantify search performance before scaling to production.
---

# RAG Evaluation and Benchmarking 101 (2/6): Measuring retrieval performance

A retrieval benchmark works only when questions, gold documents, ranked results, and metrics stay in the same loop. Fix those inputs and you can tell whether a retriever change improved the system or just changed the feel of a few examples.

This is the 2nd post in the RAG Evaluation and Benchmarking 101 series.

![Benchmark loop for queries and latency](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/02/02-01-benchmark-loop-for-queries-and-latency.en.png)
*Benchmark loop for queries and latency*
> The core of retrieval benchmarking is not the vector DB or index. It is the **repeatable loop of query, gold document, and metric collection** that lets you observe the same retriever again and again.

## Questions to Keep in Mind

- What must stay fixed to turn retrieval performance from a feeling into a benchmark loop?
- What different aspects of a retriever do hit rate, MRR, and latency measure?
- Can a small gold set still create a meaningful regression check?

## Why this matters

In Episode 1 we worked through hit rate, MRR, and nDCG on paper. In a real RAG pipeline, the retriever drifts every time you change embeddings, chunk size, or the corpus. Without a measurement harness you end up making decisions on "this feels better".

Putting the metrics in code matters for three reasons. First, you catch **regressions** the moment you change embeddings or chunking. Second, the same loop in CI removes human bias. Third, recording latency together with quality stops you from shipping a change that improves recall but doubles response time.

The loop in this post is small but complete. Episodes 3 (embedding comparison) and 4 (vector DB selection) reuse the exact same skeleton.

## Mental model

A retrieval benchmark binds four things together:

```text
QUERIES (question + gold ids)
   │
   ▼
retriever.invoke(question)  ──►  ranked_ids  ──►  metric(ranked_ids, gold_ids)
   │                                                   │
   ▼                                                   ▼
latency_ms                                       hit_rate / MRR
```

The trick is wrapping a single arrow with measurement code. Wrap `retriever.invoke()` in a timer and you isolate retrieval latency. Normalize results to `metadata["id"]` and the metric function stops depending on the retriever type.

Hold this picture in your head and BM25, hybrid retrievers, or rerankers all plug into the same harness later.

## Core concepts

| Term | Meaning | Unit |
| --- | --- | --- |
| Gold set | Question + relevant document ids | number of queries |
| Hit rate@k | Fraction of queries where any gold id appears in top-k | 0.0 – 1.0 |
| MRR | Mean of 1/rank for the first gold hit | 0.0 – 1.0 |
| Retrieval latency | Time per `retriever.invoke()` call | milliseconds |
| p95 latency | 95th percentile of all latencies | milliseconds |

Average latency hides tail behavior. Always record p95 (and ideally p99) — that is the number your users feel.

## Before vs. after

**Before**: "Switching the embedding model felt better". The evidence is three or four queries tried by hand. A week later quality drops on a different domain and you cannot tell whether that change or some other change is the cause.

**After**: Both retrievers run against the same `QUERIES` list. You compare hit rate, MRR, mean latency, and p95 latency in a single line of output. If hit rate climbs from 0.9 to 1.0 but p95 latency jumps from 80 ms to 250 ms, you see the trade-off explicitly and decide on it.

## Step-by-step walkthrough

### Step 1 — Define the gold set

Write down questions paired with the ids of relevant documents. Three to five queries are plenty to start.

```python
QUERIES = [
    ("What distance does FAISS use by default?", {"doc-faiss-basics"}),
    ("What does MRR measure?", {"doc-mrr-intro"}),
    ("Why is chunk size important in RAG?", {"doc-chunking"}),
]
```

### Step 2 — Build the measurement loop

The runnable code lives in `rag-benchmark-101/en/02-retrieval-benchmarking/main.py`. Episodes 05 and 06 require `GROQ_API_KEY`.

```bash
cd en/02-retrieval-benchmarking
python3 main.py
```

```python
import time
import numpy as np

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
latencies_ms = []
all_ranked = []

for question, _ in QUERIES[:1]:
    retriever.invoke(question)  # warm-up

for question, relevant_ids in QUERIES:
    started_at = time.perf_counter()
    docs = retriever.invoke(question)
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    ranked_ids = [doc.metadata["id"] for doc in docs]
    latencies_ms.append(elapsed_ms)
    all_ranked.append((question, ranked_ids, relevant_ids))

p95_latency_ms = float(np.percentile(latencies_ms, 95))
```

The warm-up call is not cosmetic. The first call often includes model load, cache misses, or lazy initialization. If you skip warm-up, your numbers describe startup behavior instead of the steady-state path users hit all day.

### Step 3 — Compute the metrics

![Retrieval quality axes with hit rate and MRR](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/02/02-02-retrieval-quality-axes-with-hit-rate-and.en.png)

*Retrieval quality axes with hit rate and MRR*

```python
def hit_rate(ranked, gold):
    return 1.0 if any(d in gold for d in ranked) else 0.0

def reciprocal_rank(ranked, gold):
    for idx, doc_id in enumerate(ranked, start=1):
        if doc_id in gold:
            return 1.0 / idx
    return 0.0

hits = [hit_rate(r, g) for _, r, g in all_ranked]
rrs = [reciprocal_rank(r, g) for _, r, g in all_ranked]

print(f"hit_rate@3 = {sum(hits)/len(hits):.2f}")
print(f"MRR        = {sum(rrs)/len(rrs):.2f}")
print(f"avg latency = {sum(latencies_ms)/len(latencies_ms):.1f} ms")
print(f"p95 latency = {p95_latency_ms:.1f} ms")
```

### Step 4 — Record the result

Keep the per-query ranked ids in the log. Storing only averages makes regressions impossible to debug — you cannot tell which query collapsed.

```python
report_rows = []
for question, ranked_ids, relevant_ids in all_ranked:
    report_rows.append({
        "question": question,
        "ranked_ids": ranked_ids,
        "relevant_ids": sorted(relevant_ids),
        "hit": hit_rate(ranked_ids, relevant_ids),
        "rr": reciprocal_rank(ranked_ids, relevant_ids),
    })

summary = {
    "hit_rate@3": round(sum(hits) / len(hits), 2),
    "MRR": round(sum(rrs) / len(rrs), 2),
    "avg_latency_ms": round(sum(latencies_ms) / len(latencies_ms), 1),
    "p95_latency_ms": round(p95_latency_ms, 1),
}

print(summary)
for row in report_rows:
    print(row)
```

```text
{'hit_rate@3': 0.67, 'MRR': 0.56, 'avg_latency_ms': 4.8, 'p95_latency_ms': 6.1}
{'question': 'What distance does FAISS use by default?', 'ranked_ids': ['doc-faiss-basics', 'doc-ann-overview', 'doc-chunking'], 'relevant_ids': ['doc-faiss-basics'], 'hit': 1.0, 'rr': 1.0}
{'question': 'What does MRR measure?', 'ranked_ids': ['doc-bm25', 'doc-mrr-intro', 'doc-ranking'], 'relevant_ids': ['doc-mrr-intro'], 'hit': 1.0, 'rr': 0.5}
```

That output already tells you what to try next. If hit rate is 1.0 but reciprocal rank is 0.5, the retriever is finding the right document but ranking it too low. That points to ranking quality, not coverage.

### Step 5 — Turn benchmark output into a triage order

| What you observe | First thing to inspect | Common root cause |
| --- | --- | --- |
| Low hit rate, healthy latency | embedding model, chunking, query formulation | relevant docs are missing entirely |
| High hit rate, low MRR | reranker, score fusion, top-k order | the right doc is present but too low |
| Healthy quality, bad p95 | infrastructure, caching, network path | a tail-latency issue rather than retrieval quality |
| Good average, one broken query | per-query rows | domain mismatch or gold-set labeling issue |

This is where the benchmark becomes operationally useful. It stops being just a scoreboard and starts acting like a debugger.

## Common mistakes

![High hit rate with weak ranking](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/02/02-03-high-hit-rate-with-weak-ranking.en.png)

*High hit rate with weak ranking*

- **Trusting hit rate alone** — hit rate of 1.0 with MRR of 0.4 means the gold doc is always near the bottom. Users only see the first answer.
- **Mixing embedding time into retrieval latency** — if you wrap embedding and retrieval in one timer you lose the signal for the retriever itself.
- **Using `time.time()`** — it is sensitive to system clock changes. Always use `time.perf_counter()` for short intervals.
- **Counting the first call** — the first call carries model load and cache warming. Run a warm-up iteration or two before measuring.
- **Generalizing from a tiny corpus** — a 5-document corpus that scores 1.0 will not behave the same in production. At this stage you are validating the **measurement loop itself**, not the retriever.

## In production

As the harness grows, capture more context.

- **Version metadata**: embedding model name, chunk size, retriever type, corpus hash. Without these the run is not reproducible.
- **p95 / p99 latency**: average is dragged down by fast calls. Use `numpy.percentile(latencies_ms, 95)`.
- **CI gate**: fail PRs when hit rate drops below threshold or p95 exceeds budget. Start as a warning, then promote to a block once stable.
- **Sampling strategy**: when the gold set grows to hundreds of items, run a stratified 50–100 sample on every PR and the full set in a nightly job.

## Checklist

![Benchmark record with gold IDs and logs](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/02/02-04-benchmark-record-with-gold-ids-and-logs.en.png)

*Benchmark record with gold IDs and logs*

- [ ] Wrote down relevant document ids per query.
- [ ] Wrapped only `retriever.invoke()` to isolate retrieval latency.
- [ ] Reported hit rate, MRR, mean latency, and p95 latency together.
- [ ] Kept per-query ranked ids in the output.
- [ ] Logged the embedding model, chunk size, and k used in the run.

## Exercises

1. Modify the loop to print hit rate at `k=1`, `k=3`, and `k=5` in one pass. How does hit rate move with k? What about MRR?
2. Replace `time.perf_counter()` with `time.time()`. Read the docs and describe a scenario where the measurement would be wrong.
3. Add a single warm-up call before the loop. Compare the first measured latency with and without warm-up.

## Wrap-up · what's next

This post lifted the hand-written metrics onto a real retriever and produced a single loop that captures hit rate, MRR, and latency together. The skeleton is the foundation for every comparison experiment that follows.

In Episode 3 we swap the embedding model on top of the same loop. The code change is a single line, but interpreting the result needs care.

## Pinning the benchmark input file format

The most common reproducibility failure in retrieval experiments is the question set changing between runs. Lock queries and gold document IDs in JSONL.

```json
{"query_id":"q-001","question":"What does MRR measure?","relevant_ids":["doc-mrr-01"]}
{"query_id":"q-002","question":"Why does IVF need nprobe?","relevant_ids":["doc-ivf-02","doc-ivf-03"]}
{"query_id":"q-003","question":"What happens with large chunk sizes in RAG?","relevant_ids":["doc-chunk-04"]}
```

At execution time, record the input file hash in the report.

```python
import hashlib
from pathlib import Path

def file_sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

meta = {
    "gold_set_path": "data/gold_queries.jsonl",
    "gold_set_sha256": file_sha256("data/gold_queries.jsonl"),
}
```

Without this metadata, you cannot tell whether a score difference is caused by code changes or input changes.

### Per-segment hit rate

A single average hit rate hides domain-specific regressions. Tag each query with a `segment` and compute group-level metrics.

| Segment | Example query | hit@3 | MRR | Interpretation |
| --- | --- | ---: | ---: | --- |
| Concept definition | "What is RAGAS faithfulness?" | 0.95 | 0.86 | Stable |
| Operational config | "IVF nprobe tuning" | 0.78 | 0.62 | Config doc retrieval weak |
| Incident response | "Search latency spike handling" | 0.64 | 0.49 | Runbook retrieval failing |

This table lets product and ops teams derive action items from the same report.

### Isolating latency measurement boundaries

For latency numbers to be trustworthy, clearly delineate what is included.

```text
[Included]   retriever.invoke(question)
[Excluded]   question loading, embedding model init, result serialization, log upload
```

When using a server-mode VectorDB, network RTT dominates. Record network context alongside latency.

```yaml
environment:
  region: us-east-1
  client_host: bench-runner-01
  vectordb_endpoint: qdrant.internal:6333
  transport: http
  tls: false
```

### CI regression comparison script

Compare the previous run to the current run and gate on key metrics.

```python
import json
import sys

THRESHOLDS = {
    "hit_rate@3": -0.02,
    "MRR": -0.03,
    "p95_latency_ms": 8.0,
}

before = json.load(open("reports/baseline.json", "r", encoding="utf-8"))
after = json.load(open("reports/current.json", "r", encoding="utf-8"))

delta_hit = after["aggregate"]["hit_rate@3"] - before["aggregate"]["hit_rate@3"]
delta_mrr = after["aggregate"]["MRR"] - before["aggregate"]["MRR"]
delta_p95 = after["aggregate"]["p95_latency_ms"] - before["aggregate"]["p95_latency_ms"]

if delta_hit < THRESHOLDS["hit_rate@3"] or delta_mrr < THRESHOLDS["MRR"] or delta_p95 > THRESHOLDS["p95_latency_ms"]:
    print("FAIL: retrieval benchmark regression")
    sys.exit(1)

print("PASS: retrieval benchmark thresholds satisfied")
```

This turns the team conversation from "looks good" to "passed the gate."

## Operational benchmark settings and log format

Running retrieval benchmarks as a shared team pipeline requires standardized execution config and log format.

### Execution config YAML

```yaml
benchmark:
  top_k: 5
  warmup_queries: 5
  repeats_per_query: 3
  sample_size: 120
retriever:
  type: faiss
  embedding_model: sentence-transformers/all-MiniLM-L6-v2
  search_kwargs:
    k: 5
latency:
  percentile: [50, 95]
  include_network_rtt: true
report:
  save_json: true
  save_csv: true
  out_dir: reports/retrieval
```

### Per-query log CSV columns

| Column | Description |
| --- | --- |
| run_id | Run identifier |
| query_id | Query ID |
| question | Original question text |
| ranked_ids | Top document IDs |
| relevant_ids | Gold document IDs |
| hit@k | Hit indicator |
| rr | Reciprocal rank |
| latency_ms | Retrieval latency |

Saving CSV alongside JSON lets non-engineering teammates inspect results without Python.

### Latency distribution summary

Even without charts, a text summary enables trend analysis.

```text
latency summary (ms)
  min: 3.1
  p50: 5.4
  p95: 12.8
  p99: 19.2
  max: 27.7
```

### Regression diagnosis sequence

1. Start with queries where `Recall@k = 0`.
2. Compare `ranked_ids` against `relevant_ids` for those queries.
3. Group common failure topics (abbreviations, product names, version strings).
4. Prioritize query expansion or metadata enrichment experiments.

Following this sequence as a standard procedure keeps response time consistent when regressions appear.

### Cross-run comparison table

| run_id | retriever | top_k | hit@5 | MRR | p95 (ms) |
| --- | --- | ---: | ---: | ---: | ---: |
| r-20260521-a | bm25 | 5 | 0.81 | 0.63 | 21.4 |
| r-20260521-b | faiss-flat | 5 | 0.90 | 0.77 | 34.8 |
| r-20260521-c | hybrid | 5 | 0.93 | 0.80 | 39.2 |

Accumulating this table on the same query set lets the team choose retrievers by whether the priority is quality or latency.

---

## Answering the Opening Questions

- **What must stay fixed to turn retrieval performance from a feeling into a benchmark loop?**
  Fix the question set, gold document ids, evaluation k, corpus version, and metric code so changes can be compared fairly.

- **What different aspects of a retriever do hit rate, MRR, and latency measure?**
  Hit rate measures whether any relevant document appeared, MRR measures first-hit rank, and latency measures retrieval time. Together they show quality-speed tradeoffs.

- **Can a small gold set still create a meaningful regression check?**
  A small gold set is useful for regression detection if it covers important cases, but its coverage limits must be stated.

<!-- toc:begin -->
## In this series

- [RAG Evaluation and Benchmarking 101 (1/6): Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- **RAG Evaluation and Benchmarking 101 (2/6): Measuring retrieval performance (current)**
- RAG Evaluation and Benchmarking 101 (3/6): Comparing embedding models (upcoming)
- RAG Evaluation and Benchmarking 101 (4/6): VectorDB selection criteria (upcoming)
- RAG Evaluation and Benchmarking 101 (5/6): End-to-end RAG pipeline evaluation (upcoming)
- RAG Evaluation and Benchmarking 101 (6/6): Completing the RAG benchmark (upcoming)

<!-- toc:end -->

---

## References

- [LangChain FAISS integration](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [FAISS documentation](https://faiss.ai/)
- [Python `time.perf_counter`](https://docs.python.org/3/library/time.html#time.perf_counter)
- [BEIR: heterogeneous benchmark for IR](https://github.com/beir-cellar/beir)

Tags: RAG, VectorDB, Benchmarking, LLM
