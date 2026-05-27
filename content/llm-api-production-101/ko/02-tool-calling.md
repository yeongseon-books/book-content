---
episode: 2
language: ko
last_reviewed: '2026-05-15'
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
title: "LLM API Production 101 (2/6): 툴 호출 — 함수를 모델에 연결하기"
seo_description: Groq tools와 Pydantic 검증으로 안전한 툴 호출 루프를 설계하는 방법을 다룹니다.
---

# LLM API Production 101 (2/6): 툴 호출 — 함수를 모델에 연결하기

구조화 출력이 안정화되면 곧 다음 요구가 따라옵니다. 모델이 답변만 만들지 말고 애플리케이션 기능도 선택해 주었으면 좋겠다는 요구입니다. 주문 상태를 물으면 조회 함수를 호출하고, 환율을 물으면 내부 서비스에서 값을 가져오고, 일정 생성 요청이 오면 캘린더 API까지 이어지길 기대하게 됩니다.

이 글은 LLM API 프로덕션 101 시리즈의 2번째 글입니다.

이 시점에서 많은 초기 구현은 다시 문자열 관습으로 돌아갑니다. 모델이 함수 이름과 인자를 텍스트로 내놓게 한 뒤, 애플리케이션이 `if` 문이나 수동 파서로 해석합니다. 작은 예제에서는 충분해 보이지만, 함수 이름 오탈자, 누락 인자, 허용되지 않은 추가 키, 안전하지 않은 디스패치가 금방 쌓입니다.

툴 호출이 중요한 이유는 모델이 코드를 실행해서가 아닙니다. 애플리케이션이 허용한 함수 이름, 설명, 인자 스키마를 명시적으로 공개하고, 모델은 그 안에서 선택만 하기 때문입니다. 실행 권한, 검증, 부작용 통제는 여전히 애플리케이션이 갖습니다.

이번 글에서는 Groq의 `tools` 파라미터와 `tool_calls` 응답을 사용해, 모델 선택 → 인자 검증 → 함수 실행 → 결과 재주입까지 이어지는 전체 루프를 운영 관점으로 정리하겠습니다.

여기서는 모델 응답을 안전한 함수 실행 경계로 연결하는 툴 호출 루프를 봅니다.

![툴 호출: 함수를 모델에 연결하기](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-01-tool-calling-connecting-functions-to-the.ko.png)
*툴 호출: 함수를 모델에 연결하기*
> 툴 호출은 모델에게 권한을 넘기는 기능이 아니라, 애플리케이션이 통제 가능한 형태로 실행 요청을 구조화하는 기능입니다.

## 먼저 던지는 질문

- 툴 호출은 모델에게 실행 권한을 넘기는 기능일까요, 애플리케이션이 만든 실행 경계일까요?
- `tools` 정의와 `tool_calls` 응답에서 각각 무엇을 검증해야 할까요?
- 함수 실행 루프를 운영 환경에서 안전하게 끝내려면 어떤 방어선이 필요할까요?

## 왜 이 글이 중요한가

툴 호출은 LLM 애플리케이션이 외부 세계와 만나는 첫 실행 경계입니다. 구조화 출력이 “데이터를 어떻게 안전하게 받는가”의 문제였다면, 툴 호출은 “그 데이터를 바탕으로 무엇을 실행하게 할 것인가”의 문제입니다. 이 경계를 느슨하게 만들면 모델은 똑똑해 보일지 몰라도 시스템은 금방 위험해집니다.

현업에서는 조회성 도구와 상태 변경 도구가 같은 수준으로 다뤄지는 순간부터 문제가 커집니다. 주문 상태 조회와 주문 취소는 같은 툴 호출처럼 보여도 신뢰 가정이 전혀 다릅니다. 그래서 툴 호출을 기능 확장으로만 보지 말고, 권한과 검증이 걸린 실행 인터페이스로 봐야 합니다.

또한 툴 호출은 추적성의 문제이기도 합니다. 사용자가 “왜 엉뚱한 답이 나왔나요?”라고 물었을 때, 어떤 툴이 어떤 인자로 호출되었고 어떤 결과가 돌아왔는지 같은 타임라인이 있어야 설명할 수 있습니다. 이 설명 가능성이 없으면 운영 품질은 빠르게 떨어집니다.

## 핵심 개념

### 왜 문자열 기반 디스패치는 금방 흔들리는가

![문자열 분기와 툴 계약의 차이 비교](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-01-why-string-based-dispatch-does-not-scale.ko.png)

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

![툴 정의를 이루는 구성 요소 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-02-what-goes-into-the-tools-parameter.ko.png)

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

![첫 툴 호출 요청에서 모델이 고르는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-03-sending-the-first-tool-enabled-request.ko.png)

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

