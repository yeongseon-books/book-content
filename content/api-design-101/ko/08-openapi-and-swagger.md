---
title: "API Design 101 (8/10): OpenAPI와 Swagger"
series: api-design-101
episode: 8
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
  - OpenAPI
  - Swagger
  - Documentation
  - Backend
last_reviewed: '2026-05-15'
seo_description: OpenAPI 3와 Swagger UI로 계약을 문서, 검증, SDK로 연결하는 방법을 설명합니다.
---

# API Design 101 (8/10): OpenAPI와 Swagger

문서가 코드보다 늦게 갱신되기 시작하는 순간, 팀은 문서를 참고하지 않고 직접 호출해 보는 습관을 들이게 됩니다. 그 단계까지 가면 문서는 설명서가 아니라 의심 대상이 되고, SDK와 테스트도 같은 방향으로 어긋납니다.

이 글은 API Design 101 시리즈의 여덟 번째 글입니다.

여기서는 OpenAPI와 Swagger를 문서 도구가 아니라 계약 자동화 체계로 봅니다. 하나의 spec이 validation, 예제, SDK, mock server까지 연결되어야만 단일 진실 원본이라는 말이 실제 운영 습관으로 이어집니다.

## 먼저 던지는 질문

- OpenAPI 3 문서는 어떤 구조로 이루어질까요?
- Swagger UI와 Redoc은 각각 어떤 역할을 할까요?
- code-first와 schema-first는 어떤 차이가 있을까요?

## 큰 그림

![API Design 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/08/08-01-concept-at-a-glance.ko.png)

*OpenAPI spec 하나가 문서, 검증, SDK, mock을 동시에 구동하는 구조*

OpenAPI spec 파일(`openapi.yaml`)을 중심에 두면 여러 산출물이 자동으로 파생됩니다. Swagger UI와 Redoc은 사람이 읽는 문서를 렌더링하고, openapi-generator는 클라이언트 SDK를 생성하며, Prism 같은 도구는 mock server를 띄웁니다. 서버 코드의 request validation도 같은 spec에서 schema를 가져와 적용합니다. 이 모든 것이 하나의 원본에서 나오기 때문에 "문서와 구현이 다른" 문제가 구조적으로 사라집니다.

## OpenAPI란 무엇인가

OpenAPI Specification(OAS)은 REST API의 구조를 기계가 읽을 수 있는 형태로 기술하는 표준입니다. 2015년 SmartBear가 Swagger Specification을 OpenAPI Initiative(Linux Foundation 산하)에 기증하면서 이름이 바뀌었고, 현재 Google, Microsoft, IBM 등이 참여하고 있습니다.

| 용어 | 의미 |
|---|---|
| OpenAPI | API 명세 표준 자체 (현재 3.1.x) |
| Swagger | OpenAPI 이전의 명세 이름. 현재는 도구 브랜드로만 사용 (Swagger UI, Swagger Editor, SwaggerHub) |
| OAS 3.0 vs 3.1 | 3.1은 JSON Schema 2020-12와 완전 호환. `nullable` 키워드 대신 `type: ["string", "null"]` 형태를 사용 |

### OpenAPI 3 문서의 최소 구조

```yaml
openapi: 3.0.3
info:
  title: Order API
  version: "1.0"
paths:
  /orders:
    get:
      summary: 주문 목록 조회
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, paid, shipped]
      responses:
        '200':
          description: 주문 목록
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Order'
        '400':
          $ref: '#/components/responses/ValidationError'
components:
  schemas:
    Order:
      type: object
      required: [id, status, created_at]
      properties:
        id:
          type: string
          example: "ord_001"
        status:
          type: string
          enum: [pending, paid, shipped]
        created_at:
          type: string
          format: date-time
  responses:
    ValidationError:
      description: 입력 검증 실패
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'
```

핵심 구성 요소:
- **info**: API 이름, 버전, 설명
- **paths**: endpoint별 operation(method + 파라미터 + 응답)
- **components**: 재사용 가능한 schema, response, parameter 정의


