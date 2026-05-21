---
series: web-development-101
episode: 4
title: "Web Development 101 (4/10): HTTP와 API"
status: publish-ready
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

이 글은 Web Development 101 시리즈의 네 번째 글입니다. 여기서는 HTTP 요청과 응답이 어떤 형태를 가지는지, method와 status code와 header가 각각 어떤 의미를 가지는지, API 호출이 페이지 요청과 무엇이 다른지 정리하겠습니다.

## 먼저 던지는 질문

- 클라이언트와 서버는 실제로 무엇을 주고받을까요?
- HTTP 요청과 응답은 어떤 요소로 구성될까요?
- GET, POST, PUT, DELETE는 각각 어떤 의미일까요?

## 큰 그림

![Web Development 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/04/04-01-concept-at-a-glance.ko.png)

*Web Development 101 4장 흐름 개요*

## 왜 이 구조를 알아야 하는가

웹 개발의 절반은 HTTP 메시지를 만들고 읽는 일입니다. 요청이 어떤 method로 갔는지, 응답이 왜 404인지, 서버가 JSON을 줬는지 HTML을 줬는지를 읽지 못하면 오류 원인을 좁히기 어렵습니다. 프레임워크는 이 메시지를 다루기 쉽게 감싸 줄 뿐, 메시지 자체를 없애 주지는 않습니다.

한 번 HTTP의 모양을 익혀 두면 Flask, FastAPI, React, 모바일 앱, GraphQL, gRPC를 볼 때도 공통된 감각이 생깁니다. 이름은 달라도 많은 시스템이 결국 HTTP 위에서 움직이기 때문입니다.

## 한눈에 보는 개념 지도

그림을 볼 때는 요청과 응답이 모두 같은 틀을 가진다는 점을 먼저 기억하면 좋습니다. method, URL, header, body를 보낸 뒤 서버는 status code, header, body로 답합니다.

### 직접 검증해 볼 포인트

- `curl -v https://httpbin.org/get`으로 요청 줄과 응답 헤더를 그대로 확인합니다.
- GET과 POST를 각각 보내고 method에 따라 서버 동작이 달라지는지 비교합니다.
- JSON API 응답에서 `Content-Type: application/json`이 붙는지 확인합니다.

**기대 결과:** GET과 POST는 같은 URL이라도 다른 의도를 드러내고, JSON API는 `application/json` 헤더와 함께 본문 구조를 돌려줍니다.

**실패 모드:** 모든 실패 응답을 200으로 돌려주면 클라이언트는 오류를 분기하기 어렵습니다. `Content-Type`을 무시하면 HTML과 JSON을 잘못 해석하는 버그가 생깁니다.

## 먼저 알아둘 용어

- **Method**: 무엇을 하려는지 나타냅니다. GET은 조회, POST는 생성에 자주 씁니다.
- **Status code**: 요청 결과를 나타냅니다. 2xx는 성공, 4xx는 클라이언트 오류, 5xx는 서버 오류입니다.
- **Header**: `Content-Type`, `Authorization` 같은 메타데이터입니다.
- **Body**: JSON, HTML, 이미지 바이트처럼 실제 payload가 들어가는 영역입니다.
- **API**: 브라우저 사람이 아니라 프로그램이 호출하도록 설계된 엔드포인트입니다.

## Before / After로 보는 요청 대상의 차이

**Before (HTML page request)**

```python
import requests
r = requests.get("https://example.com")
print(r.text[:80])  # <!doctype html>...
```

**After (JSON API call)**

```python
import requests
r = requests.get("https://api.github.com/repos/python/cpython")
data = r.json()
print(data["full_name"], data["stargazers_count"])
```

둘 다 HTTP이지만 응답의 `Content-Type`이 다릅니다. 전자는 HTML 문서, 후자는 JSON 데이터입니다.

## HTTP 메시지를 다섯 단계로 읽어 보기

### 1단계 — GET 요청 보내기

```python
# 1_get.py
import requests
r = requests.get("https://httpbin.org/get?lang=en")
print(r.status_code)
print(r.json()["args"])  # {'lang': 'en'}
```

GET은 읽기 요청에 가장 많이 쓰입니다. 쿼리스트링이 서버에 그대로 전달되는 것도 함께 볼 수 있습니다.

### 2단계 — POST로 본문 보내기

```python
# 2_post.py
import requests
r = requests.post("https://httpbin.org/post", json={"name": "yeongseon"})
print(r.json()["json"])
```

