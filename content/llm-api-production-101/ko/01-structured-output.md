---
episode: 1
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
title: "LLM API Production 101 (1/6): 구조화 출력 — JSON 모드와 응답 스키마"
seo_description: JSON 모드와 Pydantic 검증으로 LLM 응답을 운영 가능한 데이터 계약으로 바꾸는 방법을 다룹니다.
---

# LLM API Production 101 (1/6): 구조화 출력 — JSON 모드와 응답 스키마

LLM API를 처음 운영 경로에 올리면 많은 팀이 모델 답변의 품질부터 걱정합니다. 그런데 실제로 더 먼저 터지는 문제는 답변의 내용보다 형태입니다. 데모에서는 보기 좋은 문단 하나면 충분하지만, 서비스는 필드 이름과 타입이 고정된 응답을 원합니다. 데이터베이스에 넣어야 하고, 다른 서비스에 넘겨야 하며, 후속 로직이 그 응답을 분기 조건으로 사용하기 때문입니다.

초기 구현은 대개 단순해 보입니다. 프롬프트에 “JSON으로 반환하세요”라고 쓰고, 응답 문자열에 `json.loads()`를 적용합니다. 짧은 테스트에서는 잘 돌아가는 것처럼 보입니다. 하지만 프롬프트가 길어지고 예외 케이스가 늘어나면 모델이 설명 문장을 앞에 붙이거나, 코드 펜스를 씌우거나, 키 이름을 바꾸는 순간부터 문제가 시작됩니다.

이 실패는 모델이 멍청해서 생기는 문제가 아닙니다. 텍스트 생성과 애플리케이션 로직 사이에 명시적인 계약이 없어서 생기는 문제입니다. 사람이 읽기 좋은 응답과 프로그램이 안전하게 소비할 수 있는 응답은 같은 것이 아닙니다. 운영에서는 후자가 먼저 확보되어야 합니다.

이 글은 그 느슨한 경계를 계약으로 바꾸는 방법을 다룹니다. Groq의 JSON 모드로 응답 형태를 좁히고, Pydantic으로 의미 규칙까지 검증해 “그럴듯한 텍스트”를 “실패 가능성이 명확한 데이터 경로”로 바꾸겠습니다.

여기서는 JSON 모드와 응답 스키마를 이용해 구조화 출력 계약을 만드는 방법을 봅니다.

![구조화 출력: JSON 모드와 응답 스키마](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-01-structured-output-json-mode-and-response.ko.png)
*구조화 출력: JSON 모드와 응답 스키마*
> 프로덕션의 구조화 출력은 모델에게 예쁘게 말하게 하는 문제가 아니라, 애플리케이션이 신뢰할 수 있는 실패 경계를 만드는 문제입니다.

## 먼저 던지는 질문

- 자유 형식 텍스트 파싱은 운영 환경에서 왜 금방 깨질까요?
- JSON 모드는 무엇을 보장하고, 스키마 검증은 무엇을 따로 보장할까요?
- 구조화 출력 계약이 깨졌을 때 어디서 멈추고 무엇을 기록해야 할까요?

## 왜 이 글이 중요한가

구조화 출력은 LLM 애플리케이션의 자동화를 여는 첫 관문입니다. 응답을 사람이 읽기만 한다면 문장 품질이 중요하겠지만, 응답을 다른 코드가 즉시 소비해야 한다면 형식 안정성이 더 중요합니다. 분류, 추출, 후속 API 호출, 비즈니스 규칙 적용은 모두 구조가 안정적이라는 전제 위에서만 안전하게 작동합니다.

현업에서는 이 경계를 프롬프트 요령으로 버티려는 시도를 자주 봅니다. “정확히 JSON으로 답하라”는 문구를 더 길게 쓰고, 실패하면 파서를 조금 더 복잡하게 붙입니다. 하지만 이 방식은 문제를 해결하는 것이 아니라 프롬프트와 후처리 코드 사이에 책임을 흩뿌리는 일에 가깝습니다. 운영에서 필요한 것은 더 영리한 문자열 파싱이 아니라 더 명확한 계약입니다.

