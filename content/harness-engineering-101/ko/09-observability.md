---
title: Observability — Agent 작업을 추적하고 재현하기
series: harness-engineering-101
episode: 9
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Observability
- Tracing
last_reviewed: '2026-05-03'
seo_description: Agent가 무엇을 했는지 모르면 디버깅도 개선도 불가능합니다. Observability는 Agent의 모든 단계를
  추적, 기록, 재현…
---

# Observability — Agent 작업을 추적하고 재현하기

> Harness Engineering 101 시리즈 (9/10)

Agent가 무엇을 했는지 모르면 디버깅도 개선도 불가능합니다. Observability는 Agent의 모든 단계를 추적, 기록, 재현 가능하게 만드는 일입니다.

---
## Observability란 무엇인가요?

Observability(관측성)는 에이전트가 무엇을, 왜, 어떻게 실행했는지를 외부에서 재구성할 수 있는 능력입니다. 단순히 로그를 남기는 것이 아니라, 사고가 났을 때 "그 시점의 의사결정"을 추적하고 재현할 수 있어야 합니다.

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid

@dataclass
class Span:
    span_id: str
    trace_id: str
    parent_id: str | None
    name: str
    started_at: datetime
    ended_at: datetime | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)
    status: str = "ok"
```

`Span`은 "에이전트의 한 가지 작업 단위"입니다. 도구 호출 1회, LLM 호출 1회, 사고(reflect) 1회가 각각 하나의 span이 됩니다. 같은 trace_id를 공유하는 span들이 모여 하나의 실행 흐름이 됩니다.

## 무엇을 기록해야 할까요?

3가지 정보 계층을 모두 기록해야 추적이 가능합니다.

1. **무엇을 했는가 (What)**: tool name, input, output
2. **왜 그렇게 결정했는가 (Why)**: prompt, model, temperature, retrieved context
3. **얼마나 걸리고 얼마나 들었는가 (Cost)**: latency, token count, cost in dollars

```python
def record_llm_call(span: Span, prompt: str, model: str, response: str, usage: dict):
    span.attributes.update({
        "llm.model": model,
        "llm.prompt_tokens": usage["prompt_tokens"],
        "llm.completion_tokens": usage["completion_tokens"],
        "llm.cost_usd": _calculate_cost(model, usage),
    })
    span.events.append({
        "name": "llm.prompt",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "body": prompt,
    })
    span.events.append({
        "name": "llm.response",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "body": response,
    })
```

prompt와 response를 attributes가 아니라 events로 기록하는 것에 주의하세요. attributes는 검색·필터링용 짧은 메타데이터고, events는 시간 순서가 있는 페이로드입니다.

## Trace 모델 — 한 실행을 끝까지 따라가기

에이전트 한 번 실행은 다음과 같은 트리 구조의 trace를 만듭니다.

```python
class Tracer:
    def __init__(self, exporter):
        self.exporter = exporter
        self._stack: list[Span] = []

    def start(self, name: str, **attrs) -> Span:
        parent_id = self._stack[-1].span_id if self._stack else None
        trace_id = self._stack[0].trace_id if self._stack else str(uuid.uuid4())
        span = Span(
            span_id=str(uuid.uuid4()),
            trace_id=trace_id,
            parent_id=parent_id,
            name=name,
            started_at=datetime.now(timezone.utc),
            attributes=dict(attrs),
        )
        self._stack.append(span)
        return span

    def end(self, status: str = "ok"):
        span = self._stack.pop()
        span.ended_at = datetime.now(timezone.utc)
        span.status = status
        self.exporter.export(span)
```

```text
trace 7a3f...
├── span: agent.run         (12.3s, $0.04)
│   ├── span: llm.plan      (1.2s, $0.01)
│   ├── span: tool.search   (0.8s)
│   ├── span: llm.synthesize(2.1s, $0.02)
│   └── span: tool.send_email(0.3s)
```

이 트리만 있으면 "느린 단계는 어디였나", "비용이 어디서 터졌나", "어느 도구에서 실패했나"를 즉시 답할 수 있습니다.

## Replay — 로그에서 실행을 재현하기

좋은 trace는 "재현 가능"합니다. 동일한 입력으로 같은 단계를 다시 실행해서 같은 결과가 나오는지 확인할 수 있어야 합니다.

```python
def replay_trace(trace_id: str, store) -> list[dict]:
    spans = store.load_spans(trace_id)
    results = []
    for span in spans:
        if span.name.startswith("tool."):
            tool_name = span.attributes["tool.name"]
            tool_input = span.attributes["tool.input"]
            actual = invoke_tool(tool_name, tool_input)
            expected = span.attributes["tool.output"]
            results.append({
                "span": span.name,
                "matches": actual == expected,
                "expected": expected,
                "actual": actual,
            })
    return results