`tool_choice="auto"`는 모델이 필요할 때만 도구를 고르게 합니다. 이 시점의 응답은 최종 사용자 답이 아니라 실행 요청입니다. 애플리케이션이 아직 한 단계를 더 거쳐야 합니다.

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

![툴 호출 왕복 실행 루프 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-04-building-the-full-function-execution-loo.ko.png)

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

이 구조의 장점은 역할이 분리된다는 사실입니다. 모델은 어떤 도구가 필요한지 제안하고, 애플리케이션은 실제 실행과 검증을 맡으며, 마지막 응답은 다시 모델이 자연어로 정리합니다.

### 실패한 툴 호출도 구조화해 되돌리기

성공 경로만 예쁘게 만들면 운영에서는 절반만 끝난 셈입니다. 도구가 타임아웃되거나 권한 오류가 나면 애플리케이션은 예외 문자열을 그대로 노출하는 대신, 모델이 다시 해석할 수 있는 표준화된 오류 payload를 주는 편이 낫습니다.

```python
import json

from pydantic import BaseModel, ValidationError

class OrderStatusArgs(BaseModel):
    order_id: str

def run_tool(function_name: str, raw_arguments: str) -> dict:
    try:
        arguments = json.loads(raw_arguments)
        validated = OrderStatusArgs.model_validate(arguments)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error_type": "invalid_json",
            "message": str(exc),
        }
    except ValidationError as exc:
        return {
            "ok": False,
            "error_type": "invalid_arguments",
            "message": exc.errors()[0]["msg"],
        }

    if function_name != "get_order_status":
        return {
            "ok": False,
            "error_type": "unknown_tool",
            "message": f"unsupported tool: {function_name}",
        }

    return {
        "ok": True,
        "data": {
            "order_id": validated.order_id,
            "status": "in_transit",
            "eta_days": 2,
        },
    }

print(run_tool("get_order_status", '{"order_id": 1001}'))
print(run_tool("cancel_order", '{"order_id": "ORD-1001"}'))
```

<!-- injected-output:start -->
**실행 결과**

    {'ok': False, 'error_type': 'invalid_arguments', 'message': 'Input should be a valid string'}
    {'ok': False, 'error_type': 'unknown_tool', 'message': 'unsupported tool: cancel_order'}

<!-- injected-output:end -->

이 패턴이 실용적인 이유는 실패가 자연어 예외가 아니라 계약된 데이터로 돌아오기 때문입니다. 모델에게는 `ok: false`와 `error_type`을 보고 "주문 번호 형식이 잘못되었습니다" 같은 설명을 만들게 할 수 있고, 애플리케이션은 같은 필드로 메트릭과 알림을 모을 수 있습니다. 특히 상태 변경 도구에서는 이 표준화가 감사 로그와 재실행 금지 정책까지 자연스럽게 이어집니다.

### 운영에서 특히 지켜야 할 방어선

![툴 실행 전에 거치는 운영 방어 단계](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/02/02-05-what-to-guard-in-production.ko.png)

*툴 실행 전에 거치는 운영 방어 단계*

툴 호출은 시스템을 강하게 만들 수도 있고 위험하게 만들 수도 있습니다. 핵심 방어선은 네 가지입니다. 임의 함수 이름으로 디스패치하지 않을 것, 인자를 검증 없이 실행하지 않을 것, 읽기 전용 도구와 부작용 도구를 같은 신뢰 수준으로 다루지 않을 것, 그리고 모든 툴 요청과 결과를 추적 가능하게 기록할 것입니다.

특히 `globals()`나 동적 import 같은 방식으로 함수 이름을 그대로 실행 경로에 연결하는 패턴은 피해야 합니다. 툴 호출의 장점은 명시적 allowlist에 있습니다. 그 장점을 버리면 구조화된 실행 경계를 만든 의미가 거의 사라집니다.

### 툴 호출 라우터를 명시적 테이블로 고정하기

함수가 두세 개일 때는 단순 딕셔너리도 충분합니다. 하지만 운영에서는 권한, 타임아웃, 감사 필드가 함수마다 달라지므로 메타데이터를 함께 갖는 라우팅 테이블이 더 안전합니다.

```python
import time
from dataclasses import dataclass
from typing import Callable

@dataclass
class ToolSpec:
    func: Callable
    timeout_seconds: float
    side_effect: bool

def get_order_status(order_id: str) -> dict:
    return {"order_id": order_id, "status": "in_transit"}

def cancel_order(order_id: str, reason: str) -> dict:
    return {"order_id": order_id, "cancelled": True, "reason": reason}

TOOL_REGISTRY: dict[str, ToolSpec] = {
    "get_order_status": ToolSpec(func=get_order_status, timeout_seconds=2.0, side_effect=False),
    "cancel_order": ToolSpec(func=cancel_order, timeout_seconds=5.0, side_effect=True),
}

def run_registered_tool(name: str, **kwargs) -> dict:
    spec = TOOL_REGISTRY.get(name)
    if spec is None:
        raise ValueError(f"unknown tool: {name}")

    started = time.monotonic()
    result = spec.func(**kwargs)
    elapsed = time.monotonic() - started

    return {
        "ok": True,
        "tool": name,
        "side_effect": spec.side_effect,
        "elapsed_ms": int(elapsed * 1000),
        "data": result,
    }
```

