---
episode: 7
language: en
last_reviewed: '2026-05-03'
series: ai-data-preparation-101
status: content-ready
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
  tistory: true
title: Synthetic Data Generation - From Self-Instruct to Distillation
seo_description: The most common bottleneck in production LLM fine-tuning is a shortage
  of labeled data. Human annotation costs $1-5 per sample and takes days.
---

# Synthetic Data Generation - From Self-Instruct to Distillation

> AI Data Preparation 101 series (7/10)

In production LLM fine-tuning, the bottleneck is often labeled data rather than model capacity. When annotation is too slow or too expensive, synthetic generation becomes the practical way to expand supervision.

This is post 7 in the AI Data Preparation 101 series. Here we cover common synthetic data generation patterns, from Self-Instruct to distillation.

---
## "If we run out of data, can't we just generate more?"

The most common bottleneck in production LLM fine-tuning is a shortage of labeled data. Human annotation costs $1-5 per sample and takes days. Synthetic data generation auto-generates supervised data using a stronger LLM (the teacher).

Typical use cases:

- **Instruction tuning**: Self-Instruct, Alpaca, Evol-Instruct generating instruction-response pairs with GPT-4 etc.
- **RAG eval**: auto-generating question-answer pairs from documents
- **Data distillation**: using a large model's answers to train a smaller model

This episode walks through 4 patterns with code.

## Pattern 1 - Self-Instruct

Start with a few seed tasks and let the LLM confabulate new instructions. The Alpaca dataset was built this way.

```python
# pip install openai
from openai import OpenAI
import json, random

client = OpenAI()

SEED_TASKS = [
    {"instruction": "Translate the English sentence into Korean.", "input": "The cat sat on the mat.", "output": "고양이가 매트 위에 앉았다."},
    {"instruction": "State the time complexity of the code.", "input": "for i in range(n): print(i)", "output": "O(n)"},
]

PROMPT = """The following are example NLP tasks.
{examples}

Generate 3 new instruction-input-output triples in a JSON array.
Cover different domains.
"""

def generate_synthetic(n_rounds: int = 5, samples_per_round: int = 3) -> list[dict]:
    pool = list(SEED_TASKS)
    for _ in range(n_rounds):
        examples = "\n".join(json.dumps(t, ensure_ascii=False) for t in random.sample(pool, k=2))
        rsp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": PROMPT.format(examples=examples)}],
            response_format={"type": "json_object"},
            temperature=0.9,
        )
        try:
            data = json.loads(rsp.choices[0].message.content)
            new_tasks = data.get("tasks", data) if isinstance(data, dict) else data
            pool.extend(new_tasks[:samples_per_round])
        except (json.JSONDecodeError, KeyError):
            continue
    return pool[len(SEED_TASKS):]
```

The key is high temperature (0.8-1.0) to ensure diversity. The same seeds yield new instructions each round.

## Pattern 2 - Evol-Instruct (difficulty evolution)

Proposed in the WizardLM paper. Rewrite an existing instruction to be harder or deeper.

```python
EVOLUTION_PROMPTS = {
    "deepening": "Rewrite the instruction to require deeper reasoning:\n{instruction}",
    "concretizing": "Recast the instruction into a more concrete, practical scenario:\n{instruction}",
    "reasoning": "Add a constraint that forces multi-step reasoning:\n{instruction}",
    "complicating": "Add one more input condition to the instruction:\n{instruction}",
}

def evolve(instruction: str, kind: str = "deepening") -> str:
    rsp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": EVOLUTION_PROMPTS[kind].format(instruction=instruction)}],
        temperature=0.7,
    )
    return rsp.choices[0].message.content.strip()

simple = "Write a function that sums a list."
hard = evolve(simple, kind="complicating")
# -> "Write a function that sums a list, excluding negatives and including only even numbers."
```

Round-robin across multiple evolution kinds boosts both difficulty and domain diversity.

## Pattern 3 - Auto-generating RAG eval pairs

For each document chunk, generate 1-3 questions answerable from that chunk alone. Use directly for RAG retrieval evaluation.

