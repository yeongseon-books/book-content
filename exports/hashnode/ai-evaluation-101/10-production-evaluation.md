
# Continuous Evaluation in Production

> AI Evaluation 101 Series (10/10)

Evaluation is not a one-shot pre-deploy check; it must run continuously in production. This post covers sampling evaluation cases from production traces, monitoring online metrics, and detecting drift.

---
![Continuous evaluation in production](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/10/10-01-continuous-evaluation-in-production.en.png)

*Continuous evaluation in production*
## Deployment Is Where It Starts

![Deployment is where it starts](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/10/10-02-deployment-is-where-it-starts.en.png)

*Deployment is where it starts*
Pre-deployment evaluation is a controlled simulation. Real users send unexpected inputs, model providers silently update their models, and data distributions drift over time. When evaluation stops at deployment, quality regressions go unnoticed.

This post covers:

- Production trace sampling strategies
- Online metric collection (feedback, latency, re-ask rate)
- Drift detection for input/output distribution shifts
- Shadow mode for safe model rollout
- Baseline-relative alert thresholds
- Cost monitoring for evaluation itself

This is the final episode, connecting the previous nine into a continuous operational cycle.

---

## Section 1 — Production Trace Sampling

![Section 1 - production trace sampling](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/10/10-03-section-1-production-trace-sampling.en.png)

*Section 1 - production trace sampling*
Evaluating every production request is prohibitively expensive. You need to sample, but without bias.

### Uniform sampling

```python
import random

def uniform_sample(traces: list[dict], rate: float = 0.01) -> list[dict]:
    """Pick `rate` fraction of traces uniformly."""
    return [t for t in traces if random.random() < rate]

# 1% of 100k daily requests = 1,000 traces for evaluation
sampled = uniform_sample(today_traces, rate=0.01)
```

Simple, but rare categories (medical, legal queries) are barely represented.

### Stratified sampling

Guarantee a minimum N per category:

```python
from collections import defaultdict

def stratified_sample(traces: list[dict], per_category: int = 50) -> list[dict]:
    buckets = defaultdict(list)
    for t in traces:
        buckets[t["category"]].append(t)
    sampled = []
    for cat, items in buckets.items():
        n = min(per_category, len(items))
        sampled.extend(random.sample(items, n))
    return sampled
```

Now you can track quality even in low-volume slices.

### Failure-biased sampling

Prioritize traces with low confidence, short responses, or thumbs-down feedback. Spend the evaluation budget where problems likely exist.

```python
def failure_biased_sample(traces, rate_pass=0.005, rate_fail=0.5):
    sampled = []
    for t in traces:
        threshold = rate_fail if t.get("user_feedback") == "down" else rate_pass
        if random.random() < threshold:
            sampled.append(t)
    return sampled
```

---

## Section 2 — Online Metric Collection

![Section 2 - online metric collection](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/10/10-04-section-2-online-metric-collection.en.png)

*Section 2 - online metric collection*
Heavy LLM-as-judge evaluation runs daily. Lightweight online signals run in real time.

| Metric | Meaning | How to measure |
| --- | --- | --- |
| Thumbs up/down rate | Direct user feedback | UI button click logging |
| Re-ask rate | Same user repeats a similar question within 5 minutes | session id + query similarity |
| Conversation length | Turns to complete a task | session log aggregation |
| Latency p50 / p95 | Response speed | per-request timestamps |
| Cost per request | Tokens × price | usage field aggregation |

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TraceMetric:
    trace_id: str
    timestamp: datetime
    latency_ms: int
    input_tokens: int
    output_tokens: int
    user_feedback: str | None  # "up", "down", None
    re_asked: bool

