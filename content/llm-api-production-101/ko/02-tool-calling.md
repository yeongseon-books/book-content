---
episode: 2
language: ko
last_reviewed: '2026-05-12'
series: llm-api-production-101
status: publish-ready
tags:
- LLM
- OpenAI
- Streaming
- Python
targets:
  ebook: true
  medium: false
  mkdocs: true
  tistory: true
title: 툴 호출 — 함수를 모델에 연결하기
seo_description: '예제 코드: github.com/yeongseon-books/llm-api-production-101'
---

# 툴 호출 — 함수를 모델에 연결하기

구조화 출력이 안정화되면 곧 다음 요구가 따라옵니다. 모델이 답변만 만들지 말고 애플리케이션 기능도 선택해 주었으면 좋겠다는 요구입니다. 주문 상태를 물으면 조회 함수를 호출하고, 환율을 물으면 내부 서비스에서 값을 가져오고, 일정 생성 요청이 오면 캘린더 API까지 이어지길 기대하게 됩니다.

이 시점에서 많은 초기 구현은 다시 문자열 관습으로 돌아갑니다. 모델이 함수 이름과 인자를 텍스트로 내놓게 한 뒤, 애플리케이션이 `if` 문이나 수동 파서로 해석합니다. 작은 예제에서는 충분해 보이지만, 함수 이름 오탈자, 누락 인자, 허용되지 않은 추가 키, 안전하지 않은 디스패치가 금방 쌓입니다.

툴 호출이 중요한 이유는 모델이 코드를 실행해서가 아닙니다. 애플리케이션이 허용한 함수 이름, 설명, 인자 스키마를 명시적으로 공개하고, 모델은 그 안에서 선택만 하기 때문입니다. 실행 권한, 검증, 부작용 통제는 여전히 애플리케이션이 갖습니다.

이번 글에서는 Groq의 `tools` 파라미터와 `tool_calls` 응답을 사용해, 모델 선택 → 인자 검증 → 함수 실행 → 결과 재주입까지 이어지는 전체 루프를 운영 관점으로 정리하겠습니다.

이 글은 LLM API Production 101 시리즈의 두 번째 글입니다.

여기서는 모델 응답을 안전한 함수 실행 경계로 연결하는 툴 호출 루프를 살펴보겠습니다.

## 이 글에서 다룰 문제

- 툴 호출은 일반 문자열 기반 함수 호출과 무엇이 다를까요?
- `tools` 정의에서 이름, 설명, 파라미터는 어떻게 써야 할까요?
- `tool_calls`를 받은 뒤 어떤 검증 순서로 실행해야 안전할까요?
- 함수 실행 결과를 다시 모델에 넣어 최종 답을 받는 루프는 어떻게 만들까요?
- 툴 호출 실패나 타임아웃이 생기면 어디서 멈추고 무엇을 로그로 남겨야 할까요?

## 왜 이 글이 중요한가

툴 호출은 LLM 애플리케이션이 외부 세계와 만나는 첫 실행 경계입니다. 구조화 출력이 “데이터를 어떻게 안전하게 받는가”의 문제였다면, 툴 호출은 “그 데이터를 바탕으로 무엇을 실행하게 할 것인가”의 문제입니다. 이 경계를 느슨하게 만들면 모델은 똑똑해 보일지 몰라도 시스템은 금방 위험해집니다.

현업에서는 조회성 도구와 상태 변경 도구가 같은 수준으로 다뤄지는 순간부터 문제가 커집니다. 주문 상태 조회와 주문 취소는 같은 툴 호출처럼 보여도 신뢰 가정이 전혀 다릅니다. 그래서 툴 호출을 기능 확장으로만 보지 말고, 권한과 검증이 걸린 실행 인터페이스로 봐야 합니다.

또한 툴 호출은 추적성의 문제이기도 합니다. 사용자가 “왜 엉뚱한 답이 나왔나요?”라고 물었을 때, 어떤 툴이 어떤 인자로 호출되었고 어떤 결과가 돌아왔는지 같은 타임라인이 있어야 설명할 수 있습니다. 이 설명 가능성이 없으면 운영 품질은 빠르게 떨어집니다.