POST는 서버 상태가 바뀔 수 있는 작업에 주로 사용합니다. JSON 본문을 보내면 서버가 그 내용을 읽어 처리합니다.

### 3단계 — 헤더 확인하기

```python
# 3_headers.py
import requests
r = requests.get("https://httpbin.org/headers", headers={"X-Custom": "hi"})
print(r.json()["headers"]["X-Custom"])
```

헤더는 인증, 캐시, 콘텐츠 타입 같은 부가 정보를 실어 나릅니다. 같은 URL이라도 헤더에 따라 처리 방식이 달라질 수 있습니다.

### 4단계 — 상태 코드로 분기하기

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

클라이언트는 응답 본문만 보지 않고 상태 코드도 함께 읽어야 합니다. 같은 JSON 구조라도 200과 404는 전혀 다른 의미입니다.

### 5단계 — raw 요청과 응답 보기

```bash
curl -v https://httpbin.org/get
# > GET /get HTTP/1.1
# > Host: httpbin.org
# < HTTP/1.1 200 OK
# < Content-Type: application/json
```

`curl -v`는 HTTP가 실제로 어떤 텍스트를 주고받는지 감각을 잡는 데 좋습니다. 프레임워크 뒤에 숨은 메시지를 직접 볼 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `Content-Type`이 `text/html`인지 `application/json`인지에 따라 클라이언트 처리 방식이 달라집니다.
- POST는 서버 상태가 바뀔 수 있다는 계약을 담고 있습니다.
- 같은 URL이라도 method가 다르면 완전히 다른 동작을 할 수 있습니다.

## 여기서 자주 헷갈립니다

1. **GET으로 데이터를 생성하는 경우**: GET은 읽기 전용 계약으로 보는 편이 맞습니다.
2. **모든 응답을 200으로 돌려주는 경우**: 클라이언트가 실패를 구분할 수 없습니다.
3. **`Content-Type`을 무시하는 경우**: HTML을 JSON처럼 파싱하다가 오류가 납니다.
4. **에러 본문 형식을 제멋대로 만드는 경우**: 클라이언트가 메시지를 안정적으로 읽기 어렵습니다.
5. **인증 정보를 URL에 넣는 경우**: 로그와 히스토리에 오래 남습니다.

## 운영에서는 이렇게 보입니다

대부분의 웹과 모바일 앱은 JSON over HTTP 형태로 서버와 통신합니다. GraphQL과 gRPC도 결국 HTTP 위에 서 있습니다. 새 서비스를 처음 볼 때 API 문서를 먼저 읽는 이유도 여기에 있습니다. 요청과 응답의 형식이 시스템 계약의 중심이기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- method와 status code를 본래 의미에 맞게 씁니다.
- 에러 응답의 형식을 표준화합니다.
- 인증 정보는 header로 보내고, 토큰 수명은 짧게 둡니다.
- timeout과 retry 예산을 항상 같이 봅니다.
- API와 문서는 함께 자라야 한다고 생각합니다.

## 체크리스트

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

## 웹 서비스 품질을 높이는 추가 실전 예시

웹 개발에서는 기능 구현 속도만큼 프로토콜 이해와 운영 경계 관리가 중요합니다. 특히 HTTP 메시지 설계, 인증 흐름, 배포 구성은 기능이 늘어날수록 장애 확률과 직접 연결됩니다. 아래 예시는 실제 프로젝트에서 반복해서 쓰이는 기본 패턴입니다.

### HTTP 요청/응답 설계 예시

```http
POST /api/v1/orders HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer <access_token>
Idempotency-Key: 9a7d2f4a-31a2-4b11-9cd8-3e2f4dcf1b20

{
  "items": [{"sku": "A-100", "qty": 2}],
  "payment_method": "card"
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/orders/ord_1024

{
  "order_id": "ord_1024",
  "status": "created"
}
```

여기서 `Idempotency-Key`는 네트워크 재시도로 인한 중복 결제를 막는 핵심 장치입니다. 웹 API는 "한 번 보냈다"가 아니라 "여러 번 도착할 수 있다"를 기본 가정으로 설계해야 합니다.

### 인증 흐름: Access + Refresh 토큰 분리