def daily_summary(metrics: list[TraceMetric]) -> dict:
    n = len(metrics)
    return {
        "total": n,
        "thumbs_down_rate": sum(1 for m in metrics if m.user_feedback == "down") / n,
        "re_ask_rate": sum(1 for m in metrics if m.re_asked) / n,
        "p95_latency_ms": sorted(m.latency_ms for m in metrics)[int(n * 0.95)],
        "avg_cost_usd": sum(m.input_tokens * 0.000005 + m.output_tokens * 0.000015 for m in metrics) / n,
    }
```

Online metrics are an **early warning system**. Judge evaluations run daily because they are expensive; online metrics run by the minute.

---

## Section 3 — Drift Detection

![Section 3 - drift detection](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/10/10-05-section-3-drift-detection.en.png)

*Section 3 - drift detection*
When the input distribution changes (user behavior shift, new traffic source), your existing evaluation set no longer reflects production quality.

### Input distribution comparison — KL divergence

```python
import math
from collections import Counter

def kl_divergence(p: dict[str, float], q: dict[str, float], eps: float = 1e-9) -> float:
    """KL(P || Q): how much P diverges from Q."""
    total = 0.0
    for key, p_val in p.items():
        q_val = q.get(key, eps)
        total += p_val * math.log((p_val + eps) / (q_val + eps))
    return total

def category_distribution(traces: list[dict]) -> dict[str, float]:
    counts = Counter(t["category"] for t in traces)
    n = sum(counts.values())
    return {k: v / n for k, v in counts.items()}

baseline = category_distribution(traces_last_week)
current = category_distribution(traces_today)
drift = kl_divergence(current, baseline)

if drift > 0.1:
    alert("Input distribution drift detected")
```

A KL value above 0.1 indicates meaningful shift. Calibrate the threshold by measuring 30 days of baseline volatility first.

### Output drift

If response length, refusal rate, or tone changes for a fixed input category, the provider may have silently updated the model.

```python
def refusal_rate(traces: list[dict]) -> float:
    refusals = sum(1 for t in traces if "I cannot" in t["output"] or "I'm sorry" in t["output"])
    return refusals / len(traces)
```

Silent provider updates are invisible without monitoring.

---

## Section 4 — Shadow Mode and Canary

Before sending users to a new model or prompt, run it in **shadow mode** alongside the current one.

```python
async def shadow_call(input_text: str):
    """Serve from the primary model, log a shadow call to the candidate."""
    primary = await call_model("gpt-4o", input_text)
    asyncio.create_task(log_shadow(input_text, primary))
    return primary

async def log_shadow(input_text: str, primary_output: str):
    shadow = await call_model("gpt-4o-mini", input_text)
    await db.insert_shadow_comparison({
        "input": input_text,
        "primary": primary_output,
        "shadow": shadow,
        "timestamp": datetime.utcnow(),
    })
```

Run pairwise LLM-as-judge (Ep4) on shadow records and you can measure the candidate's win rate without exposing users to risk. Canary takes the next step: route 5% of real traffic to the candidate and compare online metrics.

---

## Section 5 — Alert Threshold Design

Fixed thresholds (`thumbs_down_rate > 5%`) are dangerous. Baselines vary by category, weekday, and hour.

### Baseline-relative thresholds

```python
def relative_alert(current: float, baseline_mean: float, baseline_std: float, k: float = 3.0) -> bool:
    """Alert when current value is more than k std from baseline mean."""
    return abs(current - baseline_mean) > k * baseline_std

# Learn baseline from past 30 days
baseline_mean = 0.03
baseline_std = 0.008
if relative_alert(today_rate, baseline_mean, baseline_std):
    page_oncall("thumbs_down_rate anomaly")
```

A 3-sigma rule fires only ~0.27% of the time under a normal baseline, which keeps false positives manageable.

### Avoid alert fatigue

Group repeated alerts within an hour. Separate severity levels (warning vs page). If on-call wakes up for every blip, every alert eventually gets ignored.

---

## Section 6 — Evaluation Cost Monitoring

LLM-as-judge has a per-call cost. Without monitoring, evaluation cost can exceed serving cost.

```python
@dataclass
class JudgeUsage:
    date: str
    judge_calls: int
    judge_cost_usd: float
    serving_cost_usd: float

