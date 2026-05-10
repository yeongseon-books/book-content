---
series: api-design-101
episode: 2
title: REST 기본
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - APIDesign
  - REST
  - HTTP
  - Backend
  - WebDevelopment
seo_description: REST의 6가지 제약과 자원 중심 사고를 정리합니다 — 백엔드 주니어를 위한 안내.
last_reviewed: '2026-05-04'
---

# REST 기본

> API Design 101 시리즈 (2/10)


## 이 글에서 다룰 문제

REST는 가장 흔한 API 스타일입니다. 잘 따르면 *예측 가능* 하고, 잘못 따르면 *어디 한 번 본 적 있는데?* 가 됩니다. 핵심을 잡아두면 모든 후속 글이 쉬워집니다.

> 규칙을 외우기보다 *왜 그 규칙인지* 를 이해하세요.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Client["Client"] -->|"GET /users/42"| Server["Server"]
    Server -->|"200 OK + JSON"| Client
    Server --- DB[("Resources")]
```

자원은 URL로 식별되고, 동작은 HTTP method로 표현됩니다.

## Before/After

**Before (RPC 스타일)**

```
POST /getUser?id=42
POST /createUser
POST /deleteUser?id=42
```

동사가 URL에 들어가 있습니다.

**After (REST 스타일)**

```
GET    /users/42
POST   /users
DELETE /users/42
```

자원은 URL, 동작은 method.

## 실습: REST 6제약 따라가기

### 1단계 — Client-Server 분리

```python
# 1_client_server.py
# 클라이언트는 UI, 서버는 데이터 — 서로 *교체 가능* 해야 한다
import requests
print(requests.get("https://api.github.com").status_code)
```

서버 구현이 바뀌어도 클라이언트는 살아남습니다.

### 2단계 — Stateless 호출

```python
# 2_stateless.py
import requests
# 매 호출이 *자기 완결적* — 토큰을 매번 보낸다
headers = {"Authorization": "token TEST"}
requests.get("https://api.example.com/me", headers=headers)
```

서버는 세션을 *기억* 하지 않습니다 — 호출이 모든 정보를 가져야 합니다.

### 3단계 — Cacheable 응답

```python
# 3_cache.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/articles/1")
def article():
    resp = jsonify(id=1, title="REST 기본")
    resp.headers["Cache-Control"] = "public, max-age=60"
    return resp
```

응답이 캐시 가능한지 *명시* 합니다.

### 4단계 — Uniform Interface

```python
# 4_uniform.py
# 같은 자원에 대해 method만 바꾼다
# GET    /users/42  -> 조회
# PUT    /users/42  -> 교체
# DELETE /users/42  -> 삭제
```

호출 규칙이 *일관* 되어야 학습 비용이 줄어듭니다.

### 5단계 — Layered + Code on Demand

```python
# 5_layered.py
# Client -> CDN -> LB -> App -> DB
# 클라이언트는 *옆 계층* 만 압니다
```

중간에 캐시·게이트웨이가 들어가도 클라이언트 코드는 안 바뀝니다.

## 이 코드에서 주목할 점

- 동사는 *method* 가, 명사는 *URL* 이 표현합니다.
- 토큰은 매 호출에 — 세션을 *서버* 에 두지 않습니다.
- `Cache-Control` 같은 *부가 약속* 도 API의 일부입니다.

## 자주 하는 실수 5가지

1. **URL에 동사 사용.** `/getUser` — RPC 신호.
2. **POST로 모든 것.** method의 의미를 버림.
3. **세션 의존.** 서버를 *수평 확장* 못 함.
4. **에러를 200으로.** 클라이언트가 분기 못 함.
5. **REST를 *URL 규칙* 으로만 이해.** 6제약을 잊음.

## 실무에서는 이렇게 쓰입니다

GitHub, Stripe, GitLab — 대부분의 공개 API는 *대체로 REST* 입니다. 완벽한 HATEOAS는 드물지만 *자원 중심 + uniform interface* 는 표준이 되었습니다. 사내에서도 REST를 기본으로 두고, 필요할 때만 GraphQL이나 gRPC로 *추가* 합니다.

## 체크리스트

- [ ] URL에 동사가 없는가?
- [ ] 같은 method 의미를 모든 자원에서 지키는가?
- [ ] 응답에 적절한 cache 헤더가 있는가?
- [ ] 인증이 매 호출에 자기 완결적인가?
- [ ] 에러 상태 코드가 명확한가?

## 정리 및 다음 단계

REST는 *6제약* 의 합입니다. 다음 글에서는 그 중심인 — 자원(resource) 설계 — 를 자세히 봅니다.

<!-- toc:begin -->
- [API란 무엇인가?](./01-what-is-an-api.md)
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

- [Roy Fielding — Architectural Styles (Ch. 5)](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [REST API Tutorial (restfulapi.net)](https://restfulapi.net/)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [Richardson Maturity Model (Martin Fowler)](https://martinfowler.com/articles/richardsonMaturityModel.html)

Tags: Computer Science, APIDesign, REST, HTTP, Backend, WebDevelopment
