---
title: 'LLM cost tracking and optimization'
series: llm-apps-ops-101
episode: 2
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-01'
---

# LLM cost tracking and optimization

> LLM Apps Ops 101 (2/6)

LLM API costs are billed per token. At development scale the numbers are negligible; at production scale they compound fast. This post covers per-call cost accounting, response caching, and prompt compression — three levers that consistently reduce spend without degrading quality.

## Example code
- [GitHub: en/ep02_cost_tracking.py](https://github.com/yeongseon-books/llm-apps-ops-101/blob/main/en/ep02_cost_tracking.py)

---

## Token cost model

Groq offers a generous free tier, but OpenAI and Anthropic charge per token. Internalizing the cost model lets you swap APIs later without rewriting tracking logic.

```python
from dataclasses import dataclass, field
from datetime import datetime

MODEL_PRICING: dict[str, dict[str, float]] = {
    "llama-3.1-8b-instant":    {"input": 0.00005,  "output": 0.00008},
    "llama-3.1-70b-versatile": {"input": 0.00059,  "output": 0.00079},
    "gpt-4o-mini":             {"input": 0.00015,  "output": 0.00060},
    "gpt-4o":                  {"input": 0.00250,  "output": 0.01000},
    "claude-3-haiku-20240307": {"input": 0.00025,  "output": 0.00125},
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return 0.0
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000

@dataclass
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @property
    def cost_usd(self) -> float:
        return estimate_cost(self.model, self.input_tokens, self.output_tokens)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
```

---

## Cumulative cost tracker

```python
from collections import defaultdict

class CostTracker:
    def __init__(self):
        self._records: list[CostRecord] = []
        self._by_model: dict[str, list[CostRecord]] = defaultdict(list)

    def record(self, model: str, input_tokens: int, output_tokens: int) -> CostRecord:
        rec = CostRecord(model=model, input_tokens=input_tokens, output_tokens=output_tokens)
        self._records.append(rec)
        self._by_model[model].append(rec)
        return rec

    def total_cost(self) -> float:
        return sum(r.cost_usd for r in self._records)

    def by_model(self) -> dict[str, dict]:
        result = {}
        for model, records in self._by_model.items():
            result[model] = {
                "calls": len(records),
                "input_tokens": sum(r.input_tokens for r in records),
                "output_tokens": sum(r.output_tokens for r in records),
                "cost_usd": round(sum(r.cost_usd for r in records), 6),
            }
        return result

    def report(self) -> dict:
        return {
            "total_calls": len(self._records),
            "total_tokens": sum(r.total_tokens for r in self._records),
            "total_cost_usd": round(self.total_cost(), 6),
            "by_model": self.by_model(),
        }
```

---

## Response caching

Calling the LLM twice for the same prompt is waste. A cache that keyed on model, prompt, and temperature returns the stored response instantly.

```python
import hashlib
import json
import time
from pathlib import Path
from typing import Optional

class ResponseCache:
    def __init__(self, cache_dir: str, ttl_seconds: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

    def _key(self, model: str, prompt: str, temperature: float) -> str:
        raw = f"{model}|{temperature}|{prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, model: str, prompt: str, temperature: float) -> Optional[str]:
        key = self._key(model, prompt, temperature)
        path = self.cache_dir / f"{key}.json"
        if not path.exists():
            self._misses += 1
            return None
        data = json.loads(path.read_text())
        if time.time() - data["ts"] > self.ttl:
            path.unlink(missing_ok=True)
            self._misses += 1
            return None
        self._hits += 1
        return data["response"]

    def set(self, model: str, prompt: str, temperature: float, response: str):
        key = self._key(model, prompt, temperature)
        (self.cache_dir / f"{key}.json").write_text(json.dumps({
            "ts": time.time(), "model": model, "response": response,
        }))

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 3) if total else 0.0,
        }
```

---

## Prompt compression

Long system prompts inflate input token counts. Stripping redundant whitespace, duplicate lines, and over-specified examples consistently saves 10–30% without affecting output quality.

```python
import re

def compress_prompt(text: str) -> str:
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.splitlines()]
    deduped = []
    for line in lines:
        if not deduped or line != deduped[-1]:
            deduped.append(line)
    return "\n".join(deduped).strip()

def token_estimate(text: str) -> int:
    """Rough estimate: 4 chars per token for English."""
    return len(text) // 4
```

---

## Integrated cost-optimized pipeline

```python
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

tracker = CostTracker()
cache = ResponseCache(".cache/llm", ttl_seconds=3600)

def cost_optimized_call(
    prompt: str,
    model: str = "llama-3.1-8b-instant",
    temperature: float = 0.0,
) -> str:
    compressed = compress_prompt(prompt)

    cached = cache.get(model, compressed, temperature)
    if cached:
        print(f"  [cache hit] saved ~{token_estimate(cached)} tokens")
        return cached

    llm = ChatGroq(model=model, api_key=os.environ["GROQ_API_KEY"], temperature=temperature)
    response = llm.invoke([HumanMessage(content=compressed)])
    content = response.content

    usage = getattr(response, "usage_metadata", None)
    if usage:
        rec = tracker.record(model, usage.get("input_tokens", 0), usage.get("output_tokens", 0))
        print(f"  [cost] ${rec.cost_usd:.6f} | {rec.total_tokens} tokens")

    cache.set(model, compressed, temperature, content)
    return content

if __name__ == "__main__":
    prompts = [
        "Explain Python decorators in one sentence.",
        "Explain Python decorators in one sentence.",  # cache hit
        "What is the difference between a generator and an iterator?",
    ]
    for p in prompts:
        ans = cost_optimized_call(p)
        print(f"  answer: {ans[:100]}...")

    import json
    print("\n=== cost report ===")
    print(json.dumps(tracker.report(), indent=2))
    print("\n=== cache stats ===")
    print(json.dumps(cache.stats(), indent=2))
```

---

## Cost optimization principles

**Measure before optimizing.** Use `CostTracker` to identify the most expensive calls, then target those first.

Caching is the highest-leverage lever. FAQ-style workloads where the same inputs repeat can hit 80%+ cache rates. Skip caching for creative generation and real-time data queries.

Small-model routing works well for mixed workloads: route simple requests to `llama-3.1-8b-instant` and escalate complex ones to a larger model. The cost difference between 8B and 70B is roughly 10x.

<!-- toc:begin -->
## In this series

- [Monitoring and logging for LLM apps](./01-monitoring-and-logging.md)
- **LLM cost tracking and optimization (current)**
- Evaluating LLM output quality (upcoming)
- LLM app security (upcoming)
- LLM app deployment strategies (upcoming)
- Completing the LLM ops pipeline (upcoming)

<!-- toc:end -->

---

## References

- [Groq pricing](https://groq.com/pricing/)
- [LangChain token usage tracking](https://python.langchain.com/docs/modules/model_io/llms/token_usage_tracking/)
- [OpenAI tokenizer](https://platform.openai.com/tokenizer)

Tags: LLMOps, Observability, Python, LLM
