---
title: "LLM Fine-tuning 101 (5/6): Model Evaluation"
series: llm-finetuning-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- Evaluation
- Perplexity
- GoldenSet
- Metrics
- Python
last_reviewed: '2026-05-01'
seo_description: Evaluation works best when you separate "internal model signals"
  from "user-facing quality."
---

# LLM Fine-tuning 101 (5/6): Model Evaluation

Evaluation is where many fine-tuning demos become misleading. This article separates internal model signals from user-facing quality so you can measure improvement and catch regressions with a repeatable loop.

This is the fifth post in the LLM Fine-tuning 101 series.

![LLM Fine-tuning 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/05/05-02-the-right-way-to-read-perplexity.en.png)
*LLM Fine-tuning 101 chapter 5 flow overview*

> Evaluation is where fine-tuning demos start lying — quantitative signals like perplexity come first, generated samples come later, and the gap between the two is exactly where regressions hide.

## Questions to Keep in Mind

- How do you compute perplexity, the first quantitative signal to look at right after fine-tuning?
- Why is comparing perplexity before and after training not a complete quality evaluation?
- Why keep a separate evaluation loop even in a tiny model demo?

## Why this matters

Right after training, the temptation is to look only at generated samples. In production you must look at quantitative signals first. The most basic one is perplexity, which shows how naturally the model predicts tokens in your evaluation data.

The real goal of episode 5 is to make evaluation an **automatable pipeline**. Eyeballing every output does not scale. Use perplexity as a regression baseline and stack a golden-set qualitative evaluation on top — building this two-tier structure with the same discipline as the 1-step training run from episode 4.

## Mental Model

Evaluation works best when you separate "internal model signals" from "user-facing quality."

```text
[Internal signals]              [User-facing quality]
- perplexity                    - answer match rate
- token-level accuracy          - format compliance
- gradient norm                 - human rating
        |                              |
        +--- fast regression line --+  |
                  |                    |
            run in CI            run on a separate
                                 schedule with golden set
```

Internal signals run fast (seconds to minutes); user-facing quality runs slow (minutes to hours). When the fast signal regresses, block the change; track the slow signal nightly.

Two more facts to memorize:

- **perplexity = exp(mean cross-entropy loss)**. If loss drops, perplexity drops. They carry the same information.
- **Evaluation data must be separate from training data.** Demos can share them for clarity, but production needs a hold-out set.

## Core concepts

| Item | Meaning |
| --- | --- |
| Perplexity | Average "surprise" when predicting the next token. Lower is better |
| Cross-entropy loss | Per-token gap between predicted distribution and ground truth. Source of perplexity |
| `model.eval()` | Switches dropout / batch normalization to inference mode |
| `torch.no_grad()` | Disables gradient computation, saving memory and time |
| Golden set | Human-curated input/output pairs for evaluation. The baseline for regression detection |
| Hold-out set | Data not used in training. Used for perplexity measurement |
| Task metric | Domain-specific metrics like exact match, BLEU, ROUGE |

## Before vs. After

**Before** — All you have is a vague impression that "loss went down so it must have learned." A few days later, when someone asks for the result, it is hard to reproduce.

**After** — Adopting the evaluation loop in episode 5 condenses the result into one line:

```text
{'before_ppl': 27431.84, 'after_ppl': 26890.17, 'delta_pct': -1.97}
```

The absolute value does not matter. What matters is (1) evaluation is separated from training, (2) the same data was measured twice to compare trends, and (3) CI produces the same numbers.

## How to read perplexity correctly

Perplexity is "lower is better," but you cannot judge quality from the absolute value alone. Tiny demo models, small datasets, and short context lengths cause large swings. So in practice, perplexity is best used as a **regression baseline** — strong at detecting whether things got worse, or whether a setting change improved the trend.

![How to read perplexity correctly](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/05/05-01-the-right-way-to-read-perplexity.en.png)

