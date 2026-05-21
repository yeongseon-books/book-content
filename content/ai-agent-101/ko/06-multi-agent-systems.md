---
title: "AI Agent 101 (6/10): Multi-Agent 시스템"
series: ai-agent-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Multi-Agent
- Coordination
- Delegation
last_reviewed: '2026-05-15'
seo_description: Multi-agent 시스템의 핵심인 역할 분리와 위임 구조를 다양한 설계 패턴과 운영 관점에서 정리합니다.
---

# AI Agent 101 (6/10): Multi-Agent 시스템

하나의 agent에 검색, 작성, 검토, 계획, 최종 응답까지 모두 맡기면 처음에는 단순해 보입니다. 하지만 요청이 길어지고 역할이 늘어나면 곧 문제가 생깁니다. 누가 계획을 세우는지, 누가 검증하는지, 누가 최종 책임을 지는지가 흐려지기 때문입니다.

이때 등장하는 해법이 multi-agent 시스템입니다. 다만 중요한 점은 agent 수를 늘리는 것 자체가 목적이 아니라는 사실입니다. 좋은 multi-agent는 역할을 나눠서 더 설명 가능하게 만들고, 나쁜 multi-agent는 역할을 나눠서 더 복잡하게 만듭니다.

실무에서 multi-agent를 잘못 도입하면 token 비용과 handoff 횟수만 늘고 품질은 오히려 떨어질 수 있습니다. 그래서 이 주제는 "여러 agent를 어떻게 띄울까"보다 "어떤 업무가 진짜로 위임 구조를 필요로 하는가"에서 출발해야 합니다.

이 글은 AI Agent 101 시리즈의 여섯 번째 글입니다.

이 글에서는 multi-agent를 모델 개수의 문제가 아니라 역할 분리와 위임 프로토콜의 문제로 정리하겠습니다.

![멀티 에이전트 handoff 그래프](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/06/06-01-multi-agent-handoff-graph.ko.png)
*멀티 에이전트 handoff 그래프*
> Multi-agent가 필요한 순간은 agent 수를 늘리고 싶을 때가 아니라, 한 agent 안에 넣기에는 책임 경계가 서로 충돌할 때입니다.

## 먼저 던지는 질문

- single agent로 충분한 업무와 multi-agent가 필요한 업무는 어디서 갈라질까요?
- supervisor, worker, handoff 계약은 각각 어떤 책임을 가져야 할까요?
- agent를 여러 개로 나눌수록 비용과 실패 지점은 어떻게 늘어날까요?

## 왜 이 글이 중요한가

multi-agent는 종종 성능 향상 도구로 소개되지만, 실제 현장에서는 구조화된 위임을 위한 도구에 더 가깝습니다. 어떤 agent가 어떤 종류의 결정을 하고 어떤 산출물만 남겨야 하는지 분리되면, 시스템이 커져도 읽기가 쉬워집니다.

반대로 역할 분리 없이 agent만 여러 개 두면 문제가 더 커집니다. 서로에게 같은 질문을 넘기고, 동일한 정보를 중복 검색하고, 최종 답변 책임이 불명확해지고, 장애가 나도 어디서 틀어졌는지 추적하기 어려워집니다. 즉, multi-agent의 난점은 모델 수가 아니라 프로토콜 설계입니다.

또한 이 주제는 운영과 평가에도 직결됩니다. route 정확도, handoff 수, agent별 latency, shared state 오염, 불필요한 delegation 비율 같은 지표는 multi-agent 구조가 있어야만 드러납니다. 그래서 역할 분리를 도입한다면 관측성도 함께 설계해야 합니다.

## 핵심 관점

multi-agent를 "여러 agent가 함께 일한다"고만 설명하면 너무 추상적입니다. 더 실용적인 설명은 누가 어떤 하위 작업을 맡고 어떤 결과만 남기는지 정의된 위임 그래프라는 것입니다. 이 관점이 있어야 supervisor와 worker, reviewer와 writer, manager와 child agent의 차이가 선명해집니다.

이 구조에서 중요한 것은 세 가지입니다. 첫째, 누가 route를 결정하는가. 둘째, 각 agent가 shared state의 어느 부분을 읽고 쓸 수 있는가. 셋째, 누가 최종 답을 사용자에게 돌려주는가. 이 세 가지가 모호하면 agent 수가 늘수록 시스템은 더 읽기 어려워집니다.

실무에서는 multi-agent를 쓰는 이유가 똑똑해 보이기 위해서가 아니라, 책임을 좁히고 실패 범위를 줄이기 위해서여야 합니다. 그래야 비용이 늘어도 얻는 운영 이점이 분명합니다.