```python
QA_PROMPT = """Generate 2 questions and answers that can be answered using only the document below.
Questions should sound natural; answers should be directly quotable from the document.

Document:
{chunk}

JSON: {{"pairs": [{{"q": "...", "a": "...", "evidence": "...sentence supporting the answer..."}}, ...]}}
"""

def generate_qa(chunk: str) -> list[dict]:
    rsp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": QA_PROMPT.format(chunk=chunk)}],
        response_format={"type": "json_object"},
        temperature=0.3,  # low because it's fact-based
    )
    return json.loads(rsp.choices[0].message.content)["pairs"]

# Verify: ensure generated evidence actually appears in the chunk
def verify_pairs(chunk: str, pairs: list[dict]) -> list[dict]:
    return [p for p in pairs if p.get("evidence", "") in chunk]
```

The verify step matters. LLMs sometimes fabricate evidence; substring match within the chunk filters those out.

## Pattern 4 - Distillation (strong model -> weak model)

Use GPT-4 answers as a dataset to fine-tune a smaller model.

```python
def distill_one(prompt: str) -> dict:
    rsp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,  # deterministic
    )
    return {"prompt": prompt, "completion": rsp.choices[0].message.content}

prompts = [...]  # tens of thousands of domain prompts
dataset = [distill_one(p) for p in prompts]
# Then LoRA fine-tune a 7B model on this dataset
```

Caveat: always check the teacher model license. OpenAI prohibits "training a competing model on OpenAI outputs". Open-source teachers (LLaMA, Qwen) have more permissive licenses.

## Quality verification - keep synthetic data from hurting training

Always verify synthetic data on 4 axes.

```python
def synthetic_quality_check(samples: list[dict]) -> dict:
    n = len(samples)
    # 1) deduplication: identical instructions should not repeat
    unique_instructions = len({s["instruction"] for s in samples})
    # 2) length distribution
    lens = [len(s["output"]) for s in samples]
    # 3) format compliance: JSON parsing success rate
    valid = sum(1 for s in samples if isinstance(s.get("output"), str))
    # 4) toxicity / refusal rate (simple heuristic)
    refusals = sum(1 for s in samples
                   if any(w in s["output"].lower() for w in ["i cannot", "i'm sorry", "as an ai"]))
    return {
        "n": n,
        "unique_ratio": unique_instructions / n,
        "avg_len": sum(lens) / n,
        "valid_ratio": valid / n,
        "refusal_ratio": refusals / n,
    }
```

A unique_ratio below 0.7 signals a diversity problem. A high refusal_ratio means prompts are too vague or touch overly sensitive topics.

## 5 common mistakes

1. **Using a teacher without checking the license**: training a competitor on OpenAI outputs violates ToS. Use an open-source teacher or hold a commercial license.
2. **Skipping verification**: synthetic QA evidence often does not exist in the source document. Verify with substring or NLI models.
3. **Temperature too low**: 0.0-0.3 kills diversity and produces repeated patterns. Self-Instruct works best at 0.8-1.0.
4. **Fine-tuning on synthetic only**: causes model collapse. Mix with real human data at 1:3 to 1:5 ratios.
5. **Ignoring bias transfer**: teacher bias is copied to student. Always measure demographic distribution.

## Key Takeaways

- Self-Instruct is the baseline pattern: LLM generates new instructions from seeds.
- Evol-Instruct evolves existing instructions to be deeper, more concrete, or multi-step.
- RAG eval pairs are generated per chunk and filtered with substring evidence verification.
- Distillation uses a strong teacher's answers as training data for a smaller student.
- Verification axes: unique_ratio, length distribution, format compliance, refusal rate.
- Mix synthetic with real to prevent model collapse.
- Episode 8 covers data augmentation.

---

<!-- toc:begin -->
## AI Data Preparation 101 series

- [Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- [Tokenization and Chunking Strategies](./05-tokenization-chunking.md)
- [Quality Filtering - Heuristics and Classifiers](./06-quality-filtering.md)
- **Synthetic Data Generation - From Self-Instruct to Distillation (current)**
- Data Augmentation Techniques (upcoming)
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)
<!-- toc:end -->

## References

- [Self-Instruct: Aligning Language Model with Self Generated Instructions (Wang et al., 2022)](https://arxiv.org/abs/2212.10560)
- [WizardLM: Empowering Large Language Models to Follow Complex Instructions (Xu et al., 2023)](https://arxiv.org/abs/2304.12244)
- [Stanford Alpaca - Instruction-tuned LLaMA](https://github.com/tatsu-lab/stanford_alpaca)
- [Synthetic Data Generation with Large Language Models (Long et al., 2024 survey)](https://arxiv.org/abs/2406.15126)

Tags: Synthetic Data, Self-Instruct, Evol-Instruct, Distillation, GPT-4, Alpaca
