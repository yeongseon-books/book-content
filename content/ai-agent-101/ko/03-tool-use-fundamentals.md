---
title: Tool Use 기초
series: ai-agent-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Agent
- Tool Use
- Function Calling
- Integration
last_reviewed: '2026-05-12'
seo_description: function calling 흐름과 tool schema 설계의 핵심을 설명합니다.
---

# Tool Use 기초

agent를 agent답게 만드는 첫 번째 차이는 외부 세계와 상호작용할 수 있다는 점입니다. 검색 API를 부르고, 데이터베이스를 조회하고, 파일을 읽고, 계산 함수를 실행하는 순간 LLM은 설명자가 아니라 실행 오케스트레이터에 가까워집니다.

하지만 tool use는 겉보기보다 까다롭습니다. 모델이 도구를 호출한다고 해서 시스템이 자동으로 안전해지는 것은 아닙니다. 도구 이름이 모호하면 잘못된 함수를 선택하고, 입력 스키마가 약하면 형식 오류가 나고, 결과를 다시 모델에 넣는 방식이 어색하면 불필요한 루프가 길어집니다.

그래서 function calling은 단지 API 옵션 하나가 아니라 설계 패턴으로 봐야 합니다. 모델이 무엇을 결정하고, 애플리케이션 코드가 무엇을 책임지며, 실패를 어디서 차단할지를 분리해야 합니다.

이 글은 AI Agent 101 시리즈의 세 번째 글입니다.

이 글에서는 function calling을 "모델의 마법"이 아니라 "모델과 애플리케이션 사이의 계약"으로 이해하겠습니다.

## 이 글에서 다룰 문제

- function calling의 4단계 흐름은 실제 코드에서 어떻게 연결될까요?
- tool schema가 약하면 어떤 종류의 실패가 반복될까요?
- 여러 도구가 있을 때 모델은 어떤 단서를 보고 하나를 고를까요?
- tool 결과를 다시 모델에 넣을 때 무엇을 반드시 보존해야 할까요?
- tool use가 붙은 agent에서 애플리케이션 코드가 끝까지 책임져야 하는 부분은 어디일까요?

## 왜 이 글이 중요한가

tool use는 agent 시스템이 현실 세계와 닿는 첫 번째 인터페이스입니다. 이 경계가 약하면 모델이 아무리 좋아도 실제 업무 자동화는 불안정합니다. 반대로 이 경계를 잘 설계하면 비교적 단순한 모델로도 강한 자동화 루프를 만들 수 있습니다.

운영에서도 중요합니다. function calling 오류는 흔히 LLM 문제처럼 보이지만, 실제로는 schema 설계, 파라미터 검증, tool registry, 결과 직렬화 문제인 경우가 많습니다. 즉, 이 주제를 이해하면 agent 실패를 더 빨리 시스템 문제로 환원할 수 있습니다.

또한 이후의 reliability, evaluation, operations 주제도 여기서 시작합니다. 잘못된 tool 선택률, invalid arguments 비율, per-tool latency, fallback path 같은 지표는 모두 tool use 계층이 있어야 측정할 수 있습니다.

## Tool Use를 이해하는 가장 좋은 방법: 모델의 판단과 코드의 실행을 분리된 계약으로 보는 것입니다

function calling은 모델이 직접 API를 호출하는 기능이 아닙니다. 모델은 어떤 도구를 어떤 인자로 호출해야 할지 제안하고, 실제 호출은 애플리케이션 코드가 수행합니다. 이 분리를 명확히 이해해야 책임 경계가 보입니다.

이 구조가 좋은 이유는 두 가지입니다. 첫째, 모델은 "무엇을 할지"를 결정하고 코드는 "어떻게 할지"를 실행하므로 관심사가 분리됩니다. 둘째, 애플리케이션이 validation, authorization, retry, timeout을 통제할 수 있어 안전장치를 붙이기 쉽습니다.

