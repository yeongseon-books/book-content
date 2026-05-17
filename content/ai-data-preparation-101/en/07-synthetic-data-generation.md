---
episode: 7
language: en
last_reviewed: '2026-05-17'
series: ai-data-preparation-101
status: publish-ready
tags:
- Synthetic Data
- Self-Instruct
- Evol-Instruct
- Distillation
- GPT-4
- Alpaca
targets:
  ebook: true
  medium: true
  mkdocs: true
  tistory: false
title: Synthetic Data Generation - From Self-Instruct to Distillation
seo_description: When labeled data runs short, synthetic-data quality depends on validating, rejecting, and approving each batch before it reaches training.
---

# Synthetic Data Generation - From Self-Instruct to Distillation

This is post 7 in the AI Data Preparation 101 series.

Synthetic data generation is not a trick for inflating dataset size. In practice, it is an operating procedure for expanding narrow-domain supervision in a controlled way. The critical question is usually not “What should we generate?” but “Which batches do we reject, and which ones are good enough to enter the training set?”

To address the weakness called out in issue #779, this chapter is no longer a loose catalog of patterns. It is rebuilt around one reproducible synthetic-data batch workflow. Self-Instruct, Evol-Instruct, RAG eval pair generation, and distillation now appear as decision branches inside the same pipeline.

## Questions this chapter answers

- What should a real synthetic-data batch start with and end with?
- When do you choose Self-Instruct, Evol-Instruct, RAG eval generation, or distillation?
- Which validation gates must a generated JSON artifact pass before it becomes training data?
- Which rejection cases should fail a batch immediately?
- Why does distillation need an output-usage policy gate in addition to quality checks?

## Why this chapter matters

Synthetic data can sharply reduce labeling bottlenecks for instruction tuning and evaluation-set creation. But if you keep generating without verification, you accumulate repeated patterns, unsupported answers, teacher bias, and policy risk at the same time.

That is why the operator view matters more than the pattern list. It is safer to think in terms of seed inputs, generation contract, sample review, rejection reasons, and final write path than to memorize four techniques in isolation.

> The success of synthetic data depends less on how many samples the model produced and more on whether the operator designed the batch so that bad samples can be rejected on purpose.

## One concrete operating scenario

Assume the following setup.

- Domain: fine-tuning a SaaS customer-support assistant
- Current problem: not enough instruction data for refunds, plan changes, and outage notices
- Existing assets: 40 human-reviewed seed tasks and 120 FAQ documents
- Goal: generate one synthetic batch this week and write only approved samples to JSONL

In that setting, the operator flow is straightforward.

1. Collect seed tasks and FAQ chunks.
2. Define the purpose of this batch.
3. Pick the generation branch that matches the purpose.
4. Generate samples under an explicit JSON contract.
5. Run schema, evidence, diversity, refusal, and policy gates.
6. Log rejection reasons and write only approved rows to the dataset path.

## Choose the branch first

The right branch depends on which supervision signal you want to expand.

| Goal | Branch | Why this branch fits |
| --- | --- | --- |
| Not enough topical coverage from a tiny seed set | Self-Instruct | It grows instruction-input-output triples across more customer situations. |
| Existing tasks are present but too easy | Evol-Instruct | It keeps the label space while increasing reasoning depth and constraints. |
| Retrieval evaluation set is missing | RAG eval pair generation | It builds question-answer pairs that can be checked against source evidence. |
| A strong teacher's response style should transfer to a student | Distillation | It can produce high-quality supervision, but only after policy review. |

In this chapter's scenario, we first want broader support-task coverage and a smaller set of evidence-grounded FAQ questions. So the default branch is Self-Instruct, hard cases are upgraded with Evol-Instruct, FAQ-grounded samples come from the RAG eval branch, and distillation stays disabled until policy review approves it.

## A reproducible synthetic-data batch workflow

The example below ties together seed inputs, generation contract, validation, rejection, and dataset write path into one minimal operator workflow.

