---
series: web-development-101
episode: 1
title: "Web Development 101 (1/10): 웹은 어떻게 동작하는가?"
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
  - DNS
  - Browser
  - Frontend
seo_description: URL 입력 뒤 DNS, HTTP, 서버, 렌더링이 이어지는 흐름을 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (1/10): 웹은 어떻게 동작하는가?

웹 개발을 처음 배울 때는 HTML, CSS, JavaScript, API 같은 단어가 따로따로 보입니다. 그런데 장애를 잡거나 성능 문제를 읽으려면 이 조각들을 하나의 흐름으로 묶어 이해해야 합니다. 주소창에 URL을 넣고 Enter를 누른 뒤 화면이 보이기까지, 실제로 어떤 단계가 지나가는지 머릿속에 그려져야 합니다.

이 글은 Web Development 101 시리즈의 첫 번째 글입니다. 여기서는 브라우저, DNS, HTTP, 서버, 렌더링이 어떤 순서로 맞물리는지 전체 지도를 먼저 잡겠습니다.

## 먼저 던지는 질문

- URL을 입력한 뒤 화면이 보일 때까지 어떤 단계가 지나갈까요?
- DNS와 HTTP는 각각 어떤 역할을 맡을까요?
- 서버가 응답을 보내면 브라우저는 그 데이터를 어떻게 화면으로 바꿀까요?

## 큰 그림

![Web Development 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/01/01-01-concept-at-a-glance.ko.png)

*Web Development 101 1장 흐름 개요*

## 왜 이 흐름이 중요한가

웹 개발자는 전체 그림을 알아야 합니다. 한 층만 잘 알아도 기능은 만들 수 있지만, 문제가 생겼을 때 어디서부터 봐야 하는지 감이 잡히지 않습니다. DNS 문제인지, TLS 연결 문제인지, 서버 응답 문제인지, 브라우저 렌더링 문제인지 구분하지 못하면 디버깅이 오래 걸립니다.

반대로 URL에서 픽셀까지의 다섯 단계를 머릿속에 넣어 두면 각 도구의 자리가 분명해집니다. DevTools Network 탭이 왜 중요한지, `curl`이 무엇을 보여 주는지, APM이 무엇을 재는지도 같은 그림 안에서 읽히기 시작합니다.

## 한눈에 보는 개념 지도

이 그림을 볼 때는 사용자가 주소를 입력한 뒤 브라우저가 DNS를 조회하고, 서버와 HTTP를 주고받고, 마지막에 렌더링으로 넘어가는 순서를 왼쪽에서 오른쪽으로 따라가면 됩니다. 이후 글에서 배우는 DOM, API, 배포, 캐싱도 모두 이 기본 흐름 위에 올라갑니다.

### 직접 검증해 볼 포인트

- `socket.gethostbyname("example.com")`를 실행해 도메인이 실제 IP로 바뀌는지 확인합니다.
- DevTools Network 탭에서 문서 요청 하나 아래에 CSS, JavaScript, 이미지 요청이 이어지는지 관찰합니다.
- `curl -I https://example.com`으로 서버가 어떤 상태 코드와 헤더를 먼저 돌려주는지 확인합니다.

**기대 결과:** DNS 조회가 성공하면 IP가 출력되고, Network 탭에서는 문서 요청 뒤에 추가 리소스 요청이 연쇄적으로 보입니다.

**실패 모드:** DNS 조회가 실패하면 HTTP 요청 자체가 시작되지 않습니다. HTML 응답은 200인데 화면이 깨지면 문제는 서버보다 렌더링 단계에 있을 가능성이 큽니다.

## 먼저 알아둘 용어

- **URL**: 리소스의 주소입니다. scheme, host, path 같은 요소로 구성됩니다.
- **DNS**: 도메인 이름을 IP 주소로 바꾸는 시스템입니다.
- **HTTP**: 요청과 응답을 주고받는 프로토콜입니다.
- **Server**: 요청을 받아 응답으로 바꾸는 프로그램입니다.
- **Browser**: 응답 데이터를 읽어 화면의 픽셀로 바꾸는 프로그램입니다.

## Before / After로 보는 감각 차이

**Before (raw IP)**

```python
# 외우기 어렵다
import socket
ip = "93.184.216.34"
```

**After (use a domain)**

```python
import socket
ip = socket.gethostbyname("example.com")
print(ip)
```

DNS는 사람이 읽는 이름과 기계가 읽는 주소 사이를 이어 줍니다. 이 변환이 없으면 웹은 지금처럼 다루기 쉬운 시스템이 되기 어렵습니다.

## 한 번의 요청을 다섯 단계로 따라가기

### 1단계 — DNS 조회

```python
# 1_dns.py
import socket
print(socket.gethostbyname("example.com"))
```

브라우저는 먼저 `example.com`이 어떤 IP를 가리키는지 확인합니다. 도메인이 IP로 바뀌어야 네트워크 연결을 시작할 수 있습니다.

### 2단계 — HTTP 요청

```python
# 2_http.py
import requests
r = requests.get("https://example.com")
print(r.status_code, len(r.text))
```

이 단계에서 클라이언트는 서버에 요청을 보내고, 서버는 상태 코드와 본문을 돌려줍니다. 보통 `200`과 함께 HTML 본문 길이가 출력됩니다.

### 3단계 — 응답 헤더 읽기

```python
# 3_headers.py
import requests
r = requests.get("https://example.com")
for k, v in r.headers.items():
    print(k, ":", v)
```