> multi-agent 시스템의 핵심은 "agent가 여러 개다"가 아니라, "역할과 handoff 규칙이 코드와 상태에 명시되어 있다"는 데 있습니다.

## 핵심 개념

### 먼저 위임 그래프를 그리면 multi-agent가 필요한지 더 빨리 판단할 수 있습니다

![위임 그래프로 multi-agent 필요성을 빠르게 판단](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/06/06-01-multi-agent-patterns.ko.png)
*multi-agent 시스템은 여러 모델을 늘어놓는 구조가 아니라, 누가 어떤 하위 작업을 맡고 어떤 상태만 공유할지 정한 위임 그래프로 보는 편이 안전합니다.*

### Orchestrator 패턴은 중앙 조율에 강합니다

```python
from typing import List, Dict
from openai import OpenAI

class WorkerAgent:
    """A specialized worker agent."""

    def __init__(self, name: str, role: str, api_key: str):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key)

    def execute(self, task: str) -> str:
        """Execute a task."""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a {self.role}."},
                {"role": "user", "content": task}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

class OrchestratorAgent:
    """An orchestrator agent that coordinates workers."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.workers: Dict[str, WorkerAgent] = {}

    def register_worker(self, worker: WorkerAgent) -> None:
        """Register a worker."""
        self.workers[worker.name] = worker

    def plan(self, request: str) -> List[Dict]:
        """Decompose the request into subtasks."""
        worker_list = "\n".join([
            f"- {name}: {w.role}"
            for name, w in self.workers.items()
        ])
        prompt = f"""Break down the following request into subtasks and assign each to the appropriate worker.

Available workers:
{worker_list}

Request: {request}

Respond in JSON format:
[
  {{"worker": "worker_name", "task": "task description"}},
  ...
]
"""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        import json
        return json.loads(response.choices[0].message.content)

    def handle(self, request: str) -> Dict:
        """Handle the request."""
        subtasks = self.plan(request)
        results = {}
        for subtask in subtasks:
            worker_name = subtask["worker"]
            task = subtask["task"]
            if worker_name in self.workers:
                results[worker_name] = self.workers[worker_name].execute(task)
        return results
```

Orchestrator는 중앙에서 route와 fallback을 관리하기 좋습니다. 단계가 명확하고 승인 지점을 넣기 쉬우며, 로그를 한곳에서 모으기도 쉽습니다. 대신 단일 병목과 단일 실패 지점이 생긴다는 단점이 있습니다.

### Peer-to-Peer는 유연하지만 프로토콜이 약하면 금방 흐려집니다

```python
from typing import List, Optional

class PeerAgent:
    """A peer agent."""

    def __init__(self, name: str, role: str, api_key: str):
        self.name = name
        self.role = role
        self.client = OpenAI(api_key=api_key)
        self.peers: List["PeerAgent"] = []
        self.message_history: List[Dict] = []

    def add_peer(self, peer: "PeerAgent") -> None:
        """Add a peer."""
        if peer not in self.peers:
            self.peers.append(peer)

    def send_message(self, recipient: "PeerAgent", message: str) -> str:
        """Send a message to a peer."""
        msg = {
            "from": self.name,
            "to": recipient.name,
            "content": message
        }
        self.message_history.append(msg)
        return recipient.receive_message(self, message)

    def receive_message(self, sender: "PeerAgent", message: str) -> str:
        """Receive a message and respond."""
        prompt = f"""You are {self.name}, a {self.role}.\nMessage from {sender.name}: {message}\n\nRespond appropriately. If you need help from another peer, mention it."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        reply = response.choices[0].message.content

        self.message_history.append({
            "from": sender.name,
            "to": self.name,
            "content": message,
            "reply": reply
        })
        return reply
```

이 패턴은 창의적 협업이나 리뷰-피드백 흐름에는 자연스럽습니다. 하지만 누가 종료를 선언하는지, 어느 시점에 escalation하는지, 동일 요청을 다시 보내면 어떻게 막을지 같은 규칙이 없으면 곧 루프와 중복이 생깁니다.

### 최소한의 handoff 스켈레톤을 직접 돌려 보면 역할 경계가 더 분명해집니다

아래 예시는 OpenAI API 없이도 orchestrator가 하위 agent를 호출하고, 각 agent가 shared state에 무엇을 남기는지 검증하는 아주 작은 프로토타입입니다.

