---
title: "AI Evaluation 101 (1/10): Why Evaluate LLM Applications"
series: ai-evaluation-101
episode: 1
language: en
status: content-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- LLM
- Testing
- Quality
last_reviewed: '2026-05-14'
seo_description: LLMs return different answers for the same input. Without evaluation,
  you cannot tell that a feature working yesterday is broken today.
---

# AI Evaluation 101 (1/10): Why Evaluate LLM Applications

LLMs return different answers for the same input. Without evaluation, you cannot tell that a feature working yesterday is broken today.

This is the first post in the AI Evaluation 101 series. Here we cover why LLM evaluation differs from regular software testing and what to measure.


![Why evaluate LLM applications](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-01-why-evaluate-llm-applications.en.png)
*Why evaluate LLM applications*
> LLM evaluation is not decorative testing; it is the dashboard that lets you keep reading quality changes.

## Questions to Keep in Mind

- Why is regular feature testing not enough to judge the quality of an LLM app?
- What problems show up too late when an LLM app runs without evaluation?
- What small unit should a first evaluation pipeline start with?

## Why Is LLM Evaluation Different from Regular Testing?

![Why is LLM evaluation different from regular Testing](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-02-why-is-llm-evaluation-different-from-reg.en.png)

*Why is LLM evaluation different from regular Testing*
Traditional unit tests are deterministic: `assert add(2, 3) == 5`. The same input produces the same output, and there is exactly one right answer.

LLMs are different.

```python
from openai import OpenAI

client = OpenAI()

def summarize(text: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Summarize in one sentence: {text}"}],
    )
    return resp.choices[0].message.content
```

Send the same `text` twice and the two responses will not match exactly. Several answers can reasonably be called "correct," and many are hard to call "wrong" with confidence. `==` comparison alone cannot evaluate this.

## What Breaks if You Run Without Evaluation?

![What breaks if you run without Evaluation](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-03-what-breaks-if-you-run-without-evaluatio.en.png)

*What breaks if you run without Evaluation*
Three things break at once.

1. **You cannot detect regressions.** You change one line of a prompt, another case breaks, and without evals you only learn from a user complaint.
2. **You become afraid to upgrade models.** You want to move from gpt-4o-mini to gpt-4.1, but with no way to measure "is it better?" you simply do not move.
3. **You have no proof you improved anything.** Saying "this prompt is better" carries no weight without numbers; you cannot convince stakeholders.

```python
# What changing a prompt without evals looks like
# Before: "Summarize in one sentence:"
# After:  "Summarize concisely in one sentence in a friendly tone:"
# -> You have no idea which cases got better and which got worse.
```

## What Should You Measure?

![What should you Measure](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-04-what-should-you-measure.en.png)

*What should you Measure*
LLM responses have at least four dimensions, and each needs a different measurement approach.

```python
from dataclasses import dataclass

@dataclass
class EvalResult:
    correctness: float  # are the facts right
    relevance: float    # does it answer the question
    safety: float       # any harm or bias
    style: float        # does it follow the requested format and tone
```

1. **Correctness**: are the facts right? In RAG, does the answer match retrieved context?
2. **Relevance**: does the answer address the question or wander around it?
3. **Safety**: any PII leakage, discriminatory language, or dangerous advice?
4. **Style**: does it follow the JSON schema, length limit, or tone you required?

Later posts in this series cover which metrics fit each dimension, one at a time.

## The Four Stages of an Evaluation Pipeline

![The four stages of an evaluation pipeline](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/01/01-05-the-four-stages-of-an-evaluation-pipelin.en.png)

*The four stages of an evaluation pipeline*
Whatever tool you use, an LLM evaluation system has the same four stages.

```python
def run_evaluation(eval_set: list[dict], system_under_test) -> dict:
    # 1. Generate — feed inputs to the system under test, collect responses
    predictions = [system_under_test(ex["input"]) for ex in eval_set]

    # 2. Score — score each response
    scores = [score_one(ex, pred) for ex, pred in zip(eval_set, predictions)]

    # 3. Aggregate — roll up the scores
    summary = {
        "accuracy": sum(s["correct"] for s in scores) / len(scores),
        "avg_relevance": sum(s["relevance"] for s in scores) / len(scores),
    }

    # 4. Compare — compare against the previous version
    return summary
```

1. **Generate**: produce system responses for the eval set inputs.
2. **Score**: score each response (deterministic metric, LLM-as-judge, human rating, or a combination).
3. **Aggregate**: roll up by dimension — average, pass rate, p95.
4. **Compare**: compare against the previous version or a baseline to catch regressions.

## Your First Evaluation — Start with Ten

"I will evaluate once we have enough data" means you will not start a year from now. Start with ten.

