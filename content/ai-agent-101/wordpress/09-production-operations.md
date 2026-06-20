---
title: "바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영"
series: ai-agent-101
episode: 9
language: ko
tags:
- Production
- Observability
- Logging
- Tracing
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영

이 글은 **바이브코딩을 위한 AI Agent 기초** 시리즈의 아홉 번째 글입니다.

---

바이브코딩으로 에이전트를 완성하고 실제 사용자에게 배포하는 순간, 완전히 새로운 도전이 시작됩니다. 개발 환경에서는 몰랐던 문제들이 운영에서 나타납니다. "어디서 느려지는지", "왜 가끔 실패하는지", "비용이 얼마나 나오는지"를 파악할 수 없으면 운영이 불가능합니다.

프로덕션 운영의 핵심은 **관측성(Observability)**입니다. 에이전트 내부에서 무슨 일이 일어나고 있는지 로그, 트레이스, 메트릭으로 확인할 수 있어야 합니다. 이 세 가지가 없으면 문제가 생겼을 때 "어떻게 됐는지"를 알 수 없습니다.

> "운영 중인 에이전트를 개선하려면 먼저 볼 수 있어야 합니다. 관측성이 없는 에이전트는 블랙박스입니다."

## 이 글에서 다룰 질문

1. 에이전트 로깅에서 반드시 기록해야 할 정보는 무엇인가요?
2. 분산 트레이싱은 멀티 에이전트에서 어떻게 활용하나요?
3. 에이전트 비용 예산을 코드로 어떻게 통제하나요?
4. FastAPI로 에이전트를 서빙할 때 주의할 점은 무엇인가요?
5. 에이전트 배포 후 어떤 메트릭을 모니터링해야 하나요?

---

## 관측성 3가지 핵심

| 도구 | 무엇을 보는가 | 언제 필요한가 |
|------|-------------|--------------|
| 로그 (Logs) | 이벤트 기록, 오류 메시지 | 무슨 일이 일어났는가 |
| 트레이스 (Traces) | 요청의 전체 실행 경로 | 어디서 느려지는가 |
| 메트릭 (Metrics) | 집계 통계 (성공률, 지연시간) | 전체적으로 어떤 상태인가 |

## Before / After: 로깅 설계

**Before (단순 print)**
```python
print("에이전트 시작")
result = agent.run(goal)
print(f"결과: {result}")
# 문제: 언제, 어떤 요청에서, 얼마나 걸렸는지 기록 없음
```

**After (구조화된 로깅)**
```python
import json
import time
from datetime import datetime

class StructuredLogger:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def log(self, event: str, level: str = "INFO", **kwargs):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "level": level,
            "event": event,
            **kwargs
        }
        print(json.dumps(entry, ensure_ascii=False))

logger = StructuredLogger("research-agent-01")

# 사용 예시
logger.log("agent_start", goal=goal, user_id=user_id)
logger.log("tool_call", tool="web_search", query=query, duration_ms=150)
logger.log("agent_complete", success=True, total_tokens=1200, cost_usd=0.02)
```

## 분산 트레이싱

```python
from contextlib import contextmanager
import uuid

class TraceContext:
    def __init__(self, trace_id: str = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.spans = []

    @contextmanager
    def span(self, name: str, **attrs):
        span_id = str(uuid.uuid4())
        start = time.time()
        try:
            yield span_id
            self.spans.append({
                "trace_id": self.trace_id,
                "span_id": span_id,
                "name": name,
                "duration_ms": (time.time() - start) * 1000,
                "status": "ok",
                **attrs
            })
        except Exception as e:
            self.spans.append({
                "trace_id": self.trace_id,
                "span_id": span_id,
                "name": name,
                "duration_ms": (time.time() - start) * 1000,
                "status": "error",
                "error": str(e)
            })
            raise
```

## 비용 예산 통제

```python
class BudgetEnforcer:
    def __init__(self, max_cost_usd: float):
        self.max_cost = max_cost_usd
        self.current_cost = 0.0

    def check_and_add(self, cost: float):
        if self.current_cost + cost > self.max_cost:
            raise RuntimeError(
                f"예산 초과: 현재 ${self.current_cost:.4f}, "
                f"추가 요청 ${cost:.4f}, "
                f"한도 ${self.max_cost:.4f}"
            )
        self.current_cost += cost
```

## FastAPI 에이전트 서빙

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

class AgentRequest(BaseModel):
    goal: str
    user_id: str
    budget_usd: float = 0.10

class AgentResponse(BaseModel):
    task_id: str
    status: str
    result: str | None = None

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(execute_agent, task_id, request)
    return AgentResponse(task_id=task_id, status="running")