```python
from dataclasses import dataclass, field

@dataclass
class SharedState:
    topic: str
    research_notes: list[str] = field(default_factory=list)
    draft: str = ""
    review_comment: str = ""

def researcher(state: SharedState) -> None:
    state.research_notes = [
        f"{state.topic}은 여러 tool call을 묶어 자동화하는 구조입니다.",
        "역할 분리가 없으면 handoff 비용만 커질 수 있습니다.",
    ]

def writer(state: SharedState) -> None:
    state.draft = " ".join(state.research_notes)

def reviewer(state: SharedState) -> None:
    if "handoff" not in state.draft:
        state.review_comment = "handoff 비용 설명이 빠졌습니다."
    else:
        state.review_comment = "Pass"

state = SharedState(topic="multi-agent 시스템")
researcher(state)
writer(state)
reviewer(state)
print(state)
```

**예상 출력:**

```text
SharedState(topic='multi-agent 시스템', research_notes=['multi-agent 시스템은 여러 tool call을 묶어 자동화하는 구조입니다.', '역할 분리가 없으면 handoff 비용만 커질 수 있습니다.'], draft='multi-agent 시스템은 여러 tool call을 묶어 자동화하는 구조입니다. 역할 분리가 없으면 handoff 비용만 커질 수 있습니다.', review_comment='Pass')
```

이 정도 스켈레톤만 있어도 각 agent가 shared state 전체를 마음대로 바꾸는지, 아니면 자신 몫의 필드만 쓰는지 바로 드러납니다. 실제 multi-agent 프레임워크를 붙이기 전에 이런 경계를 먼저 검증해 두는 편이 훨씬 안전합니다.

### Hierarchical 패턴은 큰 조직 구조를 닮습니다

부모 agent가 자식 agent에게 위임하고, 자식은 더 작은 하위 작업을 맡습니다. 규모가 큰 업무를 계층적으로 분해할 때 유용하지만, 깊이가 늘수록 context 손실과 보고 비용도 함께 커집니다. 따라서 child가 남기는 출력 계약을 매우 좁게 설계해야 합니다.

### shared state는 최소 계약만 노출하는 편이 좋습니다

- route, current_owner, worker_result 같은 핵심 필드만 공유합니다.
- 각 agent 전용 scratchpad를 전역 shared state로 노출하지 않습니다.
- handoff마다 입력과 출력 스키마를 고정합니다.
- 최종 조립 책임은 한 agent 또는 별도 finalizer에 둡니다.
- delegation 사유를 로그에 남겨 route 품질을 평가할 수 있게 합니다.

### handoff failure는 대개 프로토콜 누락에서 시작됩니다

- orchestrator가 route 이유를 남기지 않으면 왜 특정 worker에게 위임했는지 사후 분석이 어렵습니다.
- worker가 자유 형식 텍스트만 반환하면 다음 agent가 읽을 수는 있어도 검증하기 어렵습니다.
- reviewer와 writer가 같은 shared state 필드를 동시에 덮어쓰면 마지막 기록만 남아 원인 추적이 깨집니다.
- 종료 조건이 없으면 peer-to-peer 구조에서 같은 요청이 agent 사이를 왕복하기 쉽습니다.

그래서 multi-agent 설계에서는 agent 수를 늘리기 전에 `입력 스키마`, `출력 스키마`, `최대 handoff 수`, `최종 책임자` 네 가지를 먼저 고정하는 편이 좋습니다. 이 네 가지가 있어야 delegation이 설명 가능한 구조로 남습니다.

## 실전 설계 보강

### 역할 분리 기준은 모델 성능이 아니라 책임 경계입니다

멀티 에이전트 구성을 검토할 때 자주 나오는 질문은 "모델을 나누면 더 똑똑해지나"입니다. 실제로 중요한 기준은 책임 경계입니다. planner, executor, reviewer 역할이 충돌하면 단일 에이전트보다 디버깅이 어려워집니다.

| 역할 | 입력 | 출력 | 실패 모드 |
| --- | --- | --- | --- |
| Planner | goal, 정책 | 실행 계획 | 과도한 분해 |
| Executor | 단일 작업 지시 | 도구 결과 | 잘못된 도구 선택 |
| Reviewer | 계획+결과 | 승인/수정 지시 | 과도한 reject |

### 메시지 버스 스키마 예시

```json
{
  "message_id": "uuid",
  "trace_id": "uuid",
  "from": "planner",
  "to": "executor",
  "intent": "run_tool",
  "payload": {"tool": "search_docs", "args": {"q": "..."}},
  "deadline_ms": 4000,
  "retry": 0
}
```

에이전트 간 통신을 자유 텍스트로 두면 파싱 에러와 책임 전가가 반복됩니다. 구조화된 envelope를 강제해야 운영 가능성이 생깁니다.

### Supervisor 패턴의 최소 구현

