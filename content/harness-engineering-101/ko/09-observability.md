---
title: "Harness Engineering 101 (9/10): Observability — Agent 작업을 추적하고 재현하기"
series: harness-engineering-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Harness
- Observability
- Tracing
last_reviewed: '2026-05-14'
seo_description: Agent가 무엇을 했는지 모르면 디버깅도 개선도 불가능합니다. Observability는 Agent의 모든 단계를
  추적, 기록, 재현…
---

# Harness Engineering 101 (9/10): Observability — Agent 작업을 추적하고 재현하기
에이전트가 무엇을 했는지 모르면 디버깅도 개선도 불가능합니다. 이 문장은 단순한 상식처럼 보이지만, 실제 운영에서는 여전히 많은 시스템이 결과 문자열만 남기고 그 뒤의 의사결정 과정을 잃어버립니다.
문제는 에이전트 시스템이 전통적인 함수보다 훨씬 많은 중간 단계를 가진다는 점입니다. 모델 호출, retrieval, tool invocation, reflection, approval, retry가 모두 실행 경로에 들어가는데, 이 중 하나라도 기록이 끊기면 사고 재현이 거의 불가능해집니다.
Observability는 로그를 많이 남기는 일이 아니라, 한 번의 실행을 외부에서 다시 구성할 수 있게 만드는 설계입니다. 무엇을 했는지, 왜 그렇게 했는지, 얼마나 걸리고 얼마나 들었는지를 같은 trace 안에서 읽을 수 있어야 합니다.
이 글은 Harness Engineering 101 시리즈의 9번째 글입니다.
운영 가능한 에이전트는 답변만 내는 시스템이 아니라, 답변이 만들어진 경로까지 설명할 수 있는 시스템입니다.
## 먼저 던지는 질문

- Observability Harness는 agent 실행을 나중에 어떻게 다시 구성할 수 있게 해야 할까요?
- trace, replay, cost·latency dashboard는 각각 어떤 운영 질문에 답할까요?
- 어떤 신호가 사람을 깨워야 하는 alert가 되어야 할까요?

## 큰 그림

![Observability - Agent 작업을 추적하고 재현하기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/09/09-01-observability-tracing-and-replaying-agen.ko.png)

*Observability - Agent 작업을 추적하고 재현하기*

이 그림에서는 agent 작업이 trace, replay, 비용·지연 지표로 기록되어 나중에 재구성되는 흐름을 봅니다. Observability Harness는 마지막 답변을 저장하는 것이 아니라 한 번의 실행이 왜 그렇게 흘렀는지 추적 가능한 증거를 남깁니다.

> 관측 가능한 agent는 “무슨 답을 했나”가 아니라 “어떤 입력, context, tool, 비용, 판단으로 그 답이 나왔나”를 말할 수 있습니다.

## 왜 이 글이 중요한가
Observability가 중요한 첫 번째 이유는 재현성입니다. 사고가 났을 때 당시 모델이 어떤 prompt와 retrieved context를 봤는지 모르면 같은 문제를 다시 만들 수 없습니다.
두 번째 이유는 비용과 성능입니다. 에이전트는 어느 단계에서 비용이 터지고 어느 단계에서 느려졌는지 모르면 최적화 대상도 찾기 어렵습니다. 모델만 비싼 것이 아니라 retrieval, judge, reflection도 모두 비용을 만듭니다.
세 번째 이유는 책임 추적입니다. approval, retry, tool execution이 섞인 시스템에서 누가 무엇을 결정했는지 보이지 않으면 운영 개선은 추측에 머무릅니다.
## 핵심 관점
좋은 observability는 단순 로그 목록이 아니라 구조화된 trace를 남깁니다. span은 작업 단위이고, trace는 한 실행의 전체 트리입니다. 이 구조가 있어야 어떤 단계가 느렸고 어떤 단계가 실패했는지 즉시 볼 수 있습니다.
기록은 최소 세 층을 가져야 합니다. 무엇을 했는지, 왜 그렇게 했는지, 얼마나 걸리고 얼마나 들었는지입니다. 결과만 남기면 replay가 안 되고, 비용만 남기면 원인을 찾을 수 없습니다.
또한 observability는 알림 설계까지 포함합니다. 모든 이상을 다 깨우면 alert fatigue가 오므로, baseline 대비 error rate, p95 latency, per-run cost 같은 소수의 신호만 paging 대상으로 올려야 합니다.
> 결과만 남기는 로그는 설명이 아닙니다. Observability는 한 번의 실행을 외부에서 다시 구성할 수 있을 만큼 충분한 구조를 남기는 일입니다.
## 핵심 개념
Agent가 무엇을 했는지 모르면 디버깅도 개선도 불가능합니다. Observability는 Agent의 모든 단계를 추적, 기록, 재현 가능하게 만드는 일입니다.

