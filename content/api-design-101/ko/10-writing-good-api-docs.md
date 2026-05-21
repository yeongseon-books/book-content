---
title: "API Design 101 (10/10): 좋은 API 문서 만들기"
series: api-design-101
episode: 10
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
  - Documentation
  - DeveloperExperience
  - Examples
  - Backend
last_reviewed: '2026-05-15'
seo_description: Getting Started부터 changelog까지, 채택되는 API 문서의 구조를 설명합니다.
---

# API Design 101 (10/10): 좋은 API 문서 만들기

문서가 부족한 API는 기능이 없어서 외면받는 경우보다, 첫 호출까지 가는 길이 너무 길어서 포기되는 경우가 더 많습니다. 팀 안에서는 아는 사람이 구두로 메워 주지만, 외부 사용자는 그 빈칸을 메워 줄 동료가 없기 때문에 문서 품질이 곧 도입 속도가 됩니다.

이 글은 API Design 101 시리즈의 마지막 글입니다.

여기서는 좋은 API 문서를 reference 모음이 아니라 채택 경로 전체로 봅니다. Getting Started, 시나리오 튜토리얼, 예제 중심 reference, changelog, SDK 안내가 어떻게 한 흐름으로 이어져야 하는지 정리합니다.

## 먼저 던지는 질문

- API 문서는 어떤 다섯 축으로 구성하면 좋을까요?
- 사용자가 첫 호출까지 5분 안에 도달하게 하려면 무엇이 필요할까요?
- 예제는 왜 문서의 중심이어야 할까요?

## 큰 그림

![API Design 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/10/10-01-concept-at-a-glance.ko.png)

*API Design 101 10장 흐름 개요*

문서의 다섯 축 — Getting Started, Tutorial, Reference, Changelog, SDK — 이 왼쪽에서 오른쪽으로 이어지며, 사용자가 첫 호출을 성공한 뒤 점차 깊은 문서로 넘어가는 경로를 보여줍니다. Getting Started → Tutorial → Reference는 학습 흐름이고, Changelog와 SDK는 유지·운영 단계에서 반복 참조되는 문서입니다.

> 문서가 좋다는 것은 정보량이 많다는 뜻이 아닙니다. 사용자가 지금 필요한 정보를 최소 클릭으로 찾을 수 있다는 뜻입니다.

## 왜 문서가 채택률을 결정하는가

Stripe가 2016년에 공개한 개발자 설문에서 "API 선택 기준 1위"는 문서 품질이었습니다. 기능이 동일하면 문서가 좋은 쪽을 씁니다. 내부 API도 마찬가지입니다. 문서가 없으면 Slack에 질문이 쌓이고, 온보딩 비용이 사람 수에 비례해서 커집니다.

| 문서 수준 | 첫 호출까지 시간 | 지원 질문 빈도 |
|-----------|-----------------|---------------|
| Getting Started + 예제 있음 | 5분 | 주 0-1건 |
| Reference만 있음 | 30분-1시간 | 주 5-10건 |
| 문서 없음 (코드 읽기) | 반나절 이상 | 매일 |

이 표의 수치는 실측이 아니라 경험적 패턴이지만, 방향은 어디서나 동일합니다. 문서 투자 ROI가 가장 높은 구간은 "없음 → Getting Started 추가"입니다.

## 다섯 축 상세

### 1. Getting Started — 5분 규칙

Getting Started는 사용자가 아무런 사전 지식 없이 따라 했을 때 5분 안에 첫 성공 응답을 보는 것을 목표로 합니다.

필수 요소:
- 인증 정보 획득 방법 (가입 → API key 발급)
- 복사-붙여넣기 가능한 curl 또는 SDK 코드
- 기대 응답 (상태 코드 + body)
- 실패 시 다음 단계 링크

```bash
# Getting Started 예시 — 최소 curl
curl -X GET https://api.example.com/v1/health \
  -H "Authorization: Bearer sk_test_abc123"

# 기대 응답
# HTTP 200
# {"status": "ok", "version": "2026-05-01"}
```

