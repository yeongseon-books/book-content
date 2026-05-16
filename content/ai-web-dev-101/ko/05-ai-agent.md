---
title: AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기
series: ai-web-dev-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI
- LLM
- 웹 개발
- Python
- Tutorial
last_reviewed: '2026-05-14'
seo_description: Tool Use와 Function Calling으로 모델이 외부 함수를 호출하는 구조를 이해하고 간단한 에이전트를 구현합니다.
---

# AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기

지금까지 만든 AI는 텍스트만 주고받았습니다. 질문을 던지면 그럴듯한 답을 내놓지만, 실제 날씨를 확인하거나 계산을 하거나 외부 시스템을 조회하는 일은 직접 하지 못했습니다. 실서비스에서 한 단계 더 나아가려면 모델이 필요할 때 도구를 꺼내 쓰는 구조가 필요합니다.

이 글은 AI 웹 개발 입문 시리즈의 5번째 글입니다.

여기서는 Tool Use를 중심으로 AI가 외부 기능을 호출하는 흐름을 살펴보겠습니다.

## 이 글에서 다룰 문제

- 일반 챗봇과 에이전트는 무엇이 다를까요?
- Tool Use 또는 Function Calling은 어떤 계약으로 동작할까요?
- 모델은 어떻게 “이 함수를 실행해 달라”고 요청할까요?
- 여러 도구를 순서대로 쓰는 루프는 어떻게 구현할까요?
- 실제 서비스에서는 무엇을 특히 조심해야 할까요?

> 에이전트의 핵심은 모델이 모든 답을 머릿속에서 만드는 데 있지 않습니다. 어떤 순간에 외부 도구가 필요한지 판단하고, 그 결과를 다시 읽어 최종 답을 조립하는 루프를 갖는 데 있습니다.

## 챗봇과 에이전트의 차이

일반 챗봇은 질문을 이해하고 텍스트를 생성합니다. 반면 에이전트는 목표를 달성하기 위해 어떤 정보가 더 필요한지 판단하고, 필요하면 외부 도구를 호출한 뒤 그 결과를 바탕으로 다시 답을 만듭니다.

- 일반 챗봇: 가진 지식 안에서 답을 생성합니다.
- AI 에이전트: 외부 API, 데이터베이스, 계산기, 검색 도구 같은 기능을 상황에 맞게 호출합니다.

예를 들어 “오늘 서울 날씨 알려줘”라는 질문에서 일반 챗봇은 학습된 일반 지식 범위 안에서 답하려고 들 수 있습니다. 에이전트는 여기서 멈추지 않고 “실시간 날씨를 확인해야 한다”는 판단을 내린 뒤, 실제 도구 호출 요청을 보냅니다.

![챗봇과 AI 에이전트의 차이](../../../assets/ai-web-dev-101/05/assistant-vs-agent.ko.png)

*챗봇과 AI 에이전트의 차이*

## Tool Use는 어떻게 동작하나

Tool Use 또는 Function Calling의 구조는 의외로 단순합니다.

1. 개발자가 모델에게 사용 가능한 도구 목록을 알려 줍니다.
2. 모델은 사용자 질문을 보고 어떤 도구가 필요한지 판단합니다.
3. 모델은 함수를 직접 실행하지 않고, “이 함수에 이 인자를 넣어 실행해 달라”는 요청을 보냅니다.
4. 애플리케이션이 실제 함수를 실행합니다.
5. 실행 결과를 다시 모델에게 전달하면, 모델이 최종 답을 만듭니다.

실행 주체는 모델이 아니라 애플리케이션입니다. 모델은 제안하고, 애플리케이션은 검증하고, 실제로 실행합니다. 이 경계가 있어야 보안과 통제를 유지할 수 있습니다.

![모델 판단과 함수 실행이 오가는 도구 호출 흐름](../../../assets/ai-web-dev-101/05/function-calling-cycle.ko.png)

*모델 판단과 함수 실행이 오가는 도구 호출 흐름*

## OpenAI 도구 명세의 기본 구조

OpenAI API에서는 `tools` 파라미터로 함수 목록을 전달합니다. 함수 이름, 설명, 파라미터 구조를 JSON 스키마 비슷한 형태로 넣어 주면 됩니다.

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "특정 지역의 현재 날씨 정보를 가져옵니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "도시 이름 (예: 서울, 부산)"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

모델은 함수 코드 자체를 읽는 것이 아니라, 이 설명과 파라미터 계약을 읽고 판단합니다. 그래서 `description`이 빈약하면 엉뚱한 도구를 고르거나 잘못된 인자를 만들 가능성이 높아집니다.

## 실습 1: 날씨 조회 에이전트

실제 날씨 API 대신, 동작 원리만 보여 주는 작은 예제로 시작하겠습니다.

### 1. 도구 정의하기

아래 코드는 실제 파이썬 함수와 모델에 전달할 도구 명세를 함께 준비합니다.