```python
def supervisor(goal: str):
    plan = planner_agent(goal)
    for task in plan["tasks"]:
        result = executor_agent(task)
        verdict = reviewer_agent(task=task, result=result)
        if verdict["status"] == "retry":
            result = executor_agent({**task, "hint": verdict.get("hint")})
        if verdict["status"] == "fail":
            return {"ok": False, "reason": "review_failed", "task": task}
    return {"ok": True}
```

핵심은 supervisor가 재시도 예산과 종료 조건을 가진다는 점입니다. 각 에이전트가 스스로 무한 루프를 돌지 않도록 상위 제어기가 필요합니다.

### 멀티 에이전트 관측 지표

| 지표 | 의미 |
| --- | --- |
| cross_agent_hops | 목표당 에이전트 간 hop 수 |
| reviewer_reject_rate | reviewer 거절 비율 |
| arbitration_latency | supervisor 중재 지연 |
| dead_letter_count | 처리 실패 메시지 수 |

멀티 에이전트는 분업 이점이 있지만 통신 비용과 동기화 비용이 큽니다. 지표 없이 운영하면 단일 에이전트보다 느리고 비싼 시스템이 됩니다.

## 심화 운영 노트

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

### 관측성 이벤트 예시

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

구조화 로그를 먼저 도입하면 추후 OpenTelemetry, ELK, Grafana 같은 스택으로 확장할 때 마이그레이션 비용이 낮아집니다.

### 배포 체크 항목

- 모델 API 키를 환경 변수와 Secret Manager로 분리했는지 확인합니다.
- `max_steps`, `timeout_ms`, `retry_budget` 기본값이 운영 프로필에 맞는지 검증합니다.
- 장애 시 fallback 응답 문구가 사용자에게 과장된 확신을 주지 않는지 점검합니다.
- 알람 임계치(`error_rate`, `p95_latency`, `policy_violation_rate`)를 문서와 코드에서 동일하게 유지합니다.

이 항목은 기능 개발보다 눈에 덜 띄지만, 실제 장애 빈도를 줄이는 데 직접적으로 기여합니다.

### 비용 통제 포인트

| 항목 | 설명 | 권장 기본값 |
| --- | --- | --- |
| max_steps | 1회 실행당 최대 루프 | 4~8 |
| max_tool_calls | 도구 호출 상한 | 3~6 |
| input_token_budget | 입력 토큰 예산 | 서비스별 정책 |
| output_token_budget | 출력 토큰 예산 | 서비스별 정책 |

비용 통제는 성능 최적화 이후에 붙이는 부가기능이 아닙니다. 처음부터 실행 예산을 고정해야 사용량 급증 시 서비스가 안정적으로 유지됩니다.

### 품질 회귀를 막는 CI 게이트 예시

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core_ko.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

배포 파이프라인에서 최소 품질 게이트를 자동화하면 "우연히 좋아 보이는 빌드"가 운영으로 유입되는 일을 줄일 수 있습니다.

### 운영 관점 실패 분류 템플릿

실전에서는 실패를 "모델이 틀렸다" 한 문장으로 닫지 않습니다. 다음 템플릿처럼 실패 축을 분리하면 개선 우선순위가 명확해집니다.

| 분류 축 | 질문 | 예시 |
| --- | --- | --- |
| 계획 실패 | 목표를 잘못 분해했는가 | 불필요한 step 6회 반복 |
| 실행 실패 | 도구 호출이 실패했는가 | timeout, 429, schema mismatch |
| 검증 실패 | 결과 확인이 부족했는가 | 잘못된 observation 채택 |
| 정책 실패 | 안전 경계를 넘었는가 | 민감 데이터 외부 전송 시도 |

이 표를 runbook에 고정해 두면 온콜 엔지니어가 같은 기준으로 사고를 분류할 수 있습니다.

### 프롬프트/도구 버전 고정 전략

변경 추적이 어려운 팀은 대부분 프롬프트와 도구 스키마를 코드 릴리스와 분리해 관리합니다. 안정적인 팀은 아래처럼 버전 필드를 요청 컨텍스트에 명시합니다.

```json
{
  "run_id": "run_2026_05_21_001",
  "model": "gpt-4.1-mini",
  "prompt_version": "agent-101-ko-v3",
  "tool_schema_version": "tools-v5",
  "policy_version": "policy-2026-05"
}
```

버전 필드만 있어도 회귀 분석 속도가 크게 빨라집니다. 특정 시점의 품질 저하가 모델 변경인지, 프롬프트 변경인지, 도구 변경인지 즉시 좁힐 수 있기 때문입니다.

### 관측성 이벤트 예시