```python
from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import uuid

from openai import OpenAI

client = OpenAI()

SEED_TASKS = [
    {
        "task_id": "seed-001",
        "instruction": "Summarize the refund policy for a customer.",
        "input": "A customer on an annual plan asks whether a refund is still possible 10 days after payment.",
        "output": "Annual-plan payments are still within the 14-day refund review window.",
        "source_type": "self_instruct",
        "difficulty": "baseline",
        "evidence": None,
    },
    {
        "task_id": "seed-002",
        "instruction": "Answer a customer question using only the outage notice.",
        "input": "Explain the cause of the API slowdown described in the 2026-05-01 outage notice.",
        "output": "The outage notice says the direct cause was database connection-pool saturation.",
        "source_type": "rag_eval",
        "difficulty": "baseline",
        "evidence": "Cause: database connection-pool saturation",
    },
]

FAQ_CHUNKS = {
    "faq-014": "Refund policy: annual plans remain eligible for refund review within 14 days of payment; after that, partial-refund review depends on usage.",
    "faq-021": "Outage notice: from 2026-05-01 10:42 UTC, API latency increased because the database connection pool was saturated.",
}

GENERATION_CONTRACT = {
    "type": "object",
    "required": ["items"],
    "item_required": [
        "task_id",
        "instruction",
        "input",
        "output",
        "source_type",
        "difficulty",
        "reasons",
    ],
    "allowed_source_type": ["self_instruct", "evol_instruct", "rag_eval", "distillation"],
}

BRANCH_GUIDE = {
    "self_instruct": "Make a new task in the same domain but with a different customer situation.",
    "evol_instruct": "Take a baseline task and add one realistic constraint that forces deeper reasoning.",
    "rag_eval": "Generate only when the answer can be quoted from the supplied FAQ chunk.",
    "distillation": "Only use if a policy reviewer has approved output reuse for this teacher.",
}


def build_prompt(batch_goal: str, branch: str) -> str:
    return f"""
You are generating training data for a SaaS support assistant.
Batch goal: {batch_goal}
Branch guide: {BRANCH_GUIDE[branch]}

Return JSON with the shape:
{{
  "items": [
    {{
      "task_id": "syn-...",
      "instruction": "...",
      "input": "...",
      "output": "...",
      "source_type": "{branch}",
      "difficulty": "baseline|hard",
      "evidence": "required when source_type is rag_eval, otherwise null",
      "reasons": ["why this sample adds coverage"]
    }}
  ]
}}

Seed tasks:
{json.dumps(SEED_TASKS, ensure_ascii=False, indent=2)}

FAQ chunks:
{json.dumps(FAQ_CHUNKS, ensure_ascii=False, indent=2)}
"""


def generate_batch(batch_goal: str, branch: str, model: str = "gpt-4o-mini") -> list[dict]:
    rsp = client.chat.completions.create(
        model=model,
        temperature=0.7 if branch != "rag_eval" else 0.2,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": build_prompt(batch_goal, branch)}],
    )
    payload = json.loads(rsp.choices[0].message.content)
    return payload["items"]


def validate_item(item: dict) -> list[str]:
    reasons = []
    for key in GENERATION_CONTRACT["item_required"]:
        if key not in item:
            reasons.append(f"missing:{key}")
    if item.get("source_type") not in GENERATION_CONTRACT["allowed_source_type"]:
        reasons.append("invalid_source_type")
    if item.get("source_type") == "rag_eval":
        evidence = item.get("evidence")
        if not evidence:
            reasons.append("missing_evidence")
        elif not any(evidence in chunk for chunk in FAQ_CHUNKS.values()):
            reasons.append("evidence_not_found")
    if any(token in item.get("output", "").lower() for token in ["i cannot", "i'm sorry", "unable to help"]):
        reasons.append("refusal_like_output")
    if len(item.get("output", "")) < 30:
        reasons.append("too_short")
    return reasons


def validate_batch(items: list[dict]) -> tuple[list[dict], list[dict], dict]:
    accepted, rejected = [], []
    seen = Counter()

    for item in items:
        item_reasons = validate_item(item)
        dedup_key = (item.get("instruction"), item.get("input"))
        seen[dedup_key] += 1
        if seen[dedup_key] > 1:
            item_reasons.append("duplicate_instruction_input")

        if item_reasons:
            rejected.append({"item": item, "reasons": item_reasons})
        else:
            accepted.append(item)

    total = len(items) or 1
    metrics = {
        "n_total": len(items),
        "n_accepted": len(accepted),
        "n_rejected": len(rejected),
        "accept_ratio": len(accepted) / total,
        "unique_ratio": len(seen) / total,
        "refusal_ratio": sum("refusal_like_output" in r["reasons"] for r in rejected) / total,
    }
    return accepted, rejected, metrics


def write_dataset(accepted: list[dict], run_id: str) -> Path:
    out_dir = Path("datasets/ai-data-preparation-101/07-synthetic-data-generation") / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "accepted.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in accepted:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return out_path


run_id = f"support-batch-{uuid.uuid4().hex[:8]}"
items = generate_batch(batch_goal="Expand refund and outage support tasks", branch="self_instruct")
accepted, rejected, metrics = validate_batch(items)

if metrics["accept_ratio"] < 0.8 or metrics["unique_ratio"] < 0.85 or metrics["refusal_ratio"] > 0.05:
    raise RuntimeError({"run_id": run_id, "status": "reject_batch", "metrics": metrics, "rejected": rejected[:3]})

dataset_path = write_dataset(accepted, run_id)
print({"run_id": run_id, "status": "accepted", "dataset_path": str(dataset_path), "metrics": metrics})
```

