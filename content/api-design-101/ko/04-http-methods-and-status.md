---
title: "API Design 101 (4/10): HTTP method와 status code"
series: api-design-101
episode: 4
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
  - HTTP
  - Methods
  - StatusCodes
  - Backend
last_reviewed: '2026-05-15'
seo_description: GET부터 DELETE까지, 예측 가능한 API를 만드는 응답 코드를 정리합니다.
---

# API Design 101 (4/10): HTTP method와 status code

같은 작업을 해도 어떤 API는 클라이언트가 다음 행동을 쉽게 고르고, 어떤 API는 성공인지 실패인지부터 다시 해석하게 만듭니다. 그 차이는 대개 메서드 이름이 아니라 method와 status code를 얼마나 일관되게 묶어 썼는지에서 나옵니다.

이 글은 API Design 101 시리즈의 네 번째 글입니다.

여기서는 GET, POST, PATCH, DELETE를 단순 암기가 아니라 클라이언트 분기 규칙으로 정리합니다. 응답 숫자를 어떻게 고르느냐가 재시도, 캐시, 에러 처리까지 함께 결정하기 때문입니다.


![API Design 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/04/04-01-concept-at-a-glance.ko.png)
*API Design 101 4장 흐름 개요*

## 먼저 던지는 질문

- GET, POST, PUT, PATCH, DELETE는 각각 무엇을 의미할까요?
- safe와 idempotent는 어떻게 다를까요?
- 2xx, 3xx, 4xx, 5xx 계열은 어떻게 읽어야 할까요?

## 왜 중요한가

method와 status code는 클라이언트의 분기 로직을 결정합니다. 잘못된 코드를 반환하면 클라이언트는 재시도가 안전한지조차 판단할 수 없습니다. 이 둘은 API의 예측 가능성을 만드는 핵심 쌍입니다.

> status code는 단순한 숫자가 아니라 계약입니다.

## 한눈에 보는 개념

| Method | 의미 | Safe | Idempotent | 대표 성공 코드 |
|--------|------|------|------------|--------------|
| GET | 조회 | ✓ | ✓ | 200 |
| POST | 생성 | ✗ | ✗ | 201 |
| PUT | 전체 대체 | ✗ | ✓ | 200 / 204 |
| PATCH | 부분 수정 | ✗ | ✗* | 200 |
| DELETE | 삭제 | ✗ | ✓ | 204 |
| HEAD | 헤더만 조회 | ✓ | ✓ | 200 |
| OPTIONS | 허용 method 조회 | ✓ | ✓ | 204 |

*PATCH는 스펙상 idempotent가 아니지만, 실무에서는 idempotent하게 설계하는 것이 권장됩니다.

**Safe vs Idempotent 차이:**
- **Safe**: 호출해도 서버 상태가 바뀌지 않습니다. GET으로 조회한다고 데이터가 달라지지 않습니다.
- **Idempotent**: 동일 요청을 N번 보내도 결과가 1번과 같습니다. DELETE는 이미 삭제된 리소스를 다시 삭제해도 결과가 같습니다.

이 구분이 중요한 이유: 네트워크 실패 시 클라이언트가 안전하게 재시도할 수 있는지를 결정하기 때문입니다. Idempotent한 method는 timeout 시 다시 보내도 안전합니다. Non-idempotent한 POST는 그렇지 않아서 idempotency key가 필요합니다.

## 핵심 용어

| 용어 | 정의 | 예시 |
|------|------|------|
| Safe | 리소스를 변경하지 않는 호출 | GET, HEAD, OPTIONS |
| Idempotent | N번 호출해도 1번과 동일한 결과 | GET, PUT, DELETE |
| 2xx | 성공 계열 | 200 OK, 201 Created, 204 No Content |
| 4xx | 클라이언트 오류 계열 | 400 Bad Request, 404 Not Found, 409 Conflict |
| 5xx | 서버 오류 계열 | 500 Internal, 502 Bad Gateway, 503 Unavailable |
| Content Negotiation | Accept 헤더로 응답 형식 요청 | `Accept: application/json` |
| Idempotency Key | POST 재시도를 안전하게 만드는 헤더 | `Idempotency-Key: abc-123` |
## 전후 비교