```

Replay가 가능하려면 모든 입력(prompt, retrieved context, tool input)이 span에 기록되어 있어야 합니다. "결과만 기록"하면 재현할 수 없습니다.

## Cost와 Latency 대시보드

운영 중인 에이전트는 비용과 응답 시간이 갑자기 튀는 일이 잦습니다. 대시보드는 다음 4개 지표를 실시간으로 보여줘야 합니다.

```python
@dataclass
class AgentMetrics:
    total_runs: int
    avg_latency_ms: float
    p95_latency_ms: float
    avg_cost_usd: float
    error_rate: float

def aggregate(spans: list[Span]) -> AgentMetrics:
    runs = [s for s in spans if s.name == "agent.run"]
    latencies = [(s.ended_at - s.started_at).total_seconds() * 1000 for s in runs]
    costs = [s.attributes.get("total.cost_usd", 0) for s in runs]
    errors = [s for s in runs if s.status != "ok"]
    latencies_sorted = sorted(latencies)
    p95_idx = int(len(latencies_sorted) * 0.95)
    return AgentMetrics(
        total_runs=len(runs),
        avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
        p95_latency_ms=latencies_sorted[p95_idx] if latencies_sorted else 0,
        avg_cost_usd=sum(costs) / len(costs) if costs else 0,
        error_rate=len(errors) / len(runs) if runs else 0,
    )
```

p95 latency는 평균보다 훨씬 중요합니다. 평균은 정상이어도 5%의 사용자가 30초씩 기다리고 있을 수 있기 때문입니다.

## Alerting — 언제 사람을 깨워야 하는가

모든 이상을 알리면 알림 피로(alert fatigue)가 옵니다. 다음 3가지 조건만 깨우는 알림으로 둡니다.

```python
def should_alert(metrics: AgentMetrics, baseline: AgentMetrics) -> str | None:
    if metrics.error_rate > baseline.error_rate * 2 and metrics.error_rate > 0.05:
        return f"Error rate spike: {metrics.error_rate:.1%}"
    if metrics.p95_latency_ms > baseline.p95_latency_ms * 3:
        return f"P95 latency spike: {metrics.p95_latency_ms:.0f}ms"
    if metrics.avg_cost_usd > baseline.avg_cost_usd * 5:
        return f"Cost spike: ${metrics.avg_cost_usd:.4f}/run"
    return None
```

1. **에러율 급증**: baseline의 2배 이상 + 절대값 5% 이상
2. **P95 latency 급증**: baseline의 3배 이상
3. **건당 비용 급증**: baseline의 5배 이상

## 흔한 실수 5가지

1. **결과만 기록하고 입력은 안 기록**: replay가 불가능해지고, 사고 원인을 추적할 수 없습니다. prompt와 retrieved context를 반드시 기록하세요.
2. **개인정보를 그대로 로깅**: span에 사용자 이메일, 카드 번호 등이 그대로 들어갑니다. 마스킹 또는 해싱 후 기록하세요.
3. **trace_id 전파 실패**: 비동기 호출에서 context를 잃어버려 trace가 끊깁니다. async-aware tracer를 쓰거나 명시적으로 전달하세요.
4. **평균만 보고 P95 무시**: 평균은 정상이어도 5%가 30초씩 걸릴 수 있습니다. 항상 percentile을 함께 보세요.
5. **모든 이상에 알림**: 알림 피로로 진짜 알림을 놓치게 됩니다. baseline 대비 배수와 절대 임계치를 함께 쓰세요.

## 핵심 요약

- Observability는 사고 후 의사결정을 추적·재현할 수 있는 능력입니다.
- Span은 작업 단위, Trace는 한 실행의 트리 구조입니다.
- What(무엇), Why(왜), Cost(비용) 3계층을 모두 기록하세요.
- Prompt와 retrieved context까지 기록해야 replay가 가능합니다.
- 평균이 아닌 p95 latency를, baseline 대비 배수로 알림을 설계하세요.

다음 글은 Production Harness입니다. 지금까지 배운 9가지 harness를 묶어 실제 운영 환경에 배포하는 패턴을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- [Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기](./02-task-harness.md)
- [Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기](./03-context-harness.md)
- [Constraint Harness — 규칙, 경계, 금지 행동 정의하기](./04-constraint-harness.md)
- [Tool Harness — Agent가 사용할 도구를 안전하게 설계하기](./05-tool-harness.md)
- [Test Harness — 완료 조건을 테스트로 고정하기](./06-test-harness.md)
- [Feedback Loop — 실패를 고치게 만드는 반복 구조](./07-feedback-loop.md)
- [Approval Gate — 사람 승인이 필요한 지점 설계하기](./08-approval-gate.md)
- **Observability — Agent 작업을 추적하고 재현하기 (현재 글)**
- Production Harness — 운영 가능한 Agent 작업 환경 만들기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [OpenTelemetry — Tracing concepts](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Google SRE — Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [LangSmith — Tracing for LLM applications](https://docs.smith.langchain.com/observability)
- [Honeycomb — Observability engineering](https://www.honeycomb.io/blog/what-is-observability)

Tags: AI Agent, Harness, Production, Reliability