```python
import ast
import json
import operator as op

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](safe_eval(node.left), safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](safe_eval(node.operand))
    raise ValueError("허용되지 않은 수식입니다.")

# 실제로 실행될 가짜 날씨 함수
def get_weather(location):
    if "서울" in location:
        return json.dumps({"location": "서울", "temperature": "25도", "condition": "맑음"})
    elif "부산" in location:
        return json.dumps({"location": "부산", "temperature": "22도", "condition": "구름 조금"})
    else:
        return json.dumps({"location": location, "temperature": "알 수 없음", "condition": "정보 없음"})

# AI에게 전달할 도구 명세
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "특정 지역의 현재 날씨 정보를 가져옵니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "도시 이름"}
                },
                "required": ["location"]
            }
        }
    }
]
```

### 2. 모델의 판단 받기

이제 사용자 질문을 보내고, 모델이 실제로 도구 호출이 필요하다고 판단하는지 확인합니다.

```python
from openai import OpenAI
client = OpenAI()

messages = [{"role": "user", "content": "서울 날씨는 어때?"}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# AI가 함수 호출이 필요하다고 판단했는지 확인
tool_calls = response.choices[0].message.tool_calls

if tool_calls:
    print(f"AI의 판단: {tool_calls[0].function.name} 함수를 호출해야 함!")
```

### 3. 함수 실행과 결과 전달

모델은 여기서 함수를 직접 실행하지 않습니다. 대신 어떤 함수와 어떤 인자를 써야 하는지 알려 주고, 실제 실행은 우리가 맡습니다.

```python
if tool_calls:
    # 1. AI가 요청한 함수 이름과 인자 추출
    tool_call = tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    
    # 2. 실제 파이썬 함수 실행
    if function_name == "get_weather":
        function_response = get_weather(location=function_args.get("location"))
    
    # 3. AI의 메시지와 함수 실행 결과를 메시지 목록에 추가
    messages.append(response.choices[0].message) # AI의 호출 요청 추가
    messages.append({
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": function_name,
        "content": function_response,
    })
    
    # 4. 결과가 포함된 메시지 목록을 다시 AI에게 보내 최종 답변 받기
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    
    print(final_response.choices[0].message.content)
    # 출력 예시: "현재 서울의 날씨는 25도로 맑은 상태입니다."
```

이 구조를 보면 에이전트의 본질이 선명해집니다. 모델이 전부를 하는 것이 아니라, 모델은 판단과 조립을 맡고 실제 외부 행동은 애플리케이션이 수행합니다.

## 실습 2: 여러 도구를 쓰는 루프

에이전트가 진짜 에이전트처럼 보이는 순간은 도구를 한 번만 쓰는 경우보다, 여러 단계를 이어서 해결할 때입니다. 예를 들어 환율을 조회한 뒤 계산기로 수수료를 빼는 작업은 한 번의 함수 호출로 끝나지 않습니다.

```python
def get_exchange_rate(from_currency, to_currency):
    # 가짜 환율 데이터
    rates = {"USD_KRW": 1350}
    pair = f"{from_currency}_{to_currency}"
    rate = rates.get(pair, 1300)
    return json.dumps({"pair": pair, "rate": rate})

def calculate(expression):
    # 간단한 사칙연산만 허용하는 안전한 계산기
    try:
        tree = ast.parse(expression, mode="eval")
        return str(safe_eval(tree.body))
    except Exception as e:
        return f"계산 오류: {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "통화 간 실시간 환율을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string", "description": "기준 통화 (예: USD)"},
                    "to_currency": {"type": "string", "description": "대상 통화 (예: KRW)"}
                },
                "required": ["from_currency", "to_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "수학 수식을 계산합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "계산할 수식 (예: 100 * 1350 * 0.9)"}
                },
                "required": ["expression"]
            }
        }
    }
]

def run_agent(user_prompt):
    messages = [{"role": "user", "content": user_prompt}]
    
    # 최대 5번까지 도구 사용을 허용하는 루프
    for i in range(5):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools
        )
        
        message = response.choices[0].message
        messages.append(message)
        
        # AI가 최종 답변을 내놓으면 루프 종료
        if not message.tool_calls:
            break
            
        # 모든 도구 호출 처리
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # 실제 서비스에서는 LLM이 만든 인자를 그대로 실행하지 말고
            # allowlist, 타입 검사, 범위 검사로 먼저 검증해야 합니다.
            
            print(f"--- AI가 {name} 도구를 사용합니다: {args} ---")
            
            if name == "get_exchange_rate":
                result = get_exchange_rate(**args)
            elif name == "calculate":
                result = calculate(**args)
            else:
                result = "알 수 없는 도구입니다."
                
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": name,
                "content": result,
            })
            
    return messages[-1].content

# 실행 테스트
prompt = "100달러를 원화로 환전하고, 거기서 10% 수수료를 뺀 최종 금액을 알려줘."
print(f"최종 답변: {run_agent(prompt)}")
```