`Content-Type`, `Server`, `Cache-Control` 같은 헤더는 응답 본문이 무엇인지, 어떻게 다뤄야 하는지 알려 주는 메타데이터입니다.

### 4단계 — HTML 파싱

```python
# 4_parse.py
import re, requests
html = requests.get("https://example.com").text
title = re.search(r"<title>(.*?)</title>", html).group(1)
print(title)
```

브라우저는 HTML 텍스트를 그냥 보여 주지 않습니다. 먼저 구조를 해석해 트리로 만들고, 그 위에 CSS와 JavaScript를 얹어 화면을 그립니다.

### 5단계 — DevTools에서 관찰

```text
브라우저를 열고 F12를 누른 뒤 Network 탭에서 example.com을 새로고침합니다.
```

요청별 시간, 상태 코드, 전송 크기, 헤더가 모두 보입니다. 웹 디버깅에서 가장 자주 열어 보게 되는 화면이 바로 여기입니다.

## 이 코드에서 먼저 봐야 할 점

- DNS는 한 번 조회한 뒤 캐시되는 경우가 많습니다.
- HTTPS는 HTTP 위에 TCP와 TLS가 얹힌 형태입니다.
- HTML만 오는 것이 아니라 CSS와 JavaScript도 이어서 내려오고, 브라우저는 이를 병렬로 처리합니다.

## 여기서 자주 헷갈립니다

1. **DNS와 HTTP를 같은 단계로 보는 경우**: DNS는 주소를 찾는 단계이고, HTTP는 그 뒤에 요청을 보내는 단계입니다.
2. **HTTPS를 HTTP와 완전히 다른 프로토콜로 보는 경우**: HTTP 메시지를 TLS로 감싼 것이 HTTPS입니다.
3. **서버가 화면을 그린다고 생각하는 경우**: 기본적으로 화면 렌더링은 브라우저가 맡습니다.
4. **클라이언트와 서버의 책임 경계를 흐리는 경우**: 어느 쪽에서 문제가 시작됐는지 구분이 어려워집니다.
5. **DevTools 없이 감으로 디버깅하는 경우**: Network 탭은 가장 빠른 진단 도구입니다.

## 운영에서는 이렇게 보입니다

현업에서 문제가 터지면 첫 질문은 늘 같습니다. DNS 문제인가, TLS 문제인가, 서버 문제인가, 렌더링 문제인가. 이 단계 이름을 알고 있으면 30분 걸릴 디버깅이 3분으로 줄어드는 경우가 많습니다. New Relic, Datadog, Sentry 같은 도구도 결국 이 흐름의 어느 구간이 느린지 보여 줍니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 단계마다 시간 예산을 둡니다. 예를 들어 DNS 50ms, TLS 100ms처럼 봅니다.
- 캐시 가능한 것은 어디에서 캐시할지 먼저 결정합니다.
- 이 작업이 브라우저에서 돌아야 하는지 서버에서 돌아야 하는지 늘 구분합니다.
- DevTools Network 탭을 뷰어가 아니라 디버거로 씁니다.
- 추측보다 측정을 먼저 믿습니다.

## 체크리스트

- [ ] URL에서 픽셀까지 가는 다섯 단계를 설명할 수 있습니다.
- [ ] DNS와 HTTP의 차이를 설명할 수 있습니다.
- [ ] DevTools Network 탭에서 단일 요청을 분석할 수 있습니다.
- [ ] 응답에서 상태 코드를 읽을 수 있습니다.
- [ ] 캐시가 어느 단계에서 동작하는지 알고 있습니다.

## 연습 문제

1. 자주 가는 사이트 하나를 열고 Network 탭에서 가장 큰 요청을 찾아보세요.
2. `dig` 또는 `nslookup`으로 도메인 세 개를 조회해 보세요.
3. `requests`로 같은 URL을 100번 호출하고 평균 시간을 출력해 보세요.

## 정리와 다음 글

웹은 여러 프로토콜이 협력하는 시스템입니다. 이 흐름을 먼저 잡아 두면 이후에 배우는 HTML, CSS, JavaScript, DOM, API, 데이터베이스, 배포가 모두 같은 지도 안에 들어옵니다. 다음 글에서는 브라우저가 실제로 내려받는 세 가지 언어, HTML, CSS, JavaScript를 정리하겠습니다.

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

- **URL을 입력한 뒤 화면이 보일 때까지 어떤 단계가 지나갈까요?**
  - 본문의 기준은 웹은 어떻게 동작하는가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **DNS와 HTTP는 각각 어떤 역할을 맡을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **서버가 응답을 보내면 브라우저는 그 데이터를 어떻게 화면으로 바꿀까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **웹은 어떻게 동작하는가? (현재 글)**
- HTML, CSS, JavaScript (예정)
- 브라우저와 DOM (예정)
- HTTP와 API (예정)
- Frontend와 Backend (예정)
- 인증과 세션 (예정)
- 데이터베이스 연결 (예정)
- 배포 (예정)
- 성능과 캐싱 (예정)
- 작은 웹앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [How the Web works (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [Chrome DevTools Network features](https://developer.chrome.com/docs/devtools/network/)

### 개념 보강
- [What is DNS? (Cloudflare Learning Center)](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [URI generic syntax (RFC 3986)](https://www.rfc-editor.org/rfc/rfc3986)

Tags: Computer Science, WebDevelopment, HTTP, DNS, Browser, Frontend
