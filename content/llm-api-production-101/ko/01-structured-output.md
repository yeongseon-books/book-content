---
title: 구조화 출력 — JSON 모드와 응답 스키마
series: llm-api-production-101
episode: 1
language: ko
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Streaming
- Python
last_reviewed: '2026-04-30'
---

# 구조화 출력 — JSON 모드와 응답 스키마

> LLM API 프로덕션 101 시리즈 (1/6)

LLM API를 처음 붙인 뒤 가장 먼저 겪는 운영 문제는 모델 품질보다 출력 모양입니다. 데모 단계에서는 자연어 한 덩어리를 화면에 보여주면 끝이지만, 실제 서비스는 그 다음 단계가 더 중요합니다. 분류 결과를 DB에 넣어야 하고, 추출된 필드를 검증해야 하며, 후속 파이프라인이 같은 키 이름을 기대합니다. 여기서 모델이 보기 좋은 문장을 써 주는지는 두 번째 문제입니다. 더 중요한 것은 애플리케이션이 읽을 수 있는 형태로 답이 돌아오는가입니다.

많은 팀이 이 지점에서 문자열 파싱으로 시간을 잃습니다. 모델에게 "JSON으로 답해 주세요"라고 적고 `json.loads()`를 바로 호출합니다. 초기 테스트에서는 잘 되는 듯 보이지만, 프롬프트가 길어지거나 예외 상황이 끼는 순간 설명 문장이 앞에 붙고, 코드 펜스가 섞이고, 키 이름이 바뀝니다. 그때부터 장애는 모델이 아니라 계약 부재에서 시작됩니다. 애플리케이션은 엄격한 구조를 기대하는데, 모델은 여전히 텍스트 생성기처럼 동작하기 때문입니다.

이번 글의 목표는 그 느슨한 경계를 계약 기반 인터페이스로 바꾸는 것입니다. Groq API에서 `response_format={"type": "json_object"}`를 사용해 JSON 모드를 강제하고, 반환된 문자열을 Pydantic 스키마로 한 번 더 검증합니다. 이 두 단계를 거치면 모델 출력은 "그럴듯한 텍스트"가 아니라 "검증 가능한 데이터"가 됩니다. 프로덕션에서는 이 차이가 큽니다. 실패를 조기에 감지할 수 있고, 재시도 조건을 명확히 만들 수 있으며, 다운스트림 코드가 방어적으로 작성되기 쉬워집니다.

이 글에서는 다섯 가지를 다룹니다. 첫째, 왜 자연어 응답을 그대로 파싱하는 방식이 취약한지 봅니다. 둘째, JSON 모드가 정확히 무엇을 보장하고 무엇은 보장하지 않는지 정리합니다. 셋째, Groq Python SDK로 구조화 출력을 요청하는 최소 예제를 만듭니다. 넷째, Pydantic 검증을 붙여 애플리케이션 경계를 단단하게 만듭니다. 다섯째, 실패 케이스를 어떻게 로그로 남기고 복구할지 운영 관점에서 정리합니다.

핵심은 단순합니다. **프로덕션의 구조화 출력은 프롬프트 요령이 아니라 응답 계약 설계 문제입니다.**

---

## 실행 준비