### Observability란 무엇인가요?

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

### 무엇을 기록해야 할까요?

![무엇을 기록해야 할까요](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/09/09-02-what-should-you-record.ko.png)

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

### Trace 모델 — 한 실행을 끝까지 따라가기

![Trace 모델 - 한 실행을 끝까지 따라가기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/09/09-03-trace-model-following-one-run-end-to-end.ko.png)

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
├── span: agent.run           (12.3s, $0.04)
│   ├── span: llm.plan        (1.2s, $0.01)
│   ├── span: tool.search     (0.8s)
│   ├── span: llm.synthesize  (2.1s, $0.02)
│   └── span: tool.send_email (0.3s)
```

이 트리만 있으면 "느린 단계는 어디였나", "비용이 어디서 터졌나", "어느 도구에서 실패했나"를 즉시 답할 수 있습니다.

### Replay — 로그에서 실행을 재현하기

![Replay - 로그에서 실행을 재현하기](https://yeongseon-books.github.io/book-public-assets/assets/harness-engineering-101/09/09-04-replay-reproducing-a-run-from-logs.ko.png)

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

### Cost와 Latency 대시보드

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

### Alerting — 언제 사람을 깨워야 하는가

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

### OpenTelemetry 속성 표준화

Observability가 팀마다 달라지는 가장 큰 이유는 속성 키가 제각각이기 때문입니다. 어떤 서비스는 `model`, 어떤 서비스는 `llm_name`, 또 다른 서비스는 `provider_model`처럼 쓰면 공통 대시보드와 쿼리가 깨집니다. 최소 키 집합을 표준화해야 합니다.

```yaml
# tracing_conventions.yaml
span_names:
  root: agent.run
  planning: llm.plan
  synthesis: llm.synthesize
  retrieval: rag.retrieve
  tool: tool.invoke

required_attributes:
  - agent.version
  - agent.task_id
  - llm.model
  - llm.prompt_tokens
  - llm.completion_tokens
  - cost.usd
  - latency.ms
  - user.request_id
  - safety.approval_required
```

```python
REQUIRED_ATTRS = {
    "agent.version",
    "agent.task_id",
    "llm.model",
    "llm.prompt_tokens",
    "llm.completion_tokens",
    "cost.usd",
    "latency.ms",
    "user.request_id",
    "safety.approval_required",
}

def validate_span_attributes(span: Span) -> None:
    missing = sorted(REQUIRED_ATTRS - set(span.attributes.keys()))
    if missing:
        raise ValueError(f"span missing required attrs ({span.name}): {missing}")
```

이 검증을 CI와 런타임 샘플링에 함께 넣으면, observability 품질 자체를 테스트할 수 있습니다.

### PII 최소화와 보존 정책

trace가 자세할수록 보안 위험도 커집니다. 특히 prompt와 tool input을 그대로 저장하면 개인 정보가 쉽게 남습니다. Observability Harness는 기록량을 늘리는 설계와 동시에 보존 정책을 가져야 합니다.

```python
import re