### 실무에서 자주 쓰는 선언 패턴

다음은 spec 작성 시 반복적으로 사용하는 패턴입니다.

| 패턴 | 설명 | 예시 |
|---|---|---|
| `$ref` | 재사용 참조 | `$ref: '#/components/schemas/Order'` |
| `allOf` | Schema 합성 (상속) | Base + 확장 필드 |
| `oneOf` / `discriminator` | 다형성 | 결제 수단별 다른 body |
| `readOnly` / `writeOnly` | 요청/응답 방향 | `id`는 readOnly, `password`는 writeOnly |
| `nullable` (3.0) / `type: ["string", "null"]` (3.1) | 널 허용 | 선택적 필드 |

`allOf`를 활용하면 공통 필드(id, created_at, updated_at)를 base schema로 분리하고 각 리소스는 확장만 정의할 수 있습니다.

```yaml
components:
  schemas:
    BaseEntity:
      type: object
      properties:
        id: {type: string, readOnly: true}
        created_at: {type: string, format: date-time, readOnly: true}
    Order:
      allOf:
        - $ref: '#/components/schemas/BaseEntity'
        - type: object
          required: [status]
          properties:
            status: {type: string, enum: [pending, paid, shipped]}
            total_amount: {type: integer}
```
## Code-first vs Schema-first

API spec을 만드는 두 가지 접근법이 있습니다. 어느 쪽이든 "spec이 존재하고 코드와 동기화된다"는 결과는 같아야 합니다.

### Code-first

코드(Python decorator, TypeScript type 등)에서 spec을 자동 생성합니다.

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"

class Order(BaseModel):
    id: str
    status: OrderStatus
    created_at: str

app = FastAPI(title="Order API", version="1.0")

@app.get("/orders", response_model=list[Order])
def list_orders(status: OrderStatus | None = Query(None)):
    """주문 목록을 조회합니다."""
    ...
```

FastAPI는 이 코드에서 `/openapi.json`을 자동 생성합니다. Pydantic 모델이 곧 schema이므로 validation과 문서가 동시에 보장됩니다.

**장점**: 코드와 spec이 구조적으로 분리되지 않으므로 drift 가능성이 낮음
**단점**: spec을 먼저 리뷰하기 어려움. 프레임워크에 종속

### Schema-first

spec 파일을 먼저 작성하고, 서버 코드와 클라이언트를 spec에서 생성합니다.

```bash
# spec에서 Python 서버 stub 생성
openapi-generator-cli generate -i openapi.yaml -g python-flask -o ./server

