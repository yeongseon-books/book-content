---
title: "API Design 101 (2/10): REST 기본"
series: api-design-101
episode: 2
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
  - REST
  - HTTP
  - Backend
  - WebDevelopment
last_reviewed: '2026-05-20'
seo_description: REST의 여섯 제약과 리소스 중심 설계가 무엇인지 기초부터 정리합니다.
---

# API Design 101 (2/10): REST 기본

비슷해 보이는 두 API가 실제로는 전혀 다르게 느껴지는 이유는 대개 REST라는 이름 때문이 아니라 예측 가능성 때문입니다. URL은 그럴듯한데 호출할 때마다 규칙이 달라지면, 클라이언트는 문서를 읽고도 계속 추측해야 합니다.

이 글은 API Design 101 시리즈의 두 번째 글입니다.

여기서는 REST를 URL 스타일이 아니라 여섯 가지 제약이 만드는 설계 규율로 정리합니다. 그래야 이후 글에서 리소스, 메서드, 캐시, 문서 구조를 따로 배워도 같은 방향으로 이해할 수 있습니다.


![클라이언트-리소스-서버 계층 구조](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/02/02-01-concept-at-a-glance.ko.png)
*REST의 계층 구조: 클라이언트 → 캐시/LB → 서버 → 데이터*

## 먼저 던지는 질문

- REST는 어디서 나왔고 무엇을 뜻할까요?
- REST를 이루는 여섯 가지 아키텍처 제약은 무엇일까요?
- 리소스 중심 사고는 RPC 스타일과 어떻게 다를까요?

## REST의 탄생과 핵심 정의

REST(Representational State Transfer)는 Roy Fielding이 2000년 박사 논문에서 정의한 아키텍처 스타일입니다. 당시 HTTP 1.1 표준화 작업에 참여하던 Fielding은 "웹이 왜 이렇게 잘 확장되는가?"라는 질문에서 출발했습니다. 답은 웹 자체에 내재된 아키텍처 제약이었고, 그 제약을 형식화한 것이 REST입니다.

핵심 아이디어를 한 문장으로 요약하면 이렇습니다.

> 서버는 리소스의 현재 상태(representation)를 클라이언트에 전달하고, 클라이언트는 그 표현을 보고 다음 상태 전이(state transfer)를 결정합니다.

이름 자체가 이 동작을 설명합니다. Representational(표현의) State(상태) Transfer(전달). "리소스의 표현을 통해 상태를 전달한다"는 뜻입니다.

중요한 점은 REST가 프로토콜이나 표준이 아니라 **제약의 집합**이라는 것입니다. HTTP를 사용하지 않아도 REST할 수 있고, HTTP를 사용해도 REST가 아닐 수 있습니다. 제약을 따르는지가 기준입니다.

## 여섯 가지 아키텍처 제약

REST를 구성하는 제약은 다음 여섯 가지입니다. 각각은 독립적인 이점을 주지만, 함께 적용될 때 웹 규모의 확장성을 만들어 냅니다.

### 1. Client-Server 분리

클라이언트(UI)와 서버(데이터 저장·비즈니스 로직)의 관심사를 분리합니다. 클라이언트는 데이터가 어디에 저장되는지 모르고, 서버는 화면이 어떻게 그려지는지 모릅니다.

**이점:** 각자 독립적으로 진화할 수 있습니다. 모바일 앱을 새로 만들어도 서버 API는 바꿀 필요가 없고, 서버를 Python에서 Go로 재작성해도 클라이언트는 영향을 받지 않습니다.

### 2. Stateless (무상태)

각 요청은 처리에 필요한 모든 정보를 자체적으로 담아야 합니다. 서버는 클라이언트의 이전 요청을 기억하지 않습니다.

```python
# Stateless: 매 요청에 인증 정보를 포함
GET /users/42
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**이점:** 서버 인스턴스를 자유롭게 추가하거나 교체할 수 있습니다. 요청이 어느 서버로 가든 결과가 같으므로 수평 확장이 쉽습니다.

**주의:** "서버가 아무것도 저장하지 않는다"는 뜻이 아닙니다. 데이터베이스에 사용자 정보를 저장하는 것은 당연합니다. Stateless는 **요청 간 세션 상태**를 서버 메모리에 붙들지 않는다는 의미입니다.

### 3. Cacheable (캐시 가능)

응답에 캐시 가능 여부를 명시해야 합니다. 캐시 가능한 응답은 클라이언트나 중간 계층(CDN, 프록시)이 저장해 두고 재사용할 수 있습니다.

```http
HTTP/1.1 200 OK
Cache-Control: public, max-age=3600
ETag: "abc123"

