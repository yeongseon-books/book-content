---
title: "AI Evaluation 101 (2/10): Designing Evaluation Datasets"
series: ai-evaluation-101
episode: 2
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
- Dataset
- Quality
last_reviewed: '2026-05-14'
seo_description: A good evaluation dataset mirrors production traffic distribution
  while including enough edge cases.
---

# AI Evaluation 101 (2/10): Designing Evaluation Datasets

A good evaluation dataset mirrors production traffic distribution while including enough edge cases.

This is the 2nd post in the AI Evaluation 101 series. Here we cover the principles for designing a starter eval set of 50-200 examples and how to collect the data.


![Designing evaluation datasets](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/02/02-01-designing-evaluation-datasets.en.png)
*Designing evaluation datasets*
> An evaluation dataset is not an exam paper for the model; it is a compressed sample of what the product actually meets.

## Questions to Keep in Mind

- Why should a good evaluation dataset be an operating sample rather than a model exam?
- How should representative cases and failure cases be mixed to reveal real quality changes?
- What judgment becomes blurry when the eval set is not version-controlled?

## What Makes a Good Evaluation Dataset?

![What makes a good evaluation Dataset](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/02/02-02-what-makes-a-good-evaluation-dataset.en.png)

*What makes a good evaluation Dataset*
A good eval set satisfies two things at once.

1. **It mirrors production traffic distribution.** The mix of cases should look like what users actually send.
2. **It includes enough edge cases.** Cases that are rare in normal traffic but cause major incidents when they break — collect those deliberately.

You need both to catch the "average score looks great, but one case is catastrophically broken" situation.

```python
from dataclasses import dataclass

@dataclass
class EvalExample:
    id: str
    input: dict
    expected: dict | None       # only filled when a deterministic answer exists
    category: str               # one of "happy_path", "edge_case", "adversarial"
    notes: str = ""
```

Adding `category` explicitly lets you "look at edge case scores separately." Looking only at the average lets the bulk of cases hide the problems.

## Where Do You Source the Data?

![Where do you source the Data](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/02/02-03-where-do-you-source-the-data.en.png)

*Where do you source the Data*
Combine three sources.

### 1. Sample from production traces

The best source is real user input. Each week, randomly draw 50 cases from production logs as eval candidates.

```python
import random

def sample_from_production(traces: list[dict], n: int = 50) -> list[dict]:
    return random.sample(traces, min(n, len(traces)))
```

If they contain PII, mask them or convert to synthetic data (see Ep9 Observability).

### 2. Collect failure cases

User complaints, incidents from on-call, cases broken in internal dogfooding — put all of them in the eval set. This is the start of "what broke once never breaks the same way again" regression testing.

```python
def add_failure_case(eval_set: list[dict], failed_input: dict, expected: dict, source: str):
    eval_set.append({
        "id": f"regression-{len(eval_set)+1:04d}",
        "input": failed_input,
        "expected": expected,
        "category": "regression",
        "notes": f"From: {source}",
    })
```

### 3. Deliberately authored adversarial cases

A domain expert hand-writes cases they suspect will break — prompt injection, ambiguous questions, questions with no answer.

## How Many Cases Do You Need?

![How many cases do you Need](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/02/02-04-how-many-cases-do-you-need.en.png)

*How many cases do you Need*
The size depends on the purpose.

| Purpose | Recommended size | Notes |
|---------|------------------|-------|
| Smoke test (every CI run) | 10-30 | Runs fast, catches obvious regressions |
| Regression test (pre-deploy) | 100-300 | Yields meaningful per-dimension scores |
| Model comparison (gpt-4o vs claude) | 300-1000 | Lets you draw statistically meaningful conclusions |
| Academic benchmark | 1000+ | Required for generalization claims |

Start at 10-30, add 5-10 from production each week, and you reach 200 within three months.

## Labeling — How Do You Fill `expected`?