*How to read perplexity correctly*

## Step-by-step practice

### Step 1 — Write the evaluation function

```python
import math
import torch

def perplexity(model, dataset) -> float:
    losses = []
    model.eval()
    for row in dataset:
        batch = {key: torch.tensor([value]) for key, value in row.items()}
        with torch.no_grad():
            loss = model(**batch).loss
        losses.append(loss.item())
    return math.exp(sum(losses) / len(losses))
```

### Step 2 — Measure before and after training

```python
before = perplexity(peft_model, eval_dataset)
trainer.train()
after = perplexity(peft_model, eval_dataset)

delta = (after - before) / before * 100
print({"before_ppl": before, "after_ppl": after, "delta_pct": delta})
```

### Step 3 — Define a golden set

```python
golden = [
    {"prompt": "Q: How to sort a Python list?", "expected_contains": "sorted"},
    {"prompt": "Q: What is HTTP 404?", "expected_contains": "not found"},
]
```

Each item is a "prompt" and an "expected keyword." Keyword containment is more realistic than exact match for small models.

### Step 4 — Score the golden set

```python
def score_golden(model, tokenizer, golden) -> float:
    hits = 0
    for item in golden:
        ids = tokenizer(item["prompt"], return_tensors="pt").input_ids
        out = model.generate(ids, max_new_tokens=32)
        text = tokenizer.decode(out[0], skip_special_tokens=True)
        if item["expected_contains"] in text:
            hits += 1
    return hits / len(golden)
```

### Step 5 — Print both signals together

```python
print({
    "ppl_after": after,
    "golden_score": score_golden(peft_model, tokenizer, golden),
})
```

The moment these two lines print together, you see the regression baseline and user-facing quality on one screen.

## What to notice in this code

![Calculation flow from average loss to perplexity](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/05/05-03-what-to-notice-in-this-code.en.png)

*Calculation flow from average loss to perplexity*

- The evaluation function must be separate from the training loop. Otherwise you risk mutating parameters while reading the loss.
- `torch.no_grad()` and `model.eval()` are basic protections that stabilize memory usage and dropout behavior.
- This example is for trend confirmation only. Real projects need a hold-out set, task metric, and human review together.
- Golden-set scoring is the lightest possible automation that catches regressions without a human reading every output.

## Common mistakes

![Decision flow for overfit signals and comparison baselines](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/05/05-04-where-engineers-get-confused.en.png)

*Decision flow for overfit signals and comparison baselines*

- **Shipping based on perplexity alone** — format compliance, factuality, and safety need separate evaluation. Perplexity is one axis only.
- **Using the same data for training and evaluation** — numbers look optimistically good. The demo shares them for clarity, but real projects must split them.
- **Building a golden set once and forgetting it** — as the model evolves, evaluation items must grow too. A weekly habit of adding 5-10 cases works well.
- **Forgetting `model.eval()`** — dropout stays active and the same input produces different outputs. Reproducibility breaks.
- **Evaluating only the last step** — if you only score the final checkpoint, you cannot tell when things broke. Use `eval_steps` to measure periodically.
- **Skipping evaluation in CI** — when humans run it manually, regressions slip in the moment someone forgets. A 5-minute perplexity check is worth running on every PR.

## Production application

- **Two-tier structure**: fast perplexity check + slow golden-set evaluation. Fast in CI, both in nightly.
- **Regression budget**: block PRs when perplexity regresses by more than 5%. Ignore small fluctuations.
- **Categorize the golden set**: format, factuality, safety, domain knowledge — 4-5 categories make weak spots visible at a glance.
- **Pair human evaluation**: show outputs from two models side by side and ask only "which is better?" The signal is stronger than absolute scores.
- **Acknowledge automatic-eval limits**: BLEU and ROUGE see surface overlap, not meaning. Even LLM-as-judge has bias. Treat automatic scores as a guide for human evaluation.
- **Persist evaluation results as logs**: store model name, data version, and code commit hash so you can compare six months later.

