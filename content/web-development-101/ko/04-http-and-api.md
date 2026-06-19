---
series: web-development-101
episode: 4
title: "Web Development 101 (4/10): HTTP와 API"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/206"
    published_at: '2026-05-26'
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - WebDevelopment
  - HTTP
  - API
  - REST
  - Networking
seo_description: HTTP 요청과 응답, 상태 코드, JSON API의 기본 구조를 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (4/10): HTTP와 API

웹 개발을 하다 보면 결국 가장 많이 읽고 쓰는 것은 HTTP 메시지입니다. 브라우저가 페이지를 요청할 때도, JavaScript가 JSON 데이터를 가져올 때도, 모바일 앱이 서버와 통신할 때도 바닥에는 HTTP가 놓여 있습니다. 요청과 응답의 모양을 정확히 모르면 디버깅은 금방 추측 게임으로 바뀝니다.

이 글은 Web Development 101 시리즈의 4번째 글입니다.

여기서는 HTTP 요청과 응답이 어떤 형태를 가지는지, method와 status code와 header가 각각 어떤 의미를 가지는지, API 호출이 페이지 요청과 무엇이 다른지 정리하겠습니다.

![Web Development 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/04/04-01-concept-at-a-glance.ko.png)
*Web Development 101 4장 흐름 개요*

> HTTP는 method·status·header·body로 구성된 텍스트 메시지의 왕복이고, API 호출은 페이지 요청과 같은 프로토콜 위에서 데이터 모양만 달리한 호출일 뿐입니다 — 이 모양이 보이지 않으면 디버깅은 곧장 추측 게임이 됩니다.

## 이 글에서 다룰 문제

- 클라이언트와 서버는 실제로 무엇을 주고받을까요?
- HTTP 요청과 응답은 어떤 요소로 구성될까요?
- GET, POST, PUT, DELETE는 각각 어떤 의미일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 구조를 알아야 하는가

웹 개발의 절반은 HTTP 메시지를 만들고 읽는 일입니다. 요청이 어떤 method로 갔는지, 응답이 왜 404인지, 서버가 JSON을 줬는지 HTML을 줬는지를 읽지 못하면 오류 원인을 좁히기 어렵습니다. 프레임워크는 이 메시지를 다루기 쉽게 감싸 줄 뿐, 메시지 자체를 없애 주지는 않습니다.

## HTTP 메시지 구조

### 요청 (Request)

```http
POST /api/v1/todos HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Accept: application/json
X-Request-Id: req-2026-06-20-0042

{
  "text": "문서 작성하기",
  "priority": "high"
}
```

```
┌─────────────────────────────────────────────┐
│  Request Line: POST /api/v1/todos HTTP/1.1  │  ← method + path + version
│  Headers:                                   │
│    Host: api.example.com                    │  ← 필수: 어느 서버인지
│    Content-Type: application/json           │  ← body 형식
│    Authorization: Bearer <token>            │  ← 인증 정보
│  ─────────────────────────────────────────  │
│  Body:                                      │
│    {"text": "문서 작성하기"}                │  ← 실제 데이터
└─────────────────────────────────────────────┘
```

### 응답 (Response)

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/todos/123
Cache-Control: no-store
X-Request-Id: req-2026-06-20-0042

{
  "id": 123,
  "text": "문서 작성하기",
  "priority": "high",
  "done": false,
  "created_at": "2026-06-20T09:00:00Z"
}
```

## HTTP Method의 의미

```
Method    의미               멱등성  안전성  Body
─────────────────────────────────────────────────
GET       리소스 조회         O       O      X
POST      리소스 생성/처리    X       X      O
PUT       리소스 전체 교체    O       X      O
PATCH     리소스 부분 수정    X       X      O
DELETE    리소스 삭제         O       X      X
HEAD      GET이지만 body 없음 O       O      X
OPTIONS   지원 method 조회    O       O      X
```

**멱등성**: 같은 요청을 여러 번 보내도 결과가 같다. GET /users/1을 10번 해도 같은 사용자가 반환됨.

**안전성**: 서버 상태를 바꾸지 않는다. GET은 읽기만 하므로 안전하지만, POST는 서버 상태를 변경할 수 있어 안전하지 않음.

## HTTP Status Code

```
범위    의미
─────────────────────────────────────────────────
1xx    정보성 (100 Continue, 101 Switching Protocols)
2xx    성공 (200 OK, 201 Created, 204 No Content)
3xx    리다이렉트 (301 Moved, 302 Found, 304 Not Modified)
4xx    클라이언트 오류 (400 Bad Request, 401, 403, 404, 409, 422)
5xx    서버 오류 (500, 502 Bad Gateway, 503 Service Unavailable)
```

```
자주 쓰는 코드:
200 OK          — 성공적인 GET, PUT, PATCH
201 Created     — 성공적인 POST (새 리소스 생성)
204 No Content  — 성공적인 DELETE (응답 body 없음)
400 Bad Request — 잘못된 요청 형식, 유효성 검사 실패
401 Unauthorized — 인증 필요 (로그인 안 됨)
403 Forbidden   — 권한 없음 (로그인은 됐지만 접근 불가)
404 Not Found   — 리소스 없음
409 Conflict    — 충돌 (이미 존재하는 데이터)
422 Unprocessable — 형식은 맞지만 내용이 처리 불가
429 Too Many Requests — 요청 속도 초과
500 Internal Server Error — 서버 내부 오류
503 Service Unavailable — 서버 과부하 또는 점검
```

## HTTP 헤더

```http
# 요청 헤더
Host: api.example.com              # 가상 호스팅 대상
Authorization: Bearer <token>      # 인증 토큰
Content-Type: application/json     # 요청 body 형식
Accept: application/json           # 원하는 응답 형식
Accept-Language: ko-KR,ko;q=0.9   # 선호 언어
X-Request-Id: req-abc123           # 요청 추적 ID