JSON 모드와 스키마 검증을 함께 쓰면 실패가 조용히 지나가지 않습니다. 파싱이 안 되면 파싱 계층에서, 의미가 안 맞으면 검증 계층에서 바로 멈춥니다. 이 명시성이 있어야 재시도, 폴백, 로깅, 회귀 테스트도 설계할 수 있습니다.

## 핵심 개념

### 왜 자연어 파싱은 오래 버티지 못하는가

![자연어 응답이 계약 없이 깨지는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-01-why-plain-text-parsing-does-not-age-well.ko.png)

*자연어 응답이 계약 없이 깨지는 흐름*

초기 구현은 종종 짧고 매끈해 보입니다. 하지만 그 매끈함은 계약이 빠져 있다는 뜻이기도 합니다. 아래 코드는 짧지만, 출력 형식이 조금만 바뀌어도 바로 깨집니다.

```python
raw_text = "positive, confidence=0.91"
label, confidence = raw_text.split(",")
```

이 패턴의 문제는 분명합니다. 필드 이름 안정성, 값 타입 안정성, 누락 데이터 실패 처리가 모두 코드 밖에 흩어져 있습니다. 운영에서는 이 규칙을 프롬프트와 문자열 파서에 나눠 두지 말고, 하나의 계약으로 모아야 합니다.

### JSON 모드가 보장하는 것과 보장하지 않는 것

![JSON 모드와 스키마 검증의 책임 경계](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-02-what-json-mode-guarantees-and-what-it-do.ko.png)

*JSON 모드와 스키마 검증의 책임 경계*

Groq의 `response_format={"type": "json_object"}`는 모델을 JSON 객체 쪽으로 강하게 유도합니다. 이 덕분에 문자열 수술 없이 파싱 가능한 응답을 받을 가능성이 커집니다. 다만 JSON 문법이 맞는다고 해서 비즈니스 의미까지 맞는 것은 아닙니다.

```json
{
  "sentiment": "positive",
  "confidence": "high"
}
```

위 응답은 문법적으로는 유효하지만 `confidence`가 숫자가 아니라 문자열입니다. 그래서 실제 경로는 두 단계로 나뉘어야 합니다. 먼저 JSON 객체를 받게 만들고, 그다음 그 객체가 애플리케이션 스키마와 일치하는지 확인해야 합니다.

### Groq SDK로 JSON 모드 요청 보내기

![JSON 모드 요청과 응답 파싱 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-03-sending-a-json-mode-request-with-the-gro.ko.png)

*JSON 모드 요청과 응답 파싱 흐름*

아래 예제는 고객 지원 문의에서 `category`, `priority`, `summary`를 추출합니다. 코드 블록은 그대로 복사해 실행할 수 있도록 영어 원문을 유지했습니다.