**Before (의도가 불분명)**

```http
POST /users/42/update   200 OK   {"ok": true}
POST /users/42/delete   200 OK   {"ok": true}
POST /users             200 OK   {"ok": true}
GET  /users/999         200 OK   {"error": "not found"}
```

문제점:
- 모든 응답이 200이라 클라이언트는 body를 파싱해야 성공/실패를 판단합니다.
- HTTP 캐시가 에러 응답까지 캐싱할 수 있습니다.
- SDK 예외 처리가 작동하지 않습니다 (status가 항상 2xx이므로).

**After (method × status가 분명)**

```http
PATCH  /users/42   200 OK         {"id": 42, "name": "updated"}
DELETE /users/42   204 No Content
POST   /users      201 Created    Location: /users/43
GET    /users/999  404 Not Found  {"error": "user not found"}
```

성공 방식이 status만으로도 읽혀야 합니다. SDK는 4xx/5xx를 예외로 던지고, 캐시는 2xx만 저장합니다.

## 실습: 반복해서 쓰게 될 다섯 패턴

### Step 1 — Read (GET)

```python
# 1_get.py
from flask import Flask, jsonify, abort
app = Flask(__name__)
USERS = {42: {"id": 42, "name": "Y"}}

@app.get("/users/<int:uid>")
def get_user(uid):
    if uid not in USERS: abort(404)
    return jsonify(USERS[uid])
```

성공이면 200, 없으면 404입니다.

### Step 2 — Create (POST)

```python
# 2_post.py
from flask import Flask, request, jsonify
app = Flask(__name__)
NEXT = {"id": 43}

@app.post("/users")
def create_user():
    body = request.get_json()
    uid = NEXT["id"]; NEXT["id"] += 1
    return jsonify(id=uid, **body), 201, {"Location": f"/users/{uid}"}
```

생성은 보통 `201 + Location`입니다.

### Step 3 — Partial update (PATCH)

```python
# 3_patch.py
from flask import Flask, request, jsonify
app = Flask(__name__)
USERS = {42: {"id": 42, "name": "Y"}}

@app.patch("/users/<int:uid>")
def patch_user(uid):
    USERS[uid].update(request.get_json())
    return jsonify(USERS[uid])
```

PATCH는 일부 수정이고, PUT은 전체 대체입니다. 둘을 섞어 쓰면 계약 의미가 흐려집니다.

### Step 4 — Delete

```python
# 4_delete.py
from flask import Flask
app = Flask(__name__)
USERS = {42: {}}

@app.delete("/users/<int:uid>")
def delete_user(uid):
    USERS.pop(uid, None)
    return ("", 204)
```

본문이 없는 성공 삭제는 204가 잘 맞습니다.

### Step 5 — Validation failure and conflict

```python
# 5_errors.py
from flask import Flask, request, jsonify, abort
app = Flask(__name__)

@app.post("/users")
def create():
    body = request.get_json() or {}
    if "name" not in body: abort(400)        # validation
    if body["name"] == "exists": abort(409)  # conflict
    return jsonify(ok=True), 201
```

입력 검증 실패는 400, 리소스 충돌은 409처럼 결과 의미에 맞춰 골라야 합니다.

## 실용적인 status code 매핑표

| 상황 | Status Code | 이유 |
|------|-------------|------|
| 조회 성공 | 200 OK | 본문에 데이터 있음 |
| 생성 성공 | 201 Created | 새 리소스 만들어짐, Location 헤더 포함 |
| 성공, 본문 없음 | 204 No Content | DELETE 성공 등 |
| 입력 오류 | 400 Bad Request | 요청 body 형식 오류 |
| 인증 누락 | 401 Unauthorized | 토큰 없음 / 만료 |
| 권한 부족 | 403 Forbidden | 토큰은 유효하지만 권한 없음 |
| 리소스 없음 | 404 Not Found | ID에 해당하는 리소스 없음 |
| 충돌 | 409 Conflict | 이미 존재하는 리소스 / 상태 충돌 |
| 의미 오류 | 422 Unprocessable | 형식은 맞지만 비즈니스 규칙 위반 |
| Rate limit | 429 Too Many Requests | 요청 제한 초과 |
| 서버 오류 | 500 Internal Server Error | 예상치 못한 서버 장애 |
| 일시 점검 | 503 Service Unavailable | 재시도 가능한 일시 장애 |

