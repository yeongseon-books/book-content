---
title: 'LLM 앱 모니터링과 로깅'
series: llm-apps-ops-101
episode: 1
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

# LLM 앱 모니터링과 로깅

> LLM 앱 운영 101 (1/6)

LLM 앱을 프로덕션에 올리는 순간부터 모니터링이 필수입니다. 일반 웹 서비스와 달리 LLM 앱은 응답 시간이 수 초에 달하고, 토큰 소비가 비용으로 직결되며, 모델 출력이 비결정적입니다. 이 포스트에서는 구조화된 로그, 지연 시간 추적, 토큰 카운팅을 중심으로 실용적인 모니터링 기반을 구축합니다.

## 예제 코드
- [GitHub: ko/ep01_monitoring_and_logging.py](https://github.com/yeongseon-books/llm-apps-ops-101/blob/main/ko/ep01_monitoring_and_logging.py)

---

## 왜 LLM 모니터링이 다른가

일반 API 모니터링은 상태 코드, 응답 시간, 처리량 세 가지면 충분합니다. LLM 앱은 그보다 많은 것을 추적해야 합니다.

- **토큰 사용량**: 입력·출력 토큰 각각을 기록해야 비용을 역산할 수 있습니다.
- **모델 파라미터**: temperature, max_tokens가 같은 프롬프트에도 결과를 바꿉니다.
- **프롬프트 버전**: 프롬프트 변경이 품질에 미치는 영향을 추적해야 합니다.
- **지연 시간 분포**: 평균이 아닌 P95, P99가 UX에 직접 영향을 줍니다.

---

## 구조화된 로거 구현

```python
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ── 구조화 로그 포맷터 ──────────────────────────────────────────────────────
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log.update(record.extra)
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log, ensure_ascii=False)

def build_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger

logger = build_logger("llm_ops")

# ── LLM 호출 계측 ──────────────────────────────────────────────────────────
@dataclass
class LLMCallRecord:
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    success: bool = True
    error: str = ""
    prompt_preview: str = ""
    response_preview: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def log(self):
        level = logging.INFO if self.success else logging.ERROR
        logger.log(
            level,
            "llm_call",
            extra={
                "extra": {
                    "call_id": self.call_id,
                    "model": self.model,
                    "prompt_tokens": self.prompt_tokens,
                    "completion_tokens": self.completion_tokens,
                    "total_tokens": self.total_tokens,
                    "latency_ms": round(self.latency_ms, 1),
                    "success": self.success,
                    "error": self.error,
                    "prompt_preview": self.prompt_preview[:120],
                    "response_preview": self.response_preview[:120],
                    "timestamp": self.timestamp,
                }
            },
        )

# ── 계측 래퍼 ──────────────────────────────────────────────────────────────
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

def instrumented_invoke(llm: ChatGroq, prompt: str) -> tuple[str, LLMCallRecord]:
    record = LLMCallRecord(model=llm.model_name, prompt_preview=prompt)
    t0 = time.perf_counter()
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        record.latency_ms = (time.perf_counter() - t0) * 1000
        record.response_preview = response.content

        # Groq usage_metadata
        usage = getattr(response, "usage_metadata", None)
        if usage:
            record.prompt_tokens = usage.get("input_tokens", 0)
            record.completion_tokens = usage.get("output_tokens", 0)

        record.success = True
        return response.content, record

    except Exception as e:
        record.latency_ms = (time.perf_counter() - t0) * 1000
        record.success = False
        record.error = str(e)
        raise
    finally:
        record.log()
```

---

## 지연 시간 히스토그램

단순 평균은 SLA 위반을 가립니다. 지연 시간은 분포로 봐야 합니다.

```python
import math
from collections import defaultdict

class LatencyHistogram:
    """고정 버킷 히스토그램 (밀리초 단위)."""

    BUCKETS = [100, 250, 500, 1000, 2000, 5000, float("inf")]

    def __init__(self):
        self._counts: dict[float, int] = defaultdict(int)
        self._total = 0.0
        self._n = 0
        self._min = float("inf")
        self._max = 0.0

    def record(self, ms: float):
        self._total += ms
        self._n += 1
        self._min = min(self._min, ms)
        self._max = max(self._max, ms)
        for b in self.BUCKETS:
            if ms <= b:
                self._counts[b] += 1
                break

    def percentile(self, p: float) -> float:
        """근사 백분위수 (선형 보간)."""
        if self._n == 0:
            return 0.0
        target = math.ceil(p / 100 * self._n)
        cumulative = 0
        prev_b = 0.0
        for b in self.BUCKETS:
            cumulative += self._counts[b]
            if cumulative >= target:
                ratio = (target - (cumulative - self._counts[b])) / max(self._counts[b], 1)
                return prev_b + ratio * (b - prev_b if b != float("inf") else prev_b)
            prev_b = b
        return self._max

    def summary(self) -> dict:
        return {
            "n": self._n,
            "mean_ms": round(self._total / self._n, 1) if self._n else 0,
            "min_ms": round(self._min, 1) if self._n else 0,
            "max_ms": round(self._max, 1),
            "p50_ms": round(self.percentile(50), 1),
            "p95_ms": round(self.percentile(95), 1),
            "p99_ms": round(self.percentile(99), 1),
        }

# 사용 예시
histogram = LatencyHistogram()

def monitored_call(llm: ChatGroq, prompt: str) -> str:
    content, record = instrumented_invoke(llm, prompt)
    histogram.record(record.latency_ms)
    return content
```

---

## 토큰 예산 추적

```python
from dataclasses import dataclass

@dataclass
class TokenBudget:
    daily_limit: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.daily_limit - self.used)

    @property
    def utilization(self) -> float:
        return self.used / self.daily_limit if self.daily_limit else 0.0

    def consume(self, tokens: int) -> bool:
        """토큰을 소비하고 예산 초과 여부를 반환합니다."""
        self.used += tokens
        if self.used > self.daily_limit:
            logger.warning(
                "token_budget_exceeded",
                extra={
                    "extra": {
                        "used": self.used,
                        "limit": self.daily_limit,
                        "over": self.used - self.daily_limit,
                    }
                },
            )
            return False
        if self.utilization > 0.8:
            logger.warning(
                "token_budget_80pct",
                extra={"extra": {"used": self.used, "limit": self.daily_limit}},
            )
        return True

    def report(self) -> dict:
        return {
            "used": self.used,
            "limit": self.daily_limit,
            "remaining": self.remaining,
            "utilization_pct": round(self.utilization * 100, 1),
        }
```

---

## 통합 실행 예시

```python
import os

budget = TokenBudget(daily_limit=50_000)

def run_with_monitoring(prompt: str) -> str:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    content, record = instrumented_invoke(llm, prompt)
    budget.consume(record.total_tokens)
    monitored_call.__globals__["histogram"].record(record.latency_ms)
    return content

if __name__ == "__main__":
    questions = [
        "파이썬에서 리스트 컴프리헨션이란 무엇인가요?",
        "REST API와 GraphQL의 차이를 설명해 주세요.",
        "도커 컨테이너와 가상 머신의 차이는 무엇인가요?",
    ]
    for q in questions:
        ans = run_with_monitoring(q)
        print(f"\n질문: {q}")
        print(f"답변: {ans[:200]}...")

    print("\n=== 지연 시간 요약 ===")
    print(json.dumps(histogram.summary(), indent=2, ensure_ascii=False))
    print("\n=== 토큰 예산 ===")
    print(json.dumps(budget.report(), indent=2, ensure_ascii=False))
```

---

## 핵심 원칙

**계측은 코드와 함께 설계해야 합니다.** 나중에 붙이는 모니터링은 항상 놓치는 부분이 생깁니다. `instrumented_invoke`처럼 호출 지점을 래핑하면 기존 코드를 전혀 바꾸지 않고도 전수 계측이 가능합니다.

구조화 로그는 `grep`이 아닌 쿼리 언어로 분석합니다. 나중에 Elasticsearch나 BigQuery에 올려도 스키마 변환 없이 바로 사용할 수 있습니다.

P95/P99는 사용자 경험의 척도입니다. LLM 호출이 평균 1초라도 P99가 8초라면, 100명 중 1명은 매번 8초를 기다립니다.

<!-- toc:begin -->
## 시리즈 목차

- **LLM 앱 모니터링과 로깅 (현재 글)**
- LLM 비용 추적과 최적화 (예정)
- LLM 출력 품질 평가 (예정)
- LLM 앱 보안 (예정)
- LLM 앱 배포 전략 (예정)
- LLM 앱 운영 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain Callbacks](https://python.langchain.com/docs/modules/callbacks/)
- [Groq API 응답 메타데이터](https://console.groq.com/docs/api-reference)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

Tags: LLMOps, Observability, Python, LLM
