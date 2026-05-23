---
title: "API Design 101 (5/10): Request와 response schema"
series: api-design-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Computer Science
  - APIDesign
  - JSON
  - Schema
  - Validation
  - Backend
last_reviewed: '2026-05-15'
seo_description: 요청과 응답 schema를 흔들림 없이 설계하는 기준을 사례와 함께 정리합니다.
---

# API Design 101 (5/10): Request와 response schema

처음에는 JSON 몇 줄만 맞추면 되는 것처럼 보여도, 시간이 지나면 가장 자주 깨지는 부분이 바로 schema입니다. 필드 이름 하나, 날짜 형식 하나, null 허용 여부 하나가 클라이언트 파싱 로직과 데이터 정합성 문제로 바로 이어집니다.

여기서는 schema를 단순 문서 항목이 아니라 경계에서 강제해야 할 계약으로 다룹니다. 입력 검증, 응답 직렬화, 시간과 금액 표현을 함께 정리해야 나중에 버전 관리 비용도 줄어듭니다.

![API Design 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/05/05-01-concept-at-a-glance.ko.png)
*API Design 101 5장 흐름 개요*

## 먼저 던지는 질문

- JSON과 content type은 어떤 식으로 계약에 들어갈까요?
- 필드 이름 규칙은 어떻게 정해야 할까요?
- validation은 어디에서, 어떤 방식으로 해야 할까요?

## 왜 중요한가

schema가 흔들리면 클라이언트도 함께 흔들립니다. 좋은 schema는 읽기 쉽고, 시간이 지나도 진화하기 쉽습니다. 경계에서 validation을 해 두면 내부 코드도 훨씬 깨끗하게 유지할 수 있습니다.

> schema는 데이터의 문법입니다.

## 한눈에 보는 개념

Schema 설계는 네 가지 영역을 다룹니다:

1. **필드 이름 규칙**: snake_case vs camelCase, 읽어서 의미가 통하는 이름
2. **타입과 값 제약**: 문자열 길이, 숫자 범위, enum 허용값, null 허용 여부
3. **시간/금액 표현**: UTC + ISO 8601, 정수 minor-unit
4. **입출력 분리**: 요청에는 `id`가 없지만 응답에는 있음, 내부 필드는 응답에 노출 안 함

| 구성 요소 | 역할 | 예시 |
|----------|------|------|
| Content-Type 헤더 | 본문 형식 명시 | `application/json` |
| Request schema | 입력 검증 기준 | `{"username": str, "email": str}` |
| Response schema | 출력 계약 | `{"id": int, "username": str, "created_at": str}` |
| Validation layer | schema 강제 지점 | Pydantic, marshmallow, JSON Schema |

이 분리가 선명해야 handler가 비즈니스 로직에 집중할 수 있습니다. 경계 검증이 약하면 예외 처리, 기본값 보정, 타입 변환이 서비스 코드 곳곳으로 흩어지기 시작합니다.

## 핵심 용어

| 용어 | 정의 | 예시 |
|------|------|------|
| Schema | 데이터의 구조·타입·제약을 정의한 문서 | Pydantic model, JSON Schema |
| Content-Type | HTTP 본문의 표현 형식 | `application/json`, `multipart/form-data` |
| Validation | 입력이 schema를 만족하는지 검사 | 필수 필드 누락 → 400 |
| Serialization | 내부 객체를 외부 JSON으로 변환 | ORM model → response dict |
| Deserialization | 외부 JSON을 내부 객체로 변환 | request body → Pydantic model |
| ISO 8601 | 날짜/시간 표준 형식 | `2026-05-04T12:00:00Z` |
| Minor unit | 소수점 없는 정수 금액 | 1.99 USD = 199 cents |
| Envelope | 응답을 감싸는 공통 구조 | `{"data": ..., "meta": {...}}` |

## 전후 비교

**Before (자유 형식, 의미 불명)**

```json
{"u": "Y", "ct": 1714800000, "act": "ok", "bal": 19.99}
```

문제점:
- `u`가 username인지 user_id인지 알 수 없습니다.
- `ct`가 Unix timestamp인지 다른 값인지 문맥 없이 모릅니다.
- `bal: 19.99`는 float이라 반올림 오차가 누적됩니다.
- 어떤 필드가 필수이고 어떤 필드가 optional인지 알 수 없습니다.

**After (의미가 드러나는 schema)**