```python
import json
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

messages = [
    {
        "role": "system",
        "content": (
            "You classify customer support tickets. "
            "category must be one of billing/account/bug/shipping. "
            "priority must be an integer from 1 to 5. "
            "summary must be a string between 8 and 120 characters. "
            "Return exactly one JSON object with the keys category, priority, and summary."
        ),
    },
    {
        "role": "user",
        "content": (
            "Ticket: payment succeeded but the order is missing from my order history. "
            "I do not want a refund yet. I need the status checked quickly."
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

<!-- injected-output:start -->
**실행 결과**

    {'category': 'billing', 'priority': 3, 'summary': 'Order missing from order history after successful payment'}

<!-- injected-output:end -->

여기서 눈여겨볼 점은 세 가지입니다. 프롬프트 안에서도 JSON 객체 하나를 반환하라고 다시 적어 계약을 읽기 쉽게 만들었다는 사실, `temperature=0`으로 변동성을 줄였다는 사실, 그리고 `json.loads()`는 파싱만 할 뿐 의미 검증은 하지 않는다는 사실입니다.

### Pydantic으로 응답을 잠그기

![모델 출력과 검증기 구조의 관계](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-04-locking-the-response-with-pydantic.ko.png)

*모델 출력과 검증기 구조의 관계*

이제 JSON 문자열을 애플리케이션 타입으로 바꿉니다. 이 단계부터 구조화 출력은 실제 운영 경계가 됩니다.

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
                "Classify the support request. "
                "category must be one of billing/account/bug/shipping. "
                "priority must be an integer from 1 to 5. "
                "summary must be a string between 8 and 120 characters. "
                "customer_needs_followup must be a boolean. "
                "Return exactly one JSON object with the keys category, priority, summary, and customer_needs_followup."
            ),
        },
        {
            "role": "user",
            "content": (
                "Ticket: password reset emails never arrive. "
                "I need access restored today because work is blocked."
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

<!-- injected-output:start -->
**실행 결과**

    {'category': <Category.bug: 'bug'>, 'priority': 5, 'summary': 'Password reset emails not arriving, urgent access restoration needed', 'customer_needs_followup': True}

<!-- injected-output:end -->

검증이 붙는 순간 응답 경계가 강해집니다. 허용되지 않은 카테고리, 잘못된 타입, 누락 필드가 모두 즉시 실패합니다. 운영에서는 조용한 오염보다 시끄러운 실패가 훨씬 안전합니다.

### 실패를 계층으로 나눠 보기

![구조화 출력 실패 계층과 복구 경로](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/01/01-05-thinking-in-failure-layers.ko.png)

*구조화 출력 실패 계층과 복구 경로*

실패를 요청 계층, JSON 파싱 계층, 스키마 검증 계층으로 나누면 로그와 복구 정책이 선명해집니다.

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
                    "Classify the support request. "
                    "category must be one of billing/account/bug/shipping. "
                    "priority must be an integer from 1 to 5. "
                    "summary must be a string between 8 and 120 characters. "
                    "customer_needs_followup must be a boolean. "
                    "Return exactly one JSON object with the keys category, priority, summary, and customer_needs_followup."
                ),
            },
            {
                "role": "user",
                "content": "Ticket: payment was approved but the order is missing.",
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

이렇게 분리해 두면 요청 실패는 재시도 대상으로, JSON 파싱 실패는 원문 보존과 프롬프트 재검토 대상으로, 스키마 실패는 계약 단순화나 필드 정의 보강 대상으로 각각 다르게 다룰 수 있습니다.

### 검증 실패를 일부러 재현해 보기

운영에서 도움이 되는 테스트는 성공 예제 하나로 끝나지 않습니다. 계약이 깨졌을 때 어떤 로그와 예외가 나오는지도 같이 확인해야 합니다. 아래 코드는 모델 호출 없이도 스키마 검증 실패를 재현합니다.

```python
from enum import Enum

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

invalid_payload = {
    "category": "refund",
    "priority": 9,
    "summary": "short",
    "customer_needs_followup": "later",
}

try:
    TicketClassification.model_validate(invalid_payload)
except ValidationError as exc:
    print(exc)
```

<!-- injected-output:start -->
**실행 결과**

    3 validation errors for TicketClassification
    category
      Input should be 'billing', 'account', 'bug' or 'shipping'
    priority
      Input should be less than or equal to 5
    summary
      String should have at least 8 characters

<!-- injected-output:end -->

이 출력이 중요한 이유는 장애 분류 기준을 바로 코드화할 수 있기 때문입니다. enum 위반인지, 범위 위반인지, 문자열 길이 문제인지가 명확하게 드러나므로 재시도 대신 계약 보강이나 프롬프트 축소로 방향을 바로 잡을 수 있습니다. 회귀 테스트에는 이런 실패 payload를 일부러 포함하는 편이 훨씬 안전합니다.

### 함수 호출 인자도 같은 스키마 계층으로 검증하기

구조화 출력 글에서 자주 놓치는 지점이 하나 있습니다. 모델이 바로 사용자 답변을 만드는 경로뿐 아니라, 다음 단계에서 함수 호출 인자를 만드는 경로도 결국 같은 계약 문제라는 사실입니다. 즉 `response_format`으로 받은 JSON을 검증하는 것과 `tool_calls`의 `arguments`를 검증하는 것은 다른 기술이 아니라 같은 원칙의 반복입니다.

아래 예제는 주문 조회 함수 인자를 Pydantic으로 검증하는 패턴을 보여 줍니다. 글의 주제는 구조화 출력이지만, 실제 운영에서는 이 경계가 곧바로 툴 호출 단계로 이어지므로 함께 이해하는 편이 안전합니다.

```python
import json
from enum import Enum

from pydantic import BaseModel, Field, ValidationError

class Locale(str, Enum):
    ko = "ko"
    en = "en"