5분 규칙을 검증하는 가장 좋은 방법은 실제로 처음 보는 동료에게 시켜 보는 것입니다. 막히는 곳이 곧 문서의 빈칸입니다.

### 2. Tutorial — 시나리오 기반 가이드

Tutorial은 "이 API로 X를 달성하려면 어떤 순서로 호출하는가"를 보여줍니다. Reference가 사전이라면 Tutorial은 레시피입니다.

좋은 Tutorial의 조건:
- 하나의 구체적 목표 ("결제 수락", "사용자 가입 + 이메일 인증")
- 전체 호출 순서가 번호로 나열됨
- 각 단계에서 기대 응답이 명시됨
- 실패 시나리오와 복구 방법이 포함됨

```text
# Tutorial: Accept Your First Payment

1. POST /v1/customers → customer_id
2. POST /v1/payment_intents {customer_id, amount, currency}
3. Confirm payment (client-side SDK)
4. Listen for payment_intent.succeeded webhook
5. Verify: GET /v1/payment_intents/{id} → status=succeeded
```

### 3. Reference — 예제 중심 사전

Reference는 모든 endpoint, 모든 필드, 모든 에러를 나열합니다. 하지만 이름과 타입만 있는 Reference는 쓸모가 절반입니다. 각 endpoint에 최소 하나의 요청/응답 예제가 있어야 합니다.

```markdown
## 예제 엔드포인트: POST /v1/customers

Creates a new customer.

### Request Body

| field | type   | required | description          |
|-------|--------|----------|----------------------|
| name  | string | yes      | Customer display name |
| email | string | yes      | Unique email address  |

### Example

Request:
  POST /v1/customers
  {"name": "Alice", "email": "alice@example.com"}

Response (201):
  {"id": "cus_abc", "name": "Alice", "email": "alice@example.com", "created_at": "2026-05-20T09:00:00Z"}

### Errors

| code             | status | meaning                  |
|------------------|--------|--------------------------|
| validation_error | 422    | name or email missing    |
| email.duplicate  | 409    | email already registered |
```

### 4. Changelog — 변경 이력

Changelog는 "지난번에 되던 게 왜 안 되지?"를 1분 안에 답하게 해 줍니다.

좋은 Changelog 규칙:
- 역시간순 (최신이 위)
- 변경 분류: BREAKING, ADD, DEPRECATE, FIX
- 영향받는 endpoint 명시
- migration path 링크

```text
# Changelog

## 변경 이력 예시: 2026-05-01 (v2.3.0)
- BREAKING: POST /v1/users — `name` removed. Use `full_name`.
- ADD: GET /v1/users/{id} — `created_at` field added.
- DEPRECATE: /v1/legacy-auth — sunset 2027-01-31.

## 변경 이력 예시: 2026-04-15 (v2.2.0)
- FIX: PATCH /v1/orders — partial update now returns 200 (was 204).
- ADD: rate limit headers (X-RateLimit-Remaining).
```

### 5. SDK와 인터랙티브 환경

SDK는 curl 예제의 "다음 단계"입니다. 사용자가 실제 프로덕션 코드를 작성할 때 쓰는 것은 SDK이므로, Getting Started에서 curl로 성공한 뒤 바로 SDK 예제로 넘어갈 수 있어야 합니다.
```python
# Python SDK 예시
from example_api import Client

client = Client(api_key="sk_test_abc123")
customer = client.customers.create(name="Alice", email="alice@example.com")
print(customer.id)  # cus_abc
```

인터랙티브 환경(Swagger UI, Postman collection, API playground)은 별도 설치 없이 브라우저에서 바로 호출해 볼 수 있게 합니다. 이것은 Getting Started의 마찰을 극한까지 줄이는 도구입니다.

## 문서를 코드와 동기화하는 전략