```json
{
  "username": "yeongseon",
  "created_at": "2026-05-04T12:00:00Z",
  "active": true,
  "balance_cents": 1999,
  "currency": "USD"
}
```

필드명만 읽어도 데이터의 의미와 단위가 명확합니다.

## 실습: schema를 따라가는 다섯 단계

### 단계 1 — JSON 본문과 헤더

```python
# 1_json.py
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.post("/echo")
def echo():
    if request.headers.get("Content-Type") != "application/json":
        return jsonify(error="json required"), 415
    return jsonify(request.get_json())
```

서버는 content type을 직접 확인해야 합니다.

### 단계 2 — 검증 라이브러리
```python
# 2_validate.py
from pydantic import BaseModel, Field
class CreateUser(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: str
```

Pydantic이나 marshmallow 같은 도구는 schema를 코드로 표현하게 해 줍니다.

### 단계 3 — 응답 스키마 분리
```python
# 3_response.py
from pydantic import BaseModel
class UserOut(BaseModel):
    id: int
    username: str
    created_at: str   # ISO 8601 string
```

입력과 출력은 다른 schema입니다. `In`과 `Out`으로 분리하는 관례가 널리 쓰입니다.

### 단계 4 — 날짜와 시간대

```python
# 4_time.py
from datetime import datetime, timezone
now = datetime.now(timezone.utc).isoformat()
print(now)   # "2026-05-04T12:00:00+00:00"
```

시간은 UTC와 ISO 8601로 저장하고 전송하는 편이 가장 안전합니다.

클라이언트가 `2026-05-04T12:00:00Z`처럼 타임존 오프셋을 포함한 문자열을 받으면, 표시할 때 사용자의 로컬 시간대로 변환하면 됩니다. 서버 쪽에서는 항상 UTC 기준으로 정렬과 비교를 수행하므로, 시간대 변환으로 인한 버그를 원천 차단할 수 있습니다.

### 단계 5 — 금액과 숫자 표현

```python
# 5_money.py
# 돈: 정수 소수 단위 — 1.99 USD = 199센트
amount_cents = 1999
currency = "USD"

# 응답 예시
response = {
    "amount": 1999,
    "currency": "USD",
    "display": "$19.99"  # 표시용은 별도 필드로
}
```

float를 쓰면 `0.1 + 0.2 = 0.30000000000000004` 같은 오차가 누적됩니다. Stripe, Shopify 등 금융 API는 모두 정수 minor-unit을 씁니다.

**필드 이름 규칙 정리:**

| 규칙 | 설명 | 예시 |
|------|------|------|
| snake_case | JSON 표준은 없지만 Python/Ruby 생태계 표준 | `created_at`, `user_id` |
| camelCase | JavaScript 생태계 표준 | `createdAt`, `userId` |
| 하나만 선택 | 한 API 내에서 섞어 쓰지 않음 | 전체 snake_case 또는 전체 camelCase |
| 단위 포함 | 숫자 필드는 단위를 이름에 넣음 | `timeout_ms`, `balance_cents` |
| boolean 접두사 | is/has/can으로 시작 | `is_active`, `has_password` |

## 이 코드에서 봐야 할 점

- validation과 handler가 분리되어 있습니다.
- 입력 schema와 출력 schema가 다릅니다.
- 시간은 UTC, 금액은 정수입니다.

## 자주 하는 실수 다섯 가지

1. **validation을 handler 안에 넣습니다.** 코드가 지저분해지고 같은 검사가 반복됩니다.
2. **내부 모델을 그대로 응답으로 반환합니다.** 내부 변경이 외부 파괴로 이어집니다.
3. **시간대를 무시합니다.** 클라이언트마다 시간을 다르게 해석합니다.
4. **금액에 float를 씁니다.** 사소한 반올림 오차가 실제 금액 오류가 됩니다.
5. **필드 이름을 지나치게 줄입니다.** 몇 달 뒤에는 읽는 사람도 뜻을 모르게 됩니다.

## 실무에서는 이렇게 드러납니다

### FastAPI의 schema 자동화

```python
# fastapi_schema.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI()

class UserCreate(BaseModel):  # 입력 schema
    username: str = Field(min_length=3, max_length=32)
    email: str

class UserResponse(BaseModel):  # 출력 schema
    id: int
    username: str
    created_at: datetime

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(body: UserCreate):
    # FastAPI가 자동으로:
    # 1) 요청 본문을 UserCreate로 검증
    # 2) 실패 시 422 + 상세 에러 반환
    # 3) 응답을 UserResponse로 직렬화
    ...
```