### The generated artifact should look like this

The output must be a reviewable JSON artifact, not just a stream of convenient text. A minimum example looks like this.

```json
{
  "items": [
    {
      "task_id": "syn-101",
      "instruction": "Explain the refund and rebilling sequence when a customer upgrades from a monthly plan to an annual plan.",
      "input": "The customer paid for a monthly plan 3 days ago and now wants the annual discount as well.",
      "output": "First confirm whether the monthly charge is still within the refund-review window, then explain the annual-plan rebilling sequence separately.",
      "source_type": "self_instruct",
      "difficulty": "baseline",
      "evidence": null,
      "reasons": ["Adds a rare case where refund logic and upgrade flow appear together."]
    },
    {
      "task_id": "syn-102",
      "instruction": "Answer the API-latency question using only the outage notice.",
      "input": "Summarize the cause of the 2026-05-01 slowdown for a support reply.",
      "output": "According to the public outage notice, the direct cause was database connection-pool saturation.",
      "source_type": "rag_eval",
      "difficulty": "hard",
      "evidence": "database connection-pool saturation",
      "reasons": ["Creates a retrieval-evaluation sample that requires direct evidence." ]
    }
  ]
}
```

The important detail is not that the JSON is pretty. It is that every row contains fields the operator can use to reject it later. Without `source_type`, `difficulty`, `evidence`, and `reasons`, batch failure becomes hard to diagnose.

## Design rejection logic before you chase scale

In production, the most valuable property of a synthetic sample is often not that it looks good, but that you can explain why it was discarded. The workflow above rejects common failure modes such as:

- **Schema omissions**: required keys such as `instruction`, `output`, or `source_type` are missing.
- **Evidence failure**: a `rag_eval` sample cites an evidence string that does not appear in any FAQ chunk.
- **Refusal-heavy output**: the batch contains too many safety refusals to help downstream supervision.
- **Duplicate growth**: the same instruction-input pair keeps recurring with cosmetic wording changes.
- **Under-informative output**: the answer is too short to be useful training signal.

Those rejection reasons should be logged, not hidden. Otherwise the operator cannot explain whether the next fix belongs in the prompt, the seed set, or the branch choice.

## The four patterns are decision branches inside one workflow

### Self-Instruct: the default coverage branch

If the dataset lacks breadth, Self-Instruct is the natural default. But high temperature alone is not enough. With a tiny seed set, near-duplicates arrive quickly, so diversity thresholds and dedup gates matter as much as the prompt itself.

### Evol-Instruct: the difficulty branch

If baseline tasks exist but reasoning depth is shallow, evolve them instead of generating from scratch. Turning “answer the refund question” into “answer the refund question when a partial-refund exception already exists” raises supervision quality without changing the problem family.

### RAG eval pair generation: the evidence branch

If your goal is retrieval evaluation rather than instruction tuning, the branch should be separated and labeled as `source_type="rag_eval"`. In this branch, evidence fidelity matters more than stylistic diversity, so lower temperature and mandatory evidence checks are appropriate.

### Distillation: the branch with an extra policy gate

Distillation is powerful when you want a strong teacher's behavior to transfer into a student dataset. But quality checks are not enough. You also need a hard stop before dataset creation unless output-usage review has already approved the chosen teacher.

