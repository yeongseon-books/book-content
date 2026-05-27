---
title: "AI Evaluation 101 (8/10): Regression Testing — Don't Let Yesterday's Wins Break Today"
series: ai-evaluation-101
episode: 8
language: en
status: content-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- Regression Testing
- CI
- GitHub Actions
last_reviewed: '2026-05-14'
seo_description: Changing one line of a prompt can break other cases. This post covers
  a CI-integrated LLM regression test suite, golden datasets, and…
---

# AI Evaluation 101 (8/10): Regression Testing — Don't Let Yesterday's Wins Break Today

Changing one line of a prompt can break other cases.

This is the 8th post in the AI Evaluation 101 series. Here we cover a CI-integrated LLM regression test suite, golden datasets, and threshold-based failure policies.


![Regression testing - Don't let Yesterday's wins break today](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/08/08-01-regression-testing-don-t-let-yesterday-s.en.png)
*Regression testing - Don't let Yesterday's wins break today*
> Regression testing is not a one-time evaluation ritual; it is the guardrail that protects quality whenever change enters.

## Questions to Keep in Mind

- Why should regression testing move LLM evaluation from a pre-release event into the PR gate?
- What changes should the golden dataset and thresholds block?
- What tolerance and fail policy are needed when non-determinism makes evals noisy?

## Evaluate Every Time, Not Just Once

![Evaluate every Time, not just once](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/08/08-02-evaluate-every-time-not-just-once.en.png)

*Evaluate every Time, not just once*
Ep1-Ep7 covered evaluation methods. But **when** do you run them? The common pattern:

- Run once after a big prompt change
- Run once when switching models
- Otherwise forget

The problem is that **regressions reach production**. Yesterday's good answers are worse today, and nobody notices. Evaluation must run **like unit tests, automatically on every PR**.

This post covers:

- Golden dataset design
- Thresholds and fail policy
- GitHub Actions integration
- What to do when a regression fires

---

## Golden Dataset — The Tests That Should Never Move

![Golden dataset - the tests that should never move](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/08/08-03-golden-dataset-the-tests-that-should-nev.en.png)

*Golden dataset - the tests that should never move*
A regression dataset is different from your production eval dataset (Ep2).

| | Production eval (Ep2) | Regression (Ep8) |
|---|----------------------|------------------|
| Size | 100-1000 | 20-50 |
| Churn | Add monthly | Almost never |
| Purpose | Overall quality | Block core regressions |
| Cost | $10-100 per run | $0.50-5 per PR |

**Selection criteria**:
1. **Top 20% of usage** — most common query patterns
2. **Past regression cases** — inputs that have broken before
3. **Edge cases** — empty, very long, multilingual, ambiguous intent

```python
# regression/golden_dataset.py
import json

GOLDEN = [
    # Top usage cases
    {"id": "freq-001", "input": "today's weather", "expected_intent": "weather_query"},
    {"id": "freq-002", "input": "change my password", "expected_intent": "account_password"},

    # Past regressions (with commit reference)
    {"id": "reg-001", "input": "where is my order?",
     "expected_contains": ["order", "status"],
     "note": "v1.2 returned 'item' instead of 'order' (PR #234)"},

    # Edge cases
    {"id": "edge-001", "input": "", "expected_behavior": "ask_clarification"},
    {"id": "edge-002", "input": "asdfgh", "expected_behavior": "ask_clarification"},
    {"id": "edge-003", "input": "Hi! I'm John. Actually I'm Mike. No wait, Sarah.",
     "expected_behavior": "ask_clarification"},
]

with open("regression/golden.jsonl", "w") as f:
    for item in GOLDEN:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
```

**Rule**: keep Golden at **20-50 items**. Larger sets make every PR slow and expensive.

---

## Thresholds and Fail Policy

![Thresholds and fail policy](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/08/08-04-thresholds-and-fail-policy.en.png)

*Thresholds and fail policy*
A score is not enough. You must define **what counts as fail**.