예제를 바로 실행하려면 Python 3.10 이상 환경에서 아래 준비를 먼저 끝내면 됩니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install groq pydantic
export GROQ_API_KEY="여기에-발급받은-키"
```

이 글의 모든 코드는 `llama-3.1-8b-instant`와 `groq` SDK를 기준으로 작성했습니다.

---

## 왜 자연어 파싱은 오래 버티지 못하는가

입문 단계에서 흔한 패턴은 아래와 같습니다. 모델에게 상품 후기에서 감정을 뽑아 달라고 요청하고, 답을 문자열로 받아 몇 줄의 후처리로 해석합니다.

```python
raw_text = "positive, confidence=0.91"
label, confidence = raw_text.split(",")
```

처음에는 빨라 보입니다. 하지만 이 방식은 모델과 애플리케이션 사이에 명확한 계약이 없습니다. 모델이 `Positive`로 대문자를 쓰거나, 설명 문장을 하나 덧붙이거나, `confidence: 0.91`처럼 구두점을 바꾸는 순간 파서는 깨집니다. 더 나쁜 점은 실패 원인이 코드인지 모델인지 로그만 보고 구분하기 어렵다는 것입니다.

프로덕션에서는 보통 세 가지 요구가 동시에 생깁니다.

- 필드 이름이 항상 같아야 합니다.
- 타입이 항상 맞아야 합니다.
- 누락이나 범위 초과를 코드가 즉시 감지해야 합니다.

예를 들어 티켓 분류 시스템이라면 `category`는 정해진 집합 중 하나여야 하고, `priority`는 정수 범위 안에 있어야 하며, `summary`는 비어 있지 않아야 합니다. 자연어 응답을 문자열로 파싱하면 이 제약을 프롬프트와 파싱 로직 곳곳에 흩뿌리게 됩니다. JSON 모드와 스키마 검증을 함께 쓰면 이 제약이 한곳으로 모입니다.

---

## JSON 모드가 해 주는 일과 해 주지 않는 일

Groq의 `response_format={"type": "json_object"}`는 모델 출력 형식을 JSON 객체로 유도합니다. 이것이 중요한 이유는 최소한의 구문 계약을 만들기 때문입니다. 응답이 자유로운 산문이 아니라 중괄호 기반 객체 형태로 돌아오게 만들 수 있습니다.

다만 여기서 과신하면 안 됩니다. JSON 모드는 **JSON 문법 쪽 문제를 줄여 주는 도구**이지, **비즈니스 스키마를 완전히 보장하는 도구**는 아닙니다. 예를 들어 모델이 아래처럼 응답할 수는 있습니다.

```json
{
  "sentiment": "positive",
  "confidence": "high"
}
```

문법은 JSON이지만 `confidence`는 우리가 기대한 `float`가 아닙니다. 또는 필요한 `reasons` 필드가 빠질 수도 있습니다. 그래서 실전에서는 두 단계를 분리해서 생각해야 합니다.

1. 모델이 JSON 객체를 내놓게 강제한다.
2. 애플리케이션이 그 JSON을 스키마로 검증한다.

첫 단계가 없다면 파싱 자체가 흔들리고, 두 번째 단계가 없다면 의미 검증이 비어 있습니다. 둘 중 하나만 있어서는 운영 안정성이 충분하지 않습니다.

---

## Groq SDK로 JSON 모드 요청 보내기

아래 예제는 고객 문의 문장에서 `category`, `priority`, `summary`를 추출합니다. 모델은 `llama-3.1-8b-instant`, 패키지는 `groq`를 사용합니다.

```python
import json
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": (
            "당신은 고객 문의를 분류하는 분석기입니다. "
            "category는 billing/account/bug/shipping 중 하나입니다. "
            "priority는 1~5 정수입니다. "
            "summary는 8~120자 문자열입니다. "
            "반드시 category, priority, summary 키를 가진 JSON 객체 하나만 반환하세요."
        ),
    },
    {
        "role": "user",
        "content": (
            "문의: 결제는 완료됐는데 주문 내역에 보이지 않습니다. "
            "환불을 원하지는 않고, 주문 상태만 빨리 확인하고 싶습니다."
        ),
    },
]

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    response_format={"type": "json_object"},
    temperature=0,
)

content = completion.choices[0].message.content
payload = json.loads(content)

print(payload)
```

여기서 운영적으로 중요한 지점은 세 군데입니다.

첫째, 시스템 메시지에서 "JSON 객체 하나만 반환"을 명시합니다. JSON 모드를 걸더라도 프롬프트 계약을 같이 적어 두는 편이 좋습니다. 모델이 해야 할 일을 사람도 읽을 수 있게 남겨 두는 효과가 있기 때문입니다.

둘째, `temperature=0`으로 변동성을 줄입니다. 구조화 추출 작업에서는 창의성이 아니라 일관성이 더 중요합니다.

셋째, `json.loads()`는 파서일 뿐 검증기가 아닙니다. 이 단계에서 성공해도 스키마가 맞는다는 뜻은 아닙니다. 다음 단계에서 Pydantic이 필요합니다.

---

## Pydantic으로 응답 스키마를 고정하기

구조화 출력이 프로덕션에서 힘을 가지는 순간은 검증이 붙을 때입니다. 아래 예제는 모델 응답을 Python 타입으로 변환하면서 누락과 타입 오류를 즉시 감지합니다.

```python
import json
import os
from enum import Enum

