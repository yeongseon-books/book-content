---
title: "RAG Evaluation and Benchmarking 101 (6/6): Completing the RAG benchmark"
series: rag-benchmark-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- Benchmarking
- Pipeline
- CI
- Reproducibility
- Reporting
last_reviewed: '2026-05-01'
seo_description: Integrate RAG evaluation into a repeatable benchmark. Build a CI pipeline to compare results against baselines and detect regressions automatically.
---

# RAG Evaluation and Benchmarking 101 (6/6): Completing the RAG benchmark

A finished benchmark has to encode its experimental knobs in configuration and reproduce the same result from the same inputs. That is what turns scattered evaluation code into something you can use for regression checks, candidate comparison, and operational tracking.

This is the final post in the RAG Evaluation and Benchmarking 101 series.

![End-to-end benchmark pipeline in one run](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-01-end-to-end-benchmark-pipeline-in-one-run.en.png)
*End-to-end benchmark pipeline in one run*
> A finished RAG benchmark is **not a single number**. It is a reproducible pipeline that splits retrieval and generation and runs them under the same fixed experimental conditions, on demand.

## Questions to Keep in Mind

- What turns a one-off benchmark script into a repeatable decision tool?
- Which failure cases should an automatic report show beyond average scores?
- What regression thresholds should become blockers when the benchmark runs in CI?

## Why this matters

If we leave the tools we built so far scattered across notebooks, they will not actually drive decisions. Measurements that require a human to run them by hand eventually stop being run. When that happens, the perceived quality of a RAG system collapses back to "how the last few answers felt."

Wrapping the benchmark into one executable and emitting a standard report unlocks four things:

- **PR regression detection**: scores before and after a change are compared automatically.
- **Model and infrastructure decisions**: candidate embeddings, vector DBs, and LLMs are evaluated under identical conditions.
- **Operational monitoring**: a nightly job tracks the score trajectory.
- **Reproducibility**: six months later, the same command yields the same result.

The pipeline we build in this post is small, but it is the skeleton that supports all four.

## Mental model

A finished benchmark is a single function:

```text
run_benchmark(config) ──►  report
   │
   ├─ Phase 1: build retriever (corpus + embedding + index)
   ├─ Phase 2: run queries → collect (ranked_ids, latency, contexts)
   ├─ Phase 3: generate answers via LLM
   ├─ Phase 4: compute retrieval metrics (hit, MRR, latency)
   ├─ Phase 5: compute generation metrics (faithfulness, answer_relevancy)
   └─ Phase 6: emit report (JSON + per-question log)
```

`config` lists every variable: embedding model, top-k, LLM model, dataset path. The contract is simple: the same `config` must always produce the same numbers.

## Core concepts

| Item | Meaning |
| --- | --- |
| Run config | Every parameter needed for one benchmark execution (a dict or YAML file) |
| Run id | Unique identifier per execution (timestamp + git sha) |
| Report | Two parts: aggregate metrics and per-question log |
| Baseline | A previous run we compare against (typically the latest run on `main`) |
| Regression | A metric drop greater than the threshold versus baseline |

Splitting the report into aggregate and per-question pieces matters. With only the aggregate you cannot debug; with only the log you cannot compare quickly.

## Before vs. after

**Before**: PR authors open a notebook by hand to spot-check hit rate. Some PRs get checked, others do not. A month later we notice quality has dropped, but cannot tell which PR caused it.

**After**: every PR runs `python3 run_benchmark.py --config configs/ci.yaml` automatically and posts a one-line comparison against baseline as a comment.

```text
                  baseline  this PR  delta
hit_rate@3        0.94      0.96    +0.02 ✓
MRR               0.78      0.81    +0.03 ✓
faithfulness      0.91      0.84    -0.07 ✗
answer_relevancy  0.85      0.86    +0.01 ✓
avg_latency_ms    62.1      63.4    +1.3
```

A 0.07 drop in faithfulness fails the gate automatically. There is nothing for a human to forget.

## Step-by-step walkthrough

### Step 1 — Define the run config

```yaml
# configs/ci.yaml
corpus_path: "data/corpus.jsonl"
gold_set_path: "data/gold.jsonl"
embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
index_type: "IndexFlatIP"
top_k: 3
llm_model: "llama-3.1-8b-instant"
ragas_metrics: ["faithfulness", "answer_relevancy"]
```

### Step 2 — Write the integrated function

The runnable code lives at `rag-benchmark-101/en/06-benchmark-complete/main.py`. It expects `GROQ_API_KEY` to be set.

```bash
cd en/06-benchmark-complete
export GROQ_API_KEY=...
python3 main.py
```

