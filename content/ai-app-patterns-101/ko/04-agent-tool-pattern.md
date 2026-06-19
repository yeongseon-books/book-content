---
series: ai-app-patterns-101
episode: 4
title: "AI App Patterns 101 (4/6): Agent Tool 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Agent
  - ReAct
  - ToolCalling
  - LLM
  - Autonomous
seo_description: ReAct 패턴, @tool 데코레이터, 도구 레지스트리, 오류 핸들링을 에이전트 관찰로 처리하는 방법까지 Agent Tool 패턴 핵심을 정리합니다
last_reviewed: '2026-06-20'
---

# AI App Patterns 101 (4/6): Agent Tool 패턴

에이전트는 LLM이 어떤 도구를 언제 호출할지 스스로 결정하고, 도구 결과를 관찰해 다음 행동을 계획하는 패턴입니다. 단순한 챗봇이나 RAG와 달리, 에이전트는 여러 단계의 추론-행동-관찰 루프를 반복하며 목표를 달성합니다. 이 패턴의 핵심은 도구를 얼마나 안전하고 예측 가능하게 설계하느냐입니다.

이 글은 AI App Patterns 101 시리즈의 4번째 글입니다.

![Agent Tool 패턴 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/04/04-01-concept-at-a-glance.ko.png)
*ReAct 루프와 도구 레지스트리가 결합된 에이전트 아키텍처*

## 이 글에서 다룰 문제

- ReAct 패턴에서 Thought, Action, Observation 각 단계의 역할은 무엇일까요?
- 도구를 안전하게 설계하려면 어떤 제약이 필요할까요?
- 도구 오류가 발생했을 때 에이전트가 복구하는 방법은 무엇일까요?
- 에이전트가 무한 루프에 빠지는 것을 어떻게 방지할 수 있을까요?
- 프로덕션 에이전트에서 반드시 로깅해야 할 정보는 무엇일까요?

## 핵심 개념 한 줄 정리

- **ReAct**: Reasoning + Acting의 약자로, LLM이 생각(Thought)하고 행동(Action)하고 결과를 관찰(Observation)하는 반복 루프입니다.
- **Tool**: 에이전트가 호출할 수 있는 함수로, 입력 스키마와 설명이 LLM에 제공됩니다.
- **Tool Registry**: 사용 가능한 도구 목록을 관리하고 이름으로 조회하는 시스템입니다.
- **Observation**: 도구 실행 결과로, 에이전트의 다음 추론에 입력됩니다.
- **Max Iterations**: 에이전트 루프의 최대 반복 횟수로, 무한 루프를 방지합니다.

## 에이전트 vs 체인 비교

| 특성 | 체인(Chain) | 에이전트(Agent) |
|---|---|---|
| 흐름 결정 | 사전 정의된 순서 | LLM이 동적으로 결정 |
| 도구 선택 | 고정 | 상황에 따라 유연하게 선택 |
| 예측 가능성 | 높음 | 낮음 |
| 적합 상황 | 반복적 작업 | 다양한 도구가 필요한 복잡한 작업 |
| 디버깅 난이도 | 낮음 | 높음 |

## 실습 1: 도구 정의와 레지스트리

도구를 함수로 정의하고, 레지스트리로 관리합니다. LLM에는 도구의 이름, 설명, 입력 스키마가 전달됩니다.