## 툴 호출을 이해하는 가장 좋은 방법: 모델 자율성이 아니라 애플리케이션이 설계한 실행 경계로 보는 것입니다

툴 호출의 핵심은 모델이 직접 함수를 실행하는 것이 아니라, 애플리케이션이 공개한 도구 상자에서 적절한 항목을 고르는 데 있습니다. 애플리케이션은 허용 목록을 만들고, 인자 스키마를 정의하고, 실제 실행 전에 검증과 권한 확인을 수행합니다. 모델은 그 계약 안에서 어떤 도구가 필요한지 제안합니다.

이 관점으로 보면 설계 우선순위도 달라집니다. 가장 먼저 고민해야 할 것은 “모델이 얼마나 똑똑하게 고르는가”보다 “허용된 선택지가 얼마나 명확하고 안전한가”입니다. 이름이 애매하거나 설명이 부정확하면 잘못된 툴 선택이 늘어납니다. 검증이 느슨하면 잘못된 인자가 실행 경로로 흘러갑니다.

> 툴 호출은 모델에게 권한을 넘기는 기능이 아니라, 애플리케이션이 통제 가능한 형태로 실행 요청을 구조화하는 기능입니다.

## 핵심 개념

![툴 호출: 함수를 모델에 연결하기](../../../assets/llm-api-production-101/02/02-01-tool-calling-connecting-functions-to-the.ko.png)

*툴 호출: 함수를 모델에 연결하기*

### 왜 문자열 기반 디스패치는 금방 흔들리는가

![문자열 분기와 툴 계약의 차이 비교](../../../assets/llm-api-production-101/02/02-01-why-string-based-dispatch-does-not-scale.ko.png)

*문자열 분기와 툴 계약의 차이 비교*

문자열 기반 분기는 가장 먼저 시도하기 쉬운 패턴입니다. 하지만 계약이 코드와 프롬프트 사이에 숨어 버린다는 문제가 있습니다.

```python
if "shipping" in user_question:
    result = get_order_status(order_id)
elif "refund" in user_question:
    result = get_refund_policy()
```

또는 모델에게 `{"function": "get_order_status", "order_id": "ORD-1001"}` 같은 텍스트를 출력하게 만들고 직접 파싱할 수도 있습니다. 둘 다 불가능한 방식은 아니지만, 함수 집합, 인자 요구사항, 응답 구조가 명시적으로 드러나지 않기 때문에 운영 경계가 약합니다.

### `tools` 파라미터에는 무엇이 들어가는가

![툴 정의를 이루는 구성 요소 구조](../../../assets/llm-api-production-101/02/02-02-what-goes-into-the-tools-parameter.ko.png)

*툴 정의를 이루는 구성 요소 구조*

툴 정의는 이름, 설명, 인자 스키마를 담은 함수 서술자입니다. 이름은 allowlist의 일부이고, 설명은 모델의 선택 기준이며, 파라미터는 호출 계약입니다.

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up shipping status by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "An order identifier such as ORD-1001",
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    }
]
```

`additionalProperties=False` 같은 제약은 사소해 보여도 중요합니다. 허용되지 않은 키를 줄여 주고, 애플리케이션이 이해하지 못하는 인자가 실행 경로에 섞이는 일을 예방합니다.

### 첫 번째 툴 사용 요청 보내기

![첫 툴 호출 요청에서 모델이 고르는 흐름](../../../assets/llm-api-production-101/02/02-03-sending-the-first-tool-enabled-request.ko.png)

*첫 툴 호출 요청에서 모델이 고르는 흐름*

이제 모델이 실제로 툴을 고르게 만듭니다.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up shipping status by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    }
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "Use tools when order questions require a live lookup.",
        },
        {
            "role": "user",
            "content": "Please check the shipping status for order ORD-1001.",
        },
    ],
    tools=tools,
    tool_choice="auto",
    temperature=0,
)

message = completion.choices[0].message
print(message.tool_calls)
```

<!-- injected-output:start -->
**실행 결과**

    [ChatCompletionMessageToolCall(id='1jcy87msp', function=Function(arguments='{"order_id":"ORD-1001"}', name='get_order_status'), type='function')]

<!-- injected-output:end -->