## Checklist

- [ ] I understand that perplexity is the exponential of mean loss.
- [ ] I can explain why the evaluation loop uses `no_grad` and `eval`.
- [ ] I ran `python main.py` and verified the before/after perplexity output.
- [ ] I can explain the meaning and limits of a golden set.
- [ ] I have a habit of running minimum quantitative evaluation before serving.

## Exercises

1. Grow the eval dataset from 2 to 20 entries and observe how perplexity behaves. Does variance shrink?
2. Add 5 "math computation" items to the golden set and compare scores before and after fine-tuning. Does fine-tuning improve every category equally?
3. Remove the `model.eval()` call and run the perplexity function twice. How do the results differ?

## Summary · Next article

Evaluation is unglamorous, but it is the step that earns trust in a fine-tuning pipeline. Establishing a baseline before looking at generated samples makes future experiments depend less on intuition. The production pattern is the two-tier setup: fast quantitative signals (perplexity) below, slow qualitative evaluation (golden set, human review) above.

The next article (episode 6) covers serving. We will deploy the LoRA adapter separated from the base model and reduce inference memory and latency in code.

## Metric tiers: why perplexity alone is not enough

Perplexity is fast and useful, but insufficient as a sole indicator. In practice, stacking metrics in tiers produces a more stable evaluation system.

| Tier | Metric | Cadence | Purpose |
| --- | --- | --- | --- |
| Fast regression | perplexity, eval loss | every PR/commit | block failures immediately |
| Task performance | exact match, F1, format pass rate | daily/nightly | track functional quality |
| User experience | human eval, pairwise preference | weekly/pre-release | deployment decision |

This structure naturally enforces the operational principle: "fast signals automated, slow signals focused."

## Common pitfalls when computing perplexity

| Pitfall | Wrong conclusion | Correction |
| --- | --- | --- |
| Train/eval data overlap | excessive optimism | enforce hold-out split |
| Ignoring length distribution | false regression signal | compare within same-length buckets |
| Evaluating with dropout active | reproducibility collapse | force `model.eval()` |
| Too few samples | high variance | use at least dozens to hundreds |

In evaluation automation, the important thing is not the number itself but ensuring it is always computed under identical conditions.

## Golden set scoring format example

Storing the eval set as JSONL makes it easy to share between CI and manual review.

```json
{"id": "fmt-001", "prompt": "FastAPI 400 error example", "must_include": ["HTTPException", "400"], "must_not_include": ["Django"]}
{"id": "fmt-002", "prompt": "How to reverse a list", "must_include": ["[::-1]", "reverse"], "must_not_include": ["numpy"]}
```

A scoring function can start with simple keyword containment. What matters is having a system that "evaluates the same prompts with the same rules repeatedly."

## Evaluation output example: a human-readable report

```text
run_id=2026-05-20-lora-r16
eval_samples=320
before_ppl=18.42
after_ppl=16.95
delta_pct=-7.98
golden_pass_rate=0.81
format_pass_rate=0.93
blocked=0
```

This format is easy to read in a terminal and easy to export to CSV or a dashboard later.

## Reading loss curve and perplexity together

Checking the relationship below at evaluation time speeds up interpretation.

1. Train loss falling + eval perplexity falling: likely genuine improvement
2. Train loss falling + eval perplexity stagnant/rising: suspect overfitting or data leakage
3. Train loss oscillating + eval perplexity oscillating: suspect excessive learning rate or batch instability

A model whose "training loss alone improved" is not a deployment candidate. The evaluation metric direction must align.

## Before/after generation comparison: anchoring quantitative metrics

```text
[Prompt]
Explain the difference between HTTP 401 and 403 in two sentences.

[Before]
401 and 403 are authentication errors and related with forbidden access.

[After]
401 is returned when credentials are missing or invalid.
403 is returned when the user is authenticated but lacks permission for the resource.
```