from groq import Groq
from pydantic import BaseModel, Field, ValidationError

class Category(str, Enum):
    billing = "billing"
    account = "account"
    bug = "bug"
    shipping = "shipping"

class TicketClassification(BaseModel):
    category: Category
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=8, max_length=120)
    customer_needs_followup: bool

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": (
                "고객 문의를 분류하세요. "
                "category는 billing/account/bug/shipping 중 하나입니다. "
                "priority는 1~5 정수입니다. "
                "summary는 8~120자 문자열입니다. "
                "customer_needs_followup는 불리언입니다. "
                "반드시 category, priority, summary, customer_needs_followup 키를 가진 JSON 객체 하나만 반환하세요."
            ),
        },
        {
            "role": "user",
            "content": (
                "문의: 비밀번호 재설정 메일이 오지 않습니다. "
                "업무를 시작해야 해서 오늘 안에 해결이 필요합니다."
            ),
        },
    ],
    response_format={"type": "json_object"},
    temperature=0,
)

raw = completion.choices[0].message.content
data = json.loads(raw)

try:
    ticket = TicketClassification.model_validate(data)
except ValidationError as exc:
    print("validation failed")
    print(exc)
    raise

print(ticket.model_dump())
```

이 코드가 하는 일은 단순하지만 효과는 큽니다. 모델이 `priority`를 문자열로 내거나, 허용되지 않은 `category`를 반환하거나, `summary`를 비워 두면 예외가 발생합니다. 그 순간 애플리케이션은 실패를 숨기지 않고 드러낼 수 있습니다. 운영에서는 이 동작이 중요합니다. 잘못된 데이터를 조용히 저장하는 것보다, 명시적으로 실패하고 재시도나 폴백 경로로 넘기는 편이 훨씬 안전하기 때문입니다.

Pydantic을 붙이면 후속 코드도 단순해집니다. `ticket.priority`는 이미 정수이고, `ticket.category`는 열거형이며, `ticket.customer_needs_followup`는 불리언입니다. 다운스트림 로직이 일일이 형 변환과 방어 코드를 반복하지 않아도 됩니다.

---

## 실패를 어떻게 다뤄야 하는가

구조화 출력 경로에서 실패는 크게 세 층으로 나뉩니다.

첫 번째는 **API 호출 실패**입니다. 인증 오류, 네트워크 오류, 타임아웃이 여기에 들어갑니다. 이 경우에는 모델 출력 이전 단계에서 실패한 것이므로 일반적인 재시도 정책을 검토하면 됩니다.

두 번째는 **JSON 파싱 실패**입니다. `response_format`를 썼더라도 드물게 빈 문자열이나 비정상 응답을 만날 수 있습니다. 이때는 원문 응답을 로그에 남기고, 재시도 가능한지 판단해야 합니다.

세 번째는 **스키마 검증 실패**입니다. 실전에서는 이 층이 가장 자주 운영 판단을 요구합니다. 문법은 맞지만 필드가 비즈니스 규칙을 어겼기 때문입니다. 예를 들어 `priority=7`은 JSON으로는 문제없지만 업무 규칙에는 맞지 않습니다.

다음처럼 계층을 분리해 두면 로깅이 명확해집니다.

```python
import json
import logging
import os

from groq import Groq
from pydantic import BaseModel, Field, ValidationError
from enum import Enum

class Category(str, Enum):
    billing = "billing"
    account = "account"
    bug = "bug"
    shipping = "shipping"

class TicketClassification(BaseModel):
    category: Category
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=8, max_length=120)
    customer_needs_followup: bool