def redact_pii(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b\d{2,3}-\d{3,4}-\d{4}\b", "[REDACTED_PHONE]", text)
    text = re.sub(r"\b\d{6}-\d{7}\b", "[REDACTED_KR_RRN]", text)
    return text

def sanitize_event_payload(event: dict) -> dict:
    body = event.get("body")
    if isinstance(body, str):
        event["body"] = redact_pii(body)
    return event
```

```yaml
# retention_policy.yaml
retention:
  hot_trace_days: 14
  warm_trace_days: 90
  cold_archive_days: 365
  delete_after_days: 365

sampling:
  default_rate: 0.2
  error_rate: 1.0
  high_risk_action_rate: 1.0
```

보존 정책을 명시하지 않으면 비용과 규정 준수 문제가 동시에 터집니다. 반대로 너무 빨리 지우면 재현이 불가능해집니다. 보통 정상 트래픽은 샘플링하고, 실패/고위험 이벤트는 100% 보존하는 이중 전략이 현실적입니다.

### 실행 재현 리포트 자동 생성

trace를 저장하는 것과 사람이 이해할 수 있는 보고서를 만드는 것은 별개입니다. 장애 대응 속도를 높이려면 trace 한 건에서 핵심 요약을 자동 생성해야 합니다.

```python
def build_incident_report(trace_id: str, store) -> dict:
    spans = store.load_spans(trace_id)
    root = next(s for s in spans if s.parent_id is None)
    failed = [s for s in spans if s.status != "ok"]

    return {
        "trace_id": trace_id,
        "agent_version": root.attributes.get("agent.version"),
        "task_id": root.attributes.get("agent.task_id"),
        "total_latency_ms": root.attributes.get("latency.ms"),
        "total_cost_usd": root.attributes.get("cost.usd"),
        "failed_spans": [
            {
                "name": s.name,
                "status": s.status,
                "error": s.attributes.get("error.message", ""),
            }
            for s in failed
        ],
    }
```

이 리포트는 on-call이 처음 5분 안에 보는 핵심 자료입니다. 디버깅을 잘하는 팀은 로그를 많이 보는 팀이 아니라, 첫 화면에서 다음 액션이 보이도록 자료를 정리하는 팀입니다.

### 분산 실행에서 trace_id 전파

agent 런타임이 단일 프로세스가 아니라 큐, 워커, 외부 도구 서비스로 분리되면 trace가 쉽게 끊깁니다. trace_id 전파 규칙을 프로토콜 수준에서 강제해야 end-to-end 재현이 가능합니다.

```python
def inject_trace_headers(headers: dict, trace_id: str, span_id: str) -> dict:
    h = dict(headers)
    h["x-trace-id"] = trace_id
    h["x-parent-span-id"] = span_id
    return h

def extract_trace_headers(headers: dict) -> tuple[str | None, str | None]:
    return headers.get("x-trace-id"), headers.get("x-parent-span-id")

def enqueue_with_trace(queue, message: dict, trace_id: str, span_id: str) -> None:
    message = dict(message)
    message["_trace"] = {"trace_id": trace_id, "parent_span_id": span_id}
    queue.publish(message)
```

이 규칙이 없으면 tool 호출 지연이 생겼을 때 root trace와 연결이 안 되어 원인 분석 시간이 크게 늘어납니다.

### 운영 대시보드 예시 쿼리

관측 데이터가 쌓여도 질문을 못 던지면 소용이 없습니다. 아래는 on-call에서 가장 자주 쓰는 질문입니다.

```text
Q1. 지난 30분 실패율이 높은 task_id는 무엇인가?
Q2. approval_required=true 인 요청에서 bypass 시도가 있었는가?
Q3. model=... 버전 전환 이후 cost.usd/run 증가는 얼마인가?
Q4. policy_violation이 특정 tool에서 집중되는가?
Q5. repeated_failure_signature 상위 10개는 무엇인가?
```

```python
def top_failed_tasks(spans: list[Span], window_minutes: int = 30) -> list[tuple[str, int]]:
    import collections
    failures = collections.Counter()
    for s in spans:
        if s.name == "agent.run" and s.status != "ok":
            task_id = s.attributes.get("agent.task_id", "unknown")
            failures[task_id] += 1
    return failures.most_common(10)

def approval_bypass_attempts(spans: list[Span]) -> int:
    return sum(1 for s in spans if s.attributes.get("safety.approval_bypass") is True)
```

핵심은 대시보드를 화려하게 만드는 것이 아니라, 장애 대응 질문에 즉시 답할 수 있는 쿼리를 준비하는 것입니다.

운영 주기가 길어질수록 지표 정의도 버전 관리해야 합니다. 예를 들어 `cost.usd` 계산식이 모델 가격표 변경으로 달라지면 과거와 현재를 그대로 비교할 수 없습니다. metric definition version을 함께 기록하면 "지표가 나빠진 것인지 계산식이 바뀐 것인지"를 분리해 해석할 수 있습니다.

또한 주간 리뷰에서 "가장 비싼 상위 20개 trace"를 정기적으로 확인하면 비용 최적화 기회가 빠르게 보입니다. 대부분은 모델 자체보다 불필요한 reflect 반복이나 과도한 retrieval 문서 수에서 발생합니다.

관측 데이터 접근 권한도 계층화해야 합니다. on-call은 전체 trace 메타데이터를 보되, 원문 prompt/body 열람은 최소 권한 그룹으로 제한하면 보안과 운영 편의의 균형을 맞출 수 있습니다. Observability Harness는 기술 구성뿐 아니라 접근 통제까지 포함한 운영 정책으로 완성됩니다.

마지막으로 replay 성공률 자체를 KPI로 두면 좋습니다. 샘플 trace 중 재현에 성공한 비율을 주간 지표로 관리하면 "기록은 남았지만 실제로는 재현이 안 되는" 숨은 품질 문제를 조기에 발견할 수 있습니다.
## 흔히 헷갈리는 지점
- 출력만 저장해도 디버깅은 가능하다고 생각하기 쉽지만, prompt와 retrieved context가 없으면 replay가 불가능합니다.
- PII는 나중에 마스킹하면 된다고 보기 쉽지만, raw span에 들어가는 순간 이미 새로운 위험이 됩니다.
- trace_id 전파는 구현 세부라고 생각하기 쉽지만, 비동기 경계에서 trace가 끊기면 전체 실행을 읽을 수 없습니다.
- 평균 latency만 보면 충분하다고 생각하기 쉽지만, 실제 체감 문제는 대개 p95에서 먼저 나타납니다.
- 모든 이상에 paging을 걸면 더 안전할 것 같지만, alert fatigue는 결국 진짜 알림을 묻어 버립니다.
## 운영 체크리스트
- [ ] 모든 실행을 trace와 span 구조로 기록합니다.
- [ ] What, Why, Cost 세 층의 메타데이터를 함께 저장합니다.
- [ ] prompt, retrieved context, tool input처럼 replay에 필요한 입력을 남깁니다.
- [ ] 대시보드에 error rate, p95 latency, avg cost per run을 기본 지표로 둡니다.
- [ ] baseline 대비 급증 조건에만 paging을 걸고 나머지는 리포트성 알림으로 분리합니다.
## 정리
Observability는 에이전트가 무엇을 했는지 보는 기능이 아니라, 왜 그런 결과가 나왔는지 나중에 다시 설명할 수 있게 만드는 운영 능력입니다. 이것이 있어야 디버깅, 비용 최적화, 사고 분석이 모두 가능해집니다.
여기서 가장 중요한 것은 구조입니다. span과 trace로 실행을 묶고, 결과뿐 아니라 입력과 근거와 비용을 함께 남겨야 replay가 가능합니다.
다음 글에서는 마지막으로 Production Harness를 다룹니다. 지금까지 만든 모든 harness를 배포, 롤백, on-call까지 포함한 실제 운영 환경으로 묶는 단계입니다.

## 처음 질문으로 돌아가기

- **Observability Harness는 agent 실행을 나중에 어떻게 다시 구성할 수 있게 해야 할까요?**
  - 요청 id, 입력, context snapshot, tool call, 중간 판단, 비용, latency, 오류, 최종 결과를 하나의 trace로 묶어야 합니다.
- **trace, replay, cost·latency dashboard는 각각 어떤 운영 질문에 답할까요?**
  - trace는 경로를, replay는 재현 가능성을, dashboard는 비용·지연·오류의 추세와 병목을 보여 줍니다.
- **어떤 신호가 사람을 깨워야 하는 alert가 되어야 할까요?**
  - 사용자 영향이 큰 실패율 증가, 비용 폭주, 반복 tool 실패, 승인 우회 시도, rollback 실패처럼 즉시 조치가 필요한 신호가 alert가 되어야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Harness Engineering 101 (1/10): Harness Engineering이란 무엇인가?](./01-what-is-harness-engineering.md)
- [Harness Engineering 101 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기](./02-task-harness.md)
- [Harness Engineering 101 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기](./03-context-harness.md)
- [Harness Engineering 101 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기](./04-constraint-harness.md)
- [Harness Engineering 101 (5/10): Tool Harness — Agent가 사용할 도구를 안전하게 설계하기](./05-tool-harness.md)
- [Harness Engineering 101 (6/10): Test Harness — 완료 조건을 테스트로 고정하기](./06-test-harness.md)
- [Harness Engineering 101 (7/10): Feedback Loop — 실패를 고치게 만드는 반복 구조](./07-feedback-loop.md)
- [Harness Engineering 101 (8/10): Approval Gate — 사람 승인이 필요한 지점 설계하기](./08-approval-gate.md)
- **Harness Engineering 101 (9/10): Observability — Agent 작업을 추적하고 재현하기 (현재 글)**
- Harness Engineering 101 (10/10): Production Harness — 운영 가능한 Agent 작업 환경 만들기 (예정)

<!-- toc:end -->

## 참고 자료
### 공식 문서

- [OpenTelemetry — Tracing concepts](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Google SRE — Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [LangSmith — Tracing for LLM applications](https://docs.smith.langchain.com/observability)
- [Honeycomb — Observability engineering](https://www.honeycomb.io/blog/what-is-observability)
### 관련 시리즈

- [LangGraph 101 — 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Safety & Guardrails 101 — 운영 가드레일 시스템 구축](../../ai-safety-guardrails-101/ko/10-production-guardrail-system.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/harness-engineering-101/ko/09-observability)

Tags: AI Agent, Harness, Production, Reliability