```python
# regression/thresholds.py
THRESHOLDS = {
    "exact_match":  0.80,   # Ep3
    "bleu":         0.40,
    "judge_score":  4.0,    # Ep4 on 1-5 scale
    "faithfulness": 0.85,   # Ep6 RAG
    "task_success": 0.90,   # Ep7 agent
}

FAIL_POLICY = "any"  # "any" | "majority" | "weighted"
```

Three fail policies compared:

| Policy | Meaning | Pro | Con |
|--------|---------|-----|-----|
| `any` | Any metric below threshold → fail | Safe | Many false positives |
| `majority` | Majority below → fail | Balanced | Misses single sharp drops |
| `weighted` | Weighted average below → fail | Domain-tuned | Requires weight tuning |

**Recommendation**: start with `any`. If false positives are noisy, move to `weighted`.

---

## CI Integration — GitHub Actions

![CI integration - GitHub actions](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/08/08-05-ci-integration-github-actions.en.png)

*CI integration - GitHub actions*
A workflow that runs evaluation on every PR:

```yaml
# .github/workflows/eval.yml
name: Regression Eval
on:
  pull_request:
    paths:
      - "src/**"
      - "prompts/**"
      - "regression/**"

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt

      - name: Run regression eval
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python -m regression.run > eval_report.json

      - name: Check thresholds
        run: |
          python -m regression.check_thresholds eval_report.json

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-report
          path: eval_report.json
```

```python
# regression/check_thresholds.py
import json, sys
from .thresholds import THRESHOLDS, FAIL_POLICY

def check(report_path: str) -> int:
    with open(report_path) as f:
        report = json.load(f)

    failures = []
    for metric, threshold in THRESHOLDS.items():
        if metric not in report:
            continue
        score = report[metric]
        if score < threshold:
            failures.append(f"{metric}: {score:.3f} < {threshold}")

    if FAIL_POLICY == "any" and failures:
        print("FAIL — threshold violations:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("PASS — all metrics above threshold")
    return 0

if __name__ == "__main__":
    sys.exit(check(sys.argv[1]))
```

The PR cannot merge if the eval fails. Regressions are stopped before they reach main.

---

## Handling Non-Determinism — Seed and Tolerance

LLM evaluation is not deterministic. The same PR can score 0.02 differently across two runs. Two responses:

### Response 1: Pin temperature and seed

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    temperature=0,
    seed=42,  # OpenAI seed parameter
)
```

`seed` is best-effort, not guaranteed, but it cuts variance significantly.

### Response 2: Add tolerance to thresholds

```python
# regression/thresholds.py
THRESHOLDS_WITH_TOLERANCE = {
    "exact_match":  (0.80, 0.02),  # pass at >= 0.78 (0.02 tolerance)
    "judge_score":  (4.0,  0.1),
    "faithfulness": (0.85, 0.02),
}

def check_with_tolerance(metric: str, score: float) -> bool:
    threshold, tol = THRESHOLDS_WITH_TOLERANCE[metric]
    return score >= (threshold - tol)
