---
series: web-development-101
episode: 4
title: "바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - HTTP
  - API
  - REST
  - 네트워킹
seo_description: 바이브코딩으로 만드는 웹앱에서 HTTP 요청과 API 호출을 이해하고 디버깅하는 방법을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 네 번째 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다.

---

바이브코딩으로 만든 앱에서 가장 자주 막히는 부분이 API 연결입니다. "API가 안 돼요"라는 말은 매우 광범위합니다. 요청을 잘못 보내는 건지, 서버가 오류를 돌려주는 건지, 인증이 없는 건지, URL이 틀린 건지 구분하지 못하면 AI에게 제대로 된 도움을 요청할 수 없습니다.

HTTP 메시지의 모양을 알면 이 모든 구분이 가능해집니다. 요청 method, URL, 헤더, 본문을 보내고, 서버는 상태 코드, 헤더, 본문으로 응답합니다. 이 틀을 알면 DevTools의 Network 탭에서 요청 하나를 열어보는 것만으로 문제의 위치를 좁힐 수 있습니다.

바이브코딩에서 API는 피할 수 없습니다. 날씨 정보를 가져오든, 로그인을 처리하든, 데이터를 저장하든 모두 HTTP API를 통합니다. 이 글에서는 HTTP 요청과 응답의 구조, method와 상태 코드의 의미, API 호출이 페이지 요청과 어떻게 다른지 정리합니다.

> HTTP는 method·status·header·body로 구성된 텍스트 메시지의 왕복입니다. 바이브코딩 중 API 오류는 대부분 이 구조를 모르면 어디가 틀렸는지 보이지 않습니다.

## 이 글에서 다룰 문제

- 클라이언트와 서버는 실제로 무엇을 주고받을까요?
- HTTP 요청과 응답은 어떤 요소로 구성될까요?
- GET, POST, PUT, DELETE는 각각 어떤 의미일까요?
- 상태 코드로 어떻게 오류를 구분할까요?
- 바이브코딩 중 API 문제를 어떻게 진단할까요?

## 바이브코딩 관점: HTTP를 알아야 하는 이유

AI가 만들어준 코드에 `fetch('/api/todos')`가 있다면, 이것은 GET 요청입니다. 데이터를 저장하려면 `fetch('/api/todos', { method: 'POST', body: ... })`가 필요합니다. 이 차이를 모르면 "데이터가 저장이 안 돼요"라는 문제를 AI에게 설명할 때도 핵심 정보를 빠뜨리게 됩니다.

상태 코드도 마찬가지입니다. 서버가 `404`를 돌려준다면 "URL이 존재하지 않는다"는 의미입니다. `401`은 "인증이 필요하다", `500`은 "서버 내부 오류"입니다. 이 코드들을 알면 "404 에러가 나는데 왜 그런지 봐줘"처럼 AI에게 구체적으로 질문할 수 있습니다.

## 먼저 알아둘 용어

- **Method**: 무엇을 하려는지 나타냅니다. GET은 조회, POST는 생성에 자주 씁니다.
- **Status code**: 요청 결과를 나타냅니다. 2xx는 성공, 4xx는 클라이언트 오류, 5xx는 서버 오류입니다.
- **Header**: `Content-Type`, `Authorization` 같은 메타데이터입니다.
- **Body**: JSON, HTML처럼 실제 데이터가 들어가는 영역입니다.
- **API**: 프로그램이 호출하도록 설계된 엔드포인트입니다.

## Before / After: 요청 대상의 차이

**Before — HTML 페이지 요청**

```python
import requests
r = requests.get("https://example.com")
print(r.text[:80])  # <!doctype html>...
```

**After — JSON API 호출**

```python
import requests
r = requests.get("https://api.github.com/repos/python/cpython")
data = r.json()
print(data["full_name"], data["stargazers_count"])
```

둘 다 HTTP지만 응답의 `Content-Type`이 다릅니다. 전자는 HTML, 후자는 JSON입니다. AI가 만들어준 코드에서 이 차이를 구분해야 응답을 올바르게 처리할 수 있습니다.

## HTTP 메시지를 다섯 단계로 읽어 보기

### 1단계 — GET 요청 보내기