문서가 코드와 어긋나는 순간 신뢰가 무너집니다. 동기화 전략 세 가지:

| 전략 | 장점 | 단점 |
|------|------|------|
| Code-first (docstring → 자동 생성) | 코드가 진실 | 서술형 설명 부족 |
| Spec-first (OpenAPI → stub + docs) | 계약이 명확 | 초기 셋업 비용 |
| CI 검증 (예제 실행 + link check) | drift 즉시 발견 | CI 시간 증가 |

실무에서는 세 가지를 조합합니다. Reference는 OpenAPI에서 생성하고, Tutorial은 수동으로 쓰되 예제 코드 블록을 CI에서 실제 실행합니다.

```yaml
# GitHub Actions: 예제 코드 검증
- name: Validate doc examples
  run: |
    for f in docs/examples/*.py; do
      python "$f" || exit 1
    done
```

## DX(Developer Experience) 체크리스트

| 항목 | 질문 | 통과 기준 |
|------|------|-----------|
| 발견 | 문서 진입점을 3초 안에 찾을 수 있는가? | 랜딩 페이지에 링크 |
| 첫 성공 | 5분 안에 첫 호출 성공하는가? | Getting Started 존재 |
| 탐색 | 원하는 endpoint를 30초 안에 찾는가? | 검색 + 사이드바 |
| 이해 | 예제를 복사하면 바로 동작하는가? | 실행 가능한 예제 |
| 변경 추적 | 최근 변경을 1분 안에 파악하는가? | Changelog 역시간순 |
| 에러 해결 | 에러 코드로 검색하면 해결법이 나오는가? | 에러별 문서화 |

## 자주 하는 실수와 개선 방향

| 실수 | 왜 문제인가 | 개선 |
|------|------------|------|
| Reference만 있음 | 시작점이 없어서 포기 | Getting Started 추가 |
| 예제가 없거나 오래됨 | 복사해도 실행 안 됨 → 신뢰 붕괴 | CI에서 예제 실행 검증 |
| Changelog 없음 | breaking change에 고객이 장애 | 릴리스마다 changelog 필수화 |
| 에러 미문서화 | 4xx 본문이 비밀 | Reference에 에러 표 포함 |
| 문서가 별도 저장소 | 코드 변경 시 문서 누락 | monorepo 또는 CI link check |
| 인증 설명 분산 | 매 페이지마다 다른 안내 | 인증 전용 페이지 + 일관된 헤더 참조 |
## 실무 사례: Stripe vs 내부 API

**Stripe 문서 구조:**
1. 첫 화면 = Getting Started (API key 발급 → 첫 charge 생성)
2. 시나리오별 Guide (결제, 구독, 환불, 분쟁)
3. 전체 API Reference (좌: 설명, 우: 코드 예제)
4. Changelog (날짜 + 분류 + migration guide 링크)
5. SDK 7개 언어 + Postman collection

**내부 API에서 흔히 빠지는 것:**
- Getting Started ("다 아는 사람끼리니까")
- Changelog ("Slack에 공지했으니까")
- 에러 문서화 ("코드 보면 되니까")

내부라도 팀이 3명을 넘거나 온보딩이 분기 1회 이상이면, 외부 수준 문서가 총 비용을 줄입니다.

## 시니어 엔지니어의 문서 습관

- 문서를 코드와 같은 저장소에 둡니다 — PR 하나에 코드 + 문서가 함께 리뷰됩니다.
- 예제 코드 블록을 CI에서 실행합니다 — 깨진 예제가 머지되지 않습니다.
- Changelog를 PR template에 넣습니다 — "이 변경은 changelog에 해당하나요?" 체크박스.
- 5분 규칙을 분기마다 실측합니다 — 신규 입사자에게 타이머를 돌립니다.
- 가장 많이 방문되는 페이지부터 개선합니다 — analytics가 우선순위를 정합니다.
- 문서 품질을 SLI로 취급합니다 — 지원 티켓 중 "문서에 있었는데 못 찾음" 비율을 추적합니다.