{"id": 42, "name": "Alice"}
```

**이점:** 네트워크 트래픽과 서버 부하가 줄어듭니다. 동일한 리소스를 수천 명이 조회해도 서버는 한 번만 처리하면 됩니다.

### 4. Uniform Interface (일관된 인터페이스)

모든 리소스에 동일한 규칙으로 접근합니다. HTTP에서는 이렇게 구현됩니다.

| 원칙 | 의미 |
|---|---|
| 리소스 식별 | URI로 리소스를 고유하게 지정 (`/users/42`) |
| 표현을 통한 조작 | JSON/XML 형태로 리소스를 읽고 수정 |
| 자기 서술 메시지 | 요청/응답에 처리에 필요한 모든 정보 포함 |
| HATEOAS | 응답에 다음 가능한 행동의 링크 포함 |

**이점:** 하나의 endpoint 사용법을 배우면 나머지도 비슷하게 동작합니다. 학습 비용이 크게 줄어듭니다.

### 5. Layered System (계층화)

클라이언트는 직접 연결된 계층만 알면 됩니다. 그 뒤에 로드 밸런서, 캐시 서버, 보안 게이트웨이가 있든 없든 클라이언트 코드는 바뀌지 않습니다.

```text
Client → CDN → Load Balancer → API Gateway → App Server → Database
         ^                       ^
         |                       |-- 인증/인가, rate limit
         |-- 정적 자산 캐시
```

**이점:** 인프라를 자유롭게 진화시킬 수 있습니다. CDN을 추가하든, WAF를 넣든, 서버를 분산하든 클라이언트 계약은 그대로입니다.

### 6. Code on Demand (선택적)

서버가 실행 가능한 코드(JavaScript 등)를 클라이언트에 전달할 수 있습니다. 이 제약은 유일하게 **선택 사항**입니다.

**현실:** 웹 브라우저가 서버에서 JavaScript를 받아 실행하는 것이 대표적인 예입니다. REST API 설계에서는 거의 사용하지 않으므로 이 시리즈에서는 깊게 다루지 않습니다.

## RPC 스타일 vs REST 스타일

REST의 핵심을 가장 빠르게 이해하는 방법은 RPC 스타일과 비교하는 것입니다.

| 비교 항목 | RPC 스타일 | REST 스타일 |
|---|---|---|
| URL 의미 | 동작(verb) | 리소스(noun) |
| Method 사용 | 대부분 POST | GET/POST/PUT/DELETE 의미대로 |
| 예시 | `POST /getUserById` | `GET /users/42` |
| 예시 | `POST /createOrder` | `POST /orders` |
| 예시 | `POST /cancelOrder` | `DELETE /orders/99` 또는 `PATCH /orders/99 {"status": "cancelled"}` |
| 캐시 활용 | 어려움 (모두 POST) | 자연스러움 (GET은 캐시 가능) |
| 발견 가능성 | 낮음 (endpoint마다 고유 이름) | 높음 (리소스 + method 조합) |

RPC가 나쁜 것은 아닙니다. gRPC처럼 내부 서비스 간 고성능 통신에는 RPC가 더 적합한 경우도 많습니다. 하지만 **외부에 공개하는 API**에서는 REST의 예측 가능성과 캐시 친화성이 대부분의 경우 더 큰 이점을 줍니다.

## 전후 비교: 같은 기능, 다른 설계

**Before (RPC 스타일)**

```http
POST /api/getUser
Content-Type: application/json

{"userId": 42}
```

```http
POST /api/createUser
Content-Type: application/json

{"name": "Alice", "email": "alice@example.com"}
```

```http
POST /api/deleteUser
Content-Type: application/json

{"userId": 42}
```

모든 요청이 POST입니다. URL에 동사가 있습니다. 캐시가 불가능합니다. endpoint 목록이 늘어날수록 이름 짓기가 어려워집니다.

**After (REST 스타일)**

```http
GET /users/42
```

```http
POST /users
Content-Type: application/json