logger = logging.getLogger(__name__)
client = Groq(api_key=os.environ["GROQ_API_KEY"])

try:
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "고객 문의를 분류하세요. "
                    "category는 billing/account/bug/shipping 중 하나입니다. "
                    "priority는 1~5 정수입니다. "
                    "summary는 8~120자 문자열입니다. "
                    "customer_needs_followup는 불리언입니다. "
                    "반드시 category, priority, summary, customer_needs_followup 키를 가진 JSON 객체 하나만 반환하세요."
                ),
            },
            {
                "role": "user",
                "content": "문의: 결제 승인 후 주문 내역이 보이지 않습니다.",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    raw = completion.choices[0].message.content
    data = json.loads(raw)
    ticket = TicketClassification.model_validate(data)
except json.JSONDecodeError:
    logger.exception("json parse failed")
except ValidationError:
    logger.exception("schema validation failed")
except Exception:
    logger.exception("llm request failed")
```

이 구조가 좋은 이유는 복구 전략도 층별로 달라질 수 있기 때문입니다. 요청 실패는 재시도 대상일 수 있고, JSON 파싱 실패는 프롬프트 개선이나 응답 원문 보존이 필요할 수 있으며, 스키마 실패는 더 엄격한 지시문이나 enum 설명 보강이 필요할 수 있습니다.

---

## 프롬프트보다 계약이 먼저다

구조화 출력 작업을 하다 보면 프롬프트 문구를 계속 손보게 됩니다. 물론 지시문 품질도 중요합니다. 다만 운영 관점에서는 "모델에게 잘 부탁한다"보다 "애플리케이션이 어디서 실패를 잡는가"가 먼저입니다. JSON 모드는 출력 형태를 좁혀 주고, Pydantic은 의미 계약을 강제합니다. 이 두 장치를 갖춘 뒤에야 프롬프트 미세 조정이 의미를 가집니다.

현장에서 특히 유용한 원칙은 세 가지입니다.

- 추출 필드는 작게 시작합니다.
- enum과 범위를 코드에 명시합니다.
- 검증 실패 로그에는 원문 응답을 함께 남깁니다.

필드 수를 한 번에 많이 늘리면 모델과 검증기 둘 다 흔들립니다. 처음에는 정말 필요한 필드만 남기고, 그 계약이 안정화된 뒤 확장하는 편이 좋습니다. 또한 "우선순위가 높다" 같은 자연어 표현보다 `1~5 정수`처럼 코드로 직접 검증 가능한 형태가 운영에 유리합니다.

---

## 마무리

이번 글에서는 구조화 출력을 프로덕션 관점에서 정리했습니다. 핵심은 `response_format={"type": "json_object"}`로 JSON 문법을 좁히고, Pydantic으로 비즈니스 스키마를 다시 검증하는 이중 방어선입니다. 이 패턴을 쓰면 모델 응답은 더 이상 느슨한 문자열이 아니라 애플리케이션 계약의 일부가 됩니다.

앞선 글에서 LLM API의 기본 요청·응답 구조를 익혔다면, 이제부터는 그 응답을 프로그램이 안전하게 소비하는 방향으로 넘어가야 합니다. 다음 주제에서는 이 계약 위에 툴 호출을 올려, 모델이 단순히 답변하는 것을 넘어 함수 실행까지 연결되는 경계를 어떻게 설계하는지 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- **구조화 출력 — JSON 모드와 응답 스키마 (현재 글)**
- 툴 호출 — 함수를 모델에 연결하기 (예정)
- 스트리밍 심화 — 청크 처리와 오류 복구 (예정)
- 캐싱 전략 — 비용과 지연 시간 줄이기 (예정)
- 재시도와 오류 처리 — 안정적인 API 호출 만들기 (예정)
- 속도 제한 관리 — Rate Limit 대응 패턴 (예정)

<!-- toc:end -->

---

## 참고 자료

- <https://console.groq.com/docs/text-chat>
- <https://console.groq.com/docs/text-chat#json-mode>
- <https://docs.pydantic.dev/latest/concepts/models/>

Tags: LLM, OpenAI, Streaming, Python