## 연습 문제

1. 현재 프로젝트의 API에 Getting Started가 없다면, 5분 규칙을 만족하는 한 페이지를 작성해 보세요.
2. 가장 많이 호출되는 endpoint 3개에 요청/응답 예제와 에러 표를 추가해 보세요.
3. GitHub Actions에서 `docs/examples/` 디렉터리의 Python 파일을 모두 실행하는 CI step을 만들어 보세요.
4. 최근 3개월의 API 변경 사항을 역시간순 Changelog로 정리해 보세요.

## 정리와 시리즈 마무리

API는 코드가 아니라 경험입니다. 이 시리즈는 첫 글에서 "API는 계약"이라는 출발점을 잡고, REST 원칙, 리소스 설계, HTTP method/status, schema, pagination, error, OpenAPI, versioning을 거쳐 마지막으로 문서까지 왔습니다.

10편을 관통하는 하나의 원칙이 있다면: **사용자(호출자)의 경험을 중심에 두라**는 것입니다. endpoint 이름, 에러 메시지, 버전 정책, 문서 구조 — 모두 "이 API를 처음 쓰는 사람이 가장 빠르게 성공하려면?"이라는 질문에서 답이 나옵니다.

가장 좋은 복습은 작은 API 하나를 처음부터 끝까지 직접 설계하고, 이 시리즈의 체크리스트로 스스로 리뷰해 보는 것입니다.


## 실전 계약 확장: 스펙·예제·운영 신호를 한 번에 맞추기

개념을 이해한 뒤 실제 팀에서 흔들리는 지점은 거의 같습니다. 문장 설명은 충분한데, 요청/응답 예제와 오류 형식, 페이지네이션 규칙, 버전 정책, 레이트 리밋 신호가 문서와 코드에서 따로 놀기 시작하는 순간입니다. 이 절은 그 간극을 줄이기 위해, 어떤 주제의 API 글이든 공통으로 넣어야 하는 실전 앵커를 정리합니다.

### OpenAPI 조각: endpoint 계약을 텍스트가 아니라 스키마로 고정하기

```yaml
openapi: 3.1.0
info:
  title: API Design 101 Example
  version: 1.2.0
paths:
  /v1/orders:
    get:
      summary: 주문 목록 조회
      parameters:
        - in: query
          name: limit
          schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
        - in: query
          name: cursor
          schema: { type: string }
      responses:
        '200':
          description: 조회 성공
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderListResponse'
        '429':
          description: 요청 제한 초과
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
components:
  schemas:
    OrderListResponse:
      type: object
      required: [data, page]
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Order'
        page:
          $ref: '#/components/schemas/PageInfo'
    PageInfo:
      type: object
      required: [has_next]
      properties:
        next_cursor: { type: string, nullable: true }
        has_next: { type: boolean }
    ErrorResponse:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message, trace_id]
          properties:
            code: { type: string, example: RATE_LIMIT_EXCEEDED }
            message: { type: string }
            trace_id: { type: string }
            retryable: { type: boolean, default: false }
```

스키마를 이렇게 고정하면 팀원마다 "대충 이런 형식"으로 기억하던 상태에서 벗어납니다. 특히 `429` 응답처럼 운영에서 자주 만나는 경계 케이스를 spec에 먼저 넣어 두면, 문서·테스트·SDK가 같은 신호를 보게 됩니다.

### 요청/응답 JSON 샘플: 클라이언트가 바로 호출 가능한 수준으로 제시하기

