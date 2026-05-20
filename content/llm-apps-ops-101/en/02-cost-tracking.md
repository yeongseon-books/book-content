---
title: "LLM Apps Ops 101 (2/6): LLM cost tracking and optimization"
series: llm-apps-ops-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-14'
seo_description: Cost tracking is not bookkeeping for its own sake. It is the feedback loop that makes caching, prompt compression, and routing decisions measurable.
---

# LLM Apps Ops 101 (2/6): LLM cost tracking and optimization

LLM costs often look harmless until repeated prompts, traffic growth, or background jobs make them visible all at once. If you do not measure cost per call early, optimization decisions stay qualitative much longer than they should.

This is the second post in the LLM Apps Ops 101 series. Here, we will turn token usage into an explicit cost feedback loop that supports caching, prompt compression, and routing decisions.

Cost optimization does not work as a slogan. You need to know which calls create spend before you can decide what to compress, cache, reroute, or rate-limit.

## Questions to Keep in Mind

- Why should LLM cost be tracked per call instead of waiting for the monthly bill?
- What operations experiments become easier when the price card is separated in code?
- How do you decide whether to cut cost first with caching, model changes, or prompt compression?

## Big Picture

![Cost tracking flow and optimization points](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/02/02-01-big-picture.en.png)

*Cost tracking flow and optimization points*

This picture shows per-call token usage passing through a price card into cost records, then pointing to cache, model, and prompt optimization points. Cost tracking is not a savings tip; it is the operating layer that explains unit economics.

> Cost is not a number to discover at month end; it is an operating signal to record on every request.

## Why this layer matters
![Per-call tokens become cumulative cost](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/02/02-01-why-this-layer-matters.en.png)

*Per-call tokens become cumulative cost*

Cost becomes more important as the feature succeeds, which is exactly why the math should exist in code early.

LLM costs usually start small enough to ignore, then jump when repeated prompts, background jobs, or traffic growth hit at once. If you do not record usage per call, optimization becomes guesswork.

Example file: `en/02-cost-tracking/main.py`

## Minimal runnable example
```python
import json
import os
from dataclasses import asdict, dataclass

from groq import Groq

MODEL = "llama-3.1-8b-instant"
INPUT_PRICE_PER_MILLION_TOKENS = 0.05
OUTPUT_PRICE_PER_MILLION_TOKENS = 0.08

@dataclass
class CostRecord:
    prompt: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float

def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    prompt_cost = (prompt_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION_TOKENS
    completion_cost = (completion_tokens / 1_000_000) * OUTPUT_PRICE_PER_MILLION_TOKENS
    return round(prompt_cost + completion_cost, 8)

def run_prompt(client: Groq, prompt: str) -> CostRecord:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a concise Python assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    usage = response.usage
    if usage is None:
        raise RuntimeError("usage metadata missing from Groq response")
    return CostRecord(
        prompt=prompt,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        total_tokens=usage.total_tokens,
        cost_usd=estimate_cost(usage.prompt_tokens, usage.completion_tokens),
    )

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    prompts = [
        "Summarize Python decorators in one sentence.",
        "Summarize Python decorators in one sentence.",
        "Summarize asyncio.gather in one sentence.",
    ]
    records = [run_prompt(client, prompt) for prompt in prompts]
    report = {
        "input_price_per_million_tokens": INPUT_PRICE_PER_MILLION_TOKENS,
        "output_price_per_million_tokens": OUTPUT_PRICE_PER_MILLION_TOKENS,
        "total_calls": len(records),
        "total_tokens": sum(record.total_tokens for record in records),
        "total_cost_usd": round(sum(record.cost_usd for record in records), 8),
        "records": [asdict(record) for record in records],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

## What to notice in this code
![Repeated prompts become cache candidates](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/02/02-02-what-to-notice-in-this-code.en.png)

*Repeated prompts become cache candidates*
- Separate input and output pricing constants keep the example aligned with how Groq bills this model.
- Persisting one `CostRecord` per call lets you analyze outliers without recomputing reports.
- Repeating one prompt on purpose gives you a baseline for later cache experiments.

## Separate the price card before you need it

Real systems quickly hit two complications. Different models cost different amounts, and input tokens may be priced differently from output tokens. If your code shape already reflects that split, pricing changes become a data update instead of a report rewrite.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PriceCard:
    input_per_million: float
    output_per_million: float

PRICE_CARDS = {
    "llama-3.1-8b-instant": PriceCard(input_per_million=0.05, output_per_million=0.08),
    "llama-3.1-70b-versatile": PriceCard(input_per_million=0.59, output_per_million=0.79),
}

def estimate_split_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    price = PRICE_CARDS[model]
    input_cost = (prompt_tokens / 1_000_000) * price.input_per_million
    output_cost = (completion_tokens / 1_000_000) * price.output_per_million
    return round(input_cost + output_cost, 8)
```

This matters because a request with a long prompt and short answer behaves differently from a request with a short prompt and long answer, even when total tokens look similar.

## Build one report shape for every optimization experiment

