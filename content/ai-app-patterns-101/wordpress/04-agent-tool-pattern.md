---
title: "바이브코딩을 위한 AI 앱 패턴 (4/6): 에이전트 도구 패턴"
series: ai-app-patterns-101
episode: 4
language: ko
tags:
- Agent Tool Pattern
- Tool Registry
- ReAct Loop
- 바이브코딩
- Vibe Coding
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 앱 패턴 (4/6): 에이전트 도구 패턴

이 글은 **바이브코딩을 위한 AI 앱 패턴** 시리즈의 네 번째 글입니다.

---

바이브코딩으로 AI 앱을 만들다 보면 "LLM이 필요에 따라 다른 API를 알아서 호출하게 하고 싶다"는 요구가 생깁니다. 단순한 체인(Chain)은 정해진 순서대로 실행하지만, 에이전트 도구 패턴은 LLM이 상황에 따라 어떤 도구를 언제 사용할지 스스로 결정합니다.

에이전트 도구 패턴의 핵심은 **도구 레지스트리**와 **ReAct 루프**입니다. 도구 레지스트리는 사용 가능한 모든 도구를 등록하고 관리하며, ReAct 루프는 LLM이 도구를 선택하고 실행하고 결과를 관찰하는 사이클을 반복합니다.

> "체인은 '항상 이 순서대로'이고, 에이전트는 '필요에 따라 선택'입니다. 유연성이 필요할 때 에이전트 도구 패턴을 씁니다."

## 이 글에서 다룰 질문

1. 에이전트와 단순 체인은 어떻게 다른가요?
2. 도구 레지스트리를 데코레이터로 구현하는 방법은?
3. ReAct 루프에서 도구 오류를 어떻게 처리하나요?
4. 도구 호출 기록(AgentRunRecord)은 왜 필요한가요?
5. 역할 기반 도구 정책은 어떻게 구현하나요?

---

## 에이전트 vs 체인 비교

| 구분 | 체인 | 에이전트 |
|------|------|----------|
| 실행 방식 | 고정된 순서대로 | LLM이 동적으로 결정 |
| 유연성 | 낮음 | 높음 |
| 예측 가능성 | 높음 | 낮음 |
| 적합한 상황 | 정해진 프로세스 | 상황에 따라 다른 도구 필요 |
| 디버깅 | 쉬움 | 어려움 (도구 선택 추적 필요) |

## 데코레이터로 도구 레지스트리 구현

```python
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class Tool:
    name: str
    description: str
    function: Callable
    when_to_use: str = ""

class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, when_to_use: str = ""):
        """데코레이터로 도구를 등록합니다."""
        def decorator(fn: Callable) -> Callable:
            self.tools[name] = Tool(
                name=name,
                description=description,
                function=fn,
                when_to_use=when_to_use
            )
            return fn
        return decorator

    def get_schemas(self) -> list[dict]:
        """OpenAI Function Calling 형식으로 스키마를 반환합니다."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": f"{tool.description}\n사용 시점: {tool.when_to_use}",
                }
            }
            for tool in self.tools.values()
        ]

registry = ToolRegistry()

@registry.register(
    "query_sales_data",
    "판매 데이터를 조회합니다",
    when_to_use="특정 기간이나 제품의 판매 실적이 필요할 때"
)
def query_sales_data(start_date: str, end_date: str, product: str = None) -> dict:
    # 실제 DB 쿼리 로직
    return {"period": f"{start_date}~{end_date}", "total": 1500000}

@registry.register(
    "send_slack_message",
    "Slack 채널에 메시지를 보냅니다",
    when_to_use="분석 결과나 알림을 팀에 공유할 때"
)
def send_slack_message(channel: str, message: str) -> dict:
    # Slack API 호출
    return {"sent": True, "channel": channel}
```

## ReAct 루프 구현