실무에서 agent를 안정화할 때도 결국 이 경계를 다듬게 됩니다. 도구 등록 형식, 파라미터 타입, 에러 표현, 결과 요약 방식이 모두 이 계약 안에 들어 있기 때문입니다.

> 좋은 tool use 설계는 모델에게 더 많은 자유를 주는 것이 아니라, 모델의 선택을 코드가 안전하게 실행할 수 있는 형태로 제한하는 것입니다.

## 핵심 개념

### function calling의 기본 흐름은 네 단계입니다

```python
import openai

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Retrieves current weather for a specific location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., Seoul, New York)"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools,
    tool_choice="auto"  # LLM decides whether to use tools
)
```

첫 단계는 도구 정의를 모델에 보여 주는 것입니다. 이때 이름, 설명, 파라미터 스키마가 곧 모델이 보는 전체 인터페이스입니다. 설명이 약하면 라우팅이 흔들리고, 타입이 약하면 인자 품질이 흔들립니다.

```python
# Example response from LLM
{
    "role": "assistant",
    "content": null,
    "tool_calls": [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "Seoul"}'
            }
        }
    ]
}
```

두 번째 단계에서 모델은 tool call을 제안합니다. 여기서 중요한 점은 아직 아무 도구도 실제로 실행되지 않았다는 사실입니다. 모델은 실행을 요청했을 뿐이고, 시스템은 이제부터 검증과 실행 책임을 집니다.

```python
import json

def execute_tool(tool_name: str, arguments: str) -> str:
    """Execute the requested tool and return results."""
    params = json.loads(arguments)

    if tool_name == "get_weather":
        # Call actual weather API
        weather_data = get_weather_api(params["location"])
        return json.dumps(weather_data)

    return json.dumps({"error": "Unknown tool"})

# Execute tool
tool_call = response.choices[0].message.tool_calls[0]
result = execute_tool(tool_call.function.name, tool_call.function.arguments)
```

세 번째 단계는 애플리케이션이 도구를 실행하는 구간입니다. 여기서는 파싱, validation, auth check, timeout, retry 같은 모든 현실 문제가 발생합니다. 그래서 production 코드에서는 이 함수가 생각보다 두꺼워지는 것이 정상입니다.

```python
# Add tool result to conversation
messages = [
    {"role": "user", "content": "What's the weather in Seoul?"},
    response.choices[0].message,  # Assistant's tool call
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result  # Tool execution result
    }
]

# Get final answer
final_response = openai.chat.completions.create(
    model="gpt-4",
    messages=messages
)

print(final_response.choices[0].message.content)
# Output: "The current weather in Seoul is sunny with a temperature of 15°C."
```

네 번째 단계는 결과를 모델에 되돌려 최종 답을 생성하는 구간입니다. 여기서 `tool_call_id` 연결이 깨지면 multi-tool turn이 흔들리고, 결과를 너무 장황하게 넣으면 context budget이 빠르게 소모됩니다.

### 반복 루프로 감싸야 비로소 agent가 됩니다

```python
from typing import Dict, Any, List
import openai
import json

def agent_with_tools(
    user_query: str,
    tools: List[Dict[str, Any]],
    max_iterations: int = 5
) -> str:
    """Agent loop with tool support."""

    messages = [{"role": "user", "content": user_query}]

    for iteration in range(max_iterations):
        # Call LLM
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Check if LLM wants to use a tool
        if not assistant_message.tool_calls:
            # No tool call = final answer ready
            return assistant_message.content

        # Add assistant's tool call to conversation
        messages.append(assistant_message)

        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments

            # Execute tool
            result = execute_tool(tool_name, tool_args)

            # Add result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    return "Max iterations reached without completion."
```

이 루프가 중요한 이유는 tool use가 한 번으로 끝나지 않는 경우가 많기 때문입니다. 검색하고, 그 결과를 바탕으로 다시 조회하고, 마지막에 요약해야 하는 작업이 흔합니다. 따라서 단일 tool call 예제만 이해하고 있으면 실제 agent의 비용, 오류, 종료 조건을 과소평가하기 쉽습니다.