```text
1) 사용자가 로그인하면 서버가 access(짧은 수명) + refresh(긴 수명)를 발급
2) 클라이언트는 access로 API 호출
3) access 만료 시 refresh로 재발급 요청
4) refresh 탈취 위험을 줄이기 위해 회전(rotation)과 폐기(revoke) 정책 적용
```

```python
# pseudo-auth-service.py
from datetime import timedelta

def issue_tokens(user_id: str) -> dict:
    return {
        "access_expires": timedelta(minutes=15),
        "refresh_expires": timedelta(days=14),
        "token_type": "Bearer",
    }
```

브라우저 환경에서는 refresh 토큰을 `HttpOnly`, `Secure`, `SameSite` 정책이 적용된 쿠키로 다루는 방식이 일반적입니다. 인증 실패 응답은 `401`과 명확한 오류 코드를 함께 제공해야 클라이언트 재시도 전략을 안정적으로 구성할 수 있습니다.

### 배포 구성: 앱/프록시/헬스체크 분리

```yaml
# docker-compose.prod.yml
services:
  web:
    image: ghcr.io/example/web:1.4.0
    env_file: .env
    ports: ["8000"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
  nginx:
    image: nginx:1.27
    ports: ["80:80", "443:443"]
    depends_on: [web]
```

헬스체크를 배포 단위에 포함하면 롤링 업데이트 중 비정상 인스턴스를 조기에 제외할 수 있습니다. 프록시 계층에서 TLS 종료와 정적 파일 캐싱을 처리하면 애플리케이션 서버는 비즈니스 로직에 더 집중할 수 있습니다.

### 운영 체크 포인트

- API마다 타임아웃, 재시도, 멱등 처리 기준을 문서화합니다.
- 인증 토큰 만료/재발급 실패 비율을 대시보드로 모니터링합니다.
- 배포 후 15분 동안 5xx 비율, p95, 로그인 성공률을 집중 관찰합니다.
- CORS 정책을 `*`로 열어두지 않고 허용 출처를 명시합니다.

웹 개발의 난이도는 화면 구현보다 경계 관리에서 더 크게 올라갑니다. HTTP 계약, 인증 수명주기, 배포 안전장치를 초기에 고정해 두면 기능 확장 시에도 장애 반경을 작게 유지할 수 있고, 팀 전체의 디버깅 속도도 안정적으로 유지됩니다.

## HTTP-인증-배포를 함께 검증하는 점검 루틴

웹 서비스는 단일 기능이 아니라 경로 전체의 안정성으로 평가됩니다. 따라서 API 스펙, 인증 예외, 배포 헬스체크를 같은 릴리스 체크리스트로 묶는 편이 안전합니다.

```text
배포 전 점검
1) 핵심 API 3개에 대해 상태 코드/응답 스키마 계약 테스트 실행
2) access 만료, refresh 만료, revoke 토큰 시나리오 재현
3) /health, /ready 엔드포인트를 배포 환경에서 실제 호출
4) CDN/브라우저 캐시 무효화 정책 확인
```

### 장애 예방을 위한 최소 헤더 정책

```http
Cache-Control: no-store
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```

헤더 정책은 프론트엔드 코드 변경 없이도 보안/캐시 동작을 크게 바꿉니다. 기능 개발과 별개로 표준 헤더를 고정해 두면 릴리스 변동성이 줄어듭니다.

### 배포 후 15분 관찰 항목

- 5xx 비율과 p95 지연 시간의 급격한 상승 여부
- 로그인 성공률, 토큰 재발급 성공률
- 정적 자산 404 발생률

이 루틴을 반복하면 "배포는 되었지만 정상 운영은 아닌" 상태를 초기에 감지할 수 있습니다.

## 처음 질문으로 돌아가기

- **클라이언트와 서버는 실제로 무엇을 주고받을까요?**
  - 본문의 기준은 HTTP와 API를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **HTTP 요청과 응답은 어떤 요소로 구성될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **GET, POST, PUT, DELETE는 각각 어떤 의미일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Web Development 101 (1/10): 웹은 어떻게 동작하는가?](./01-how-the-web-works.md)
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- **HTTP와 API (현재 글)**
- Frontend와 Backend (예정)
- 인증과 세션 (예정)
- 데이터베이스 연결 (예정)
- 배포 (예정)
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [HTTP request methods (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [HTTP response status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)

### 검증용 자료
- [httpbin](https://httpbin.org/)
- [HTTP Semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110)

Tags: Computer Science, WebDevelopment, HTTP, API, REST, Networking