이 예제에서 모델은 먼저 환율 도구를 쓰고, 그 결과를 바탕으로 계산기 도구를 다시 호출한 뒤 최종 답을 조립할 수 있습니다. 즉, 한 번의 도구 호출이 아니라 판단 → 실행 → 관찰 → 재판단 루프를 돌게 됩니다.

![여러 도구를 순차적으로 사용하는 에이전트](../../../assets/ai-web-dev-101/05/multi-tool-example-flow.ko.png)

*여러 도구를 순차적으로 사용하는 에이전트*

## 에이전트 루프를 읽는 법

에이전트 루프는 보통 다음 순서로 이해하면 됩니다.

1. 사용자 입력
2. 모델의 판단
3. 도구 실행 요청
4. 애플리케이션의 실제 실행
5. 실행 결과 관찰
6. 완료 또는 다음 단계 반복

이 흐름이 있으면 모델은 마치 스스로 문제를 해결하는 것처럼 보입니다. 하지만 실제로는 각 단계가 명시된 프로토콜로 이어져 있을 뿐입니다. 이 점을 분명히 이해해야 디버깅도 쉬워집니다.

![판단과 실행이 반복되는 에이전트 루프](../../../assets/ai-web-dev-101/05/agent-loop-overview.ko.png)

*판단과 실행이 반복되는 에이전트 루프*

## 실제 서비스에서 꼭 조심할 점

에이전트는 편리하지만, 일반 챗봇보다 위험 반경도 넓습니다. 특히 아래 다섯 가지는 초반부터 안전장치로 넣어 두는 편이 좋습니다.

1. 도구 설명 품질: 모델은 `description`을 보고 판단하므로 언제 써야 하는지 분명히 적어야 합니다.
2. 무한 루프 방지: 최대 반복 횟수를 정해 두지 않으면 같은 도구를 계속 호출할 수 있습니다.
3. 인자 검증과 권한 범위: LLM이 만든 인자를 그대로 실행하지 말고 allowlist, 타입 검사, 범위 검사를 먼저 거칩니다.
4. 타임아웃과 재시도 한도: 외부 API 실패가 전체 루프를 붙잡지 않게 해야 합니다.
5. 비용 관리: 도구가 늘어나면 모델 호출 횟수도 늘어나므로 지연과 비용이 함께 증가합니다.

![도구 사용 권한과 안전 경계](../../../assets/ai-web-dev-101/05/tool-permission-boundary.ko.png)

*도구 사용 권한과 안전 경계*

## 체크리스트

- [ ] 도구 설명과 파라미터 명세를 충분히 적었다.
- [ ] 모델이 만든 인자를 실행 전에 검증한다.
- [ ] 최대 반복 횟수와 타임아웃 한도를 정했다.
- [ ] 부작용이 큰 도구는 권한 경계를 따로 둔다.

## 정리

에이전트는 “더 똑똑한 챗봇”이라기보다, 모델이 외부 도구를 필요에 따라 호출하는 실행 루프를 가진 시스템입니다.

- Tool Use의 핵심은 모델이 실행을 직접 하지 않고, 함수 호출 요청을 만든다는 점입니다.
- 애플리케이션은 그 요청을 검증하고 실제로 수행한 뒤 결과를 다시 모델에 넘깁니다.
- 여러 도구를 이어 쓰는 루프가 붙으면 에이전트다운 행동이 나타납니다.
- 실서비스에서는 권한, 검증, 반복 한도, 비용 통제가 필수입니다.

다음 글에서는 지금까지 만든 AI 기능을 실제 사용자에게 보여 줄 수 있도록 배포와 운영 관점으로 넘어가겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기](./01-hello-ai-api.md)
- [프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술](./02-prompt-engineering.md)
- [AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현](./03-ai-chatbot.md)
- [RAG 입문 — 내 데이터로 답하는 AI 만들기](./04-rag-intro.md)
- **AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기 (현재 글)**
- AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 (예정)
- AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법 (예정)

<!-- toc:end -->

## 참고 자료

- [OpenAI: Function calling guide](https://platform.openai.com/docs/guides/function-calling) — `tools`, `tool_choice`, `tool_calls` 응답 흐름의 정식 명세
- [OpenAI: Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) — 도구 스키마와 응답 스키마를 JSON Schema로 강제하는 방법
- [OpenAI Cookbook: function calling and tools](https://cookbook.openai.com/topic/tools) — 실제 도구 호출 루프 코드 예제
- [Anthropic: Tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — 동일한 도구 호출 패턴을 다른 모델 공급자가 어떻게 정의하는지 비교용
- [LangGraph: Agent runtime](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/) — 직접 짠 루프 대신 프레임워크가 제공하는 에이전트 런타임의 구성 요소
- [JSON Schema specification](https://json-schema.org/specification.html) — `parameters` 스키마 작성에 필요한 키워드와 검증 규칙

Tags: AI, LLM, 웹 개발, Python, Tutorial