```python
import json
import inspect
from typing import Any, Callable
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    description: str
    func: Callable
    parameters: dict


class ToolRegistry:
    """에이전트가 사용할 도구를 등록하고 조회합니다."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, parameters: dict):
        """함수를 도구로 등록하는 데코레이터입니다."""
        def decorator(func: Callable):
            self._tools[name] = Tool(
                name=name,
                description=description,
                func=func,
                parameters=parameters,
            )
            return func
        return decorator

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        """OpenAI function calling 형식으로 도구 목록을 반환합니다."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]


# 도구 레지스트리 초기화
registry = ToolRegistry()


@registry.register(
    name="search_web",
    description="웹에서 최신 정보를 검색합니다.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "검색 쿼리"},
            "num_results": {"type": "integer", "description": "결과 수", "default": 3},
        },
        "required": ["query"],
    },
)
def search_web(query: str, num_results: int = 3) -> str:
    """실제 구현에서는 검색 API를 호출합니다."""
    # 예시 구현
    return f"'{query}' 검색 결과: [결과 1], [결과 2], [결과 3]"


@registry.register(
    name="calculate",
    description="수학 계산을 수행합니다. 안전한 수식만 허용합니다.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "계산할 수식 (예: 2 + 3 * 4)"},
        },
        "required": ["expression"],
    },
)
def calculate(expression: str) -> str:
    """안전한 수학 계산을 수행합니다."""
    # 안전성 검증: 숫자와 기본 연산자만 허용
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "오류: 허용되지 않은 문자가 포함되어 있습니다."
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"계산 오류: {str(e)}"
```

## 실습 2: ReAct 에이전트 루프

LLM이 도구를 선택하고, 실행하고, 결과를 관찰하며 목표를 달성하는 루프를 구현합니다.

```python
from openai import OpenAI
import json

client = OpenAI()

SYSTEM_PROMPT = """당신은 도구를 사용해 사용자의 질문에 답하는 에이전트입니다.
필요한 경우 도구를 호출하고, 결과를 바탕으로 다음 단계를 결정하세요.
충분한 정보를 얻었으면 최종 답변을 제공하세요."""


def run_agent(
    user_query: str,
    max_iterations: int = 5,
    verbose: bool = True,
) -> str:
    """ReAct 루프로 에이전트를 실행합니다."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
    tools = registry.list_tools()

    for iteration in range(max_iterations):
        if verbose:
            print(f"\n[Iteration {iteration + 1}/{max_iterations}]")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024,
        )

        message = response.choices[0].message
        messages.append(message)

        # 도구 호출이 없으면 최종 답변 반환
        if not message.tool_calls:
            if verbose:
                print(f"[Final Answer] {message.content}")
            return message.content

        # 도구 호출 실행
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if verbose:
                print(f"[Action] {tool_name}({tool_args})")

            tool = registry.get(tool_name)
            if tool:
                try:
                    observation = tool.func(**tool_args)
                except Exception as e:
                    observation = f"도구 실행 오류: {str(e)}"
            else:
                observation = f"알 수 없는 도구: {tool_name}"

            if verbose:
                print(f"[Observation] {observation}")

            # 관찰 결과를 메시지에 추가
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": observation,
            })

    return "최대 반복 횟수에 도달했습니다. 지금까지의 정보를 바탕으로 답변드립니다."


# 사용 예시
result = run_agent("3의 제곱은 얼마인지 계산하고, 파이썬이란 무엇인지 검색해 주세요.")
print(f"\n최종 결과: {result}")
```

## 실습 3: 오류를 관찰로 처리하기

도구 실행 중 오류가 발생하면 에이전트에게 오류 내용을 알려 복구를 시도하게 합니다.

```python
from openai import OpenAI
import json
import time

client = OpenAI()


def safe_tool_call(
    tool: Tool,
    args: dict,
    max_retries: int = 2,
) -> str:
    """도구 호출에 재시도와 오류 처리를 적용합니다."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            result = tool.func(**args)
            return result
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(0.5 * (attempt + 1))
            continue

    # 오류를 에이전트가 이해할 수 있는 관찰로 변환
    return (
        f"도구 '{tool.name}' 실행 실패 (시도 {max_retries + 1}회): "
        f"{type(last_error).__name__}: {str(last_error)}. "
        "다른 접근 방법을 시도하거나 사용자에게 알려주세요."
    )


def run_agent_with_error_handling(
    user_query: str,
    max_iterations: int = 5,
) -> dict:
    """오류 처리를 포함한 에이전트 실행입니다."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]
    tools = registry.list_tools()
    tool_calls_log = []

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024,
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return {
                "answer": message.content,
                "iterations": iteration + 1,
                "tool_calls": tool_calls_log,
            }

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool = registry.get(tool_name)

            if tool:
                observation = safe_tool_call(tool, tool_args)
                status = "error" if "실행 실패" in observation else "success"
            else:
                observation = f"도구 '{tool_name}'를 찾을 수 없습니다."
                status = "not_found"

            tool_calls_log.append({
                "tool": tool_name,
                "args": tool_args,
                "status": status,
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": observation,
            })

    return {
        "answer": "최대 반복 횟수 도달",
        "iterations": max_iterations,
        "tool_calls": tool_calls_log,
    }
```