`tool_choice="auto"`는 모델이 필요할 때만 도구를 고르게 합니다. 이 시점의 응답은 최종 사용자 답이 아니라 실행 요청입니다. 즉, 애플리케이션이 아직 한 번 더 일해야 한다는 뜻입니다.

### `tool_calls`를 파싱하고 안전하게 라우팅하기

실행 전에 필요한 검사는 단순합니다. 함수 이름이 허용 목록에 있는지, 인자가 기대한 형태인지 확인해야 합니다.

```python
import json
import os

from groq import Groq
from pydantic import BaseModel

class OrderStatusArgs(BaseModel):
    order_id: str

def get_order_status(order_id: str) -> dict:
    fake_db = {
        "ORD-1001": {"status": "in_transit", "eta_days": 2},
        "ORD-1002": {"status": "delivered", "eta_days": 0},
    }
    return fake_db.get(order_id, {"status": "not_found", "eta_days": None})

available_tools = {
    "get_order_status": get_order_status,
}

client = Groq(api_key=os.environ["GROQ_API_KEY"])

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up shipping status by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    }
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "Use tools for order lookup requests."},
        {"role": "user", "content": "Check ORD-1001 for me."},
    ],
    tools=tools,
    tool_choice="auto",
    temperature=0,
)

message = completion.choices[0].message

for tool_call in message.tool_calls or []:
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name not in available_tools:
        raise ValueError(f"unknown tool: {function_name}")

    validated_args = OrderStatusArgs.model_validate(arguments)
    result = available_tools[function_name](**validated_args.model_dump())
    print(function_name, arguments, result)
```

<!-- injected-output:start -->
**실행 결과**

    get_order_status {'order_id': 'ORD-1001'} {'status': 'in_transit', 'eta_days': 2}

<!-- injected-output:end -->

이 단계는 아직 최종 답이 아닙니다. 모델은 툴 사용을 요청했고, 애플리케이션은 그 요청을 실행했습니다. 이제 그 결과를 다시 대화에 넣어야 사용자 응답이 완성됩니다.

### 함수 실행 루프를 끝까지 만들기

![툴 호출 왕복 실행 루프 흐름](../../../assets/llm-api-production-101/02/02-04-building-the-full-function-execution-loo.ko.png)

*툴 호출 왕복 실행 루프 흐름*

전체 루프는 “모델이 선택한다 → 애플리케이션이 실행한다 → 모델이 설명한다”의 구조입니다.

```python
import json
import os

from groq import Groq
from pydantic import BaseModel

class OrderStatusArgs(BaseModel):
    order_id: str

def get_order_status(order_id: str) -> dict:
    fake_db = {
        "ORD-1001": {
            "status": "in_transit",
            "location": "Seoul hub",
            "eta_days": 2,
        }
    }
    return fake_db.get(order_id, {"status": "not_found"})

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up shipping status by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    }
]

available_tools = {"get_order_status": get_order_status}

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {"role": "system", "content": "Use tools for order lookups, then answer briefly."},
    {"role": "user", "content": "What is happening with order ORD-1001?"},
]

first = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    temperature=0,
)

assistant_message = first.choices[0].message
messages.append(assistant_message.model_dump())

if not assistant_message.tool_calls:
    print(assistant_message.content)
    raise SystemExit(0)

for tool_call in assistant_message.tool_calls or []:
    function_name = tool_call.function.name
    if function_name not in available_tools:
        raise ValueError(f"unknown tool: {function_name}")

    try:
        arguments = json.loads(tool_call.function.arguments)
        validated_args = OrderStatusArgs.model_validate(arguments)
    except json.JSONDecodeError as exc:
        raise ValueError("tool arguments were not valid JSON") from exc

    tool_result = available_tools[function_name](**validated_args.model_dump())

    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(tool_result, ensure_ascii=False),
        }
    )

final = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    tools=tools,
    temperature=0,
)

print(final.choices[0].message.content)
```

이 구조의 장점은 역할이 분리된다는 점입니다. 모델은 어떤 도구가 필요한지 제안하고, 애플리케이션은 실제 실행과 검증을 책임지며, 마지막 응답은 다시 모델이 자연어로 정리합니다.

### 운영에서 특히 지켜야 할 방어선