# spec에서 TypeScript 클라이언트 생성
openapi-generator-cli generate -i openapi.yaml -g typescript-axios -o ./client
```

**장점**: API 계약을 코드 전에 리뷰 가능. 다중 언어 SDK 생성 용이
**단점**: 생성된 코드가 프레임워크와 맞지 않으면 커스터마이징 필요

### 어떤 것을 선택할까?

| 조건 | 권장 |
|---|---|
| FastAPI, NestJS 등 spec 자동 생성 지원 | Code-first |
| 프론트/백 팀이 분리되어 있고 계약 선행 필요 | Schema-first |
| 다중 언어 클라이언트가 필요 | Schema-first |
| 빠른 프로토타이핑 | Code-first |
| 이미 운영 중인 API에 spec 추가 | Code-first (역생성) |


팀 내에서 한 번 선택하면 모든 서비스에 동일하게 적용합니다. 혼용하면 "이 spec은 코드에서 나온 건가, 수동으로 쓴 건가?"를 파악할 수 없어서 어느 쪽도 신뢰할 수 없게 됩니다. 참고로 Django REST Framework는 `drf-spectacular`, Spring Boot는 `springdoc-openapi`, NestJS는 `@nestjs/swagger`가 code-first를 지원합니다. Go 생태계에서는 `oapi-codegen`이 schema-first를 지원합니다.
## Swagger UI vs Redoc

| 기능 | Swagger UI | Redoc |
|---|---|---|
| "Try it out" (실시간 호출) | 지원 | 미지원 (별도 플러그인 필요) |
| 읽기 편의성 | 기능 중심 | 문서 중심, 3-panel 레이아웃 |
| 커스터마이징 | 테마 변경 가능 | 더 유연한 스타일링 |
| 적합한 대상 | 내부 개발자, QA | 외부 API 사용자, 파트너 |

실무에서는 내부용은 Swagger UI(`/docs`), 외부 공개 문서는 Redoc을 쓰는 팀이 많습니다. 두 도구 모두 같은 `openapi.json`을 입력으로 받으므로 동시에 제공해도 유지보수 비용이 추가되지 않습니다. 추가로 Scalar(https://scalar.com)도 최근 인기를 얻고 있으며, Swagger UI와 유사한 인터랙티브 기능을 더 현대적인 UI로 제공합니다.


## Spec 파일 구성 팁

### 파일 분리

규모가 커지면 하나의 `openapi.yaml`이 수천 줄이 됩니다. `$ref`로 파일을 분리하면 PR diff가 읽기 쉬워집니다.

```text
specs/
├── openapi.yaml          # 진입점 (info + paths 참조)
├── paths/
│   ├── orders.yaml       # /orders 관련 operation
│   └── users.yaml        # /users 관련 operation
└── components/
    ├── schemas/
    │   ├── Order.yaml
    │   └── User.yaml
    └── responses/
        └── errors.yaml
```

`@redocly/cli bundle specs/openapi.yaml -o bundled.yaml`로 번들링하면 단일 파일로 합칠 수 있습니다.

### 네이밍 규칙

| 대상 | 규칙 | 예시 |
|---|---|---|
| Schema 이름 | PascalCase | `Order`, `UserProfile` |
| Property 이름 | snake_case | `created_at`, `order_id` |
| Path | kebab-case 복수형 | `/order-items`, `/users` |
| Operation ID | camelCase | `listOrders`, `createUser` |
| Error code | snake_case + dot | `order.not_found` |

일관된 네이밍은 SDK 생성 시 메서드명과 클래스명이 자연스럽게 나오도록 합니다. `operationId`가 없으면 generator가 path에서 이름을 추측해야 하므로 결과가 예측하기 어렵습니다.

### Deprecation 표시

필드나 endpoint를 제거하기 전에 `deprecated: true`를 먼저 표시합니다.

```yaml
paths:
  /v1/orders:
    get:
      deprecated: true
      summary: "사용 중단 예정 — /v2/orders를 사용하세요"
```

Swagger UI는 deprecated endpoint를 취소선으로 표시하므로 사용자가 자연스럽게 마이그레이션할 수 있습니다.
## Spec을 단일 진실 원본으로 유지하는 CI 전략

spec이 코드와 어긋나면 "자동화된 문서"라는 말은 거짓이 됩니다. CI에서 동기화를 강제하는 방법:

### Code-first 프로젝트

```yaml
# .github/workflows/check-spec.yml
- name: Generate spec
  run: python -c "from app.main import app; import json; print(json.dumps(app.openapi()))" > generated.json

- name: Compare with committed spec
  run: diff openapi.json generated.json || (echo "Spec drift detected" && exit 1)
```

코드를 바꾸면 spec도 함께 커밋해야 CI가 통과합니다.

### Schema-first 프로젝트

```yaml
- name: Validate spec
  run: npx @redocly/cli lint openapi.yaml

- name: Check breaking changes
  run: npx oasdiff breaking openapi.yaml openapi-main.yaml