# 응답 헤더
Content-Type: application/json     # 응답 body 형식
Content-Length: 284                # body 크기 (bytes)
Cache-Control: max-age=3600        # 캐시 정책
ETag: "v1-abc123"                  # 버전 식별자
Location: /api/v1/todos/123        # 새 리소스 위치 (201 Created)
```

## REST API 설계

REST API는 HTTP method와 URL을 조합해 리소스를 표현합니다.

```
리소스: /api/v1/todos

GET    /api/v1/todos              — 목록 조회
POST   /api/v1/todos              — 생성
GET    /api/v1/todos/{id}         — 단건 조회
PUT    /api/v1/todos/{id}         — 전체 수정
PATCH  /api/v1/todos/{id}         — 부분 수정
DELETE /api/v1/todos/{id}         — 삭제

GET    /api/v1/users/{id}/todos   — 특정 사용자의 할 일 목록
```

```
좋은 URL:
  GET /api/v1/todos?status=done&limit=20

나쁜 URL:
  GET /api/v1/getTodoList
  POST /api/v1/deleteTodo
  GET /api/v1/todo_list
```

리소스 이름은 복수형 명사로, 동작은 HTTP method로 표현합니다.

## 실제 HTTP 요청 보내기

### curl로 테스트

```bash
# GET
curl https://httpbin.org/get

# POST with JSON body
curl -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" \
  -d '{"name": "alice", "age": 30}'

# 헤더 확인
curl -I https://example.com

# Verbose 모드 (전체 요청/응답 보기)
curl -v https://httpbin.org/get

# 상태 코드만 추출
curl -o /dev/null -s -w "%{http_code}" https://example.com

# Bearer 토큰으로 인증
curl -H "Authorization: Bearer eyJ..." https://api.example.com/me
```

### Python으로 API 호출

```python
import requests

# GET
r = requests.get("https://httpbin.org/get", params={"lang": "ko"})
print(r.status_code)              # 200
print(r.headers["Content-Type"]) # application/json
print(r.json()["args"])           # {'lang': 'ko'}

# POST
r = requests.post(
    "https://httpbin.org/post",
    json={"name": "alice"},
    headers={"X-Request-Id": "req-001"}
)
print(r.json()["json"])  # {'name': 'alice'}

# 오류 처리
r = requests.get("https://httpbin.org/status/404")
if r.ok:              # status_code < 400
    print("성공")
else:
    print(f"실패: {r.status_code}")
    r.raise_for_status()  # HTTPError 발생
```

### JavaScript Fetch API

```js
// GET
const response = await fetch("/api/todos");
if (!response.ok) {
  throw new Error(`HTTP error: ${response.status}`);
}
const todos = await response.json();

// POST
const newTodo = await fetch("/api/todos", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  },
  body: JSON.stringify({ text: "새 할 일" }),
});

// 응답 처리
const created = await newTodo.json();
console.log(created.id);  // 서버가 할당한 ID

// 에러 응답 형식
if (!newTodo.ok) {
  const error = await newTodo.json();
  // { "error": { "code": "VALIDATION_ERROR", "message": "text is required" } }
  console.error(error.error.message);
}
```

## 오류 응답 형식 표준화

일관된 오류 형식이 없으면 프론트엔드가 오류 메시지를 처리하기 어렵습니다.

```json
// 통일된 오류 응답 형식 예시
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "text 필드는 필수입니다",
    "field": "text",
    "request_id": "req-2026-06-20-0042"
  }
}
```

```python
# Flask 예시: 일관된 오류 응답
from flask import Flask, jsonify, request