```python
def run_benchmark(config):
    retriever = build_retriever(config)
    rows, retrieval_metrics = [], []

    for case in load_gold_set(config["gold_set_path"]):
        t0 = time.perf_counter()
        docs = retriever.invoke(case["question"])
        latency_ms = (time.perf_counter() - t0) * 1000

        ranked = [d.metadata["id"] for d in docs]
        contexts = [d.page_content for d in docs]
        retrieval_metrics.append({
            "hit": hit_rate(ranked, case["gold"]),
            "rr": reciprocal_rank(ranked, case["gold"]),
            "latency_ms": latency_ms,
        })

        answer = generate_answer(case["question"], contexts, config)
        rows.append({
            "question": case["question"],
            "contexts": contexts,
            "answer": answer,
            "ranked_ids": ranked,
        })

    ragas_scores = run_ragas(rows, config)
    return assemble_report(retrieval_metrics, ragas_scores, rows, config)
```

### Step 3 — Split the report

![Retrieval and generation report split](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-02-retrieval-and-generation-report-split.en.png)

*Retrieval and generation report split*

```python
def assemble_report(retrieval_metrics, ragas_scores, rows, config):
    return {
        "run_id": f"{datetime.utcnow():%Y%m%dT%H%M%S}-{git_sha()[:7]}",
        "config": config,
        "retrieval": {
            "hit_rate@k": mean([m["hit"] for m in retrieval_metrics]),
            "MRR": mean([m["rr"] for m in retrieval_metrics]),
            "avg_latency_ms": mean([m["latency_ms"] for m in retrieval_metrics]),
            "p95_latency_ms": percentile([m["latency_ms"] for m in retrieval_metrics], 95),
        },
        "generation": {
            "faithfulness": ragas_scores["faithfulness"],
            "answer_relevancy": ragas_scores["answer_relevancy"],
        },
        "per_question": rows,
    }
```

### Step 4 — Compare against the baseline

```python
def compare(report, baseline):
    deltas = {}
    for layer in ["retrieval", "generation"]:
        for k, v in report[layer].items():
            base = baseline[layer].get(k)
            if isinstance(v, (int, float)) and isinstance(base, (int, float)):
                deltas[f"{layer}.{k}"] = v - base
    return deltas
```

### Step 5 — The CI gate

![Branching search failures from generation failures](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-03-branching-search-failures-from-generatio.en.png)

*Branching search failures from generation failures*

```python
THRESHOLDS = {
    "retrieval.hit_rate@k": -0.02,
    "generation.faithfulness": -0.03,
}

def gate(deltas):
    failed = [k for k, t in THRESHOLDS.items() if deltas.get(k, 0) < t]
    if failed:
        sys.exit(f"Regression in: {failed}")
```

## Common mistakes

- **Collapsing into a single score** — a single weighted average hides which layer dropped. Keep retrieval and generation separated end to end.
- **Throwing away the per-question log** — keeping only aggregate scores makes it impossible to ask "why did it drop?" Always persist per-question rows alongside the summary.
- **Auto-bumping the baseline** — refreshing the baseline on every merge to `main` lets gradual regressions accumulate. Only bump it explicitly at release time.
- **Unfrozen config** — if `temperature`, `seed`, and `top_k` differ between notebooks, the comparison is meaningless. Put every variable in the config file.
- **Ignoring retry/timeout for hosted LLMs** — Groq, OpenAI, and friends occasionally return 502 or time out. Without retries and caching the CI becomes flaky.

## Field notes

![Baseline-to-decision benchmark loop](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-04-baseline-to-decision-benchmark-loop.en.png)

*Baseline-to-decision benchmark loop*

- **Embed git sha in the run id**: results and the code that produced them are tied 1:1.
- **Cost tracking**: include LLM token usage and an estimated USD cost in the report.
- **Parallel runs**: when the dataset grows, shard it and run chunks in parallel, then merge results. External parallelism is safer than relying solely on RAGAS' `max_workers`.
- **Caching**: reuse answers for `(question, context)` pairs you have seen before. CI cost drops sharply.
- **Dashboard**: load the report JSON into a time-series store (e.g. PostgreSQL + Grafana) to track 30/60/90-day trends.
- **Threshold tuning**: start with warnings, then promote to blocking after one to two weeks of stability.

## Checklist

- [ ] Retrieval and generation are measured in the same execution.
- [ ] Their scores are stored under separate keys.
- [ ] Run config lists embedding model, top-k, LLM model, and dataset path.
- [ ] Run id contains a timestamp plus git sha.
- [ ] Aggregate report and per-question log are persisted together.
- [ ] CI compares against the baseline and blocks when a threshold is crossed.
- [ ] Retries and timeouts are applied to all LLM calls.

## Exercises

1. Extend the function above to compare four combinations — two embedding models × two LLMs — in a single execution.
2. Add the git sha to the run id and run twice on the same sha. If the results differ, what residual non-determinism is leaking in?
3. Make the CI threshold a function of dataset size (for example, allow ±0.05 with 50 samples and ±0.02 with 500).