class OrderLookupArgs(BaseModel):
    order_id: str = Field(min_length=6, max_length=32)
    include_history: bool = False
    locale: Locale = Locale.ko

raw_tool_arguments = '{"order_id":"ORD-1001","include_history":true,"locale":"ko"}'

try:
    args_dict = json.loads(raw_tool_arguments)
    args = OrderLookupArgs.model_validate(args_dict)
    print(args.model_dump())
except json.JSONDecodeError as exc:
    print("tool args json parse failed", exc)
except ValidationError as exc:
    print("tool args schema validation failed", exc)
```

이 패턴의 장점은 명확합니다. 함수 구현 본문은 이미 검증된 타입만 받는다는 가정으로 단순해지고, 실패는 호출 전 단계에서 일관되게 멈춥니다. 결과적으로 구조화 출력 계약은 “모델 답변 파싱”을 넘어서 “실행 경계 검증”까지 확장됩니다.

### 응답 계약 버전 관리: 스키마를 바꾸면 키도 바꾼다

운영에서 자주 발생하는 사건은 필드 추가입니다. 예를 들어 `summary`만 쓰다가 `root_cause`를 새로 추가하면, 새 코드와 옛 응답이 같은 경로에서 섞일 수 있습니다. 이때는 프롬프트만 바꾸는 대신 응답 계약 버전을 명시적으로 올려야 합니다.

```python
from pydantic import BaseModel, Field

class TicketClassificationV2(BaseModel):
    schema_version: str = "v2"
    category: str
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=8, max_length=120)
    root_cause: str = Field(min_length=3, max_length=200)

def build_contract_context() -> dict:
    return {
        "schema_version": "v2",
        "allowed_categories": ["billing", "account", "bug", "shipping"],
    }
```

버전 필드는 사소해 보이지만 운영 사고를 줄이는 데 크게 기여합니다. 로그에서 어떤 계약으로 생성된 응답인지 즉시 식별할 수 있고, 캐시 키나 테스트 fixture도 버전 단위로 분리할 수 있습니다. 특히 구조화 출력이 여러 서비스로 전달되는 경우에는 이 버전 필드가 사실상 호환성의 기준점이 됩니다.

### 구조화 출력 품질을 수치로 보는 회귀 테스트

운영 품질을 안정적으로 유지하려면 “이번 배포에서 스키마 실패율이 올랐는가”를 숫자로 볼 수 있어야 합니다. 아래처럼 샘플 입력 묶음을 고정해 두고 통과율을 계산하면 프롬프트 변경이나 모델 교체의 영향을 빠르게 파악할 수 있습니다.

```python
import json
from dataclasses import dataclass

from pydantic import BaseModel, Field, ValidationError

class TicketClassification(BaseModel):
    category: str
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=8, max_length=120)

@dataclass
class EvalCase:
    name: str
    raw_json: str

cases = [
    EvalCase("valid", '{"category":"bug","priority":4,"summary":"Password reset mail is missing"}'),
    EvalCase("bad-priority", '{"category":"bug","priority":9,"summary":"Password reset mail is missing"}'),
    EvalCase("bad-json", '{"category":"bug","priority":4,"summary":"oops"'),
]

passed = 0
for case in cases:
    try:
        payload = json.loads(case.raw_json)
        TicketClassification.model_validate(payload)
        passed += 1
    except (json.JSONDecodeError, ValidationError):
        pass