If quantitative metrics improved, before/after comparisons like this should show consistent quality gains.

## Evaluation automation script skeleton

```python
def evaluate_run(model, tokenizer, eval_dataset, golden_set):
    ppl = perplexity(model, eval_dataset)
    golden_score = score_golden(model, tokenizer, golden_set)
    return {
        "perplexity": round(ppl, 4),
        "golden_score": round(golden_score, 4),
    }

result = evaluate_run(peft_model, tokenizer, eval_dataset, golden)
print(result)
```

You do not need a complex framework right away. A small function like this is enough to escape the "training without evaluation" state quickly.

## End-to-end pattern: verifying data, LoRA config, and training inputs in one flow

Fine-tuning quality is determined at the input contract before model architecture matters. Validate the dataset template, LoRA settings, and length statistics in the same pipeline to reduce debugging cost.

```python
from dataclasses import dataclass
from typing import Iterable

from peft import LoraConfig

@dataclass
class Sample:
    instruction: str
    input: str
    output: str

def render(sample: Sample) -> str:
    return (
        "### Instruction:\n" + sample.instruction + "\n\n"
        "### Input:\n" + sample.input + "\n\n"
        "### Response:\n" + sample.output
    )

def build_lora_config() -> LoraConfig:
    return LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )

def length_stats(lengths: Iterable[int]) -> tuple[int, float, int]:
    data = sorted(lengths)
    if not data:
        return 0, 0.0, 0
    avg = sum(data) / len(data)
    p95 = data[int(len(data) * 0.95) - 1]
    return min(data), avg, p95
```

Operationally, `target_modules` and the data template must be managed together. When the template changes, the token length distribution changes, which directly affects batch size and training stability. Record the data version, LoRA config version, and evaluation metrics as a single experiment unit so you can quickly isolate whether a quality change comes from data or adapter configuration.

## Eval set design: category-based regression detection

Collecting golden-set items randomly makes it hard to explain the cause of a regression. Tagging items by category is far more useful.

| Category | Example prompt count | Primary metric |
| --- | --- | --- |
| Format compliance | 30 | format pass rate |
| Factuality | 40 | keyword + human check |
| Domain terminology | 30 | exact/contains |
| Safety | 20 | blocked response rate |

In operations, review category-level scores weekly and focus review only on the segments that declined.

## Standard evaluation result output format

```text
model=llama-3-8b + adapter:v3
dataset=eval_2026_05
perplexity=15.84
golden_total=120
golden_pass=98
format_pass_rate=0.95
safety_block_rate=0.99
```

Fixing this format means experiment notes, CI logs, and dashboards all speak the same language.

## Before/after generation quality comparison: minimum examples for an eval report

```text
[Prompt]
Show me a Flask 404 exception handling example.

[Before]
Flask has error handling and you can customize 404 pages.

[After]
@app.errorhandler(404)
def handle_404(_):
    return {"error": "not found"}, 404
```

Keeping 5-10 samples like this alongside quantitative metrics helps reach conclusions faster in release meetings.

## Decision rules when perplexity and user metrics conflict

| Situation | Recommended decision |
| --- | --- |
| Perplexity improved, golden score declined | hold deployment, inspect data/prompts |
| Perplexity worsened, golden score improved | acceptable if small; watch long-term trend |
| Both worsened | immediate rollback candidate |
| Both improved | deployment candidate |

The core of evaluation is not a single number but having decision rules defined in advance.

## Evaluation execution example: minimum CLI report

```bash
python eval.py \
  --base-model meta-llama/Llama-3-8B-Instruct \
  --adapter artifacts/adapter-v3 \
  --eval-jsonl data/eval.jsonl \
  --golden-jsonl data/golden.jsonl
```