```

`oasdiff`는 필수 파라미터 추가, 응답 필드 제거 같은 breaking change를 자동 감지합니다.

### Mock server 활용

spec에서 mock server를 생성하면 프론트엔드 팀이 백엔드 구현을 기다리지 않고 개발할 수 있습니다.

```bash
# Prism으로 mock server 실행
npx @stoplight/prism mock openapi.yaml
# → http://localhost:4010 에서 spec 기반 응답 반환
```

Prism은 schema의 `example` 값을 사용해 응답을 생성합니다. `example`이 없으면 타입에 맞는 랜덤 값을 반환합니다. 이 접근법은 프론트/백 병렬 개발뿐 아니라 통합 테스트의 fixture로도 활용할 수 있습니다.

### Contract testing

spec을 계약으로 삼아 서버 응답이 실제로 spec과 일치하는지 테스트할 수도 있습니다.

```python
# pytest + schemathesis로 contract test
import schemathesis

schema = schemathesis.from_uri("http://localhost:8000/openapi.json")

@schema.parametrize()
def test_api(case):
    response = case.call()
    case.validate_response(response)
```

`schemathesis`는 spec의 모든 endpoint에 대해 자동으로 fuzzing 테스트를 생성합니다. 응답이 spec에 정의된 schema와 다르면 즉시 실패합니다. 이 방식을 CI에 넣으면 drift를 실시간으로 잡을 수 있습니다.

## 실무에서 자주 빠뜨리는 것들

### 1. 예제(examples)

```yaml
components:
  schemas:
    Order:
      type: object
      properties:
        id:
          type: string
          example: "ord_abc123"
        status:
          type: string
          example: "paid"
```

예제가 없으면 Swagger UI의 "Try it out"에서 사용자가 무엇을 입력해야 할지 모릅니다.

### 2. 에러 응답

```yaml
responses:
  '404':
    description: 주문을 찾을 수 없음
    content:
      application/problem+json:
        schema:
          $ref: '#/components/schemas/ProblemDetail'
        example:
          type: "https://api.example.com/errors/order-not-found"
          title: "Order not found"
          status: 404
          code: "order.not_found"
```

200만 문서화하고 4xx/5xx를 비워 두면, 클라이언트 개발자는 실패 경로를 알 수 없습니다.

### 3. 인증 정보

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
security:
  - BearerAuth: []
```

`securitySchemes`가 없으면 Swagger UI에서 인증이 필요한 endpoint를 테스트할 수 없습니다.

## 자주 하는 실수 다섯 가지

| # | 실수 | 결과 | 해결 |
|---|---|---|---|
| 1 | spec과 코드가 따로 놂 | 문서를 믿을 수 없음 | CI에서 동기화 검증 |
| 2 | 예제 없음 | 사용자가 뭘 보내야 할지 모름 | 모든 schema에 `example` 추가 |
| 3 | 4xx/5xx 미문서화 | 실패 경로를 알 수 없음 | error response도 spec에 포함 |
| 4 | spec 버전 관리 안 함 | 변경 이력 추적 불가 | git에 커밋, PR diff 리뷰 |
| 5 | 내부 endpoint 노출 | 공개 spec에 내부 정보 유출 | 공개/내부 spec 분리 |

## 시니어 엔지니어는 이렇게 판단합니다

- code-first와 schema-first 중 하나를 팀 전체에서 명확히 선택합니다. 혼용하면 어느 쪽도 신뢰할 수 없게 됩니다.
- spec 파일을 git에 커밋하고 PR diff로 리뷰합니다. "API 계약이 바뀌었다"는 사실이 코드 리뷰에서 명시적으로 보여야 합니다.
- 예제를 반드시 채웁니다. 사용자는 설명을 읽기 전에 예제를 복사합니다.
- breaking change를 CI에서 자동 감지합니다. 필드 제거, 필수 파라미터 추가, enum 값 삭제 같은 변경이 리뷰 없이 merge되면 안 됩니다.
- 공개용 spec과 내부용 spec을 분리합니다. 내부 관리 endpoint가 외부에 노출되면 보안 문제입니다.

## 검증 포인트와 실패 신호