**클라이언트 분기 로직 기준:**
- `2xx` → 성공, 결과 사용
- `4xx` → 클라이언트가 고칠 수 있음, 재시도 무의미 (429 제외)
- `5xx` → 서버 문제, 재시도 가능 (exponential backoff)
## 자주 하는 실수 다섯 가지

1. **성공을 전부 200으로 반환합니다.** 생성과 삭제, 수정의 차이가 사라집니다.
2. **검증 실패를 500으로 반환합니다.** 클라이언트는 재시도하면 될 문제라고 오해합니다.
3. **DELETE에 본문을 싣습니다.** idempotency와 캐시 의미를 흐립니다.
4. **PATCH로 전체 대체를 합니다.** PUT의 의미가 무너집니다.
5. **404와 401, 403을 혼동합니다.** 보안 정보가 새거나 인증 버그를 가립니다.

## 실무에서는 이렇게 드러납니다

### GitHub API 응답 패턴

```http
POST /repos/{owner}/{repo}/issues       → 201 Created + Location
PATCH /repos/{owner}/{repo}/issues/1    → 200 OK
GET /repos/{owner}/{repo}/issues/9999   → 404 Not Found
DELETE /repos/{owner}/{repo}/comments/1  → 204 No Content
```

### Stripe API Idempotency

```http
POST /v1/charges
Idempotency-Key: order_abc_123
```

Stripe는 POST에 Idempotency-Key 헤더를 보내면 동일 요청을 중복 실행하지 않습니다. 네트워크 실패로 클라이언트가 재시도해도 결제가 두 번 되지 않습니다. Non-idempotent한 POST를 안전하게 만드는 실무 패턴입니다.

### 401 vs 403 구분

```text
토큰 없음 / 만료           → 401 Unauthorized  ("너 누구야?")
토큰 유효, 권한 부족     → 403 Forbidden     ("너인 건 알지만 안 돼")
리소스 존재 숨기고 싶을 때 → 404 Not Found     ("그런 거 없는데?")
```

보안 관점에서 403을 돌려주면 "리소스가 존재한다"는 정보가 노출됩니다. 민감한 리소스는 권한 없을 때 404를 돌려주는 팀도 있습니다 (GitHub private repo가 이 패턴).

## 시니어 엔지니어는 이렇게 생각합니다

- **먼저 클라이언트 분기 로직을 그린 뒤 status code를 매핑합니다.** "이 응답을 받으면 클라이언트는 다음에 무엇을 해야 하는가?"를 기준으로 코드를 고릅니다.
- **재시도 가능한 작업은 idempotent하게 설계합니다.** POST에는 Idempotency-Key를 도입하고, PUT/DELETE는 자연스럽게 idempotent하므로 클라이언트에게 재시도 안전성을 명시합니다.
- **`4xx`는 사용자가 고칠 수 있는 문제, `5xx`는 서버가 고쳐야 하는 문제로 봅니다.** 이 구분이 alert과 모니터링 설계를 결정합니다. 4xx는 클라이언트 버그 또는 사용자 실수, 5xx는 즉시 on-call 대응 대상입니다.
- **표준 status code 안에서 해결하려고 합니다.** 커스텀 코드(599 같은)를 만들면 모든 클라이언트 라이브러리가 그것을 알아야 하므로 호환성이 깨집니다.
- **자세한 이유는 body의 일관된 형식 안에 담습니다.** status code는 분기 신호, body는 상세 정보를 담당합니다. 에러 본문 형식은 7장에서 다룹니다.

## 검증 포인트와 실패 신호

- **Expected output:** 생성 호출은 `201 + Location`, 삭제 성공은 `204`, 조회 실패는 `404`처럼 결과만 보고도 후속 분기가 그려져야 합니다.
- **First check:** 비슷한 실패를 `400`, `409`, `422` 중 아무 숫자로나 섞어 쓰고 있다면 클라이언트 계약이 이미 모호해진 상태입니다.
- **Failure mode:** 모든 성공을 `200`으로 뭉개면 캐시 정책, SDK 예외 처리, 재시도 제어가 전부 본문 파싱에 의존하게 됩니다.

