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

## 먼저 던지는 질문

- GET, POST, PUT, PATCH, DELETE는 각각 무엇을 의미할까요?
- safe와 idempotent는 어떻게 다를까요?
- 2xx, 3xx, 4xx, 5xx 계열은 어떻게 읽어야 할까요?

## 큰 그림

![API Design 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/api-design-101/04/04-01-concept-at-a-glance.ko.png)

*API Design 101 4장 흐름 개요*

클라이언트는 응답의 status code를 보고 재시도, 캐시, 에러 메시지 표시를 결정합니다. 그림은 요청이 들어오면 method로 의도를 판별하고, 처리 결과를 status code로 응답하는 흐름을 보여줍니다. method와 status는 항상 쌍으로 읽어야 합니다.

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
## Before / After

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

- [HTTP Methods (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [HTTP Status Codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [RFC 7231 — HTTP/1.1 Semantics](https://www.rfc-editor.org/rfc/rfc7231)
- [Idempotency in REST APIs (Stripe blog)](https://stripe.com/blog/idempotency)

Tags: Computer Science, APIDesign, HTTP, Methods, StatusCodes, Backend