```python
def require_policy_review(branch: str, teacher_name: str, review_ticket: str | None) -> None:
    if branch != "distillation":
        return
    if not review_ticket:
        raise RuntimeError(
            f"Stop: review output-usage rights for {teacher_name} before creating a distillation dataset."
        )


require_policy_review(
    branch="distillation",
    teacher_name="OpenAI API model",
    review_ticket=None,  # must be populated by legal/policy review
)
```

The main operational point is not to rely on memory about a provider's rules. For OpenAI, output ownership language and usage-policy restrictions are documented separately, so the safe workflow is to review the current provider terms and policy docs before generating a distillation dataset. The right guidance here is not “always allowed” or “always prohibited,” but “document the latest output-use decision before the run starts.”

## Batch approval should end in explicit thresholds

For this workflow, reasonable minimum thresholds could be:

- `accept_ratio >= 0.80`
- `unique_ratio >= 0.85`
- `refusal_ratio <= 0.05`
- every `rag_eval` row has `evidence_not_found == 0`
- any distillation run without a `policy_review_ticket` stops immediately

These numbers are not universal truths. They are practical gates for catching batches that look large but are operationally weak. For example, a `unique_ratio` of 0.62 is usually not a signal to generate more. It is a signal to redesign the prompt and seed set.

## Common points of confusion

- **Synthetic data gets better if we simply generate more**: no. Without rejection logic, scale just multiplies noise.
- **A stronger teacher automatically makes distillation safe**: no. Quality and policy are separate gates.
- **RAG eval data should be judged the same way as instruction-tuning data**: no. Evidence fidelity comes first.
- **If the output is JSON, it is ready for training**: no. Schema success is only the first gate.

## Operational checklist

- [ ] Define the batch goal first, then choose Self-Instruct, Evol-Instruct, RAG eval, or distillation
- [ ] Include `source_type`, `difficulty`, `evidence`, and `reasons` in the generation contract
- [ ] Document accept ratio, unique ratio, and refusal ratio before the run starts
- [ ] Verify that every `rag_eval` evidence string exists in the source chunk
- [ ] Do not start distillation without an output-usage review ticket
- [ ] Write only approved rows to `datasets/ai-data-preparation-101/07-synthetic-data-generation/<run_id>/accepted.jsonl`

## Summary

Synthetic data generation is not about memorizing four named patterns. It is about operating one reliable batch workflow with seed inputs, a JSON contract, rejection logic, validation gates, and a dataset write path.

Self-Instruct expands coverage, Evol-Instruct raises difficulty, RAG eval builds evidence-bound evaluation data, and distillation transfers teacher behavior. But regardless of branch, validation and policy review should come before scale.

Next, we will stay in the same late-series workflow arc and look at augmentation: how to widen the training distribution by transforming existing samples without breaking their labels.

<!-- toc:begin -->
## AI Data Preparation 101 series

- [Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- [Tokenization and Chunking Strategies](./05-tokenization-chunking.md)
- [Quality Filtering - Heuristics and Classifiers](./06-quality-filtering.md)
- **Synthetic Data Generation - From Self-Instruct to Distillation (current)**
- Data Augmentation - From EDA to Back-Translation (upcoming)
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)
<!-- toc:end -->

## References

### Official documentation
- [OpenAI Terms of Use](https://openai.com/policies/terms-of-use/)
- [OpenAI Usage Policies](https://openai.com/policies/usage-policies/)
- [OpenAI API Developer Docs](https://platform.openai.com/docs/overview)

### Papers and implementation references
- [Self-Instruct: Aligning Language Model with Self Generated Instructions (Wang et al., 2022)](https://arxiv.org/abs/2212.10560)
- [WizardLM: Empowering Large Language Models to Follow Complex Instructions (Xu et al., 2023)](https://arxiv.org/abs/2304.12244)
- [Stanford Alpaca - Instruction-tuned LLaMA](https://github.com/tatsu-lab/stanford_alpaca)
- [Synthetic Data Generation with Large Language Models (Long et al., 2024 survey)](https://arxiv.org/abs/2406.15126)

Tags: Synthetic Data, Self-Instruct, Evol-Instruct, Distillation, GPT-4, Alpaca