@app.get("/agent/status/{task_id}")
async def get_status(task_id: str):
    # 작업 상태 조회
    return task_store.get(task_id)
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 로그에 user_id, trace_id 없음 | 특정 요청 추적 불가 | 구조화된 로그에 식별자 포함 |
| 동기 API로 에이전트 서빙 | 타임아웃, UX 나쁨 | 비동기 + 폴링 패턴 |
| 비용 예산 없음 | 예기치 않은 청구 폭탄 | BudgetEnforcer로 요청별 한도 설정 |
| 로컬에서만 테스트 | 운영 환경 차이 발견 불가 | 스테이징 환경에서 검증 |

## AI 팁

OpenTelemetry를 사용하면 로그, 트레이스, 메트릭을 표준화된 방식으로 수집하고 다양한 모니터링 도구(Grafana, Jaeger 등)에 연결할 수 있습니다. 에이전트 운영 규모가 커지면 이 표준을 도입하면 관측성 인프라를 한 번만 구축하면 됩니다.

에이전트 응답이 10초 이상 걸릴 수 있다면 동기 API 대신 "작업 제출 → 폴링으로 결과 확인" 패턴을 사용하세요. 사용자 경험이 훨씬 좋아집니다.

## 체크리스트

- [ ] 모든 에이전트 이벤트를 구조화된 JSON 로그로 기록한다
- [ ] trace_id로 전체 요청 경로를 추적할 수 있다
- [ ] 요청별 비용 예산을 코드로 통제한다
- [ ] 에이전트 서빙을 비동기 패턴으로 구현했다
- [ ] 성공률, 응답시간, 비용을 모니터링 대시보드에서 본다

## 처음 질문으로 돌아가기

**에이전트 로깅에서 반드시 기록해야 할 정보는?** timestamp, agent_id, user_id, trace_id, 이벤트 유형, 도구 호출 정보, 소요 시간, 비용.

**분산 트레이싱은 어떻게 활용하나요?** trace_id로 하나의 요청이 여러 에이전트, 도구, 서비스를 거치는 전체 경로를 하나의 트레이스로 연결해 병목 지점을 파악합니다.

**에이전트 비용 예산 통제는?** BudgetEnforcer로 요청별 최대 비용을 설정하고, 초과 시 즉시 중단하고 오류를 반환합니다.

**FastAPI 에이전트 서빙 주의점은?** 에이전트 실행이 오래 걸리므로 동기 방식은 타임아웃 위험이 있습니다. 백그라운드 태스크로 실행하고 task_id를 반환해 폴링하는 패턴이 안전합니다.

**배포 후 모니터링할 메트릭은?** 요청 성공률, 평균 응답 시간, P95/P99 지연시간, 평균 비용/요청, 도구별 오류율.

## 정리

에이전트 프로덕션 운영의 핵심은 관측성입니다. 구조화된 로그, 분산 트레이싱, 메트릭 수집 — 이 세 가지가 없으면 운영 중 문제를 파악하고 개선할 수 없습니다. 비용 예산 통제와 비동기 서빙 패턴도 프로덕션에서 필수입니다. 바이브코딩으로 에이전트를 배포하기 전에 관측성 인프라를 먼저 갖추세요.

다음 글에서는 이 시리즈의 모든 것을 통합해 **첫 번째 에이전트 만들기**를 실습합니다.

## 참고 자료

- [AI Agent 기초 원문: 프로덕션 운영](../ko/09-production-operations.md)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI Agent 기초 (1/10): AI 에이전트란 무엇인가](./01-what-is-an-ai-agent.md)
2. [바이브코딩을 위한 AI Agent 기초 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
3. [바이브코딩을 위한 AI Agent 기초 (3/10): 도구 사용 기초](./03-tool-use-fundamentals.md)
4. [바이브코딩을 위한 AI Agent 기초 (4/10): 에이전트 워크플로우 설계](./04-agent-workflow-design.md)
5. [바이브코딩을 위한 AI Agent 기초 (5/10): 메모리와 상태 관리](./05-memory-and-state.md)
6. [바이브코딩을 위한 AI Agent 기초 (6/10): 멀티 에이전트 시스템](./06-multi-agent-systems.md)
7. [바이브코딩을 위한 AI Agent 기초 (7/10): 에이전트 평가](./07-agent-evaluation.md)
8. [바이브코딩을 위한 AI Agent 기초 (8/10): 오류 처리와 신뢰성](./08-error-handling-reliability.md)
9. **바이브코딩을 위한 AI Agent 기초 (9/10): 프로덕션 운영 (현재 글)**
10. [바이브코딩을 위한 AI Agent 기초 (10/10): 첫 번째 에이전트 만들기](./10-building-first-agent.md)
<!-- toc:end -->

Tags: Production, Observability, Logging, Tracing, 바이브코딩