```text
Pass  run_id=2026-05-21-v3
Pass  perplexity=15.42 (baseline=16.10, delta=-4.22%)
Pass  golden_pass_rate=0.84 (threshold=0.80)
Pass  format_pass_rate=0.95 (threshold=0.92)
Fail  safety_block_rate=0.97 (threshold=0.99)
```

This output can be used directly for release decisions. It shows clearly which metric failed and why.

## Evaluation dataset leakage prevention checks

| Check item | Method |
| --- | --- |
| Train/eval overlap | hash-based deduplication |
| Template leakage | check ratio of identical prompt patterns |
| Temporal leakage | verify recent data is not disproportionately in eval set |
| Answer leakage | check if expected text appears directly in prompts |

Leakage makes metrics look artificially good and leads to quality degradation after deployment.

## Metric extension example: format compliance scoring function

```python
def format_pass_rate(outputs):
    passed = 0
    for text in outputs:
        cond_1 = "```python" in text or "@app" in text
        cond_2 = len(text.strip()) > 20
        if cond_1 and cond_2:
            passed += 1
    return passed / len(outputs)
```

Expressing format rules as explicit functions like this lets the entire team share evaluation criteria through the same code.

## Recommended evaluation result storage format

```json
{
  "run_id": "2026-05-21-v3",
  "model": "llama-3-8b + lora-v3",
  "perplexity": 15.42,
  "golden_pass_rate": 0.84,
  "format_pass_rate": 0.95,
  "safety_block_rate": 0.97,
  "decision": "hold"
}
```

Persisting result files like this connects directly to serving release automation in episode 6 as a deployment gate.

The goal of evaluation automation is not to produce pretty scores but to detect regressions quickly and reduce deployment risk. Fixing this perspective as a team agreement greatly reduces metric interpretation conflicts.

## Answering the Opening Questions

- **How do you calculate perplexity—the first quantitative signal to check right after fine-tuning?**
  - Collect per-batch loss on the evaluation dataset, average them, then compute `exp(mean loss)`. The article's `perplexity()` function gathered losses inside `model.eval()` and `torch.no_grad()`, applying `math.exp(...)` at the end. The key is not the absolute value but repeatedly comparing before-and-after on the same hold-out set.
- **Why isn't a before/after perplexity comparison alone sufficient for evaluation?**
  - Perplexity shows token-prediction unfamiliarity but cannot stand in for format compliance, factuality, safety, or user satisfaction. The article added golden-set scores, format pass rate, and safety criteria alongside, with decision rules for when metrics conflict. Perplexity is a fast regression-detection line, not the entire deployment conclusion.
- **Why maintain a separate evaluation loop even on a tiny demo model?**
  - A few generated samples can look good by chance, but without a separate eval loop there's no way to compare fairly against the next experiment. Automating hold-out perplexity and golden-set scoring even for small models connects directly to a deployment gate before episode 6's serving. The eval loop exists for reproducibility and rollback decisions regardless of model size.

<!-- toc:begin -->
## In this series

- [LLM Fine-tuning 101 (1/6): LLM Fine-tuning Primer](./01-intro.md)
- [LLM Fine-tuning 101 (2/6): Dataset Preparation and Preprocessing](./02-dataset.md)
- [LLM Fine-tuning 101 (3/6): Configuring LoRA Adapters](./03-lora.md)
- [LLM Fine-tuning 101 (4/6): Training Loop and Hyperparameters](./04-training.md)
- **LLM Fine-tuning 101 (5/6): Model Evaluation (current)**
- LLM Fine-tuning 101 (6/6): Model Serving (upcoming)

<!-- toc:end -->

---

## References

- [Perplexity of fixed-length models](https://huggingface.co/docs/transformers/perplexity)
- [Evaluation best practices for language models](https://huggingface.co/docs/evaluate/index)
- [LLM-as-a-judge survey](https://arxiv.org/abs/2306.05685)
- [HELM: Holistic Evaluation of Language Models](https://crfm.stanford.edu/helm/)

Tags: Fine-tuning, LoRA, LLM, Python