app = Flask(__name__)

def error_response(code, message, status_code, field=None):
    body = {"error": {"code": code, "message": message}}
    if field:
        body["error"]["field"] = field
    return jsonify(body), status_code

@app.post("/api/todos")
def create_todo():
    data = request.get_json()
    if not data or not data.get("text"):
        return error_response("VALIDATION_ERROR", "text 필드는 필수입니다", 400, "text")
    # ... 생성 로직
    return jsonify({"id": 1, "text": data["text"]}), 201
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 방법 |
|------|------|-------------|
| GET으로 데이터 생성 | 멱등성 위반, 캐시 오염 | 생성은 POST, 수정은 PUT/PATCH |
| 모든 오류 응답을 200으로 반환 | 프론트엔드가 실패 감지 불가 | 상황에 맞는 4xx/5xx 코드 사용 |
| `Content-Type` 헤더 누락 | 서버가 body 형식 해석 실패 | 항상 body가 있으면 `Content-Type` 명시 |
| 오류 응답 형식을 매 엔드포인트마다 다르게 | 클라이언트 파싱 코드 복잡화 | 오류 구조를 API 전체에서 통일 |
| 인증 정보를 URL에 넣기 | 로그에 토큰 노출 | `Authorization` 헤더로 전송 |
| timeout 없이 HTTP 호출 | 응답 안 오면 영원히 대기 | requests.get(url, timeout=5) |

## 직접 검증해 볼 포인트

```bash
# 1. GET/POST 차이 확인
curl https://httpbin.org/get
curl -X POST https://httpbin.org/post -H "Content-Type: application/json" -d '{}'

# 2. 다양한 상태 코드 재현
curl -o /dev/null -s -w "%{http_code}" https://httpbin.org/status/200
curl -o /dev/null -s -w "%{http_code}" https://httpbin.org/status/404
curl -o /dev/null -s -w "%{http_code}" https://httpbin.org/status/500

# 3. 리다이렉트 추적
curl -L https://httpbin.org/redirect/3
curl -v https://httpbin.org/redirect/1 2>&1 | grep "< HTTP"
```

**기대 결과:** GET과 POST는 같은 URL이라도 다른 의도를 드러내고, JSON API는 `application/json` 헤더와 함께 구조화된 본문을 돌려줍니다.

**실패 모드:** 모든 실패 응답을 200으로 돌려주면 클라이언트는 오류를 분기하기 어렵습니다. `Content-Type`을 무시하면 HTML과 JSON을 잘못 해석하는 버그가 생깁니다.

## 운영에서는 이렇게 보입니다

대부분의 웹과 모바일 앱은 JSON over HTTP 형태로 서버와 통신합니다. GraphQL과 gRPC도 결국 HTTP 위에 서 있습니다. 새 서비스를 처음 볼 때 API 문서를 먼저 읽는 이유도 여기에 있습니다. 요청과 응답의 형식이 시스템 계약의 중심이기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- method와 status code를 본래 의미에 맞게 씁니다.
- 오류 응답의 형식을 표준화합니다.
- 인증 정보는 header로 보내고, 토큰 수명은 짧게 둡니다.
- timeout과 retry 예산을 항상 같이 봅니다.
- API와 문서는 함께 자라야 한다고 생각합니다.

## 운영 체크리스트

- [ ] 네 가지 기본 method의 의미를 알고 있습니다.
- [ ] 2xx, 4xx, 5xx 범위의 뜻을 알고 있습니다.
- [ ] `Content-Type`을 읽고 처리 분기를 할 수 있습니다.
- [ ] timeout과 retry를 설정할 수 있습니다.
- [ ] `curl`로 raw 요청을 날릴 수 있습니다.

## 연습 문제

1. `httpbin.org/anything`에 GET, POST, PUT, DELETE를 보내고 응답 차이를 비교해 보세요.
2. 3xx redirect를 따라가지 않는 코드를 작성해 보세요.
3. 공개 API 하나를 골라 세 개 이상의 엔드포인트를 호출해 보세요.

## 정리와 다음 글

HTTP는 문자 기반 계약이지만, 웹 개발에서는 가장 중요한 바닥 구조입니다. 요청과 응답의 모양을 알면 API를 읽고 서버를 디버깅하는 속도가 달라집니다. 다음 글에서는 이 계약의 양쪽 끝, Frontend와 Backend의 책임 경계를 정리하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- **Web Development 101 (4/10): HTTP와 API (현재 글)**
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [Web Development 101 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [Web Development 101 (8/10): 배포](./08-deployment.md)
- [Web Development 101 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [HTTP request methods (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [HTTP response status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)

### 검증용 자료
- [httpbin](https://httpbin.org/)
- [HTTP Semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, HTTP, API, REST, Networking