```python
eval_set = [
    {"input": "What is RAG?", "expected_keywords": ["retrieval", "generation"]},
    {"input": "Explain async/await", "expected_keywords": ["coroutine", "await"]},
    # ... 8 more
]

def score_one(ex, pred: str) -> dict:
    keywords_found = sum(1 for kw in ex["expected_keywords"] if kw.lower() in pred.lower())
    return {
        "correct": keywords_found == len(ex["expected_keywords"]),
        "keyword_recall": keywords_found / len(ex["expected_keywords"]),
    }

results = run_evaluation(eval_set, summarize)
print(f"Accuracy: {results['accuracy']:.0%}")
```

Even ten cases give you signals like "case #5 dropped after the prompt change." That single signal catches 90% of regressions.

## A Minimal Evaluation Harness You Can Run Today

If you want the first useful version, make it boring. Put the task behind one function, store a tiny eval set in version control, and print both the aggregate score and the failed case IDs.

```python
from dataclasses import dataclass

@dataclass
class EvalCase:
    case_id: str
    prompt: str
    must_include: list[str]

def run_smoke_eval(cases: list[EvalCase], system_under_test) -> dict:
    failed_cases = []
    scores = []

    for case in cases:
        answer = system_under_test(case.prompt)
        matched = sum(1 for kw in case.must_include if kw.lower() in answer.lower())
        passed = matched == len(case.must_include)
        scores.append(int(passed))
        if not passed:
            failed_cases.append(
                {
                    "case_id": case.case_id,
                    "answer": answer,
                    "missing": [kw for kw in case.must_include if kw.lower() not in answer.lower()],
                }
            )

    return {
        "pass_rate": sum(scores) / len(scores),
        "failed_cases": failed_cases,
    }

smoke_cases = [
    EvalCase("rag-001", "What is RAG?", ["retrieval", "generation"]),
    EvalCase("async-001", "Explain async/await", ["coroutine", "await"]),
    EvalCase("json-001", "Return valid JSON with a title field", ["title"]),
]

report = run_smoke_eval(smoke_cases, summarize)
print(report)
```

**Expected output:**

```text
{
  'pass_rate': 0.67,
  'failed_cases': [
    {
      'case_id': 'async-001',
      'answer': '...',
      'missing': ['coroutine']
    }
  ]
}
```

That is enough to make a pull request actionable. Instead of arguing about whether the output "feels better," you can point to the exact case that regressed.

## Failure Modes to Watch in Week One

The first evaluation loop usually fails for process reasons, not math reasons.

| Failure mode | What it looks like | What to do next |
|---|---|---|
| Only happy-path cases | Pass rate looks strong, but support tickets keep rising | Add two or three recent user complaints every week |
| One giant aggregate score | Accuracy improves while safety or format compliance worsens | Split results by correctness, relevance, safety, and style |
| No per-case diff | The team knows the score dropped but not why | Print failed case IDs, missing keywords, and raw answers |
| Eval is run manually | Prompt tweaks skip evaluation because "this is a tiny change" | Wire the smoke suite into CI or pre-merge review |

The point of the first harness is not elegance. The point is to make regressions visible faster than user complaints.

## A Minimal CI Evaluation Pipeline Your Team Can Adopt Today

Evaluation that lives only in documentation collapses within a month. It must run automatically on every PR under the same conditions. Below is the smallest viable GitHub Actions pipeline.

```yaml
# .github/workflows/llm-eval-smoke.yml
name: LLM Eval Smoke

on:
  pull_request:
    paths:
      - "src/**"
      - "prompts/**"
      - "evals/**"

jobs:
  smoke-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - name: Run smoke evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python -m evals.smoke.run --input evals/smoke.jsonl --output evals/result.json
      - name: Enforce gate
        run: python -m evals.smoke.gate --report evals/result.json --min-pass-rate 0.8
```

```python
# evals/smoke/gate.py
import json
import argparse
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--min-pass-rate", type=float, required=True)
    args = parser.parse_args()

    with open(args.report) as f:
        report = json.load(f)

    pass_rate = report["pass_rate"]
    if pass_rate < args.min_pass_rate:
        print(f"FAIL: pass_rate={pass_rate:.2%} < {args.min_pass_rate:.2%}")
        for case in report.get("failed_cases", []):
            print(f"- {case['case_id']}: missing={case.get('missing', [])}")
        sys.exit(1)

    print(f"PASS: pass_rate={pass_rate:.2%}")


if __name__ == "__main__":
    main()
```

The point is not a fancy dashboard. It is a baseline that automatically blocks quality regressions at the PR stage.

## Four-Week Adoption Roadmap

For teams introducing evaluation for the first time, adoption order matters more than tool choice. Limiting scope to four one-week increments avoids the "we built a harness but nobody runs it" trap.

| Week | Goal | Deliverable |
|---|---|---|
| 1 | Build a 10–20 case smoke eval | `evals/smoke.jsonl`, pass/fail script |
| 2 | Introduce per-dimension scores | Separate correctness/relevance report |
| 3 | Wire PR auto-gate | GitHub Actions fail gate |
| 4 | Start the failure feedback loop | Weekly failed-case addition rule |