```

**Rule**: set tolerance at roughly **2x the standard deviation of recent main branch scores**. Too large and you miss regressions; too small and you ship false positives.

---

## What to Do When the Eval Fails

When a PR fails the regression eval:

1. **Re-run**: it could be non-determinism. Try once more.
2. **Look at individual cases**: which inputs regressed?
   ```python
   # regression/diff_report.py
   def diff_against_main(current: dict, main_baseline: dict) -> list[str]:
       regressed = []
       for case_id in current:
           if current[case_id]["score"] < main_baseline[case_id]["score"] - 0.1:
               regressed.append(case_id)
       return regressed
   ```
3. **Decide**:
   - **Intentional change**: update the threshold to the new baseline and document in the PR description.
   - **Bug**: fix the code or prompt and re-run.

---

## Common Mistakes

### Mistake 1: Golden dataset too large

500 golden cases per PR means 30 minutes and $20-50 per run. **Cap at 20-50** and run the larger production dataset nightly.

### Mistake 2: Thresholds set too high

`exact_match >= 0.95` will fail constantly due to natural LLM variance. **Start at -2σ from the current main score.**

### Mistake 3: Setting thresholds once and forgetting

Models, prompts, and data improve. Baselines should rise. **Review thresholds quarterly** and tighten ones that have become loose.

### Mistake 4: Not testing the eval code itself

A bug in the eval function makes every score fake. **Write unit tests for eval functions** with known input → expected score.

### Mistake 5: Not monitoring eval cost

$5 per PR over 100 PRs/month = $500/month. **Track CI cost weekly**; if it climbs more than 10% switch to sampling.

---

## Key Takeaways

- Evaluation must run on **every PR like unit tests**, otherwise regressions reach production.
- Golden datasets are **20-50 items**: top usage + edge cases + past regressions.
- Three fail policies (any/majority/weighted) plus tolerance manage false positives.
- GitHub Actions runs the eval on every PR and blocks merge on threshold violations.
- On failure: re-run → diff → decide if it's an intentional change (raise threshold) or a bug (fix it).

The next post covers **A/B testing** to decide statistically which of two models or prompts is actually better.

---

## Operational checklist

- [ ] Keep the golden regression suite small enough to run on every PR.
- [ ] Encode thresholds and fail policy in code instead of tribal memory.
- [ ] Add a tolerance policy that reflects recent baseline variance.
- [ ] Diff failed cases against main so reviewers can see the exact regression.
- [ ] Revisit thresholds on a schedule instead of freezing them forever.

## Answering the Opening Questions

- **Why should regression testing move LLM evaluation from a pre-release event into the PR gate?**
  - Prompts, models, retrieval, and tools can regress in small PRs, so quality must be checked at each change rather than once before release.
- **What changes should the golden dataset and thresholds block?**
  - They should block changes that break core flows, past incidents, safety standards, or cost and latency limits.
- **What tolerance and fail policy are needed when non-determinism makes evals noisy?**
  - Use seeds where possible, repeated runs, confidence intervals, dimension-level tolerances, and a policy that fails critical cases regardless of the average.
<!-- toc:begin -->
## In this series

- [AI Evaluation 101 (1/10): Why Evaluate LLM Applications](./01-why-evaluate-llm-apps.md)
- [AI Evaluation 101 (2/10): Designing Evaluation Datasets](./02-evaluation-dataset-design.md)
- [AI Evaluation 101 (3/10): Deterministic Metrics — Exact Match, BLEU, ROUGE](./03-deterministic-metrics.md)
- [AI Evaluation 101 (4/10): LLM-as-Judge — Evaluating Models with Models](./04-llm-as-judge.md)
- [AI Evaluation 101 (5/10): Designing Rubric-Based Scoring](./05-rubric-based-scoring.md)
- [AI Evaluation 101 (6/10): Evaluating RAG Systems](./06-rag-evaluation.md)
- [AI Evaluation 101 (7/10): Evaluating Agents — Trajectories, Not Single Responses](./07-agent-evaluation.md)
- **AI Evaluation 101 (8/10): Regression Testing — Don't Let Yesterday's Wins Break Today (current)**
- AI Evaluation 101 (9/10): A/B Testing LLMs — Which Prompt Is Better? (upcoming)
- AI Evaluation 101 (10/10): Continuous Evaluation in Production (upcoming)

<!-- toc:end -->

## References

- [OpenAI — Reproducible Outputs with seed parameter](https://platform.openai.com/docs/api-reference/chat/create#chat-create-seed)
- [GitHub Actions — Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [LangSmith — Regression Testing for LLM Apps](https://docs.smith.langchain.com/evaluation/tutorials/regression)
- [Eugene Yan — Patterns for LLM Eval in CI](https://eugeneyan.com/writing/llm-evaluators/)

Tags: AI Evaluation, Regression Testing, CI, GitHub Actions
