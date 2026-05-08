
# Completing the RAG Benchmark

## Questions this post answers

![Questions this post answers](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-01-questions-this-post-answers.en.png)

*Questions this post answers*

- How do we wire dataset → retrieval → generation → evaluation into a **single executable**?
- What separation do we need when merging retrieval metrics and RAGAS scores into one report?
- Which experimental knobs should be frozen first in the final pipeline benchmark?
- How do we attach the benchmark to CI so it blocks regressions automatically?

> A finished RAG benchmark is **not a single number**. It is a reproducible pipeline that splits retrieval and generation and runs them under the same fixed experimental conditions, on demand.

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

```
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

```
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

![End-to-end benchmark pipeline in one run](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-01-end-to-end-benchmark-pipeline-in-one-run.en.png)

*End-to-end benchmark pipeline in one run*

The runnable code lives at `rag-benchmark-101/en/06-benchmark-complete/main.py`. It expects `GROQ_API_KEY` to be set.

```bash
cd /root/Github/rag-benchmark-101/en/06-benchmark-complete
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

## In this series

- [Understanding RAG evaluation metrics](./01-evaluation-metrics.md)
- [Measuring retrieval performance](./02-retrieval-benchmarking.md)
- [Comparing embedding models](./03-embedding-comparison.md)
- [VectorDB selection criteria](./04-vectordb-selection.md)
- [End-to-end RAG pipeline evaluation](./05-e2e-evaluation.md)
- **Completing the RAG Benchmark (current)**

---

## References

- [RAGAS documentation](https://docs.ragas.io/)
- [LangChain retrieval overview](https://python.langchain.com/docs/concepts/retrieval/)
- [FAISS documentation](https://faiss.ai/)
- [GitHub Actions](https://docs.github.com/en/actions)

Tags: RAG, VectorDB, Benchmarking, LLM

---

© 2026 YeongseonBooks. All rights reserved.
