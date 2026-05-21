---
title: "AI Agent 101 (10/10): 첫 Agent 만들기"
series: ai-agent-101
episode: 10
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Tutorial
- Python
- Hands-on
last_reviewed: '2026-05-12'
seo_description: 작은 research assistant agent를 직접 구현하며 핵심 구조를 연결합니다.
---

# AI Agent 101 (10/10): 첫 Agent 만들기

이제까지 이 시리즈에서는 agent를 이루는 부품을 하나씩 떼어 보았습니다. agent의 정의, 컨텍스트, tool use, workflow, memory, evaluation, operations를 각각 따로 설명했지만, 실제 개발에서는 이 요소들이 한 파일 안에서 동시에 만납니다.

그래서 마지막 글에서는 작은 research assistant agent를 끝까지 묶어 봅니다. 중요한 목표는 기능을 많이 넣는 것이 아니라, 지금까지 다룬 설계 원칙이 실제 코드에서 어떻게 연결되는지 확인하는 것입니다. 작은 예제라도 구조가 분명하면 이후 LangGraph나 CrewAI 같은 프레임워크로 확장하기 쉽습니다.

또한 첫 구현은 학습용이면서 동시에 기준선 역할을 합니다. 어떤 부분이 직접 코드로 충분하고, 어느 시점부터 framework가 유용한지 판단하는 데도 도움이 됩니다. 즉, 이 글은 단순한 튜토리얼이 아니라 아키텍처 감각을 정리하는 마무리 단계입니다.

이 글은 AI Agent 101 시리즈의 마지막 글입니다.

이 글에서는 작은 agent를 직접 구현하면서 개념을 코드 감각으로 바꾸는 데 집중하겠습니다.

## 먼저 던지는 질문

- 첫 agent를 만들 때 연구 도우미가 맡을 범위와 맡지 않을 범위는 어디서 정해야 할까요?
- tool, memory, agent loop, eval은 어떤 순서로 붙여야 실패가 작게 보일까요?
- raw code, LangGraph, CrewAI 중 무엇을 고를지는 어떤 기준으로 판단해야 할까요?

## 큰 그림

![end-to-end 구현 지도](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/10/10-01-end-to-end-build-map.ko.png)

*end-to-end 구현 지도*

이 그림에서는 연구 도우미 agent가 질문 분석, 검색, 계산, 종합, 대화 이력 저장을 거쳐 하나의 end-to-end 실행 흐름을 만드는 과정을 봅니다. 첫 agent의 목표는 기능을 많이 붙이는 것이 아니라 앞선 설계 원칙을 작고 검증 가능한 루프로 묶는 일입니다.

> 첫 agent는 데모가 아니라 경계, tool, memory, eval을 한 번에 검증하는 작은 운영 골격이어야 합니다.

## 왜 이 글이 중요한가

개념을 이해했다고 해서 곧 구현 감각이 생기지는 않습니다. 실제로는 tool schema를 어디에 두는지, memory를 어떤 형식으로 저장하는지, tool result를 어떻게 다시 모델로 넣는지 같은 세부 구조에서 감각 차이가 크게 납니다. 마지막으로 한 번 직접 묶어 보는 이유가 여기에 있습니다.

또한 첫 구현은 과한 프레임워크 추상화에 가려 본질을 놓치지 않게 해 줍니다. 직접 loop를 돌려 보면 agent가 결국 메시지 배열, tool registry, validation, stop condition 위에 세워진다는 사실이 선명해집니다. 그 다음에 framework를 봐야 추상화가 왜 필요한지 제대로 이해할 수 있습니다.

현업에서도 작은 기준 구현은 중요합니다. 나중에 LangGraph나 multi-agent 구조로 커지더라도, 가장 작은 end-to-end 경로가 있어야 regression test와 architecture review의 기준점이 생깁니다.

## 핵심 관점

이 글의 목표는 가장 화려한 agent를 만드는 것이 아닙니다. 오히려 작지만 읽기 쉬운 구조로 agent의 핵심 계층을 한 번에 연결하는 것이 중요합니다. tool 정의, memory, loop, error handling이 각각 어디에 들어가는지 보이게 만들어야 합니다.

이 관점이 있으면 구현 순서도 자연스럽습니다. 먼저 책임이 작은 tool을 만들고, 그 tool을 노출할 schema와 registry를 정의하고, 현재 대화를 담을 memory를 만들고, 마지막으로 LLM-tool loop를 연결합니다. 이렇게 쌓아야 디버깅도 쉽습니다.