schema를 코드로 정의하면 문서(OpenAPI), 검증, 타입 안전성이 동시에 해결됩니다.

### Envelope 패턴

```json
{
  "data": {"id": 42, "username": "yeongseon"},
  "meta": {"request_id": "req_abc123", "timestamp": "2026-05-04T12:00:00Z"}
}
```

목록 응답에서는 pagination 정보를 `meta`에 담습니다:

```json
{
  "data": [{"id": 1}, {"id": 2}],
  "meta": {"total": 100, "page": 1, "per_page": 20}
}
```

이 패턴을 쓰면 본래 단일 객체였던 응답에 나중에 메타데이터를 추가해도 breaking change가 되지 않습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **경계의 첫 줄에 schema를 둡니다.** handler가 validation 코드로 시작하면 비즈니스 로직이 묻힙니다. Pydantic/marshmallow 같은 도구로 경계에서 끝냅니다.
- **입력은 엄격하게, 출력은 진화 가능하게 설계합니다.** 입력에 알 수 없는 필드가 들어오면 거부하고, 출력에 필드를 추가해도 기존 클라이언트가 깨지지 않게 만듭니다.
- **시간과 금액은 표준 형식만 사용합니다.** UTC ISO 8601, 정수 minor-unit. 예외를 만들면 클라이언트마다 변환 로직을 들고 갑니다.
- **기존 필드의 의미를 바꾸지 않고 새 필드를 추가합니다.** `status: "active"`의 의미를 다른 것으로 바꾸면 breaking change입니다. 대신 `account_status`를 추가합니다.
- **클라이언트가 모르는 필드를 무시할 수 있게 설계합니다.** 응답에 필드가 추가되어도 기존 클라이언트가 에러 없이 동작해야 합니다 (forward compatibility).

## 검증 포인트와 실패 신호

- **Expected output:** 잘못된 `Content-Type`은 `415`, 필수 필드 누락은 검증 에러, 정상 데이터는 예측 가능한 JSON 구조로 돌아와야 합니다.
- **First check:** 응답 예제에 내부 ORM 필드나 임시 축약어가 그대로 보이면 입력·출력 schema 분리가 약한 상태입니다.
- **Failure mode:** 시간대와 금액 표현을 초기에 통일하지 않으면, 이후 분석 파이프라인과 프런트엔드 포맷터가 각자 보정 로직을 들고 가게 됩니다.

## 체크리스트

- [ ] 모든 endpoint에 입력 schema가 있는가?
- [ ] 응답 schema가 입력 schema와 분리되어 있는가?
- [ ] timestamp가 UTC + ISO 8601인가?
- [ ] 금액을 정수 minor unit으로 표현하는가?
- [ ] 필드 이름이 읽어서 이해 가능한 수준인가?

## 연습 문제

1. 가장 자주 쓰는 응답 구조를 Pydantic 모델로 표현해 보세요.
2. 실수로 KST로 저장된 데이터를 UTC 기준으로 되돌리는 마이그레이션 전략을 적어 보세요.
3. 입력 schema에서 알 수 없는 필드를 거부할지 무시할지 정하고 그 trade-off를 써 보세요.

## 정리와 다음 글

schema는 데이터의 문법입니다. 다음 글에서는 거의 모든 목록 API가 마주치는 주제인 pagination과 filtering을 다룹니다.

## 팀 운영 관점의 보강: 설계 결정이 배포 후 어떻게 드러나는가

문서에서 맞아 보이던 선택이 운영에서 실패하는 이유는 대부분 관측 지점이 없기 때문입니다. 그래서 설계 단계에서 아래 세 가지를 같이 준비해야 합니다.

### 1) 요청 식별자 전파

