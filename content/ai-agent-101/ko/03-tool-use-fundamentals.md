---
title: "AI Agent 101 (3/10): Tool Use 기초"
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

# AI Agent 101 (3/10): Tool Use 기초

agent를 agent답게 만드는 첫 번째 차이는 외부 세계와 상호작용할 수 있다는 점입니다. 검색 API를 부르고, 데이터베이스를 조회하고, 파일을 읽고, 계산 함수를 실행하는 순간 LLM은 설명자가 아니라 실행 오케스트레이터에 가까워집니다.

하지만 tool use는 겉보기보다 까다롭습니다. 모델이 도구를 호출한다고 해서 시스템이 자동으로 안전해지는 것은 아닙니다. 도구 이름이 모호하면 잘못된 함수를 선택하고, 입력 스키마가 약하면 형식 오류가 나고, 결과를 다시 모델에 넣는 방식이 어색하면 불필요한 루프가 길어집니다.

그래서 function calling은 단지 API 옵션 하나가 아니라 설계 패턴으로 봐야 합니다. 모델이 무엇을 결정하고, 애플리케이션 코드가 무엇을 책임지며, 실패를 어디서 차단할지를 분리해야 합니다.

이 글은 AI Agent 101 시리즈의 세 번째 글입니다.

이 글에서는 function calling을 "모델의 마법"이 아니라 "모델과 애플리케이션 사이의 계약"으로 이해하겠습니다.

![도구 호출 루프](https://yeongseon-books.github.io/book-public-assets/assets/ai-agent-101/03/03-01-tool-calling-loop.ko.png)
*도구 호출 루프*
> Tool use는 모델의 추론과 코드의 실행을 분리하고, 그 사이를 schema와 검증으로 연결하는 설계입니다.

## 먼저 던지는 질문

- function calling에서 모델이 결정하는 일과 애플리케이션 코드가 실행하는 일은 어디서 갈라질까요?
- tool schema가 애매하면 agent는 어떤 방식으로 잘못 실패할까요?
- tool 결과를 다시 모델에게 넣기 전에 무엇을 검증해야 할까요?

## 왜 이 글이 중요한가

tool use는 agent 시스템이 현실 세계와 닿는 첫 번째 인터페이스입니다. 이 경계가 약하면 모델이 아무리 좋아도 실제 업무 자동화는 불안정합니다. 반대로 이 경계를 잘 설계하면 비교적 단순한 모델로도 강한 자동화 루프를 만들 수 있습니다.

운영에서도 중요합니다. function calling 오류는 흔히 LLM 문제처럼 보이지만, 실제로는 schema 설계, 파라미터 검증, tool registry, 결과 직렬화 문제인 경우가 많습니다. 즉, 이 주제를 이해하면 agent 실패를 더 빨리 시스템 문제로 환원할 수 있습니다.

또한 이후의 reliability, evaluation, operations 주제도 여기서 시작합니다. 잘못된 tool 선택률, invalid arguments 비율, per-tool latency, fallback path 같은 지표는 모두 tool use 계층이 있어야 측정할 수 있습니다.

## 핵심 관점

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
    model="gpt-4.1",
    messages=[{"role": "user", "content": "What's the weather in Seoul?"}],
    tools=tools,
    tool_choice="auto"  # LLM decides whether to use tools
)
```

이런 예제에서는 `gpt-4.1`처럼 현재 tool calling을 지원하는 모델을 쓰는 편이 안전합니다. `gpt-4`는 legacy 맥락을 명시적으로 설명할 때만 남겨 두는 것이 좋습니다.

첫 단계는 도구 정의를 모델에 보여 주는 것입니다. 이때 이름, 설명, 파라미터 스키마가 곧 모델이 보는 전체 인터페이스입니다. 설명이 약하면 라우팅이 흔들리고, 타입이 약하면 인자 품질이 흔들립니다.

```python
# LLM의 응답 예시
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
        # 실제 weather API 호출
        weather_data = get_weather_api(params["location"])
        return json.dumps(weather_data)

    return json.dumps({"error": "Unknown tool"})

# Execute tool
tool_call = response.choices[0].message.tool_calls[0]
result = execute_tool(tool_call.function.name, tool_call.function.arguments)
```

세 번째 단계는 애플리케이션이 도구를 실행하는 구간입니다. 여기서는 파싱, validation, auth check, timeout, retry 같은 모든 현실 문제가 발생합니다. 그래서 production 코드에서는 이 함수가 생각보다 두꺼워지는 것이 정상입니다.

```python
# 대화에 도구 실행 결과 추가
messages = [
    {"role": "user", "content": "What's the weather in Seoul?"},
    response.choices[0].message,  # Assistant's tool call
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result  # Tool execution result
    }
]

# 최종 답변 생성
final_response = openai.chat.completions.create(
    model="gpt-4.1",
    messages=messages
)

print(final_response.choices[0].message.content)
# 출력: "서울의 현재 날씨는 맑고 기온은 15°C입니다."
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
            model="gpt-4.1",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # LLM이 도구를 사용하려는지 확인
        if not assistant_message.tool_calls:
            # 도구 호출이 없으면 최종 답변 준비 완료
            return assistant_message.content

        # assistant의 도구 호출을 대화에 추가
        messages.append(assistant_message)

        # 각 도구 호출 실행
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments

            # Execute tool
            result = execute_tool(tool_name, tool_args)

            # 실행 결과를 대화에 추가
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