- **Expected output:** `/openapi.json`과 `/docs`가 같은 endpoint, 같은 schema, 같은 예제를 보여 줘야 하며 CI에서도 그 동기화가 깨지지 않아야 합니다.
- **First check:** 코드 리뷰 없이 spec 파일만 수동 수정되거나, 반대로 코드만 바뀌고 spec diff가 비어 있다면 drift가 시작된 것입니다.
- **Failure mode:** 성공 응답만 문서화하고 4xx/5xx를 비워 두면, 사용자는 try-it 화면을 보고도 실제 실패 경로를 재현하지 못합니다.

## 체크리스트

- [ ] spec이 코드와 동기화되는가? CI에서 확인하는가?
- [ ] 모든 endpoint에 예제가 있는가?
- [ ] 4xx와 5xx가 spec에 정의되어 있는가?
- [ ] `components/schemas`를 `$ref`로 재사용하는가?
- [ ] 공개 spec과 내부 spec이 분리되어 있는가?
- [ ] breaking change를 CI에서 감지하는가?
- [ ] `securitySchemes`가 정의되어 있는가?

## 연습 문제

1. 현재 프로젝트의 가장 복잡한 endpoint를 OpenAPI 3.0으로 표현해 보세요. 파라미터, 요청 body, 성공 응답, 에러 응답을 모두 포함합니다.
2. FastAPI로 `POST /orders`를 작성하고, 자동 생성된 `/openapi.json`에 request body schema와 validation error가 포함되는지 확인해 보세요.
3. `oasdiff`나 `@redocly/cli`로 두 버전의 spec을 비교하고, breaking change를 자동 감지하는 CI step을 설계해 보세요.

## 정리와 다음 글

OpenAPI는 API의 프로토콜이자 문서이자 코드 생성 입력입니다. spec을 중심에 두면 문서, SDK, validation, mock이 모두 하나의 원본에서 파생되므로 drift가 구조적으로 사라집니다. 다음 글에서는 이 계약을 안전하게 바꾸는 기술, versioning을 다룹니다.


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


## 처음 질문으로 돌아가기

- **OpenAPI 3 문서는 어떤 구조로 이루어질까요?**
  - `info`(메타데이터), `paths`(endpoint별 operation), `components`(재사용 schema/response/parameter) 세 블록으로 구성됩니다. paths에서 `$ref`로 components를 참조하면 중복 없이 일관된 타입을 유지할 수 있습니다.
- **Swagger UI와 Redoc은 각각 어떤 역할을 할까요?**
  - Swagger UI는 "Try it out" 기능으로 개발자가 즉시 API를 호출해 볼 수 있는 인터랙티브 도구이고, Redoc은 3-panel 레이아웃으로 읽기 편한 문서를 제공합니다. 내부 개발용은 Swagger UI, 외부 공개 문서는 Redoc이 적합합니다.
- **code-first와 schema-first는 어떤 차이가 있을까요?**
  - code-first는 코드(decorator, type)에서 spec을 자동 생성하므로 drift가 낮지만 프레임워크에 종속됩니다. schema-first는 spec을 먼저 합의한 뒤 코드와 SDK를 생성하므로 계약 선행 리뷰와 다중 언어 지원에 유리하지만, 생성 코드 커스터마이징 비용이 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST 기본](./02-rest-basics.md)
- [API Design 101 (3/10): 리소스 설계](./03-resource-design.md)
- [API Design 101 (4/10): HTTP method와 status code](./04-http-methods-and-status.md)
- [API Design 101 (5/10): Request와 response schema](./05-request-and-response-schema.md)
- [API Design 101 (6/10): Pagination과 filtering](./06-pagination-and-filtering.md)
- [API Design 101 (7/10): Error response 설계](./07-error-response-design.md)
- **OpenAPI와 Swagger (현재 글)**
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Redoc](https://redocly.com/redoc/)
- [FastAPI: Automatic docs](https://fastapi.tiangolo.com/features/)
- [oasdiff — OpenAPI breaking change detection](https://github.com/Tufin/oasdiff)

Tags: Computer Science, APIDesign, OpenAPI, Swagger, Documentation, Backend