def cost_ratio_alert(usage: JudgeUsage, max_ratio: float = 0.1):
    ratio = usage.judge_cost_usd / usage.serving_cost_usd
    if ratio > max_ratio:
        alert(f"Judge cost is {ratio:.1%} of serving cost — exceeds {max_ratio:.0%} budget")
```

When evaluation cost exceeds 10% of serving cost, lower the sampling rate or switch to a cheaper judge model.

---

## Section 7 — Recycling Production Failures into Regression Sets

Failures discovered in production (low rating, re-ask, escalation) are the most valuable evaluation data you have. Add them to the regression set from Ep8 so the next deploy automatically guards against them.

```python
def harvest_failures_to_regression_set(failed_traces: list[dict], regression_path: str):
    new_cases = [
        {
            "input": t["input"],
            "expected": t.get("ground_truth") or "TBD - human label needed",
            "category": t["category"],
            "source": "production_failure",
            "harvested_at": datetime.utcnow().isoformat(),
        }
        for t in failed_traces
    ]
    with open(regression_path, "a") as f:
        for case in new_cases:
            f.write(json.dumps(case) + "\n")
```

Closing this loop turns production → regression set → next deploy → production into an automated cycle. Every failure becomes a permanent asset.

---

## Common Mistakes

1. **Uniform sampling only** — rare categories become invisible. Combine stratified and failure-biased sampling.
2. **Fixed-threshold alerts** — ignoring category and time-of-day patterns produces false positives that erode trust.
3. **Relying on judge alone** — judges cannot run by the minute. Pair them with lightweight signals like thumbs and re-ask.
4. **Logging shadow mode without analyzing it** — collection without comparison is wasted I/O. Schedule weekly win-rate reviews.
5. **Not tracking evaluation cost** — judge calls quietly outgrow serving cost. Cost is a metric too.

---

## Key Takeaways

- **Production trace sampling** combines uniform, stratified, and failure-biased strategies.
- **Online metrics** (thumbs, re-ask, latency, cost) are the early-warning layer above judge evaluation.
- **Drift detection** uses KL divergence on inputs and refusal rate on outputs.
- **Shadow mode and canary** validate new models without exposing users.
- **Baseline-relative alerts** (mean ± 3σ) outperform fixed thresholds.
- **Recycle production failures into regression sets** to close the evaluation-deployment loop.

Evaluation is not a pre-deployment milestone. It is a continuous operational discipline. This concludes the AI Evaluation 101 series.

---

## AI Evaluation 101 Series

- [Why Evaluate LLM Apps](./01-why-evaluate-llm-apps.md)
- [Evaluation Dataset Design](./02-evaluation-dataset-design.md)
- [Deterministic Metrics — Exact Match, BLEU, ROUGE](./03-deterministic-metrics.md)
- [LLM-as-Judge — Evaluating Models with Models](./04-llm-as-judge.md)
- [Rubric-Based Multi-Dimensional Scoring](./05-rubric-based-scoring.md)
- [RAG Evaluation](./06-rag-evaluation.md)
- [Agent Evaluation](./07-agent-evaluation.md)
- [Regression Testing](./08-regression-testing.md)
- [A/B Testing LLMs](./09-ab-testing-llms.md)
- **Continuous Evaluation in Production (current)**
## References

- [OpenAI Evals — Production Monitoring Patterns](https://github.com/openai/evals)
- [LangSmith Online Evaluations](https://docs.smith.langchain.com/observability/how_to_guides/online_evaluations)
- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Evidently AI — Data Drift Detection](https://docs.evidentlyai.com/presets/data-drift)

Tags: AI Evaluation, Production, Drift Detection, Monitoring

---

© 2026 YeongseonBooks. All rights reserved.