### schema 품질이 tool 선택 품질을 좌우합니다

- 이름은 `tool1`보다 `search_customer_history`처럼 의도가 드러나야 합니다.
- description은 언제 이 도구를 써야 하는지까지 포함해야 합니다.
- parameters는 JSON Schema로 타입, enum, required 필드를 명확히 밝혀야 합니다.
- 잘못된 입력이 오면 어디서 차단할지 실행 계층에서 정해야 합니다.

모델은 결국 이름과 설명과 스키마를 읽고 도구를 고릅니다. 그래서 tool use 품질의 상당 부분은 프롬프트 엔지니어링보다 인터페이스 설계 문제입니다.

## 흔히 헷갈리는 지점

- 모델이 tool call을 반환하면 실제 API가 이미 호출된 것처럼 착각하기 쉽지만, 실행 책임은 애플리케이션에 있습니다.
- description 없이 이름만 좋아도 충분하다고 보기 쉽지만, 실제로는 description이 라우팅 품질에 큰 영향을 줍니다.
- 결과를 그대로 모델에 다시 넣으면 된다고 생각하기 쉽지만, 너무 큰 payload는 곧 token 비용 문제로 이어집니다.
- tool schema가 있으면 validation이 끝났다고 보기 쉽지만, 서버 측 검증과 권한 검사는 별도로 필요합니다.
- 단일 예제가 잘 동작한다고 production readiness를 착각하기 쉽지만, multi-tool loop와 failure path를 같이 봐야 합니다.

## 운영 체크리스트

- [ ] tool name, description, parameter schema가 역할 분리를 충분히 드러내는가
- [ ] 모델이 반환한 인자를 서버 측에서 다시 검증하는가
- [ ] unknown tool, invalid arguments, timeout에 대한 명시적 처리 경로가 있는가
- [ ] tool 결과를 다시 넣을 때 `tool_call_id`와 직렬화 형식을 일관되게 유지하는가
- [ ] 최대 반복 횟수와 per-tool latency를 측정할 수 있는가

## 정리

tool use는 agent를 실세계 시스템과 연결하는 첫 번째 계층입니다. 이 계층을 이해하면 LLM이 실제로 하는 일과 애플리케이션 코드가 끝까지 책임져야 하는 일을 분리해서 볼 수 있습니다. 이 분리가 있어야 안정성이 생깁니다.

좋은 function calling 설계는 복잡한 프롬프트보다 좋은 인터페이스에서 나옵니다. 이름이 명확하고, 설명이 구체적이며, 파라미터 타입이 엄격하고, 실행 계층이 검증과 실패 처리를 책임질 때 모델의 판단 품질도 함께 올라갑니다.

다음 글에서는 이 tool use를 더 큰 작업 흐름 안에 넣는 방법을 다룹니다. 결국 agent는 도구 하나를 부르는 시스템이 아니라, 여러 단계를 어떤 순서와 조건으로 엮을지 설계하는 시스템이기 때문입니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [컨텍스트 엔지니어링](./02-context-engineering.md)
- **Tool Use 기초 (현재 글)**
- Agent Workflow 설계 (예정)
- Memory와 State (예정)
- Multi-Agent 시스템 (예정)
- Agent 평가 (예정)
- 에러 처리와 안정성 (예정)
- 운영 (예정)
- 첫 Agent 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [OpenAI Platform - Function calling guide](https://platform.openai.com/docs/guides/function-calling)
- [JSON Schema](https://json-schema.org/)
- [Anthropic - Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [LangChain - Tool calling](https://python.langchain.com/docs/concepts/tools/)

### 관련 시리즈

- [LangGraph 101 - Tool Calling](../../langgraph-101/ko/04-tool-calling-agent.md)
- [Prompt Engineering 101 - 구조화 출력](../../multimodal-ai-101/ko/05-multimodal-rag.md)

Tags: AI Agent, LLM, Tool Use, Python