```json
{
  "request": {
    "method": "POST",
    "path": "/v1/orders",
    "headers": {
      "Authorization": "Bearer {ACCESS_TOKEN}",
      "Idempotency-Key": "b7f9f7b8-6cd1-4c9e-9ad0-58ad8e9f45ac",
      "Content-Type": "application/json"
    },
    "body": {
      "customer_id": "cus_2026_001",
      "items": [
        {"product_id": "p-100", "quantity": 2},
        {"product_id": "p-200", "quantity": 1}
      ],
      "currency": "KRW"
    }
  },
  "response": {
    "status": 201,
    "headers": {
      "Location": "/v1/orders/ord_01JXYZ",
      "X-RateLimit-Remaining": "119"
    },
    "body": {
      "id": "ord_01JXYZ",
      "status": "created",
      "total_amount": 54000,
      "currency": "KRW",
      "created_at": "2026-05-21T09:30:00Z"
    }
  }
}
```

실제 소비자는 문장 정의보다 예제를 먼저 읽습니다. 그래서 예제는 "읽기 좋은 형태"가 아니라 "실행 가능한 형태"로 제공해야 합니다. 헤더 이름, 필드 타입, 상태 코드가 모두 들어간 샘플이 있어야 첫 호출 실패율이 내려갑니다.

### 오류 응답 스키마: 디버깅 단서를 일관된 키로 고정하기

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "items[1].quantity must be >= 1",
    "trace_id": "4b6f39e6c4f14f8f9f4aa2f1a7b8c918",
    "retryable": false,
    "details": [
      {
        "field": "items[1].quantity",
        "reason": "min_value",
        "expected": ">= 1",
        "actual": 0
      }
    ]
  }
}
```

`code`와 `trace_id`를 고정하면 운영 중 협업 속도가 크게 올라갑니다. 클라이언트는 `code`로 분기하고, 서버 운영자는 `trace_id`로 로그를 찾습니다. 이 둘이 매번 바뀌면 같은 장애를 두 번 분석하게 됩니다.

### 페이지네이션·필터·정렬: 확장 가능한 쿼리 규칙으로 설계하기

```http
GET /v1/orders?limit=20&cursor=eyJpZCI6Im9yZF8wMUpYWiJ9&status=paid&sort=-created_at
```

```json
{
  "data": [
    {"id": "ord_01JXYZ", "status": "paid", "created_at": "2026-05-20T23:59:20Z"},
    {"id": "ord_01JXYY", "status": "paid", "created_at": "2026-05-20T23:58:02Z"}
  ],
  "page": {
    "next_cursor": "eyJpZCI6Im9yZF8wMUpYWSJ9",
    "has_next": true,
    "limit": 20
  }
}
```

커서 기반 구조를 초기에 잡아 두면 데이터가 커졌을 때도 계약을 바꾸지 않고 버틸 수 있습니다. offset이 당장 단순해 보여도, 쓰기 부하가 높은 시스템에서는 중복/누락 페이지 이슈가 빠르게 드러납니다.

### 레이트 리밋: 숫자와 복구 시점을 같이 전달하기

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1716286500
Content-Type: application/json
```

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Retry after 30 seconds.",
    "trace_id": "f0e8d83a8d8f4d1da8f796f0dfcb66f6",
    "retryable": true
  }
}
```

`429`를 반환하면서 복구 시점을 주지 않으면 클라이언트는 무의미한 재시도를 반복합니다. `Retry-After`와 남은 quota 헤더를 같이 제공해야 트래픽이 안정적으로 회복됩니다.

### 버전 전략: 경로/헤더 정책과 폐기 절차를 함께 운영하기

```http
Deprecation: true
Sunset: Wed, 31 Dec 2026 23:59:59 GMT
Link: </docs/changelog#v1-sunset>; rel="deprecation"
```

버전 표기는 시작일 뿐입니다. 중요한 것은 종료 절차를 예측 가능하게 운영하는 일입니다. 어떤 필드가 언제 사라지는지, 대체 엔드포인트가 무엇인지, SDK 최소 버전이 무엇인지를 changelog와 reference에 동시에 반영해야 실제 마이그레이션이 진행됩니다.

### 구현 체크: 계약 드리프트를 CI에서 차단하기

- OpenAPI lint 실패를 merge 차단 규칙으로 둡니다.
- 스키마 예제 JSON을 contract test 입력으로 재사용합니다.
- `429`, `409`, `422` 같은 경계 응답을 스냅샷 테스트에 포함합니다.
- changelog가 없는 breaking change PR은 리뷰 단계에서 반려합니다.

요약하면, 좋은 API 글의 품질은 설명 문단 길이가 아니라 "코드·문서·운영이 같은 계약을 바라보는가"로 측정됩니다. 이 절의 앵커를 반복적으로 적용하면 시리즈의 어느 장을 읽더라도 독자가 같은 설계 원칙을 재사용할 수 있습니다.


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


## 문서 품질을 측정하는 운영 지표

문서 개선은 감각보다 지표로 관리해야 지속됩니다. 최소한 다음 네 가지를 추적하면 문서 품질이 실제 채택률과 연결되는지 판단할 수 있습니다: 첫 호출 성공률, 첫 성공까지 걸린 시간(Time to First Successful Call), 지원 채널 질문량, changelog 미확인으로 인한 장애 건수. 지표가 없다면 문서는 "많이 썼다"와 "잘 썼다"를 구분하기 어렵습니다.

```yaml
doc_metrics:
  ttfsc_minutes_p50: 4.5
  first_call_success_rate: 0.91
  support_questions_per_week: 3
  change_related_incidents_per_quarter: 1