{"name": "Alice", "email": "alice@example.com"}
```

```http
DELETE /users/42
```

리소스(`/users`)는 같고 method가 의도를 표현합니다. GET은 캐시 가능하고, DELETE는 멱등합니다. 새로운 리소스를 추가해도 동일한 패턴을 반복합니다.

## 실습: 여섯 제약을 코드로 확인하기

### Step 1 — Client-Server 분리 확인

```python
# 1_client_server.py
import requests

# 클라이언트는 서버가 Python인지 Go인지 모름
# 오직 계약(URL + method + 응답 형태)만 알면 됨
r = requests.get("https://api.github.com")
print(r.status_code)  # 200
print(r.json().keys())  # 사용 가능한 리소스 URL 목록
```

서버 구현이 바뀌어도 계약이 유지되면 이 코드는 그대로 동작합니다.

### Step 2 — Stateless 요청

```python
# 2_stateless.py
import requests

# 매 요청에 인증 정보를 포함 — 서버는 이전 요청을 기억하지 않음
headers = {"Authorization": "Bearer my-token-123"}

# 이 두 요청은 서로 독립적 — 어느 서버 인스턴스가 받아도 동일 결과
r1 = requests.get("https://api.example.com/users/1", headers=headers)
r2 = requests.get("https://api.example.com/users/2", headers=headers)
```

### Step 3 — 캐시 헤더 설정

```python
# 3_cache.py
from flask import Flask, jsonify, make_response

app = Flask(__name__)

@app.get("/articles/<int:article_id>")
def get_article(article_id):
    article = {"id": article_id, "title": "REST Basics", "author": "Alice"}
    resp = make_response(jsonify(article))
    # 이 응답은 60초간 캐시 가능
    resp.headers["Cache-Control"] = "public, max-age=60"
    resp.headers["ETag"] = f'"{article_id}-v1"'
    return resp

@app.post("/articles")
def create_article():
    # POST 응답은 캐시하지 않음
    resp = make_response(jsonify(id=99, title="New"), 201)
    resp.headers["Cache-Control"] = "no-store"
    return resp
```

GET 응답에는 캐시 정책을 명시하고, POST/PUT/DELETE 응답에는 `no-store`를 붙이는 것이 일반적입니다.

### Step 4 — Uniform Interface 실전

```python
# 4_uniform.py
from flask import Flask, jsonify, request

app = Flask(__name__)
users = {1: {"id": 1, "name": "Alice"}, 2: {"id": 2, "name": "Bob"}}

@app.get("/users/<int:uid>")
def get_user(uid):
    """같은 리소스 URI, GET = 조회"""
    if uid not in users:
        return jsonify(error="not_found"), 404
    return jsonify(users[uid])

@app.put("/users/<int:uid>")
def replace_user(uid):
    """같은 리소스 URI, PUT = 전체 교체"""
    users[uid] = request.json
    users[uid]["id"] = uid
    return jsonify(users[uid])

@app.delete("/users/<int:uid>")
def delete_user(uid):
    """같은 리소스 URI, DELETE = 삭제"""
    users.pop(uid, None)
    return "", 204
```

하나의 URI(`/users/{id}`)에 대해 method만 바꾸면 의도가 달라집니다. 이 패턴이 모든 리소스에 동일하게 적용되므로, 하나를 배우면 나머지도 예측할 수 있습니다.

### Step 5 — 계층 투명성

```python
# 5_layered.py
import requests

