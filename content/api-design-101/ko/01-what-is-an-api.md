---
title: API란 무엇인가?
series: api-design-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
  - Computer Science
  - APIDesign
  - REST
  - HTTP
  - Backend
  - WebDevelopment
last_reviewed: '2026-05-12'
seo_description: API의 정의, 역할, 좋은 API의 조건을 시리즈의 첫 글에서 정리합니다.
---

# API란 무엇인가?

이 글은 API Design 101 시리즈의 첫 번째 글입니다. 이후 글이 모두 자연스럽게 이어지려면, 먼저 API가 정확히 무엇이고 어떤 역할을 하며 무엇이 좋은 API를 만드는지부터 분명하게 잡아 둘 필요가 있습니다.

## 이 글에서 다룰 문제

- API는 정확히 무엇이며, 왜 시스템의 외부 계약이라고 부를까요?
- 라이브러리 API와 웹 API는 무엇이 같고 무엇이 다를까요?
- 좋은 API라고 부르려면 어떤 조건을 갖춰야 할까요?
- 클라이언트와 서버는 API를 사이에 두고 어떤 계약을 맺는 걸까요?
- 이 시리즈 전체는 어떤 흐름으로 이어질까요?

## 왜 중요한가

API는 시스템의 얼굴입니다. 내부 구현은 얼마든지 바뀔 수 있지만 API가 안정적으로 유지되면 외부 사용자는 영향을 적게 받습니다. 반대로 API가 흔들리면, 내부의 작은 수정 하나가 외부에서는 큰 장애처럼 번질 수 있습니다.

> 좋은 API는 쉽게 바뀌는 인터페이스가 아니라 오래 유지되는 약속에 가깝습니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Client["Client"] -->|"request"| API["API contract"]
    API --> Server["Server (impl)"]
    Server -->|"response"| API
    API --> Client
```

클라이언트가 알아야 하는 것은 서버 내부가 아니라 계약입니다.

## 핵심 용어

- **API (Application Programming Interface)**: 호출하는 쪽과 제공하는 쪽 사이의 계약입니다.
- **Endpoint**: 호출 대상입니다. 보통 URL과 HTTP method의 조합을 뜻합니다.
- **Request/Response**: 호출과 응답의 단위입니다.
- **Contract**: 입력과 출력의 형태, 그리고 그 의미입니다.
- **Versioning**: 시간이 지나면서 계약이 어떻게 바뀌는지 관리하는 방식입니다.

## Before / After

**Before (계약이 없음)**

```python
# the client has to know the server's internals
data = open("/var/db/users.json").read()
```

클라이언트가 서버 내부 파일 구조까지 알아야 합니다.

**After (API를 사용함)**

```python
# only the contract is required
import requests
data = requests.get("https://api.example.com/users").json()
```

계약만 유지되면 내부 구현은 바뀌어도 됩니다.

## 실습: API를 이해하는 다섯 단계

### Step 1 — Call a library API

```python
# 1_lib_api.py
import json
data = json.dumps({"a": 1})
print(data)
```

`json.dumps`도 API입니다. 약속된 입력을 넣으면 약속된 출력이 나옵니다.

### Step 2 — Call a web API

```python
# 2_web_api.py
import requests
r = requests.get("https://api.github.com/repos/python/cpython")
print(r.status_code, r.json()["full_name"])
```

웹 API에서는 HTTP가 가장 흔한 전송 수단입니다.

### Step 3 — Look at the contract

```python
# 3_contract.py
# from https://docs.github.com/en/rest, GET /repos/{owner}/{repo}
# - input: owner, repo (path)
# - output: 200 OK + JSON (full_name, stargazers_count, ...)
```

문서는 단순한 설명서가 아니라 계약 그 자체입니다.

### Step 4 — A minimal server

```python
# 4_min_server.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/health")
def health(): return jsonify(status="ok")

if __name__ == "__main__":
    app.run(port=8000)
```

가장 작은 계약은 `GET /health`가 `{"status": "ok"}`를 돌려준다는 약속입니다.

### Step 5 — Verify with a client

```python
# 5_call.py
import requests
r = requests.get("http://localhost:8000/health")
assert r.status_code == 200
assert r.json() == {"status": "ok"}
```

테스트는 계약이 실제로 지켜지는지 검증합니다.

## 이 코드에서 봐야 할 점

- 클라이언트는 서버 내부 구현을 몰라도 됩니다.
- 계약만 유지된다면 구현은 자유롭게 바꿀 수 있습니다.
- 상태 코드와 본문은 응답 계약의 두 축입니다.

## 자주 하는 실수 다섯 가지

1. **계약 문서 없이 시작합니다.** 클라이언트가 구현을 추측해야 합니다.
2. **상태 코드를 무시합니다.** 모든 응답을 200으로 돌려보냅니다.
3. **에러 본문이 제각각입니다.** 클라이언트가 일관되게 파싱할 수 없습니다.
4. **버전 없이 배포합니다.** 변경이 곧 외부 장애가 됩니다.
5. **클라이언트 관점 없이 설계합니다.** 쓰는 사람의 경험이 빠집니다.

## 실무에서는 이렇게 드러납니다

GitHub REST API, Stripe API, Google Maps API는 모두 문서화된 계약입니다. 내부 시스템에서도 OpenAPI나 Swagger가 같은 역할을 합니다. 성숙한 팀일수록 내부 API도 외부 공개 API처럼 관리합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 코드보다 먼저 계약을 그립니다.
- 항상 클라이언트 관점에서 호출해 봅니다.
- 상태 코드와 본문을 함께 설계합니다.
- 에러에도 별도의 형태를 부여합니다.
- 문서는 코드와 함께 진화하게 만듭니다.

## 체크리스트

- [ ] 이 API에 공개 문서가 있는가?
- [ ] 입력과 출력의 형태가 명시적인가?
- [ ] 상태 코드 목록이 명시적인가?
- [ ] 에러 본문의 형태가 일관적인가?
- [ ] 클라이언트 예제가 함께 제공되는가?

## 연습 문제

1. 자주 쓰는 라이브러리에서 API 함수 다섯 개를 골라 입력과 출력을 표로 정리해 보세요.
2. 공개 웹 API 문서를 하나 읽고 실제로 endpoint 하나를 호출해 보세요.
3. 작은 Flask 서버를 띄우고 `/health` 계약을 직접 정의해 보세요.

## 정리와 다음 글

API는 계약입니다. 이 시리즈의 다음 글에서는 그 계약이 가장 자주 구현되는 형태인 REST의 기본을 다룹니다.

<!-- toc:begin -->
- **API란 무엇인가? (현재 글)**
- REST 기본 (예정)
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

- [What is an API? (MDN)](https://developer.mozilla.org/en-US/docs/Glossary/API)
- [GitHub REST API](https://docs.github.com/en/rest)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [Flask Quickstart](https://flask.palletsprojects.com/quickstart/)

Tags: Computer Science, APIDesign, REST, HTTP, Backend, WebDevelopment