print({"total": len(cases), "passed": passed, "pass_rate": round(passed / len(cases), 2)})
```

이 테스트는 모델 품질 평가를 대체하지는 않지만, 계약 안정성의 하한선을 지켜 줍니다. 특히 시리즈의 다음 단계인 툴 호출과 결합하면 “도구 실행 전 스키마 통과율”이라는 더 직접적인 운영 지표로 확장할 수 있습니다.

## 흔히 헷갈리는 지점

- JSON 모드를 켰다고 해서 비즈니스 규칙까지 자동으로 보장되는 것은 아닙니다.
- `json.loads()` 성공은 스키마 검증 성공과 같은 뜻이 아닙니다.
- 구조화 출력 문제를 프롬프트 문구만 손봐서 해결하려 하면 장애 원인이 더 흐려집니다.
- enum, 범위, 필수 필드 같은 규칙은 프롬프트 설명보다 코드 검증에 먼저 있어야 합니다.
- 검증 실패를 “모델 품질 문제”로만 보면 로깅과 복구 계층 설계가 늦어집니다.

## 운영 체크리스트

- [ ] Pydantic 모델 또는 JSON Schema로 출력 구조를 명시했다
- [ ] 스키마 위반 시 로깅과 재시도 기준을 분리했다
- [ ] enum, 범위, 필수 여부를 코드 검증 계층에 반영했다
- [ ] 검증 실패 시 원문 응답을 추적 가능하게 남겼다
- [ ] 샘플 입력 기반 회귀 테스트로 스키마 변경 영향을 확인했다

## 정리

이번 글에서는 구조화 출력을 프롬프트 요령이 아니라 응답 계약으로 다뤘습니다. `response_format={"type": "json_object"}`는 출력의 구문 형태를 좁혀 주고, Pydantic은 그 출력이 애플리케이션 규칙을 만족하는지 검사합니다. 이 둘이 함께 있어야 문자열 파싱에 기대던 경로를 운영 가능한 데이터 경계로 바꿀 수 있습니다.

중요한 것은 실패가 더 이상 애매하지 않다는 사실입니다. 파싱이 실패했는지, JSON은 맞지만 스키마가 틀렸는지, 요청 자체가 실패했는지가 계층별로 드러납니다. 이 차이가 있어야 재시도 정책, 폴백 설계, 품질 로그가 모두 현실적인 형태를 갖습니다.

시리즈의 다음 글에서는 이 계약을 함수 실행 요청까지 확장합니다. 구조화 출력이 데이터를 안전하게 받는 방법이었다면, 툴 호출은 그 데이터를 바탕으로 애플리케이션 기능을 안전하게 연결하는 방법입니다.

## 처음 질문으로 돌아가기

- **자유 형식 텍스트 파싱은 운영 환경에서 왜 금방 깨질까요?**
  자연어 응답은 설명 문장, 코드 펜스, 키 이름 변경처럼 작은 변형에도 파서가 흔들리기 때문에 운영 경로에서 오래 버티기 어렵습니다.

- **JSON 모드는 무엇을 보장하고, 스키마 검증은 무엇을 따로 보장할까요?**
  JSON 모드는 파싱 가능한 JSON 객체 쪽으로 출력을 좁히지만, 필수 필드와 값 범위 같은 의미 규칙은 Pydantic 같은 스키마 검증이 맡습니다.

- **구조화 출력 계약이 깨졌을 때 어디서 멈추고 무엇을 기록해야 할까요?**
  파싱 실패와 검증 실패를 나눠 멈추고, 원본 응답·검증 오류·요청 식별자를 남겨 재시도와 폴백을 분리해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **LLM API Production 101 (1/6): 구조화 출력 — JSON 모드와 응답 스키마 (현재 글)**
- LLM API Production 101 (2/6): 툴 호출 — 함수를 모델에 연결하기 (예정)
- LLM API Production 101 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구 (예정)
- LLM API Production 101 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기 (예정)
- LLM API Production 101 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기 (예정)
- LLM API Production 101 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Groq Text Chat docs](https://console.groq.com/docs/text-chat)
- [Groq JSON mode guide](https://console.groq.com/docs/text-chat#json-mode)
- [Pydantic model concepts](https://docs.pydantic.dev/latest/concepts/models/)

### 검증 보조 자료
- [JSON Schema object reference](https://json-schema.org/understanding-json-schema/reference/object)

### 관련 시리즈
- [툴 호출 — 함수를 모델에 연결하기](./02-tool-calling.md)
- [LLM API Production 101 시리즈](../)
- [LLM App Foundations 101](../../llm-app-foundations-101/ko/01-llm-api-first-call.md) — 이 시리즈가 시작되는 지점에 있는 "첫 호출, 토큰, 프롬프트 기초"를 정리합니다. 구조화 출력이나 툴 호출이 어떤 메시지 패턴 위에서 작동하는지가 흐릿하면 한 단계 위로 올라가 읽기를 권장합니다.

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-api-production-101/ko/01-structured-output)

Tags: LLM, OpenAI, Streaming, Python