![Labeling - how do you fill expected](https://yeongseon-books.github.io/book-public-assets/assets/ai-evaluation-101/02/02-05-labeling-how-do-you-fill-expected.en.png)

*Labeling - how do you fill expected*
There are three labeling styles, and you can use different ones per case.

```python
@dataclass
class Label:
    style: str  # "exact", "keywords", "rubric"
    payload: dict
```

1. **Exact answer**: "What is the capital of Korea?" → "Seoul". Use when there is only one right answer.
2. **Required keywords**: a list of words the summary must contain.
3. **Rubric**: when many answers are valid, score per dimension like "accuracy: X out of 5" (covered in detail in Ep5).

```python
examples = [
    EvalExample(
        id="qa-001",
        input={"question": "What is the capital of Korea?"},
        expected={"style": "exact", "answer": "Seoul"},
        category="happy_path",
    ),
    EvalExample(
        id="summary-001",
        input={"text": "..."},
        expected={"style": "keywords", "must_include": ["microservice", "latency"]},
        category="happy_path",
    ),
    EvalExample(
        id="advice-001",
        input={"question": "How should I structure my React app?"},
        expected={"style": "rubric"},
        category="edge_case",
    ),
]
```

## How Do You Version-Control the Eval Set?

The eval set lives next to the code, in version control. Save as JSONL and commit to git.

```python
import json
from pathlib import Path

def save_eval_set(eval_set: list[EvalExample], path: Path):
    with path.open("w") as f:
        for ex in eval_set:
            f.write(json.dumps({
                "id": ex.id,
                "input": ex.input,
                "expected": ex.expected,
                "category": ex.category,
                "notes": ex.notes,
            }, ensure_ascii=False) + "\n")

def load_eval_set(path: Path) -> list[EvalExample]:
    with path.open() as f:
        return [EvalExample(**json.loads(line)) for line in f]
```

Pinning the version into the filename is a good habit: `evals/customer-support/v3.jsonl`. When you create a new version, do not delete the old one — bump the name.

## Golden Dataset Promotion Rules

Not every sample from production logs should be promoted to the regression golden set — that becomes unmaintainable. Define promotion rules based on "which cases must never regress."

```python
from dataclasses import dataclass


@dataclass
class EvalCandidate:
    case_id: str
    user_impact: str          # "low", "medium", "high"
    reproducible: bool
    category: str             # "faq", "billing", "policy", "safety"
    observed_failures: int


def should_promote_to_golden(c: EvalCandidate) -> bool:
    if c.user_impact == "high" and c.reproducible:
        return True
    if c.observed_failures >= 3 and c.reproducible:
        return True
    if c.category == "safety" and c.reproducible:
        return True
    return False
```

Operational rules as plain text:

- High impact + reproducible → immediate golden promotion
- Same failure 3+ times → include in weekly regression set
- Safety/policy violation → include regardless of impact

With rules in code, dataset expansion becomes policy rather than intuition.

## Labeling Quality Checklist

As datasets grow, labeling inconsistency becomes the primary source of score fluctuation. Check these items periodically.

| Check | Question | Failure signal |
|---|---|---|
| Label consistency | Do two evaluators score the same input similarly? | Excessive per-evaluator score variance |
| Metadata completeness | Are category, source, and expected format all filled? | Many null rows at aggregation time |
| PII safety | Does raw data still contain personal information? | Email/phone regex detections |
| Temporal relevance | Are current user patterns represented? | Zero coverage of new categories |

Without labeling quality management, you risk mistaking label drift for model improvement.

## Golden Set Promotion Workflow

```python
def promote_pipeline(candidates: list[dict]) -> list[dict]:
    promoted = []
    for c in candidates:
        if c.get("severity") == "critical" and c.get("reproducible"):
            promoted.append(c)
            continue
        if c.get("user_reports", 0) >= 3 and c.get("reproducible"):
            promoted.append(c)
    return promoted


def cap_by_category(rows: list[dict], max_per_category: int = 15) -> list[dict]:
    out = []
    counts: dict[str, int] = {}
    for r in rows:
        cat = r["category"]
        counts.setdefault(cat, 0)
        if counts[cat] >= max_per_category:
            continue
        out.append(r)
        counts[cat] += 1
    return out
```

Without the category cap, one category becomes over-represented and the overall score no longer reflects real-world distribution.

## Eval Set Changelog Template

```text
Eval Set Changelog
- version: v7 -> v8
- added_cases: 14
- removed_cases: 2
- major_reason:
  - production failure harvest (8)
  - new product feature coverage (4)
  - safety policy update (2)
- expected impact:
  - billing category difficulty up
```

This record is essential for interpreting whether a score drop is a model problem or a dataset difficulty increase.

## Collection–Label–Review Role Separation

Dataset quality improves more from role separation in the review process than from raw data collection. When one person collects, labels, and reviews, bias compounds.

| Stage | Owner | Output |
|---|---|---|
| Collection | Ops / analytics | Candidate input list |
| First-pass label | Domain expert | expected, category, severity |
| Review | Different evaluator | Label approval/correction record |

```python
def dual_review_consensus(label_a: dict, label_b: dict) -> bool:
    same_style = label_a.get("style") == label_b.get("style")
    same_expected = label_a.get("expected") == label_b.get("expected")
    return same_style and same_expected
```

Low consensus rate for a category signals that the labeling guideline needs anchor examples before more data is collected.

## Dataset Aging Check

As an eval set ages, it drifts from current user queries. Check similarity to recent traffic at least monthly.

```python
def aging_score(recent_ratio: float) -> str:
    # recent_ratio: fraction of cases matching last-30-day input patterns
    if recent_ratio >= 0.8:
        return "fresh"
    if recent_ratio >= 0.6:
        return "watch"
    return "stale"
```

Repeated "stale" results mean you need to increase the new-category collection rate. When a new feature ships, bucket its inputs separately and enforce minimum coverage.

## Eval Set Documentation Minimums

Storing dataset files without a companion README causes interpretation quality to plummet on team turnover. Maintain at least:

```text
Dataset README minimums
- Data source (production logs / synthetic / manual)
- Labeling rules and exceptions
- Exclusion criteria (PII, duplicates, ambiguous queries)
- Per-version change summary
- Intended use (PR regression / nightly quality / model comparison)
```

```text
Metadata example
- created_at: 2026-05-01
- last_reviewed_at: 2026-05-20
- owner: eval-platform
```

This metadata anchors ownership and makes freshness checks trivial.


## Five Common Mistakes

1. **The prompt author writes the eval set.** You collect only cases that flatter your prompt and end up with the wrong "it works" conclusion. Have a teammate or production source the cases.
2. **Happy path only.** With no edge cases, you miss the "90% average but 1% of users break" situation. Manage the category mix deliberately.
3. **Storing PII verbatim.** Committing real user data to git is a major incident. Mask before labeling.
4. **Filling `expected` with one style only.** Forcing exact match on every case zeros out every free-form answer. Pick a label style per case.
5. **Building the eval set once and never updating it.** When production traffic shifts, the old eval set loses meaning. Refresh 5-10 cases per week.

## Key Takeaways

- A good eval set blends production distribution with deliberate edge cases.
- Source from three places: production samples, failure cases, intentional adversarial cases.
- Target sizes: 10-30 smoke, 100-300 regression, 300-1000 model comparison.
- Choose the label style per case from exact, keywords, or rubric.
- Save as JSONL, commit to git, pin the version into the filename.

The next post covers deterministic metrics — when Exact Match, F1, BLEU, and ROUGE help, and when they hurt.

---

## Operational checklist

- [ ] Sample real production traces instead of relying only on hand-written examples.
- [ ] Keep regression cases from past incidents in the dataset permanently.
- [ ] Tag each case with a category so you can slice scores by risk type.
- [ ] Pick the labeling style per case instead of forcing exact match everywhere.
- [ ] Version the dataset file so model comparisons stay reproducible.

## Answering the Opening Questions

- **Why should a good evaluation dataset be an operating sample rather than a model exam?**
  - The score can represent product risk only when real traffic shape and incident history are included. Artificial examples drift away from production quality.
- **How should representative cases and failure cases be mixed to reveal real quality changes?**
  - Use frequent requests for baseline quality and past failures plus edge cases for regression risk. Too much of either hides either the average or the danger.
- **What judgment becomes blurry when the eval set is not version-controlled?**
  - You lose the ability to tell whether the model improved or the dataset changed, so historical score comparisons become unreliable.
<!-- toc:begin -->
## In this series

- [AI Evaluation 101 (1/10): Why Evaluate LLM Applications](./01-why-evaluate-llm-apps.md)
- **AI Evaluation 101 (2/10): Designing Evaluation Datasets (current)**
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
- [LangSmith — Evaluation concepts](https://docs.smith.langchain.com/evaluation/concepts)
- [Weights & Biases Weave — Evaluation datasets](https://weave-docs.wandb.ai/guides/evaluation/)

### Additional reading

- [Hamel Husain — Your AI product needs evals](https://hamel.dev/blog/posts/evals/)
- [Eugene Yan — Building eval datasets](https://eugeneyan.com/writing/evals/)

Tags: AI Evaluation, LLM, Dataset, Quality