```python
import requests
r = requests.get("https://httpbin.org/get?lang=ko")
print(r.status_code)         # 200
print(r.json()["args"])      # {'lang': 'ko'}
```

### 2단계 — POST로 본문 보내기

```python
import requests
r = requests.post("https://httpbin.org/post", json={"name": "alice"})
print(r.json()["json"])      # {'name': 'alice'}
```

### 3단계 — 헤더 확인하기

```python
import requests
r = requests.get("https://httpbin.org/headers", headers={"Authorization": "Bearer TOKEN"})
print(r.json()["headers"]["Authorization"])
```

### 4단계 — 상태 코드로 분기하기

```python
import requests
for url in ["https://httpbin.org/status/200", "https://httpbin.org/status/404"]:
    r = requests.get(url)
    if r.ok:
        print("OK", r.status_code)
    else:
        print("FAIL", r.status_code)
```

### 5단계 — raw 요청 보기

```bash
curl -v https://httpbin.org/get
# > GET /get HTTP/1.1
# > Host: httpbin.org
# < HTTP/1.1 200 OK
# < Content-Type: application/json
```

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| GET으로 데이터 생성 시도 | method 의미 모름 | POST/PUT/PATCH가 데이터 변경에 적합 |
| 404인데 "서버가 다운됐나" 의심 | 상태 코드 모름 | 404는 URL이 없다는 의미, 500이 서버 오류 |
| `Content-Type` 헤더 빠뜨림 | 헤더 중요성 모름 | JSON 전송 시 `application/json` 필수 |
| 모든 응답을 성공으로 처리 | 에러 처리 부재 | `r.ok` 또는 상태 코드로 분기 필요 |
| API 키를 URL에 포함 | 보안 무지 | Authorization 헤더로 전달해야 로그에 안 남음 |

## AI 팁: API 오류 설명 방법

```
"API 호출 시 다음 오류가 발생합니다:
- URL: POST https://api.example.com/todos
- 상태 코드: 422
- 응답 본문: {"error": "text field is required"}
요청 본문을 어떻게 수정해야 하는지 알려주세요."
```

URL, method, 상태 코드, 응답 본문을 모두 포함하면 AI가 정확하게 진단합니다.

## 체크리스트

- [ ] 네 가지 기본 method의 의미를 알고 있습니다.
- [ ] 2xx, 4xx, 5xx 범위의 뜻을 알고 있습니다.
- [ ] `Content-Type`을 읽고 처리 분기를 할 수 있습니다.
- [ ] DevTools Network 탭에서 API 요청을 분석할 수 있습니다.
- [ ] `curl`로 raw 요청을 날릴 수 있습니다.

## 처음 질문으로 돌아가기

- **클라이언트와 서버는 실제로 무엇을 주고받을까요?**
  method, URL, header, body로 구성된 요청을 보내고, status code, header, body로 구성된 응답을 받습니다.

- **GET, POST, PUT, DELETE는 각각 어떤 의미일까요?**
  GET은 조회, POST는 생성, PUT/PATCH는 수정, DELETE는 삭제입니다. 같은 URL이라도 method에 따라 서버가 다르게 동작합니다.

- **상태 코드로 어떻게 오류를 구분할까요?**
  200대는 성공, 400은 요청 형식 오류, 401은 인증 필요, 403은 권한 없음, 404는 없는 URL, 500은 서버 내부 오류입니다.

## 정리

HTTP 메시지의 구조를 알면 바이브코딩 중 API 문제가 생겼을 때 "어느 단계에서 무엇이 잘못됐는지"를 빠르게 좁힐 수 있습니다. DevTools Network 탭을 열어 요청 하나를 클릭하고, method, 상태 코드, 헤더, 본문을 확인하는 습관이 핵심입니다. 다음 글에서는 Frontend와 Backend의 책임 경계를 정리합니다.

## 참고 자료

- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [HTTP request methods (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [HTTP response status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)
- [httpbin](https://httpbin.org/)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- **바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API (현재 글)**
- [바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [바이브코딩을 위한 웹 개발 기초 (8/10): 배포](./08-deployment.md)
- [바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, HTTP, API, REST, 네트워킹