## Wrap-up — series finale

Across the six posts in this series we built:

| Post | Tool |
| --- | --- |
| 1 | Hand-computed intuition for hit rate / MRR / nDCG |
| 2 | Retrieval measurement loop on a single retriever |
| 3 | Embedding-model comparison helper (one variable at a time) |
| 4 | Flat vs. IVF comparison plus the recall/latency trade-off |
| 5 | RAGAS-driven faithfulness / answer_relevancy measurement |
| 6 | Integrated retrieval + generation + evaluation benchmark with a CI gate |

The recurring idea is **not a single fused number, but repeatable measurement under the same experimental conditions**. The goal of this series was to make it obvious which layer to fix when a RAG system's scores wobble.

Natural follow-ups from here include longer corpora (100k+), hybrid retrievers (BM25 + vector), rerankers, and multi-turn conversation evaluation.

## Locking the integrated benchmark into a production pipeline

At the series finale, the task shifts from "experiment code" to "production pipeline." The key is standardizing execution procedures and output formats so anyone can run the same benchmark the same way.

### Recommended directory structure

```text
rag-benchmark/
  configs/
    ci.yaml
    nightly.yaml
  data/
    corpus.jsonl
    gold_queries.jsonl
  reports/
    baseline.json
    latest.json
    history/
  src/
    run_benchmark.py
    compare_reports.py
    render_markdown.py
```

A fixed structure lets CI, local runs, and nightly batches share the same paths, reducing operational overhead.

### Required fields in the run configuration

```yaml
run:
  seed: 42
  sample_size: 200
  top_k: 5
retrieval:
  embedding_model: sentence-transformers/all-MiniLM-L6-v2
  index_type: ivf
  nprobe: 8
generation:
  llm_model: llama-3.1-8b-instant
  temperature: 0
evaluation:
  metrics: [faithfulness, answer_relevancy]
  max_workers: 1
  timeout_sec: 300
```

Recording `seed` and `sample_size` preserves comparability even in sampling-based evaluation.

### Integrated report JSON schema example

```json
{
  "run_id": "20260521T020500-1a2b3c4",
  "git_sha": "1a2b3c4d",
  "config_hash": "f2fcbf...",
  "retrieval": {
    "hit_rate@5": 0.93,
    "mrr": 0.79,
    "avg_latency_ms": 58.4,
    "p95_latency_ms": 91.2
  },
  "generation": {
    "faithfulness": 0.88,
    "answer_relevancy": 0.86
  },
  "cost": {
    "prompt_tokens": 421991,
    "completion_tokens": 109823,
    "estimated_usd": 7.42
  },
  "per_question": []
}
```

Adding `config_hash` lets you automatically detect whether two runs used the same conditions.

### Layer-separated regression gates

Judging regression with a single aggregate number is risky. Separate gates for retrieval and generation are necessary.

| Layer | Metric | Block threshold example |
| --- | --- | --- |
| Retrieval | hit_rate@5 | Drops > 0.03 below baseline |
| Retrieval | p95_latency_ms | Exceeds baseline by > 25 ms |
| Generation | faithfulness | Drops > 0.04 below baseline |
| Generation | answer_relevancy | Drops > 0.03 below baseline |

These rules watch quality degradation and latency increase simultaneously. Monitoring only one side misses the other.

### CI workflow example

```yaml
name: rag-benchmark-gate
on:
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python src/run_benchmark.py --config configs/ci.yaml --out reports/latest.json
      - run: python src/compare_reports.py --baseline reports/baseline.json --current reports/latest.json
```

This is the minimal structure. Production environments typically add caching, artifact uploads, and failure-sample log attachments.

### Generating a human-readable summary report

JSON alone makes collaboration difficult. Auto-generating a Markdown summary alongside raw data is highly effective.

```python
def render_summary_md(report: dict) -> str:
    return f"""
# RAG Benchmark Report

- run_id: {report['run_id']}
- retrieval.hit_rate@5: {report['retrieval']['hit_rate@5']:.3f}
- retrieval.mrr: {report['retrieval']['mrr']:.3f}
- generation.faithfulness: {report['generation']['faithfulness']:.3f}
- generation.answer_relevancy: {report['generation']['answer_relevancy']:.3f}
""".strip()
```

Post this summary as an auto-comment on PRs so reviewers grasp key changes without opening the raw JSON.

### Operational runbook items for the benchmark pipeline

The benchmark pipeline is itself a production system and needs incident-response procedures.

1. External LLM API timeout: check retry count and backoff policy
2. VectorDB connection failure: verify fallback index availability
3. Baseline file corruption: restore from last healthy run
4. Evaluation cost spike: switch to automatic sample-size reduction mode

Keep the runbook in the same repository as the benchmark code for fast on-call recovery.