## 운영 체크리스트

- [ ] 모든 도구에 입력 유효성 검사가 있습니다.
- [ ] max_iterations로 무한 루프를 방지합니다.
- [ ] 도구 호출 이력이 로깅됩니다.
- [ ] 위험한 도구(파일 삭제, 외부 전송)에 사전 승인 단계가 있습니다.
- [ ] 도구 실행 타임아웃이 설정되어 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| max_iterations 설정 없음 | 에이전트가 무한 루프에 빠짐 | 5-10회 제한 설정 |
| 도구 설명이 모호함 | 에이전트가 잘못된 도구를 선택 | 구체적 사용 사례와 제약 조건을 설명에 포함 |
| 오류를 exception으로만 처리 | 에이전트가 복구 불가 | 오류를 observation으로 반환해 재시도 유도 |
| 도구에 사이드 이펙트 미공개 | 예상치 못한 데이터 수정/삭제 | 도구 설명에 사이드 이펙트 명시 |
| 도구 인자 검증 없음 | 잘못된 인자로 외부 API 호출 | Pydantic으로 입력 스키마 검증 |

## 처음 질문으로 돌아가기

- **ReAct 패턴에서 각 단계의 역할은 무엇일까요?**
  Thought(생각) 단계에서 LLM이 상황을 분석하고 계획을 세웁니다. Action 단계에서 도구를 선택하고 호출합니다. Observation 단계에서 도구 결과를 받아 다음 Thought에 반영합니다. 이 루프가 반복되면서 목표에 점진적으로 접근합니다.

- **도구 오류가 발생했을 때 에이전트가 복구하는 방법은 무엇일까요?**
  오류를 exception으로 처리하지 말고, 에이전트가 이해할 수 있는 observation 문자열로 변환합니다. 에이전트는 오류 메시지를 보고 다른 도구를 시도하거나 사용자에게 문제를 안내할 수 있습니다.

- **에이전트가 무한 루프에 빠지는 것을 어떻게 방지할 수 있을까요?**
  max_iterations로 루프 횟수를 제한하고, 반복 횟수 초과 시 현재까지의 결과로 답변을 완성합니다. 같은 도구를 동일한 인자로 연속 호출하는 패턴을 감지해 루프를 강제 종료하는 로직도 추가할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI App Patterns 101 (1/6): Chatbot 패턴](./01-chatbot-pattern.md)
- [AI App Patterns 101 (2/6): RAG QA 패턴](./02-rag-qa-pattern.md)
- [AI App Patterns 101 (3/6): Document Assistant 패턴](./03-document-assistant.md)
- **AI App Patterns 101 (4/6): Agent Tool 패턴 (현재 글)**
- [AI App Patterns 101 (5/6): Workflow Automation 패턴](./05-workflow-automation.md)
- [AI App Patterns 101 (6/6): Human-in-the-Loop 패턴](./06-human-in-the-loop.md)

<!-- toc:end -->

## 참고 자료

- [OpenAI — Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [ReAct — Synergizing Reasoning and Acting in LLMs](https://arxiv.org/abs/2210.03629)
- [LangChain — Agents](https://python.langchain.com/docs/modules/agents/)
- [Anthropic — Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [book-examples — ai-app-patterns-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/ai-app-patterns-101/ko)

Tags: Agent, ReAct, ToolCalling, LLM, Autonomous