```python
def weekly_eval_review(summary: dict) -> list[str]:
    actions = []
    if summary["pass_rate"] < 0.8:
        actions.append("Review rollback of key prompt changes")
    if summary.get("safety_failures", 0) > 0:
        actions.append("Promote safety cases to golden set")
    if summary.get("flaky_cases", 0) > 3:
        actions.append("Isolate high-nondeterminism cases for separate analysis")
    return actions
```

The purpose of this roadmap is repeatability, not completeness. Starting small but running every week builds evaluation capability fast.

The best moment to introduce evaluation is not when everything is perfect — it is when changes start happening frequently. Even a small eval loop reduces quality incidents without slowing down the team's change velocity.


## Five Common Mistakes

1. **"We will evaluate once production stabilizes."** Without evaluation, you cannot know whether it has stabilized. Start with ten cases on day one.
2. **Obsessing over a single score.** "87% accuracy" hides a drop in safety. Always look per dimension.
3. **The prompt author writes the eval set.** They cherry-pick cases that favor their own prompt and the result is inflated. Pull cases from someone else or from production traces.
4. **Using only deterministic metrics.** BLEU alone penalizes "right meaning, different wording." Combine with LLM-as-judge or rubric scoring.
5. **Running the eval once.** LLMs are stochastic, so the same input can score differently. Repeat important comparisons 3-5 times and look at the variance too.

## Key Takeaways

- LLM responses are not deterministic, so `==` comparison does not work.
- Without evaluation you cannot detect regressions, upgrade models, or prove improvements.
- Measure at least four dimensions separately: correctness, relevance, safety, style.
- The pipeline is four stages: generate, score, aggregate, compare.
- Do not wait for data to accumulate — start with ten cases today.

The next post covers how to design evaluation datasets — where to source them, how many you need, and how to label them.

---

## Operational checklist

- [ ] Pick 10 real user tasks that represent the current product surface area.
- [ ] Track at least correctness, relevance, safety, and style as separate signals.
- [ ] Store the eval set in version control next to the code or prompts it protects.
- [ ] Print failed case IDs and raw outputs, not just a single average score.
- [ ] Run the smoke suite before every prompt or model change reaches production.

## Answering the Opening Questions

- **Why is regular feature testing not enough to judge the quality of an LLM app?**
  - LLM output can be correct with different wording and wrong while looking plausible, so simple assertions do not capture semantic quality.
- **What problems show up too late when an LLM app runs without evaluation?**
  - Cost growth, regressions on specific cases, hallucinations, and safety misses often appear only after they accumulate in user or operations data.
- **What small unit should a first evaluation pipeline start with?**
  - Start with a small eval set of about ten representative requests, clear expected criteria, and failure logs that make the loop repeatable.
<!-- toc:begin -->
## In this series

- **AI Evaluation 101 (1/10): Why Evaluate LLM Applications (current)**
- AI Evaluation 101 (2/10): Designing Evaluation Datasets (upcoming)
- AI Evaluation 101 (3/10): Deterministic Metrics — Exact Match, BLEU, ROUGE (upcoming)
- AI Evaluation 101 (4/10): LLM-as-Judge — Evaluating Models with Models (upcoming)
- AI Evaluation 101 (5/10): Designing Rubric-Based Scoring (upcoming)
- AI Evaluation 101 (6/10): Evaluating RAG Systems (upcoming)
- AI Evaluation 101 (7/10): Evaluating Agents — Trajectories, Not Single Responses (upcoming)
- AI Evaluation 101 (8/10): Regression Testing — Don't Let Yesterday's Wins Break Today (upcoming)
- AI Evaluation 101 (9/10): A/B Testing LLMs — Which Prompt Is Better? (upcoming)
- AI Evaluation 101 (10/10): Continuous Evaluation in Production (upcoming)

<!-- toc:end -->

## References

### Official docs

- [OpenAI Evals](https://github.com/openai/evals)
- [Anthropic — Develop tests and evaluations](https://docs.anthropic.com/en/docs/test-and-evaluate/develop-tests)
- [LangSmith — Evaluation concepts](https://docs.smith.langchain.com/evaluation/concepts)

### Additional reading

- [Hugging Face — Evaluating LLMs as a judge](https://huggingface.co/learn/cookbook/en/llm_judge)
- [Eugene Yan — LLM evaluation patterns](https://eugeneyan.com/writing/llm-evaluators/)

### Related Series

- [LLM Apps Ops 101](../../llm-apps-ops-101/en/01-monitoring-and-logging.md) — tackles the same "LLM correctness" problem from the operations side. Where this series builds pre-release quality gates, the ops series tracks the same signal in production via monitoring, logging, and alerting.

Tags: AI Evaluation, LLM, Testing, Quality
