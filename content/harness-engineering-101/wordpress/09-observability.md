---
title: "바이브코딩을 위한 하네스 엔지니어링 (9/10): Observability — Agent 작업을 추적하고 재현하기"
series: harness-engineering-101
episode: 9
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- AI Agent
- Harness
- Observability
- Tracing
---

# 바이브코딩을 위한 하네스 엔지니어링 (9/10): Observability — Agent 작업을 추적하고 재현하기

이 글은 **바이브코딩을 위한 하네스 엔지니어링** 시리즈의 아홉 번째 글입니다. 에이전트가 무엇을 했는지 추적하고 문제 발생 시 재현할 수 있는 Observability Harness를 다룹니다.

---

에이전트가 이상한 결과를 냈습니다. 다시 실행해보면 다른 결과가 나옵니다. "그때 프롬프트에 뭐가 들어갔지?", "어떤 도구를 어떤 순서로 썼지?", "토큰이 얼마나 나갔지?" — 이 질문에 답할 수 없으면, 에이전트 디버깅은 추측입니다.

Observability Harness는 에이전트의 모든 행동을 기록하고, 특정 실행을 나중에 재현할 수 있게 하는 구조입니다.

> "에이전트를 재현할 수 없으면 디버깅할 수 없습니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 에이전트 실행의 각 단계를 로그로 남기고 있나요?
2. 특정 실행을 나중에 재현할 수 있나요?
3. 에이전트가 사용한 토큰과 비용을 추적하나요?
4. 에이전트 실행 트레이스를 시각화할 수 있나요?
5. 이상한 결과가 나왔을 때 원인을 추적할 수 있나요?

---

## 트레이스 설계

```python
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class TraceSpan:
    span_id: str
    parent_id: str | None
    name: str
    start_time: datetime
    end_time: datetime | None = None
    inputs: dict = field(default_factory=dict)
    outputs: dict = field(default_factory=dict)
    error: str | None = None
    metadata: dict = field(default_factory=dict)

@dataclass
class AgentTrace:
    trace_id: str
    task_id: str
    spans: list[TraceSpan] = field(default_factory=list)
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)
```

## Tracer

```python
class AgentTracer:
    def __init__(self):
        self._traces: dict[str, AgentTrace] = {}
        self._active_trace: AgentTrace | None = None

    def start_trace(self, task_id: str) -> str:
        trace_id = str(uuid.uuid4())
        self._active_trace = AgentTrace(
            trace_id=trace_id,
            task_id=task_id,
        )
        self._traces[trace_id] = self._active_trace
        return trace_id

    def start_span(self, name: str, inputs: dict = None) -> TraceSpan:
        span = TraceSpan(
            span_id=str(uuid.uuid4()),
            parent_id=None,
            name=name,
            start_time=datetime.now(),
            inputs=inputs or {},
        )
        if self._active_trace:
            self._active_trace.spans.append(span)
        return span

    def end_span(self, span: TraceSpan, outputs: dict = None, error: str = None):
        span.end_time = datetime.now()
        span.outputs = outputs or {}
        span.error = error

    def get_trace(self, trace_id: str) -> AgentTrace | None:
        return self._traces.get(trace_id)
```

## 트레이스 사용 예시

```python
tracer = AgentTracer()

def traced_agent_run(task: dict) -> dict:
    trace_id = tracer.start_trace(task["id"])

    span = tracer.start_span("llm_call", inputs={"prompt": task["prompt"]})
    try:
        result = call_llm(task["prompt"])
        tracer.end_span(span, outputs={"response": result})
    except Exception as e:
        tracer.end_span(span, error=str(e))
        raise

    return {"result": result, "trace_id": trace_id}
```

---

## Before / After

| 항목 | Before (로그 없음) | After (Observability) |
|------|------------------|-----------------------|
| 디버깅 | 추측 | 트레이스로 추적 |
| 비용 추적 | 없음 | 스팬별 토큰/비용 기록 |
| 재현 | 불가 | trace_id로 재현 |
| 이상 탐지 | 사람이 발견 | 트레이스 분석 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| print()로만 로그 | 구조화 추적 불가 | TraceSpan으로 구조화 |
| 입출력 미기록 | 재현 불가 | inputs/outputs 필수 |
| 토큰 추적 없음 | 비용 불명 | 스팬마다 토큰 기록 |
| 트레이스 미영속화 | 재시작 후 소실 | JSON/DB 저장 |

---

## AI 활용 팁

```
에이전트 실행을 TraceSpan과 AgentTrace로 추적하는 Observability 구조를 만들어줘.
모든 LLM 호출, 도구 실행, 결과를 스팬으로 기록해야 해.
trace_id로 특정 실행을 조회하고 재현할 수 있어야 해.
각 스팬에 토큰 수와 비용을 기록하는 필드도 포함해줘.
```

---

## 체크리스트

- [ ] TraceSpan dataclass 정의
- [ ] AgentTrace dataclass 정의
- [ ] AgentTracer 구현(시작/종료/조회)
- [ ] LLM 호출에 스팬 래핑
- [ ] 스팬별 토큰/비용 기록
- [ ] 트레이스 영속화(JSON/DB)

---

## 처음 질문으로 돌아가기

"에이전트가 이상한 결과를 냈을 때 어떻게 디버깅하나요?" — 트레이스 없이는 추측만 가능합니다. AgentTracer로 모든 스팬을 기록하면, 어느 단계에서 무슨 입력으로 어떤 출력이 나왔는지 trace_id 하나로 재현할 수 있습니다.

---

## 정리

- 모든 에이전트 실행 단계를 TraceSpan으로 기록한다
- trace_id로 특정 실행을 나중에 조회하고 재현한다
- 스팬마다 토큰과 비용을 기록해 성능과 비용을 추적한다
- 트레이스를 영속화해서 재시작 후에도 분석 가능하게 한다

---

## 참고 자료

- [LangSmith 트레이싱](https://docs.smith.langchain.com/tracing)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 트레이스 설계
- Tracer
- 트레이스 사용 예시
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, AI Agent, Harness, Observability, Tracing