```python
import json
from datetime import datetime

def emit_event(event_type: str, payload: dict):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "payload": payload,
    }
    print(json.dumps(record, ensure_ascii=False))

emit_event("agent.step", {"step": 2, "tool": "search_docs", "latency_ms": 412})
```

구조화 로그를 먼저 도입하면 추후 OpenTelemetry, ELK, Grafana 같은 스택으로 확장할 때 마이그레이션 비용이 낮아집니다.

## 흔히 헷갈리는 지점

- agent를 여러 개 두면 자동으로 품질이 올라갈 것이라 기대하기 쉽지만, 실제로는 역할 경계가 먼저 필요합니다.
- orchestrator가 모든 세부 작업까지 하도록 만들면 결국 single-agent와 다를 바가 없어집니다.
- shared state를 넓게 열어 두면 유연할 것 같지만, 곧 결합도와 디버깅 난이도가 폭증합니다.
- peer-to-peer는 자유로워 보여도 종료 규칙이 없으면 무한 handoff가 생기기 쉽습니다.
- multi-agent는 전문성이 높아 보이지만, 실제로는 single-agent + better tools로 충분한 문제도 많습니다.

## 운영 체크리스트

- [ ] multi-agent가 정말 필요한지 single-agent 대안과 비교했는가
- [ ] 누가 route를 결정하고 누가 최종 답을 책임지는지 명시했는가
- [ ] handoff 입력/출력 스키마와 종료 조건이 정의되어 있는가
- [ ] shared state를 최소 필드로 제한했는가
- [ ] agent별 latency, route accuracy, handoff count를 측정하는가

## 정리

multi-agent 시스템은 여러 모델을 멋지게 묶는 기술이 아닙니다. 역할을 분리하고, 위임 경계를 명확히 하고, 최종 책임 위치를 고정해서 더 설명 가능한 자동화 구조를 만드는 방법입니다. 그래서 핵심은 agent 수보다 프로토콜 품질에 있습니다.

좋은 multi-agent 설계는 각 agent를 더 작게 만들고, shared state를 더 좁게 만들며, 최종 조립 지점을 더 선명하게 만듭니다. 반대로 나쁜 설계는 agent를 늘릴수록 누가 무엇을 했는지 알기 어려워집니다.

다음 글에서는 이런 시스템을 어떻게 평가할지 다룹니다. route가 적절했는지, trajectory가 효율적이었는지, 최종 성공률이 유지되는지를 측정하지 않으면 multi-agent의 비용을 정당화할 수 없기 때문입니다.

## 처음 질문으로 돌아가기

- **single agent로 충분한 업무와 multi-agent가 필요한 업무는 어디서 갈라질까요?**
  - 도메인, 도구, 검증 기준, 작업 소유자가 뚜렷하게 달라 한 agent의 prompt와 state에 모두 담기 어려울 때 multi-agent를 고려합니다.
- **supervisor, worker, handoff 계약은 각각 어떤 책임을 가져야 할까요?**
  - supervisor는 라우팅과 종료 판단, worker는 맡은 작업 실행, handoff 계약은 넘길 입력과 결과 형식을 책임져야 합니다.
- **agent를 여러 개로 나눌수록 비용과 실패 지점은 어떻게 늘어날까요?**
  - agent가 늘면 LLM 호출, handoff 누락, state 불일치, supervisor 병목이 함께 늘어납니다. 역할 분리가 비용 증가보다 큰 이득을 줄 때만 나눕니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent 101 (1/10): AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
- [AI Agent 101 (3/10): Tool Use 기초](./03-tool-use-fundamentals.md)
- [AI Agent 101 (4/10): Agent Workflow 설계](./04-agent-workflow-design.md)
- [AI Agent 101 (5/10): Memory와 State](./05-memory-and-state.md)
- **AI Agent 101 (6/10): Multi-Agent 시스템 (현재 글)**
- AI Agent 101 (7/10): Agent 평가 (예정)
- AI Agent 101 (8/10): 에러 처리와 안정성 (예정)
- AI Agent 101 (9/10): 운영 (예정)
- AI Agent 101 (10/10): 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph - Multi-agent workflows](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [OpenAI Platform - Agents guide](https://platform.openai.com/docs/guides/agents)
- [CrewAI Documentation](https://docs.crewai.com/)

### 관련 시리즈

- [LangGraph 101 - 멀티 에이전트 시스템](../../langgraph-101/ko/05-multi-agent.md)
- [AI Evaluation 101 - 시스템 평가 관점](../../ai-evaluation-101/ko/01-why-evaluate-llm-apps.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-agent-101/ko/06-multi-agent-systems)

Tags: AI Agent, LLM, Tool Use, Python