실무에서는 프레임워크보다 먼저 이 구조를 이해하는 팀이 훨씬 빨리 안정화합니다. framework가 숨겨 주는 부분을 알아야 문제가 생겼을 때 벗겨 볼 수 있기 때문입니다.

> 첫 agent 구현의 핵심은 많은 기능이 아니라, tool·memory·loop·검증이 어떤 경계로 연결되는지 코드에서 선명하게 드러내는 것입니다.

## 핵심 개념

### 먼저 작은 도구 집합을 정의합니다

```python
from typing import Any
from pydantic import BaseModel, Field
import json

class SearchInput(BaseModel):
    """Input schema for the search tool."""
    query: str = Field(..., description="Search query")
    top_k: int = Field(3, description="Number of results to return")

class CalculatorInput(BaseModel):
    """Input schema for the calculator tool."""
    expression: str = Field(..., description="Python arithmetic expression")

def tool_search(query: str, top_k: int = 3) -> list[dict[str, str]]:
    """Fake search tool. In production this would call an external API."""
    fake_db = [
        {"title": "FastAPI Official Docs", "snippet": "FastAPI is a modern, fast Python web framework."},
        {"title": "FastAPI Performance Benchmarks", "snippet": "FastAPI delivers performance comparable to Node.js and Go."},
        {"title": "FastAPI vs Flask", "snippet": "FastAPI beats Flask in async support and automatic documentation."},
    ]
    return fake_db[:top_k]

def tool_calculator(expression: str) -> float:
    """Safe arithmetic. Plain eval is dangerous, so we use a restricted environment."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        raise ValueError(f"Disallowed characters in expression: {expression}")
    return eval(expression, {"__builtins__": {}}, {})
```

첫 구현에서 tool은 적을수록 좋습니다. 검색과 계산처럼 역할이 분명한 두 개 정도면 충분합니다. 중요한 것은 tool 자체보다 입력 스키마와 실패 조건을 함께 설계하는 습관입니다.

### tool registry는 모델과 코드 사이의 계약입니다

```python
TOOLS = {
    "search": {
        "function": tool_search,
        "schema": SearchInput,
        "description": "Search for material by keyword.",
    },
    "calculator": {
        "function": tool_calculator,
        "schema": CalculatorInput,
        "description": "Evaluate an arithmetic expression.",
    },
}

def tools_to_openai_format() -> list[dict[str, Any]]:
    """Convert the registry to OpenAI Function Calling format."""
    result = []
    for name, info in TOOLS.items():
        result.append({
            "type": "function",
            "function": {
                "name": name,
                "description": info["description"],
                "parameters": info["schema"].model_json_schema(),
            },
        })
    return result
```

registry를 분리해 두면 나중에 tool을 추가하거나 교체할 때 영향 범위를 줄일 수 있습니다. 또한 evaluation에서 어떤 tool이 등록되어 있었는지 버전 기준을 맞추기 쉽습니다.

### memory는 단순하게 시작하되 길이 제한을 둡니다

```python
class ConversationMemory:
    """Sliding window conversation memory."""

    def __init__(self, system_prompt: str, max_messages: int = 20):
        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.messages: list[dict[str, Any]] = []

    def add(self, role: str, content: str, **extra: Any) -> None:
        """Append a message."""
        msg = {"role": role, "content": content, **extra}
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def to_openai(self) -> list[dict[str, Any]]:
        """Return messages in OpenAI Chat Completions format."""
        return [{"role": "system", "content": self.system_prompt}] + self.messages
```

첫 구현에서는 long-term memory보다 short-term memory를 안정적으로 만드는 것이 먼저입니다. history가 끝없이 커지지 않도록 상한을 두고, 메시지 형식을 LLM API가 바로 소비할 수 있게 맞추는 편이 좋습니다.

### agent loop가 모든 개념을 연결합니다