Cost reduction rarely comes from one lever. You usually combine caching, prompt compression, and model routing. The discipline is to compare those experiments through the same report shape rather than inventing a new spreadsheet every time.

```python
from collections import Counter
from dataclasses import asdict, dataclass

@dataclass
class OptimizationReport:
    total_calls: int
    repeated_prompt_count: int
    cache_candidate_ratio: float
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost_usd: float

def build_optimization_report(records: list[CostRecord]) -> OptimizationReport:
    prompt_counter = Counter(record.prompt for record in records)
    repeated = sum(count for count in prompt_counter.values() if count > 1)
    return OptimizationReport(
        total_calls=len(records),
        repeated_prompt_count=repeated,
        cache_candidate_ratio=round(repeated / len(records), 3),
        total_prompt_tokens=sum(record.prompt_tokens for record in records),
        total_completion_tokens=sum(record.completion_tokens for record in records),
        total_cost_usd=round(sum(record.cost_usd for record in records), 8),
    )

report = build_optimization_report(records)
print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
```

**Expected output:**

```text
{
  "total_calls": 3,
  "repeated_prompt_count": 2,
  "cache_candidate_ratio": 0.667,
  "total_prompt_tokens": 126,
  "total_completion_tokens": 74,
  "total_cost_usd": 0.00001
}
```

That output immediately answers three operational questions: how much repetition exists, whether prompt-side or completion-side spend dominates, and whether the next experiment should target caching, prompt shortening, or model choice.

## What to cut first in practice

In early production systems, this order is usually the fastest:

1. **Find repeated prompts.** Repetition is the cleanest caching opportunity.
2. **Measure the system prompt.** A long instruction block taxes every request.
3. **Inspect completion length.** Verbose answers can inflate spend without improving product value.
4. **Test model routing.** Send easy cases to cheaper models, but only with a quality gate beside the cost metric.

The important part is not the sequence itself. It is refusing to optimize based on intuition alone.

## Where engineers get confused
![Optimization levers need quality checks](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/02/02-03-where-engineers-get-confused.en.png)

*Optimization levers need quality checks*
- Many vendors price input and output tokens differently. Model your cost records that way from the start.
- A total-cost number alone hides spikes. You also need call count and token distribution.
- Cost optimization without quality checks often means quietly making the product worse.
- High cache hit rate can still be harmful if cache invalidation lets stale answers survive too long.

## When spend jumps, check in this order

```bash
# 1) Compare call volume and average token size first
python3 -m scripts.cost_report --since 2026-05-01 --until 2026-05-02

# 2) Check repeated prompts and the heaviest prompts
python3 -m scripts.cost_report --top-prompts 20

# 3) Break down cost by model
python3 -m scripts.cost_report --group-by model
```

Your real script names may differ. The questions rarely do. Did request count rise? Did token size rise? Did one prompt family or one model create the spike?

## Checklist
- [ ] Store `prompt_tokens`, `completion_tokens`, and `total_tokens` per call
- [ ] Keep pricing constants in one place and split them by model
- [ ] Report both cumulative and per-call cost
- [ ] Mark repeated prompts as cache candidates
- [ ] Pair every cost experiment with a quality check

## Summary
You cannot reduce spend responsibly until you can point to the exact calls that create it.

The real goal is not adding one more metric. It is turning cost signals into operating decisions. In the next post, we will look at the evaluation layer that tells you whether those cheaper calls are still good enough.

## Answering the Opening Questions

- **Why should LLM cost be tracked per call instead of waiting for the monthly bill?**
  - A monthly total cannot tell which endpoint, tenant, prompt, or model created the spend, so it hides the repair target.
- **What operations experiments become easier when the price card is separated in code?**
  - You can recompute price changes, model comparisons, cache savings, and prompt-compression effects with one calculator.
- **How do you decide whether to cut cost first with caching, model changes, or prompt compression?**
  - Start with caching for repeated inputs, smaller models when quality margin exists, and prompt compression when long system or context text is the cost driver.

<!-- toc:begin -->
## In this series

- [LLM Apps Ops 101 (1/6): Monitoring and logging for LLM apps](./01-monitoring-and-logging.md)
- **LLM Apps Ops 101 (2/6): LLM cost tracking and optimization (current)**
- LLM Apps Ops 101 (3/6): Evaluating LLM output quality (upcoming)
- LLM Apps Ops 101 (4/6): LLM app security (upcoming)
- LLM Apps Ops 101 (5/6): LLM app deployment strategies (upcoming)
- LLM Apps Ops 101 (6/6): Completing the LLM ops pipeline (upcoming)

<!-- toc:end -->

---

## References

### Official Docs

- [OpenAI API Pricing](https://openai.com/api/pricing/)
- [Anthropic API Pricing](https://www.anthropic.com/pricing#api)
- [Google AI Studio pricing](https://ai.google.dev/gemini-api/docs/pricing)

### Verification-friendly resource

- [OpenAI Prompt Caching 101](https://cookbook.openai.com/examples/prompt_caching101)

Tags: LLMOps, Observability, Python, LLM