![툴 실행 전에 거치는 운영 방어 단계](../../../assets/llm-api-production-101/02/02-05-what-to-guard-in-production.ko.png)

*툴 실행 전에 거치는 운영 방어 단계*

툴 호출은 시스템을 강하게 만들 수도 있고 위험하게 만들 수도 있습니다. 핵심 방어선은 네 가지입니다. 임의 함수 이름으로 디스패치하지 않을 것, 인자를 검증 없이 실행하지 않을 것, 읽기 전용 도구와 부작용 도구를 같은 신뢰 수준으로 다루지 않을 것, 그리고 모든 툴 요청과 결과를 추적 가능하게 기록할 것입니다.

특히 `globals()`나 동적 import 같은 방식으로 함수 이름을 그대로 실행 경로에 연결하는 패턴은 피해야 합니다. 툴 호출의 장점은 명시적 allowlist에 있습니다. 그 장점을 버리면 구조화된 실행 경계를 만든 의미가 거의 사라집니다.

## 흔히 헷갈리는 지점

- 모델이 `tool_calls`를 반환한다고 해서 스스로 코드를 실행하는 것은 아닙니다.
- 설명이 모호한 툴 정의는 모델 품질 문제가 아니라 계약 설계 문제인 경우가 많습니다.
- `json.loads()` 뒤에 곧바로 `**arguments`를 넘기면 검증 계층이 빠집니다.
- 조회성 툴과 상태 변경 툴은 같은 확인 절차로 다루면 안 됩니다.
- 최종 사용자 응답은 첫 번째 모델 호출이 아니라 툴 결과를 다시 넣은 뒤에 완성되는 경우가 많습니다.

## 운영 체크리스트

- [ ] 각 툴의 이름과 설명이 사용 시점을 명확히 드러내도록 작성했다
- [ ] 파라미터 스키마에 타입, 필수 여부, 추가 키 금지를 반영했다
- [ ] 함수 이름 allowlist와 인자 검증을 실행 전에 통과시켰다
- [ ] `role: tool` 메시지로 결과를 다시 모델에 주입하는 루프를 구현했다
- [ ] 최대 호출 수와 오류 표준화로 무한 반복과 불명확한 실패를 막았다

## 정리

이번 글에서는 툴 호출을 모델 자율성으로 보지 않고 애플리케이션이 설계한 실행 경계로 정리했습니다. `tools` 파라미터는 허용된 함수 집합과 인자 계약을 공개하고, `tool_calls`는 모델이 선택한 실행 요청을 구조적으로 돌려줍니다. 애플리케이션은 그 요청을 검증하고 실행한 뒤 다시 모델에 결과를 넣어 최종 응답을 완성합니다.

핵심은 실행 권한이 모델에 있지 않다는 점입니다. 모델은 도구를 제안할 뿐이고, 실행 책임은 여전히 애플리케이션이 집니다. 이 책임 분리가 있어야 조회, 검색, 데이터 접근, 외부 API 연동을 붙여도 운영 품질을 유지할 수 있습니다.

다음 글에서는 같은 계약 중심 관점을 스트리밍에 적용합니다. 툴 호출이 함수 실행 경계를 다뤘다면, 스트리밍은 시간에 걸쳐 도착하는 부분 응답을 어떻게 안정적으로 소비할 것인가의 문제입니다.

<!-- toc:begin -->
## 시리즈 목차

- [구조화 출력 — JSON 모드와 응답 스키마](./01-structured-output.md)
- **툴 호출 — 함수를 모델에 연결하기 (현재 글)**
- 스트리밍 심화 — 청크 처리와 오류 복구 (예정)
- 캐싱 전략 — 비용과 지연 시간 줄이기 (예정)
- 재시도와 오류 처리 — 안정적인 API 호출 만들기 (예정)
- 속도 제한 관리 — Rate Limit 대응 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- <https://console.groq.com/docs/tool-use>
- <https://json-schema.org/understanding-json-schema/>

### 관련 시리즈
- [구조화 출력 — JSON 모드와 응답 스키마](./01-structured-output.md)
- [스트리밍 심화 — 청크 처리와 오류 복구](./03-streaming-in-depth.md)

Tags: LLM, OpenAI, Streaming, Python