```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a research assistant.
Use the search and calculator tools to answer user questions.
Synthesize tool results into accurate, concise answers.
Say you do not know when you do not."""

class ResearchAgent:
    """Research assistant agent."""

    def __init__(self, model: str = "gpt-4o-mini", max_iterations: int = 5):
        self.model = model
        self.max_iterations = max_iterations
        self.memory = ConversationMemory(SYSTEM_PROMPT)

    def run(self, user_input: str) -> str:
        """Process a user question and return an answer."""
        self.memory.add("user", user_input)

        for iteration in range(self.max_iterations):
            response = client.chat.completions.create(
                model=self.model,
                messages=self.memory.to_openai(),
                tools=tools_to_openai_format(),
                tool_choice="auto",
            )
            msg = response.choices[0].message

            if not msg.tool_calls:
                self.memory.add("assistant", msg.content or "")
                return msg.content or ""

            self.memory.add(
                "assistant",
                msg.content or "",
                tool_calls=[tc.model_dump() for tc in msg.tool_calls],
            )

            for tool_call in msg.tool_calls:
                result = self._execute_tool(tool_call)
                self.memory.add(
                    "tool",
                    json.dumps(result, ensure_ascii=False),
                    tool_call_id=tool_call.id,
                )

        return "Max iterations reached without producing an answer."

    def _execute_tool(self, tool_call: Any) -> Any:
        """Execute a tool safely."""
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
            tool = TOOLS.get(name)
            if not tool:
                return {"error": f"Unknown tool: {name}"}
            validated = tool["schema"](**args)
            result = tool["function"](**validated.model_dump())
            return {"result": result}
        except Exception as exc:
            return {"error": str(exc)}
```

이 루프 안에 지금까지의 개념이 거의 모두 들어 있습니다. context는 `SYSTEM_PROMPT`와 memory에, tool use는 registry와 `_execute_tool`에, reliability는 validation과 max_iterations에, 운영 포인트는 iteration 수와 에러 반환 형태에 들어 있습니다.

### 작은 테스트와 운영 습관까지 같이 시작합니다

첫 구현이라도 아래 항목은 같이 확인하는 편이 좋습니다.

- 정상 질문, 계산 질문, tool error 질문을 각각 한 번씩 돌려 봅니다.
- tool result가 memory에 어떤 형태로 저장되는지 확인합니다.
- iteration이 과하게 늘어나는 요청을 일부러 넣어 봅니다.
- unknown tool과 bad argument가 사용자에게 어떻게 보이는지 봅니다.
- request당 token과 latency를 대략이라도 기록합니다.

## 실전 설계 보강

### 첫 배포에서도 최소 운영 장치는 포함해야 합니다

데모 단계에서 자주 빠지는 항목은 인증, 요청 제한, 구조화 로그입니다. 첫 agent라도 이 세 가지를 넣어 두면 이후 확장이 훨씬 수월합니다.

### 엔드투엔드 예시: 계획-도구-검증

```python
from dataclasses import dataclass

@dataclass
class RunConfig:
    max_steps: int = 5
    max_retries: int = 2

def build_first_agent(goal: str, config: RunConfig):
    state = {"goal": goal, "step": 0, "history": []}
    while state["step"] < config.max_steps:
        state["step"] += 1
        plan = planner(goal=state["goal"], history=state["history"])
        if plan["type"] == "final":
            return {"status": "done", "answer": plan["answer"], "state": state}
        tool_out = safe_tool_call(plan["tool"], plan.get("args", {}))
        state["history"].append({"plan": plan, "tool_out": tool_out})
        if not tool_out.get("ok") and not tool_out.get("retryable"):
            return {"status": "failed", "reason": tool_out.get("error_type"), "state": state}
    return {"status": "failed", "reason": "max_steps_exceeded", "state": state}
```

이 코드는 화려하지 않지만 운영 핵심을 담고 있습니다. step 예산, 실패 분류, 상태 기록이 명시되어 있어야 첫 배포 후 개선 루프를 만들 수 있습니다.

### system prompt 초안

```text
당신은 내부 운영 assistant agent입니다.
목표를 달성하기 위해 필요한 경우에만 도구를 호출합니다.
- 추측으로 도구 입력을 만들지 않습니다.
- 실패 시 원인 분류(timeout, unknown_tool, validation_error)를 반환합니다.
- 최종 응답은 한국어 5문장 이내로 작성합니다.
```

