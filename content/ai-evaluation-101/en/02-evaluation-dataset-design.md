---
title: Designing Evaluation Datasets
series: ai-evaluation-101
episode: 2
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Evaluation
- LLM
- Dataset
- Quality
last_reviewed: '2026-05-03'
---

# Designing Evaluation Datasets

> AI Evaluation 101 Series (2/10)

A good evaluation dataset mirrors production traffic distribution while including enough edge cases. This post covers the principles for designing a starter eval set of 50-200 examples and how to collect the data.

---
## What Makes a Good Evaluation Dataset?

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

The size depends on the purpose.

| Purpose | Recommended size | Notes |
|---------|------------------|-------|
| Smoke test (every CI run) | 10-30 | Runs fast, catches obvious regressions |
| Regression test (pre-deploy) | 100-300 | Yields meaningful per-dimension scores |
| Model comparison (gpt-4o vs claude) | 300-1000 | Lets you draw statistically meaningful conclusions |
| Academic benchmark | 1000+ | Required for generalization claims |

Start at 10-30, add 5-10 from production each week, and you reach 200 within three months.

## Labeling — How Do You Fill `expected`?

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

<!-- toc:begin -->
## AI Evaluation 101 Series

- [Why Evaluate LLM Applications](./01-why-evaluate-llm-apps.md)
- **Designing Evaluation Datasets (current)**
- Deterministic Metrics — Exact Match, BLEU, ROUGE (upcoming)
- LLM-as-Judge (upcoming)
- Rubric-Based Scoring (upcoming)
- Evaluating RAG Systems (upcoming)
- Evaluating Agents (upcoming)
- Regression Testing (upcoming)
- A/B Testing LLMs (upcoming)
- Continuous Evaluation in Production (upcoming)
<!-- toc:end -->

## References

- [Hamel Husain — Your AI product needs evals](https://hamel.dev/blog/posts/evals/)
- [OpenAI — Evals framework](https://github.com/openai/evals)
- [LangSmith — Dataset best practices](https://docs.smith.langchain.com/evaluation/concepts)
- [Eugene Yan — Building eval datasets](https://eugeneyan.com/writing/evals/)

Tags: AI Evaluation, LLM, Dataset, Quality