이렇게 고정하면 장점이 분명합니다. 실행 가능한 도구 집합이 코드 한곳에 모이고, 위험한 도구를 별도로 분류하기 쉬우며, 로그 필드도 표준화됩니다. 이후 승인 워크플로, 사용자 권한, 최대 실행 시간 같은 규칙을 붙일 때도 같은 표를 확장하면 됩니다.

### 상태 변경 도구에는 멱등성 키를 붙이기

툴 호출에서 가장 위험한 구간은 재시도입니다. 네트워크 오류로 결과를 못 받은 요청이 실제로는 이미 성공했을 수 있기 때문입니다. 조회 도구는 재호출해도 문제가 적지만, 취소/생성/결제 같은 상태 변경 도구는 멱등성 키가 없으면 중복 부작용을 만들 수 있습니다.

```python
from dataclasses import dataclass

@dataclass
class ToolExecutionContext:
    request_id: str
    idempotency_key: str

executed: dict[str, dict] = {}

def cancel_order_with_idempotency(order_id: str, reason: str, ctx: ToolExecutionContext) -> dict:
    if ctx.idempotency_key in executed:
        return executed[ctx.idempotency_key]

    result = {
        "order_id": order_id,
        "cancelled": True,
        "reason": reason,
        "request_id": ctx.request_id,
    }
    executed[ctx.idempotency_key] = result
    return result
```

운영에서는 이 키를 메모리가 아니라 Redis나 데이터베이스에 기록해야 합니다. 핵심은 “재시도는 같은 효과를 한 번만 내야 한다”는 원칙을 코드와 저장소 양쪽에서 보장하는 것입니다. 툴 호출 루프를 완성했다면, 다음 단계는 항상 멱등성입니다.

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

모델에는 실행 권한이 없습니다. 모델은 도구를 제안할 뿐이고, 실행 책임은 여전히 애플리케이션이 집니다. 이 책임 분리가 있어야 조회, 검색, 데이터 접근, 외부 API 연동을 붙여도 운영 품질을 유지할 수 있습니다.

다음 글에서는 같은 계약 중심 관점을 스트리밍에 적용합니다. 툴 호출이 함수 실행 경계를 다뤘다면, 스트리밍은 시간에 걸쳐 도착하는 부분 응답을 어떻게 안정적으로 소비할 것인가의 문제입니다.

## 처음 질문으로 돌아가기

- **툴 호출은 모델에게 실행 권한을 넘기는 기능일까요, 애플리케이션이 만든 실행 경계일까요?**
  툴 호출은 모델에게 권한을 넘기는 기능이 아니라, 애플리케이션이 허용한 함수 목록과 스키마 안에서 실행 요청을 받는 계약입니다.

- **`tools` 정의와 `tool_calls` 응답에서 각각 무엇을 검증해야 할까요?**
  `tools`에서는 이름, 설명, 파라미터 스키마를 검증하고, `tool_calls`에서는 선택된 이름과 인자가 허용 범위에 있는지 확인해야 합니다.

- **함수 실행 루프를 운영 환경에서 안전하게 끝내려면 어떤 방어선이 필요할까요?**
  허용 목록, 입력 검증, 타임아웃, 예외 구조화, 실행 결과 재주입 같은 방어선이 있어야 루프를 안전하게 닫을 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM API Production 101 (1/6): 구조화 출력 — JSON 모드와 응답 스키마](./01-structured-output.md)
- **LLM API Production 101 (2/6): 툴 호출 — 함수를 모델에 연결하기 (현재 글)**
- LLM API Production 101 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구 (예정)
- LLM API Production 101 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기 (예정)
- LLM API Production 101 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기 (예정)
- LLM API Production 101 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Groq tool use guide](https://console.groq.com/docs/tool-use)
- [JSON Schema fundamentals](https://json-schema.org/understanding-json-schema/)

### 검증 보조 자료
- [Pydantic validation errors](https://docs.pydantic.dev/latest/errors/errors/)

### 관련 시리즈
- [구조화 출력 — JSON 모드와 응답 스키마](./01-structured-output.md)
- [스트리밍 심화 — 청크 처리와 오류 복구](./03-streaming-in-depth.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-api-production-101/ko/02-tool-calling)

Tags: LLM, OpenAI, Streaming, Python