### Docker 기반 로컬 실행 구성

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AGENT_MAX_STEPS=5
```

초기 단계부터 환경 변수 기반 설정을 사용하면 개발/스테이징/운영 환경 전환이 단순해집니다.

### 첫 agent 품질 게이트

| 게이트 | 통과 기준 |
| --- | --- |
| 기능 | 핵심 시나리오 10개 중 8개 이상 성공 |
| 안정성 | 무한 루프 0건, timeout 2% 이하 |
| 비용 | 요청당 평균 토큰 예산 준수 |
| 안전성 | 정책 위반 응답 0건 |

첫 프로젝트에서 이 게이트를 잡아 두면 이후 멀티 에이전트 확장 때도 품질 기준이 흔들리지 않습니다.

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

## 흔히 헷갈리는 지점

- 첫 agent부터 framework를 반드시 써야 한다고 생각하기 쉽지만, 작은 기준 구현은 raw code가 더 교육적입니다.
- tool이 많을수록 agent가 좋아질 것 같지만, 초반에는 오히려 라우팅 난이도만 올라갑니다.
- memory를 길게 유지하면 더 똑똑해질 것 같지만, 작은 구현에서는 상한을 두는 편이 안전합니다.
- error handling은 나중에 붙여도 된다고 보기 쉽지만, unknown tool과 invalid args 처리는 첫날부터 필요합니다.
- 데모가 한 번 잘 되면 구현이 끝났다고 생각하기 쉽지만, 반복 수 제한과 기본 테스트가 없으면 쉽게 무너집니다.

## 운영 체크리스트

- [ ] tool schema와 registry가 분리되어 있는가
- [ ] memory 길이 제한과 max iteration 제한이 있는가
- [ ] tool 실행 전에 입력 검증을 수행하는가
- [ ] unknown tool과 execution error를 구조화된 형태로 반환하는가
- [ ] 최소한의 정상/실패 테스트와 비용 기록 경로가 있는가

## 정리

첫 agent 만들기의 핵심은 많은 기능을 한 번에 넣는 것이 아닙니다. 작은 구조 안에서 tool, memory, loop, reliability를 어떻게 연결하는지 눈으로 확인하는 데 있습니다. 이 감각이 있어야 이후의 프레임워크와 고급 패턴이 제대로 보입니다.

좋은 기준 구현은 작지만 설명 가능합니다. 어떤 도구가 있고, 어떤 입력을 받고, 어떻게 validation하고, 언제 멈추고, 실패하면 어떤 형태로 돌아오는지 한 번에 읽혀야 합니다. 이 선명함이 나중 확장의 기반이 됩니다.

이 시리즈는 여기서 마무리되지만 실제 작업은 여기서 시작됩니다. 다음 단계에서는 이 작은 agent를 LangGraph 같은 workflow 프레임워크로 옮겨 보거나, 더 정교한 evaluation과 observability를 붙이며 production-grade 구조로 확장해 보면 좋습니다.

## 처음 질문으로 돌아가기

- **첫 agent를 만들 때 연구 도우미가 맡을 범위와 맡지 않을 범위는 어디서 정해야 할까요?**
  - 사용자 질문을 분석하고 필요한 검색·계산·종합을 수행하는 범위까지만 맡기고, 권한이 큰 외부 변경이나 검증되지 않은 자동 실행은 제외해야 합니다.
- **tool, memory, agent loop, eval은 어떤 순서로 붙여야 실패가 작게 보일까요?**
  - tool 계약을 먼저 만들고, memory/state를 붙인 뒤, loop를 연결하고, 마지막에 eval로 각 경계를 검증하는 순서가 실패를 작게 나눕니다.
- **raw code, LangGraph, CrewAI 중 무엇을 고를지는 어떤 기준으로 판단해야 할까요?**
  - raw code는 학습과 작은 제어에, LangGraph는 명시적 상태·분기·checkpoint에, CrewAI는 역할 분리된 multi-agent 협업에 맞습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent 101 (1/10): AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
- [AI Agent 101 (3/10): Tool Use 기초](./03-tool-use-fundamentals.md)
- [AI Agent 101 (4/10): Agent Workflow 설계](./04-agent-workflow-design.md)
- [AI Agent 101 (5/10): Memory와 State](./05-memory-and-state.md)
- [AI Agent 101 (6/10): Multi-Agent 시스템](./06-multi-agent-systems.md)
- [AI Agent 101 (7/10): Agent 평가](./07-agent-evaluation.md)
- [AI Agent 101 (8/10): 에러 처리와 안정성](./08-error-handling-reliability.md)
- [AI Agent 101 (9/10): 운영](./09-production-operations.md)
- **AI Agent 101 (10/10): 첫 Agent 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [OpenAI Platform - Function calling guide](https://platform.openai.com/docs/guides/function-calling)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI documentation](https://docs.crewai.com/)

### 관련 시리즈

- [LangGraph 101](../../langgraph-101/ko/01-graph-basics.md)
- [AI Evaluation 101](../../ai-evaluation-101/ko/01-why-evaluate-llm-apps.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-agent-101/ko/10-building-first-agent)

Tags: AI Agent, LLM, Tool Use, Python