# 클라이언트는 이 URL 뒤에 CDN, LB, Gateway가 있는지 모름
# 계약만 맞으면 인프라 구성은 자유롭게 바꿀 수 있음
r = requests.get("https://api.myservice.com/products/1")
assert r.status_code == 200
```

## Richardson Maturity Model: REST 수준 측정

Martin Fowler가 정리한 Richardson Maturity Model은 API가 REST에 얼마나 가까운지를 네 단계로 분류합니다.

| Level | 설명 | 특징 |
|---|---|---|
| 0 | 단일 URI, 단일 method | `POST /api`에 모든 요청을 보냄 (SOAP) |
| 1 | 리소스 분리 | URI로 리소스를 구분하지만 method는 아직 POST 위주 |
| 2 | HTTP method 활용 | GET/POST/PUT/DELETE를 의미대로 사용 |
| 3 | HATEOAS | 응답에 다음 행동 링크를 포함 |

대부분의 실무 REST API는 **Level 2**에 해당합니다. Level 3(HATEOAS)까지 구현하는 경우는 드물지만, 이 모델을 알면 "우리 API가 얼마나 RESTful한가?"를 객관적으로 판단할 수 있습니다.

## 자주 하는 실수 다섯 가지

1. **URL에 동사를 넣습니다.** `/getUser`, `/deleteOrder`는 RPC 시절의 습관입니다. REST에서는 `/users/{id}` + `DELETE` method로 표현합니다.

2. **모든 일을 POST로 처리합니다.** 조회도 POST, 삭제도 POST면 HTTP method의 의미론이 사라집니다. 캐시도 불가능하고, 브라우저 뒤로 가기도 안전하지 않습니다.

3. **서버 세션에 의존합니다.** 로그인 후 세션 쿠키를 서버 메모리에 저장하면, 로드 밸런서가 sticky session을 강제해야 합니다. 서버를 추가하거나 재시작할 때마다 문제가 생깁니다.

4. **에러도 200으로 반환합니다.** `{"success": false, "message": "not found"}`를 200으로 보내면, 모니터링 도구는 "에러 없음"으로 인식하고 CDN은 에러 응답을 캐시합니다.

5. **REST를 URL 패턴으로만 이해합니다.** "슬래시로 구분하고 복수형 쓰면 REST"라고 생각하면, stateless·cacheable·layered 같은 진짜 이점을 놓칩니다.

## 실무에서 REST가 선택되는 이유

GitHub, Stripe, GitLab, Slack 같은 공개 API는 대체로 REST 스타일(Level 2)을 따릅니다. 순수한 HATEOAS까지 밀어붙이는 경우는 드물지만, 리소스 중심 설계와 uniform interface는 사실상 업계 표준이 되었습니다.

REST가 기본 선택지가 된 현실적 이유는 다음과 같습니다.

- **도구 생태계:** OpenAPI, Swagger UI, Postman, curl 모두 REST 친화적입니다.
- **캐시 인프라:** HTTP 캐시, CDN, 브라우저 캐시가 GET 요청에 자연스럽게 동작합니다.
- **학습 비용:** 새 개발자가 합류해도 `/resources/{id}` + HTTP method 패턴만 알면 바로 이해합니다.
- **점진적 채택:** 기존 시스템에 REST endpoint를 하나씩 추가할 수 있습니다.

반면 GraphQL(클라이언트가 필드를 선택)이나 gRPC(바이너리 고성능)는 특정 조건에서 REST보다 유리하지만, 도입 비용이 높고 범용성이 낮습니다. **기본은 REST, 이득이 분명할 때만 다른 선택지**가 현업의 경향입니다.

## 시니어 엔지니어의 REST 설계 사고방식

1. **먼저 리소스의 경계를 정의합니다.** "이 API는 어떤 명사를 다루는가?"부터 시작합니다. 동사는 HTTP method에 맡깁니다.
2. **method가 상태 전이를 표현하게 둡니다.** POST는 생성, PUT은 전체 교체, PATCH는 부분 수정, DELETE는 삭제. 이 의미를 일관되게 유지합니다.
3. **캐시, 인증, 에러도 정식 계약으로 취급합니다.** `Cache-Control`, `Authorization` 헤더, 에러 응답 형태 모두 문서화합니다.
4. **REST를 종교처럼 다루지 않습니다.** 파일 업로드, 긴 작업(long-running operation), 이벤트 스트리밍처럼 REST에 억지로 끼워 맞추면 어색해지는 영역이 있습니다. 그때는 다른 방식을 선택합니다.
5. **항상 클라이언트 입장에서 예측 가능한가를 묻습니다.** "내가 이 API를 처음 보는 개발자라면, URL과 method만 보고 의도를 알 수 있는가?"

## 검증 포인트와 실패 신호

- **Expected output:** 같은 리소스에 `GET`, `POST`, `DELETE`를 매핑했을 때, URL을 바꾸지 않고도 읽기·생성·삭제 의도를 설명할 수 있어야 합니다.
- **First check:** 엔드포인트 설명에 `/getUser`, `/deleteOrder` 같은 동사가 반복되면 RPC over HTTP로 기울고 있다는 신호입니다.
- **Failure mode:** 인증 상태를 서버 세션에 묶거나 모든 응답을 `200 OK`로 보내기 시작하면 캐시, 재시도, 수평 확장 전략이 함께 약해집니다.

## 체크리스트

- [ ] URL에 동사가 없는가?
- [ ] 같은 method가 리소스마다 비슷한 의미를 가지는가?
- [ ] 응답에 적절한 cache header가 포함되는가?
- [ ] 인증 정보가 매 요청에 자기완결적으로 담기는가?
- [ ] 에러 status code가 모호하지 않은가?
- [ ] Richardson Maturity Model 기준으로 최소 Level 2를 충족하는가?

## 연습 문제

1. 익숙한 REST API(GitHub, Stripe, JSONPlaceholder 등) 하나를 골라 endpoint 다섯 개의 method, URL, 의미를 표로 정리해 보세요. 어떤 것이 Level 2이고 어떤 것이 Level 3에 가까운지 판단해 보세요.
2. Step 4 예제에 `PATCH /users/{id}`를 추가해 보세요. PUT과의 차이를 직접 구현하면서 확인합니다. (힌트: PUT은 전체 교체, PATCH는 부분 수정)
3. 같은 기능(사용자 CRUD)을 RPC over HTTP와 REST 두 방식으로 각각 설계해 보고, endpoint 수·캐시 가능성·문서화 편의성을 비교해 보세요.

## 정리와 다음 글

REST는 단순한 URL 컨벤션이 아니라, 여섯 가지 아키텍처 제약이 함께 만드는 **확장 가능한 설계 규율**입니다. 이 제약을 따르면 캐시, 수평 확장, 계층 추가가 자연스러워지고, 클라이언트 개발자의 학습 비용이 줄어듭니다.

다음 글에서는 REST의 핵심인 **리소스 설계**를 더 깊게 다룹니다. 어떤 단위로 리소스를 나누고, URL을 어떻게 구성하며, 관계를 어떻게 표현하는지 구체적인 패턴을 살펴봅니다.


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

- **REST는 어디서 나왔고 무엇을 뜻할까요?**
  - Roy Fielding이 2000년 박사 논문에서 웹의 확장성 원리를 형식화한 아키텍처 스타일입니다. "리소스의 표현(Representation)을 통해 상태(State)를 전달(Transfer)한다"는 뜻이며, 프로토콜이 아니라 제약의 집합입니다.
- **REST를 이루는 여섯 가지 아키텍처 제약은 무엇일까요?**
  - Client-Server 분리, Stateless, Cacheable, Uniform Interface, Layered System, Code on Demand(선택)입니다. 처음 다섯 가지가 필수이며, 함께 적용될 때 웹 규모의 확장성과 예측 가능성을 만들어 냅니다.
- **리소스 중심 사고는 RPC 스타일과 어떻게 다를까요?**
  - RPC는 "무엇을 할 것인가(동사)"를 URL에 표현하고, REST는 "무엇에 대해(명사)"를 URL에 두고 동작은 HTTP method에 맡깁니다. 이 차이로 REST는 캐시 친화적이고, endpoint 패턴이 예측 가능하며, 새 리소스를 추가해도 동일한 규칙이 반복됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [API Design 101 (1/10): API란 무엇인가?](./01-what-is-an-api.md)
- **REST 기본 (현재 글)**
- 리소스 설계 (예정)
- HTTP method와 status code (예정)
- Request와 response schema (예정)
- Pagination과 filtering (예정)
- Error response 설계 (예정)
- OpenAPI와 Swagger (예정)
- Versioning (예정)
- 좋은 API 문서 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [API Design 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/api-design-101/ko)
- [Roy Fielding — Architectural Styles (Ch. 5)](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [REST API Tutorial (restfulapi.net)](https://restfulapi.net/)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [Richardson Maturity Model (Martin Fowler)](https://martinfowler.com/articles/richardsonMaturityModel.html)
- [Google API Design Guide — Resource Oriented Design](https://cloud.google.com/apis/design/resources)

Tags: Computer Science, APIDesign, REST, HTTP, Backend, WebDevelopment