```http
X-Request-Id: req_01JY2J5YQ6KZ5K6J2M2X5A7N8V
Traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

게이트웨이, API 서버, 비동기 워커가 같은 식별자를 공유하면 장애 분석 시간이 급격히 줄어듭니다. 한 서비스에서만 생성하는 방식보다 ingress에서 시작해 하위 호출로 전달하는 방식이 안정적입니다.

### 2) 상태 코드별 SLI 분해

- 성공률 SLI는 `2xx / 전체`로 단순 계산하지 않습니다.
- 사용자 실수로 발생한 `4xx`와 시스템 결함인 `5xx`를 분리합니다.
- `429` 비율은 과부하 지표이므로 별도 대시보드로 관리합니다.
- `p95` 지연 시간은 endpoint 단위로 분리해 봅니다.

이 분해가 없으면 "에러율 2%" 같은 숫자가 문제를 가립니다. 실제로는 인증 만료 폭증일 수도 있고, 특정 엔드포인트 DB 락일 수도 있습니다.

### 3) 롤아웃 가드레일

```yaml
rollout:
  strategy: canary
  steps:
    - percent: 5
      duration: 10m
    - percent: 25
      duration: 20m
    - percent: 100
  abort_if:
    error_rate_5xx: "> 1.0%"
    p95_latency_ms: "> 450"
    rate_limit_429: "> 3.0%"
```

버전 변경이나 스키마 확장은 배포 전략 없이는 안전하게 실행되지 않습니다. 특히 클라이언트 수가 많은 API는 한 번의 전면 배포보다 단계적 확대와 자동 중단 조건이 필수입니다.

### 실무 판단 기준

- 설계 변경 제안서에 "호환성 영향" 항목이 없으면 검토를 보류합니다.
- 신규 필드는 nullable로 추가하고, 필수화는 다음 메이저 버전에서 수행합니다.
- 응답 키 이름 변경은 alias 유지 기간을 명시합니다.
- 폐기 예정 항목은 최소 2개 릴리스 전부터 경고 헤더를 노출합니다.

이 원칙을 문서에 포함해 두면, 구현자와 소비자가 같은 시간표를 공유하게 됩니다. 그 결과 API 변경이 이벤트가 아니라 일상적인 운영 절차로 전환됩니다.

## 스키마 변경 관리 규칙

스키마 품질은 "현재 맞는가"보다 "다음 변경에도 안전한가"로 결정됩니다. 실무에서는 필드 추가, nullable 전환, enum 확장 같은 non-breaking 변경을 우선하고, 필드 삭제는 deprecation 기간을 거친 뒤 메이저 버전에서 수행합니다. 응답 예제를 같이 유지하면 SDK 생성기와 수동 구현이 같은 계약을 따르게 됩니다.

```json
{
  "change_policy": {
    "add_field": "allowed",
    "remove_field": "deprecated_for_2_releases_then_major",
    "enum_extension": "allowed_with_unknown_fallback",
    "required_field_addition": "major_version_only"
  }
}
```

이 규칙을 문서화해 두면 "왜 이 필드를 지금은 지우지 않는가" 같은 의사결정을 개인 취향이 아니라 팀 정책으로 설명할 수 있습니다.

## 처음 질문으로 돌아가기

- **JSON과 content type은 어떤 식으로 계약에 들어갈까요?**
  - Content-Type 헤더로 본문 형식을 명시하고, 서버는 이를 검증합니다. `application/json`이 아니면 415를 반환하고, Accept 헤더로 클라이언트가 원하는 응답 형식도 협상합니다.
- **필드 이름 규칙은 어떻게 정해야 할까요?**
  - snake_case 또는 camelCase 중 하나를 선택해서 API 전체에 일관 적용합니다. 숫자 필드에는 단위를 이름에 포함하고(`timeout_ms`, `balance_cents`), boolean은 `is_`/`has_` 접두사로 의미를 명확히 합니다.
- **validation은 어디에서, 어떤 방식으로 해야 할까요?**
  - handler 진입 전에, schema 라이브러리(Pydantic, marshmallow)로 경계에서 강제합니다. 실패 시 400/422를 반환하고, handler 안에 validation 코드를 섞지 않습니다. schema가 곶 문서이자 검증이자 타입 정의입니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST 기본](./02-rest-basics.md)
- [API Design 101 (3/10): 리소스 설계](./03-resource-design.md)
- [API Design 101 (4/10): HTTP method와 status code](./04-http-methods-and-status.md)
- **Request와 response schema (현재 글)**
- Pagination과 filtering (예정)
- Error response 설계 (예정)
- OpenAPI와 Swagger (예정)
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [JSON Schema](https://json-schema.org/)
- [pydantic Documentation](https://docs.pydantic.dev/)
- [ISO 8601 Date and Time Format](https://en.wikipedia.org/wiki/ISO_8601)
- [Stripe API: Working with Money](https://stripe.com/docs/currencies)

Tags: Computer Science, APIDesign, JSON, Schema, Validation, Backend