```python
import json
from dataclasses import dataclass, field

@dataclass
class AgentRunRecord:
    run_id: str
    goal: str
    tool_calls: list[dict] = field(default_factory=list)
    final_answer: str = ""
    success: bool = False

def run_agent(goal: str, registry: ToolRegistry, max_steps: int = 10) -> AgentRunRecord:
    record = AgentRunRecord(run_id=str(uuid.uuid4()), goal=goal)
    messages = [
        {"role": "system", "content": "도구를 사용해 목표를 달성하세요. 충분한 정보를 수집했으면 최종 답변을 제공하세요."},
        {"role": "user", "content": goal}
    ]

    for step in range(max_steps):
        response = llm.chat(messages, tools=registry.get_schemas())
        message = response.choices[0].message

        if not message.tool_calls:
            record.final_answer = message.content
            record.success = True
            break

        # 도구 실행
        for tc in message.tool_calls:
            tool_name = tc.function.name
            args = json.loads(tc.function.arguments)

            result = safe_tool_call(registry, tool_name, args)
            record.tool_calls.append({
                "tool": tool_name,
                "args": args,
                "result": result,
                "step": step
            })

            messages.append({"role": "tool", "content": json.dumps(result, ensure_ascii=False)})

    return record

def safe_tool_call(registry: ToolRegistry, name: str, args: dict, retries: int = 2) -> dict:
    """도구를 안전하게 실행하고 오류를 관찰값으로 반환합니다."""
    if name not in registry.tools:
        return {"error": f"도구 '{name}'를 찾을 수 없습니다"}

    for attempt in range(retries + 1):
        try:
            return registry.tools[name].function(**args)
        except Exception as e:
            if attempt == retries:
                return {"error": str(e), "tool": name, "attempts": attempt + 1}
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 도구 설명이 너무 짧음 | LLM이 언제 써야 할지 모름 | when_to_use 명시 |
| 도구 오류를 예외로 던짐 | 에이전트가 실패 원인 모름 | 오류를 딕셔너리로 반환 |
| 실행 기록 없음 | 디버깅과 감사 불가 | AgentRunRecord로 모든 호출 기록 |
| 권한 없는 도구 호출 허용 | 보안 위험 | 역할 기반 도구 정책 |

## AI 팁

역할 기반 도구 정책으로 특정 역할만 민감한 도구를 사용할 수 있도록 제한하세요.

```python
ROLE_TOOL_POLICY = {
    "user": ["query_sales_data"],          # 일반 사용자: 조회만
    "analyst": ["query_sales_data", "calculate"],  # 분석가: 조회 + 계산
    "admin": ["query_sales_data", "calculate", "send_slack_message"]  # 관리자: 전체
}

def get_allowed_tools(role: str, registry: ToolRegistry) -> list[dict]:
    allowed_names = ROLE_TOOL_POLICY.get(role, [])
    return [
        schema for schema in registry.get_schemas()
        if schema["function"]["name"] in allowed_names
    ]
```

이 패턴으로 같은 에이전트가 다른 역할에 따라 다른 도구 셋을 사용하도록 제어할 수 있습니다.

## 체크리스트

- [ ] 도구를 레지스트리로 중앙 관리한다
- [ ] 각 도구에 when_to_use를 명시했다
- [ ] 도구 실행 오류를 딕셔너리로 반환해 에이전트에게 전달한다
- [ ] 모든 도구 호출을 AgentRunRecord로 기록한다
- [ ] 역할 기반 도구 접근 정책을 구현했다

## 처음 질문으로 돌아가기

**에이전트 vs 체인 차이는?** 체인은 고정된 순서로 실행하고, 에이전트는 LLM이 상황에 따라 도구를 동적으로 선택합니다. 유연성이 필요할 때 에이전트를 씁니다.

**데코레이터로 도구 레지스트리 구현은?** `@registry.register(name, description)` 데코레이터로 함수를 등록하면 자동으로 스키마가 생성됩니다.

**ReAct 루프에서 도구 오류 처리는?** 예외를 던지는 대신 `{"error": "...", "tool": "..."}` 딕셔너리를 반환하면 에이전트가 오류를 관찰값으로 받아 대안을 시도합니다.

**AgentRunRecord가 필요한 이유는?** 모든 도구 호출과 결과를 기록하면 에이전트가 왜 그런 결정을 내렸는지 사후 분석이 가능하고, 감사 로그로도 활용됩니다.

**역할 기반 도구 정책은?** 사용자 역할에 따라 허용된 도구만 에이전트에게 제공해 불필요한 또는 위험한 도구 호출을 방지합니다.

## 정리

에이전트 도구 패턴은 LLM이 상황에 따라 도구를 자율적으로 선택하는 구조입니다. 도구 레지스트리로 도구를 관리하고, ReAct 루프로 실행하며, 모든 호출을 기록하고, 역할 기반 정책으로 보안을 유지하는 것이 핵심입니다.

다음 글에서는 여러 AI 단계를 순서대로 연결하는 **워크플로우 자동화** 패턴을 다룹니다.

## 참고 자료

- [AI 앱 패턴 원문: 에이전트 도구 패턴](../ko/04-agent-tool-pattern.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 앱 패턴 (1/6): 챗봇 패턴](./01-chatbot-pattern.md)
2. [바이브코딩을 위한 AI 앱 패턴 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
3. [바이브코딩을 위한 AI 앱 패턴 (3/6): 문서 어시스턴트](./03-document-assistant.md)
4. **바이브코딩을 위한 AI 앱 패턴 (4/6): 에이전트 도구 패턴 (현재 글)**
5. [바이브코딩을 위한 AI 앱 패턴 (5/6): 워크플로우 자동화](./05-workflow-automation.md)
6. [바이브코딩을 위한 AI 앱 패턴 (6/6): Human-in-the-Loop](./06-human-in-the-loop.md)
<!-- toc:end -->

Tags: Agent Tool Pattern, Tool Registry, ReAct Loop, 바이브코딩, Vibe Coding