### Accumulating reports on quarterly/monthly cadence

Single-run results cannot reveal trends. Store at least two axes to enable long-term quality management.

| Axis | Stored items |
| --- | --- |
| Branch/PR | Delta vs baseline, failed question list |
| Monthly trend | 7-day moving average, variance, regression frequency |

With accumulated trend data, "quality has been declining" becomes a statement backed by actual numbers rather than gut feeling.

## Appendix — integrated benchmark operational checkpoints

Finally, here are operational checkpoints for maintaining the integrated pipeline across an organization.

### Per-stage output conventions

| Stage | Output | Storage path example |
| --- | --- | --- |
| Retrieval run | Per-question ranked_ids, latency | `reports/run_id/retrieval.jsonl` |
| Generation run | Per-question answer, prompt tokens | `reports/run_id/generation.jsonl` |
| Evaluation run | faithfulness, answer relevancy | `reports/run_id/eval.jsonl` |
| Integrated report | Aggregate + delta + failure list | `reports/run_id/summary.json` |

Output conventions enable re-running only the failed stage during incidents.

### Including a reproduce command in every report

Without the following information, reproducing a failed run is difficult.

```text
reproduce_command:
python src/run_benchmark.py --config configs/ci.yaml --run-id 20260521T020500-1a2b3c4
```

A single-line command stored alongside results enables fast on-call reproduction.

### Cost guardrails

Teams often gate on quality regression but miss cost spikes. Add cost guardrails alongside quality gates.

| Item | Warn threshold | Block threshold |
| --- | ---: | ---: |
| Cost per run (USD) | +20% | +35% |
| Avg tokens per question | +15% | +25% |
| Projected monthly cost | 90% of budget | Over budget |

If these thresholds are crossed, even a quality improvement should trigger release re-review.

### Pre-deployment approval summary template

```text
Release Candidate Benchmark Review
- Retrieval: hit@5 0.93 (+0.01), MRR 0.80 (+0.02), p95 92ms (+4ms)
- Generation: faithfulness 0.89 (+0.01), answer_relevancy 0.87 (+0.00)
- Cost: +8.4% within budget
- Decision: PASS (no blocking regression)
```

A fixed approval template keeps release meetings numbers-driven.

### Common long-term maintenance issues

1. Baseline becomes stale and no longer reflects current data distribution
2. Evaluator model version changes make historical scores incomparable
3. Corpus refresh cycle drifts out of sync with benchmark cycle
4. Question sampling bias causes specific domain regressions to go undetected

Preventing these requires separate documented policies for baseline refresh, evaluator versioning, and data synchronization.

### Weekly operational checklist

- Review 7-day moving averages for faithfulness, MRR, and P95 latency.
- Classify common root causes across PRs blocked by regression gates.
- Check whether the top-20 failure questions cluster in the same domain.
- Verify evaluation cost is within budget norms.
- Decide whether a baseline refresh is needed and record the decision.

Performing this checklist regularly transforms the benchmark from a one-time event into a continuous quality management loop.

Additionally, schedule a quarterly dataset representativeness review. As product features change, user question distributions shift. An outdated question set cannot catch recent regressions. This review is not about reducing benchmark maintenance cost — it is about reducing operational risk from false confidence.

## Answering the Opening Questions

- **What turns a one-off benchmark script into a repeatable decision tool?**
  It needs a fixed dataset, version record, reproducible command, structured JSON output, readable report, and regression thresholds.

- **Which failure cases should an automatic report show beyond average scores?**
  Reports should show worst queries, score drops, latency increases, raw failures, and diffs from the previous run, not only averages.

- **What regression thresholds should become blockers when the benchmark runs in CI?**
  Block CI when key metrics such as Recall, MRR, faithfulness, or latency cross the agreed regression threshold.

<!-- toc:begin -->
## In this series

- [RAG Evaluation and Benchmarking 101 (1/6): Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [RAG Evaluation and Benchmarking 101 (2/6): Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [RAG Evaluation and Benchmarking 101 (3/6): Comparing embedding models](./03-embedding-comparison.md)
- [RAG Evaluation and Benchmarking 101 (4/6): VectorDB selection criteria](./04-vectordb-selection.md)
- [RAG Evaluation and Benchmarking 101 (5/6): End-to-end RAG pipeline evaluation](./05-e2e-evaluation.md)
- **RAG Evaluation and Benchmarking 101 (6/6): Completing the RAG benchmark (current)**

<!-- toc:end -->

---

## References

- [RAGAS documentation](https://docs.ragas.io/)
- [LangChain retrieval overview](https://python.langchain.com/docs/concepts/retrieval/)
- [FAISS documentation](https://faiss.ai/)
- [GitHub Actions](https://docs.github.com/en/actions)

Tags: RAG, VectorDB, Benchmarking, LLM
