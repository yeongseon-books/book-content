
# HTTP와 API

> Web Development 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 클라이언트와 서버는 *무엇* 을 주고받나요?

> 요청(method/url/header/body)과 응답(status/header/body) — 이게 *전부* 입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- HTTP 요청과 응답의 구조
- method (GET/POST/PUT/DELETE)와 status code
- 헤더의 역할
- JSON API 호출과 파싱
- API와 단순 페이지 요청의 차이

## 왜 중요한가

웹 개발의 절반은 *HTTP 메시지를 만들고 읽는 일* 입니다. 메시지의 모양을 모르면 디버깅이 추측 게임이 됩니다. 한 번만 정확히 익혀두면 어떤 프레임워크에서도 통합니다.

> HTTP는 *문자로 된 약속* 입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Client["Client"] -->|"GET /users/1"| Server["Server"]
    Server -->|"200 OK + JSON"| Client
```

요청 한 줄, 응답 한 줄.

## 핵심 용어 정리

- **Method**: 무엇을 할지 (GET = 읽기, POST = 만들기 등).
- **Status code**: 결과 (2xx 성공, 4xx 클라이언트 오류, 5xx 서버 오류).
- **Header**: 메타정보 (Content-Type, Authorization 등).
- **Body**: 실제 데이터 (JSON, HTML, 이미지 등).
- **API**: 코드가 호출하는 *프로그래밍용 엔드포인트*.

## Before/After

**Before (HTML 페이지 요청)**

```python
import requests
r = requests.get("https://example.com")
print(r.text[:80])  # <!doctype html>...
```

**After (JSON API 호출)**

```python
import requests
r = requests.get("https://api.github.com/repos/python/cpython")
data = r.json()
print(data["full_name"], data["stargazers_count"])
```

같은 HTTP, 다른 *Content-Type*.

## 실습: HTTP 메시지 5단계

### 1단계 — GET 요청

```python
# 1_get.py
import requests
r = requests.get("https://httpbin.org/get?lang=ko")
print(r.status_code)
print(r.json()["args"])  # {'lang': 'ko'}
```

### 2단계 — POST로 데이터 보내기

```python
# 2_post.py
import requests
r = requests.post("https://httpbin.org/post", json={"name": "yeongseon"})
print(r.json()["json"])
```

### 3단계 — 헤더 살펴보기

```python
# 3_headers.py
import requests
r = requests.get("https://httpbin.org/headers", headers={"X-Custom": "hi"})
print(r.json()["headers"]["X-Custom"])
```

### 4단계 — Status code 분기

```python
# 4_status.py
import requests
for url in ["https://httpbin.org/status/200", "https://httpbin.org/status/404"]:
    r = requests.get(url)
    if r.ok:
        print("OK", r.status_code)
    else:
        print("FAIL", r.status_code)
```

### 5단계 — 직접 raw로 보기

```bash
curl -v https://httpbin.org/get
# > GET /get HTTP/1.1
# > Host: httpbin.org
# < HTTP/1.1 200 OK
# < Content-Type: application/json
```

## 이 코드에서 주목할 점

- `Content-Type` 이 `text/html` 인지 `application/json` 인지가 *전부* 를 가른다.
- POST는 *서버 상태를 바꿀 수 있다* 는 약속이다.
- 같은 URL이 method에 따라 다르게 동작한다.

## 자주 하는 실수 5가지

1. **GET으로 데이터를 만든다.** GET은 *읽기 전용* 약속.
2. **모든 응답을 200으로 보낸다.** 클라이언트가 오류를 못 걸러낸다.
3. **`Content-Type` 을 안 본다.** JSON인 척 HTML을 파싱한다.
4. **에러 본문이 자유 형식.** 클라이언트가 메시지를 못 꺼낸다.
5. **인증 헤더를 URL에 넣는다.** 로그에 그대로 남는다.

## 실무에서는 이렇게 쓰입니다

대부분의 모바일/웹 앱은 *JSON over HTTP* 로 서버와 통신합니다. GraphQL, gRPC도 결국 HTTP 위에서 동작합니다. 새 서비스를 다룰 때 가장 먼저 보는 것이 *API 문서* 인 이유입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- method와 status code의 *의미* 를 정확히 쓴다.
- 에러 본문을 *형식화* 한다.
- 인증은 *헤더* 로, 토큰은 *짧은 수명* 으로.
- 응답에 항상 *시간 예산* 을 둔다 (timeout).
- API는 *문서가 코드와 함께 자란다*.

## 체크리스트

- [ ] 4가지 method의 의미를 안다.
- [ ] 2xx/4xx/5xx의 범위를 안다.
- [ ] `Content-Type` 헤더를 읽고 분기할 수 있다.
- [ ] timeout과 retry를 설정할 수 있다.
- [ ] curl로 raw 요청을 던질 수 있다.

## 연습 문제

1. `httpbin.org` 의 `/anything` 엔드포인트에 GET/POST/PUT/DELETE를 각각 보내고 응답을 비교하세요.
2. 3xx 응답을 받았을 때 redirect를 따라가지 *않는* 코드를 작성하세요.
3. 좋아하는 공개 API 한 개를 골라 *3개의 엔드포인트* 를 호출해 보세요.

## 정리 및 다음 단계

HTTP는 *문자로 된 약속* 입니다. 다음 글에서는 그 약속의 양쪽 — Frontend와 Backend — 의 분리를 봅니다.

- [웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [브라우저와 DOM](./03-browser-and-dom.md)
- **HTTP와 API (현재 글)**
- Frontend와 Backend (예정)
- 인증과 세션 (예정)
- 데이터베이스 연결 (예정)
- 배포 (예정)
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)
## 참고 자료

- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [HTTP methods (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [HTTP status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [httpbin (request/response service)](https://httpbin.org/)

Tags: Computer Science, WebDevelopment, HTTP, API, REST, Networking

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