## 체크리스트

- [ ] 생성은 201 + Location을 반환하는가?
- [ ] 성공적인 삭제는 204를 반환하는가?
- [ ] 검증 실패는 400 또는 422인가?
- [ ] 인증 누락은 401, 권한 부족은 403으로 구분되는가?
- [ ] PATCH와 PUT이 각자의 의미대로 쓰이는가?

## 연습 문제

1. endpoint 하나를 골라 가능한 4xx 응답 다섯 개를 적어 보세요.
2. Step 2 예제에 중복 username 검사를 추가하고 409를 반환해 보세요.
3. 현재 코드베이스에서 non-idempotent한 endpoint 세 개를 찾아 어떻게 개선할지 적어 보세요.

## 정리와 다음 글

method와 status code는 항상 짝으로 읽어야 합니다. 다음 글에서는 그 사이를 오가는 실제 데이터, 즉 request와 response schema를 다룹니다.


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


## 운영 전 최종 점검 시나리오

릴리스 직전에는 method와 status code를 "엔드포인트별 표"가 아니라 "사용자 여정"으로 다시 점검해야 합니다. 예를 들어 회원가입 흐름이면 `POST /users -> 201`, 중복 이메일이면 `409`, 입력 오류면 `422`, 인증 없는 조회면 `401`처럼 실제 분기 순서로 확인합니다. 이 점검을 자동화하면 배포 직후 발생하는 회귀를 줄일 수 있습니다.

```yaml
contract_smoke_tests:
  - name: create-user-success
    request: POST /v1/users
    expect_status: 201
  - name: create-user-duplicate-email
    request: POST /v1/users
    expect_status: 409
  - name: create-user-invalid-email
    request: POST /v1/users
    expect_status: 422
```

핵심은 "성공 코드"보다 "실패 코드를 얼마나 예측 가능하게 유지하느냐"입니다. 소비자는 실패 케이스에서 API 신뢰도를 판단합니다.

## 처음 질문으로 돌아가기

- **GET, POST, PUT, PATCH, DELETE는 각각 무엇을 의미할까요?**
  - GET은 조회(safe+idempotent), POST는 생성(non-safe, non-idempotent), PUT은 전체 대체(idempotent), PATCH는 부분 수정, DELETE는 삭제(idempotent)입니다. method가 의도를 담으므로 URL에 동사를 넣을 필요가 없습니다.
- **safe와 idempotent는 어떻게 다를까요?**
  - safe는 "서버 상태를 바꾸지 않는다", idempotent는 "N번 호출해도 1번과 결과가 같다"입니다. DELETE는 safe하지 않지만(상태가 바뀌므로) idempotent합니다(이미 삭제된 것을 다시 삭제해도 결과 동일). 이 구분이 클라이언트 재시도 정책을 결정합니다.
- **2xx, 3xx, 4xx, 5xx 계열은 어떻게 읽어야 할까요?**
  - 2xx는 성공(후속 처리 진행), 4xx는 클라이언트가 고칠 문제(재시도 무의미), 5xx는 서버 문제(재시도 의미 있음)로 읽습니다. 이 세 줄 분기로 클라이언트 에러 핸들러를 설계합니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- [API Design 101 (2/10): REST 기본](./02-rest-basics.md)
- [API Design 101 (3/10): 리소스 설계](./03-resource-design.md)
- **HTTP method와 status code (현재 글)**
- Request와 response schema (예정)
- Pagination과 filtering (예정)
- Error response 설계 (예정)
- OpenAPI와 Swagger (예정)
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [HTTP Methods (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [HTTP Status Codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [RFC 7231 — HTTP/1.1 Semantics](https://www.rfc-editor.org/rfc/rfc7231)
- [Idempotency in REST APIs (Stripe blog)](https://stripe.com/blog/idempotency)

Tags: Computer Science, APIDesign, HTTP, Methods, StatusCodes, Backend
