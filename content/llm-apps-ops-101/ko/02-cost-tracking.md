---
title: 'LLM 비용 추적과 최적화'
series: llm-apps-ops-101
episode: 2
language: ko
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

# LLM 비용 추적과 최적화

> LLM 앱 운영 101 (2/6)

LLM API 비용은 토큰 단위로 청구됩니다. 개발 단계에서는 미미하지만, 트래픽이 늘면 급격히 올라갑니다. 이 포스트에서는 호출별 비용을 정확히 계산하고, 캐싱과 프롬프트 압축으로 비용을 줄이는 방법을 다룹니다.

## 예제 코드
예제 코드: [github.com/yeongseon-books/llm-apps-ops-101](https://github.com/yeongseon-books/llm-apps-ops-101/tree/main/ko)

---

## 토큰 비용 계산

Groq는 현재 무료 티어를 제공하지만, OpenAI나 Anthropic은 토큰당 요금을 부과합니다. 비용 모델을 코드에 내재화해야 나중에 API를 교체해도 추적 로직을 다시 짜지 않아도 됩니다.

```python
from dataclasses import dataclass, field
from datetime import datetime

# ── 모델 가격표 (1000 토큰당 USD) ──────────────────────────────────────────
MODEL_PRICING: dict[str, dict[str, float]] = {
    "llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},
    "llama-3.1-70b-versatile": {"input": 0.00059, "output": 0.00079},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.00060},
    "gpt-4o": {"input": 0.00250, "output": 0.01000},
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """USD 단위 비용을 추정합니다."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return 0.0
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000

# ── 호출별 비용 레코드 ────────────────────────────────────────────────────
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

## 누적 비용 추적기

```python
from collections import defaultdict
from typing import Optional

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

    def total_tokens(self) -> int:
        return sum(r.total_tokens for r in self._records)

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
            "total_tokens": self.total_tokens(),
            "total_cost_usd": round(self.total_cost(), 6),
            "by_model": self.by_model(),
        }
```

---

## 응답 캐싱으로 비용 절감

동일한 프롬프트에 대해 LLM을 반복 호출하는 것은 낭비입니다. 의미적으로 동일한 요청을 캐시에서 반환하면 비용과 지연 시간을 동시에 줄입니다.

```python
import hashlib
import json
import time
from pathlib import Path

class ResponseCache:
    """파일 기반 LLM 응답 캐시."""

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
        path = self.cache_dir / f"{key}.json"
        path.write_text(json.dumps({
            "ts": time.time(),
            "model": model,
            "response": response,
        }, ensure_ascii=False))

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total else 0.0

    def stats(self) -> dict:
        return {"hits": self._hits, "misses": self._misses, "hit_rate": round(self.hit_rate, 3)}
```

---

## 프롬프트 압축

시스템 프롬프트가 길면 입력 토큰이 늘어납니다. 불필요한 공백, 반복 지시, 과도한 예시를 제거하는 것만으로도 토큰을 줄일 수 있습니다.

```python
import re

def compress_prompt(text: str) -> str:
    """기본 프롬프트 압축: 공백 정규화, 중복 줄 제거."""
    # 연속 공백 → 단일 공백
    text = re.sub(r" {2,}", " ", text)
    # 연속 빈 줄 → 단일 빈 줄
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 줄 앞뒤 공백 제거
    lines = [line.strip() for line in text.splitlines()]
    # 중복된 연속 줄 제거
    deduped = []
    for line in lines:
        if not deduped or line != deduped[-1]:
            deduped.append(line)
    return "\n".join(deduped).strip()

def token_estimate(text: str) -> int:
    """토큰 수 근사치 (영어 기준 4자/토큰, 한국어 기준 2자/토큰)."""
    korean_chars = sum(1 for c in text if "\uAC00" <= c <= "\uD7A3")
    other_chars = len(text) - korean_chars
    return korean_chars // 2 + other_chars // 4
```

---

## 통합 비용 최적화 파이프라인

```python
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

tracker = CostTracker()
cache = ResponseCache(".cache/llm", ttl_seconds=3600)

def cost_optimized_call(prompt: str, model: str = "llama-3.1-8b-instant", temperature: float = 0.0) -> str:
    compressed = compress_prompt(prompt)

    # 캐시 조회
    cached = cache.get(model, compressed, temperature)
    if cached:
        print(f"  [캐시 히트] 토큰 절감: ~{token_estimate(cached)}토큰")
        return cached

    llm = ChatGroq(model=model, api_key=os.environ["GROQ_API_KEY"], temperature=temperature)
    response = llm.invoke([HumanMessage(content=compressed)])
    content = response.content

    usage = getattr(response, "usage_metadata", None)
    if usage:
        rec = tracker.record(model, usage.get("input_tokens", 0), usage.get("output_tokens", 0))
        print(f"  [비용] ${rec.cost_usd:.6f} | {rec.total_tokens} 토큰")

    cache.set(model, compressed, temperature, content)
    return content

if __name__ == "__main__":
    prompts = [
        "파이썬 데코레이터를 한 문장으로 설명해 주세요.",
        "파이썬 데코레이터를 한 문장으로 설명해 주세요.",  # 캐시 히트
        "제너레이터와 이터레이터의 차이는 무엇인가요?",
    ]
    for p in prompts:
        ans = cost_optimized_call(p)
        print(f"  답변: {ans[:100]}...")

    print("\n=== 비용 리포트 ===")
    import json
    print(json.dumps(tracker.report(), indent=2, ensure_ascii=False))
    print("\n=== 캐시 통계 ===")
    print(json.dumps(cache.stats(), indent=2, ensure_ascii=False))
```

---

## 비용 최적화 원칙

**측정 없이 최적화는 없습니다.** `CostTracker`로 호출별 비용을 먼저 파악하고, 가장 비싼 호출부터 공략해야 합니다.

캐싱은 가장 확실한 비용 절감 수단입니다. FAQ 응답처럼 동일 입력이 반복되는 경우 hit rate 80% 이상도 가능합니다. 단, 창의적 응답이 필요하거나 실시간 데이터를 다룰 때는 캐싱을 적용하지 않습니다.

소형 모델로 먼저 처리하고, 복잡한 요청만 대형 모델로 에스컬레이션하는 라우팅 전략도 효과적입니다. `llama-3.1-8b-instant`의 비용은 `llama-3.1-70b-versatile`의 약 10분의 1입니다.

<!-- blog-only:start -->
다음 글: [LLM 출력 품질 평가](./03-evaluation.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- **LLM 비용 추적과 최적화 (현재 글)**
- LLM 출력 품질 평가 (예정)
- LLM 앱 보안 (예정)
- LLM 앱 배포 전략 (예정)
- LLM 앱 운영 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Groq 가격 정책](https://groq.com/pricing/)
- [LangChain 응답 메타데이터](https://python.langchain.com/docs/modules/model_io/llms/token_usage_tracking/)
- [OpenAI 토큰 카운팅](https://platform.openai.com/tokenizer)

Tags: LLMOps, Observability, Python, LLM