```

이 숫자를 릴리스 단위로 기록하면 어떤 문서 섹션이 실제로 효과가 있었는지 확인할 수 있고, 다음 분기 투자 우선순위도 명확해집니다.

## 처음 질문으로 돌아가기

- **API 문서는 어떤 다섯 축으로 구성하면 좋을까요?**
  - Getting Started(첫 호출 안내), Tutorial(시나리오 가이드), Reference(endpoint 사전 + 예제), Changelog(변경 이력), SDK/인터랙티브 환경. 이 다섯 축이 사용자의 학습 → 개발 → 유지보수 경로를 빈칸 없이 연결합니다.
- **사용자가 첫 호출까지 5분 안에 도달하게 하려면 무엇이 필요할까요?**
  - 인증 정보 획득 방법, 복사-붙여넣기 가능한 curl 예제, 기대 응답 세 가지가 한 페이지에 있어야 합니다. 추가 설치나 사전 지식 없이 따라 하면 성공하는 구조가 5분 규칙의 핵심입니다.
- **예제는 왜 문서의 중심이어야 할까요?**
  - 개발자는 설명을 읽기 전에 예제를 복사합니다. 예제가 동작하면 신뢰가 생기고, 예제가 깨지면 문서 전체가 의심받습니다. 따라서 예제는 장식이 아니라 문서의 신뢰 기반이며, CI에서 실행 검증까지 해야 가치가 유지됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST 기본](./02-rest-basics.md)
- [API Design 101 (3/10): 리소스 설계](./03-resource-design.md)
- [API Design 101 (4/10): HTTP method와 status code](./04-http-methods-and-status.md)
- [API Design 101 (5/10): Request와 response schema](./05-request-and-response-schema.md)
- [API Design 101 (6/10): Pagination과 filtering](./06-pagination-and-filtering.md)
- [API Design 101 (7/10): Error response 설계](./07-error-response-design.md)
- [API Design 101 (8/10): OpenAPI와 Swagger](./08-openapi-and-swagger.md)
- [API Design 101 (9/10): Versioning](./09-api-versioning.md)
- **좋은 API 문서 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [Stripe Documentation](https://stripe.com/docs)
- [Twilio Documentation](https://www.twilio.com/docs)
- [Write the Docs — API documentation](https://www.writethedocs.org/topic-guides/api-documentation/)
- [Diataxis Framework (tutorials/how-to/reference/explanation)](https://diataxis.fr/)

Tags: Computer Science, APIDesign, Documentation, DeveloperExperience, Examples, Backend