## 실전 설계 보강

### 도구 스키마는 API 문서가 아니라 안전 경계입니다

tool schema를 자세히 쓰는 이유는 모델이 똑똑하지 않아서가 아니라, 실행 경계를 코드로 강제하기 위해서입니다. `additionalProperties: false`, enum 제한, 길이 제한 같은 제약은 토큰 비용보다 장애 비용을 줄입니다.

```json
{
  "type": "function",
  "name": "create_incident",
  "description": "장애 티켓을 생성합니다.",
  "parameters": {
    "type": "object",
    "properties": {
      "severity": {"type": "string", "enum": ["SEV-1", "SEV-2", "SEV-3"]},
      "title": {"type": "string", "minLength": 10, "maxLength": 120},
      "service": {"type": "string"}
    },
    "required": ["severity", "title", "service"],
    "additionalProperties": false
  }
}
```

### Python 도구 실행 래퍼 예시

```python
import time

def call_tool(name: str, args: dict, registry: dict[str, callable]) -> dict:
    started = time.time()
    if name not in registry:
        return {"ok": False, "error_type": "unknown_tool", "retryable": False}
    try:
        data = registry[name](**args)
        return {
            "ok": True,
            "data": data,
            "latency_ms": int((time.time() - started) * 1000)
        }
    except TimeoutError:
        return {"ok": False, "error_type": "timeout", "retryable": True}
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__, "retryable": False}
```

반환값에 `retryable`을 포함하면 planner가 다음 행동을 결정할 때 정책 분기가 명확해집니다. 도구 실패를 예외로만 던지면 agent 루프가 중단되기 쉽고, 실패 데이터가 누락됩니다.

### 병렬 도구 호출과 병합 전략

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_lookup(city: str):
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(get_weather, city)
        f2 = ex.submit(get_air_quality, city)
        return {"weather": f1.result(), "air": f2.result()}
```

병렬 호출을 쓸 때는 병합 규칙을 미리 정해야 합니다. 서로 상충하는 데이터가 들어오면 최신 timestamp 우선, 신뢰도 점수 우선 같은 규칙이 필요합니다. 이 규칙이 없으면 동일 입력에서도 최종 답변이 흔들립니다.

### 도구 관측성 대시보드 최소 항목

| 지표 | 의미 | 경보 기준 예시 |
| --- | --- | --- |
| tool_call_count | 도구 호출량 | 평시 대비 2배 급증 |
| tool_error_rate | 실패 비율 | 5분 평균 3% 초과 |
| p95_tool_latency | 지연 시간 | 1500ms 초과 |
| unknown_tool_rate | 미등록 도구 요청 비율 | 0.5% 초과 |

도구 사용은 agent 정확도의 기반이면서 동시에 운영 리스크의 근원입니다. 지표가 없으면 정확도 저하를 모델 문제로 오해하기 쉽습니다.

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

### 품질 회귀를 막는 CI 게이트 예시

```bash
python3 scripts/eval_agent.py --dataset eval/agent_core_ko.jsonl --min-success 0.82
python3 scripts/check_tool_schema.py --strict
python3 scripts/check_prompt_version.py --require-changelog
```

배포 파이프라인에서 최소 품질 게이트를 자동화하면 "우연히 좋아 보이는 빌드"가 운영으로 유입되는 일을 줄일 수 있습니다.

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

## 처음 질문으로 돌아가기

- **function calling에서 모델이 결정하는 일과 애플리케이션 코드가 실행하는 일은 어디서 갈라질까요?**
  - 모델은 어떤 도구를 어떤 인자로 부를지 요청하고, 애플리케이션 코드는 그 요청을 검증한 뒤 실제 API나 함수를 실행합니다.
- **tool schema가 애매하면 agent는 어떤 방식으로 잘못 실패할까요?**
  - 도구 이름과 인자 의미가 흐리면 모델은 비슷한 도구를 고르거나 잘못된 값을 채워 넣고, 실패 원인이 모델인지 schema인지 구분하기 어려워집니다.
- **tool 결과를 다시 모델에게 넣기 전에 무엇을 검증해야 할까요?**
  - 인자 타입, 허용 범위, 에러 형식, 민감 정보 포함 여부, 다음 판단에 필요한 최소 결과만 전달되는지를 확인해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Agent 101 (1/10): AI Agent란 무엇인가?](./01-what-is-an-ai-agent.md)
- [AI Agent 101 (2/10): 컨텍스트 엔지니어링](./02-context-engineering.md)
- **AI Agent 101 (3/10): Tool Use 기초 (현재 글)**
- AI Agent 101 (4/10): Agent Workflow 설계 (예정)
- AI Agent 101 (5/10): Memory와 State (예정)
- AI Agent 101 (6/10): Multi-Agent 시스템 (예정)
- AI Agent 101 (7/10): Agent 평가 (예정)
- AI Agent 101 (8/10): 에러 처리와 안정성 (예정)
- AI Agent 101 (9/10): 운영 (예정)
- AI Agent 101 (10/10): 첫 Agent 만들기 (예정)

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-agent-101/ko/03-tool-use-fundamentals)

Tags: AI Agent, LLM, Tool Use, Python
