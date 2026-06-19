---
series: web-development-101
episode: 1
title: "Web Development 101 (1/10): 웹은 어떻게 동작하는가?"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/203"
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
  - DNS
  - Browser
  - Frontend
seo_description: URL 입력 뒤 DNS, HTTP, 서버, 렌더링이 이어지는 흐름을 설명합니다.
last_reviewed: '2026-05-15'
---

# Web Development 101 (1/10): 웹은 어떻게 동작하는가?

웹 개발을 처음 배울 때는 HTML, CSS, JavaScript, API 같은 단어가 따로따로 보입니다. 그런데 장애를 잡거나 성능 문제를 읽으려면 이 조각들을 하나의 흐름으로 묶어 이해해야 합니다. 주소창에 URL을 넣고 Enter를 누른 뒤 화면이 보이기까지, 실제로 어떤 단계가 지나가는지 머릿속에 그려져야 합니다.

이 글은 Web Development 101 시리즈의 첫 번째 글입니다.

여기서는 브라우저, DNS, HTTP, 서버, 렌더링이 어떤 순서로 맞물리는지 전체 지도를 먼저 잡겠습니다.

![Web Development 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/01/01-01-concept-at-a-glance.ko.png)
*Web Development 101 1장 흐름 개요*

> URL을 입력하고 화면이 보이기까지의 흐름은 브라우저·DNS·HTTP·서버·렌더링이 한 줄로 맞물린 파이프라인입니다 — 이 한 흐름이 머릿속에 그려져야 장애와 성능 문제를 추측 대신 단계 단위로 끊어서 읽을 수 있습니다.

## 이 글에서 다룰 문제

- URL을 입력한 뒤 화면이 보일 때까지 어떤 단계가 지나갈까요?
- DNS와 HTTP는 각각 어떤 역할을 맡을까요?
- 서버가 응답을 보내면 브라우저는 그 데이터를 어떻게 화면으로 바꿀까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 흐름이 중요한가

웹 개발자는 전체 그림을 알아야 합니다. 한 층만 잘 알아도 기능은 만들 수 있지만, 문제가 생겼을 때 어디서부터 봐야 하는지 감이 잡히지 않습니다. DNS 문제인지, TLS 연결 문제인지, 서버 응답 문제인지, 브라우저 렌더링 문제인지 구분하지 못하면 디버깅이 오래 걸립니다.

반대로 URL에서 픽셀까지의 다섯 단계를 머릿속에 넣어 두면 각 도구의 자리가 분명해집니다. DevTools Network 탭이 왜 중요한지, `curl`이 무엇을 보여 주는지, APM이 무엇을 재는지도 같은 그림 안에서 읽히기 시작합니다.

## 요청 한 번의 전체 흐름

```
사용자 입력: https://example.com/page
      |
      v
[1] DNS 조회
      브라우저 캐시 → OS 캐시 → ISP DNS → 권한 DNS 서버
      example.com  →  93.184.216.34
      |
      v
[2] TCP + TLS 연결
      SYN → SYN-ACK → ACK           (TCP 3-way handshake)
      ClientHello → ServerHello → ... (TLS handshake)
      |
      v
[3] HTTP 요청 전송
      GET /page HTTP/1.1
      Host: example.com
      |
      v
[4] 서버 처리 및 응답
      200 OK
      Content-Type: text/html
      <html>...</html>
      |
      v
[5] 브라우저 렌더링
      HTML 파싱 → DOM 트리
      CSS 파싱 → CSSOM
      DOM + CSSOM → Render Tree → Layout → Paint
```

이 다섯 단계 중 어느 하나라도 막히면 화면이 나오지 않거나 느려집니다. 디버깅의 첫 질문은 "어느 단계에서 막혔는가?"입니다.

## 먼저 알아둘 용어

- **URL**: 리소스의 주소입니다. scheme, host, path 같은 요소로 구성됩니다.
- **DNS**: 도메인 이름을 IP 주소로 바꾸는 시스템입니다.
- **HTTP**: 요청과 응답을 주고받는 프로토콜입니다.
- **TLS**: HTTP 메시지를 암호화하는 보안 계층입니다. HTTPS = HTTP + TLS입니다.
- **Server**: 요청을 받아 응답으로 바꾸는 프로그램입니다.
- **Browser**: 응답 데이터를 읽어 화면의 픽셀로 바꾸는 프로그램입니다.

## URL의 구조

```
https://api.example.com:443/v1/users?page=2#section
  |         |           |      |        |      |
scheme    host         port   path    query  fragment
```

URL 각 부분은 서로 다른 역할을 합니다. `scheme`은 어떤 프로토콜을 쓸지, `host`는 어느 서버로 갈지, `path`는 서버 안에서 어느 리소스인지를 가리킵니다. `query`는 추가 파라미터, `fragment`는 브라우저가 로컬에서 처리하는 위치 정보입니다.

## 1단계: DNS 조회

브라우저는 `example.com`이라는 이름을 바로 네트워크로 보낼 수 없습니다. IP 주소가 필요합니다.

```bash
# 도메인이 어떤 IP를 가리키는지 조회
dig example.com

# 또는
nslookup example.com

# 응답 예시
# example.com.  3600  IN  A  93.184.216.34
```

DNS 조회 순서: 브라우저 캐시 → OS `/etc/hosts` → OS DNS 캐시 → ISP의 재귀 DNS 서버 → 권한 DNS 서버

TTL(Time To Live)이 남아 있으면 캐시된 결과를 씁니다. 새 도메인이나 IP가 바뀐 직후에는 DNS 전파가 완료될 때까지 시간이 걸리는 이유입니다.

```python
# Python으로 DNS 조회 재현
import socket
ip = socket.gethostbyname("example.com")
print(ip)  # 93.184.216.34
```

## 2단계: HTTP 요청

IP를 알면 서버에 요청을 보냅니다. HTTP 요청은 텍스트 메시지입니다.

```http
GET /index.html HTTP/1.1
Host: example.com
Accept: text/html,application/xhtml+xml
Accept-Language: ko-KR,ko;q=0.9
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...
Connection: keep-alive
```

```python
import requests

r = requests.get("https://example.com")
print(r.status_code)   # 200
print(r.headers["Content-Type"])  # text/html; charset=UTF-8
print(len(r.text))     # HTML 본문 길이
```

## 3단계: HTTP 응답 헤더 읽기

서버는 요청을 처리한 뒤 상태 코드와 헤더, 본문을 돌려줍니다.

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 1256
Cache-Control: max-age=86400
Server: nginx/1.24.0
X-Content-Type-Options: nosniff
```

```python
import requests

r = requests.get("https://example.com")
for key, val in r.headers.items():
    print(f"{key}: {val}")
```

`Content-Type`은 브라우저가 응답 본문을 어떻게 해석할지 결정합니다. `Cache-Control`은 다음 요청 때 서버를 다시 칠지 여부를 결정합니다.

## 4단계: HTML 파싱과 렌더링

브라우저가 HTML을 받으면 그것을 화면으로 바꾸는 파이프라인이 시작됩니다.

```
HTML 텍스트
    |
    v  파싱
DOM 트리 (노드들의 트리 구조)
    |
    +--- CSS 파싱 → CSSOM
    |
    v  결합
Render Tree (화면에 실제로 그려질 노드)
    |
    v  Layout
각 요소의 크기와 위치 계산
    |
    v  Paint
픽셀 그리기
    |
    v  Composite
레이어 합성 → 최종 화면
```

```python
# 응답 HTML에서 title 추출 (파싱 흉내)
import re, requests

html = requests.get("https://example.com").text
title = re.search(r"<title>(.*?)</title>", html)
if title:
    print(title.group(1))  # Example Domain
```

## 5단계: DevTools에서 전체 흐름 관찰

```
브라우저 F12 → Network 탭
  - Name: 요청 URL
  - Status: 상태 코드
  - Type: 리소스 종류 (document, stylesheet, script, fetch ...)
  - Size: 전송 크기
  - Time: 총 소요 시간
  - Waterfall: DNS, TCP, TLS, TTFB, 다운로드 시간대 시각화
```

Network 탭에서 첫 문서 요청 아래에 CSS, JavaScript, 이미지 요청이 연쇄적으로 나타납니다. 이것이 실제 웹 페이지 로딩입니다.

```bash
# curl로 헤더만 빠르게 확인
curl -I https://example.com

# curl로 verbose 모드로 전체 흐름 보기
curl -v https://example.com 2>&1 | head -40
```

## TLS 핸드쉐이크: HTTPS가 어떻게 동작하는가

HTTPS는 HTTP 메시지를 TLS로 감싼 것입니다. 연결이 맺어지기 전에 브라우저와 서버가 암호화 방식을 협상합니다.

```
TLS 1.3 핸드쉐이크 (간략):
  클라이언트 → ClientHello (지원 암호 목록, 난수)
  서버        ← ServerHello (선택된 암호, 인증서, 서버 공개키)
  클라이언트 → 인증서 검증 → 세션 키 유도
  ────────────────────────────────────────
  이후 모든 HTTP 메시지는 세션 키로 암호화

TLS 1.2 대비 TLS 1.3의 개선:
  - 핸드쉐이크 1 RTT (1.2는 2 RTT)
  - 0-RTT 재개 (이전 연결 재사용 시)
  - 취약한 암호 알고리즘 제거
```

```bash
# 인증서 정보 확인
curl -v https://example.com 2>&1 | grep -E "(SSL|TLS|certificate|expire)"

# 인증서 만료일 확인
echo | openssl s_client -connect example.com:443 2>/dev/null \
  | openssl x509 -noout -dates
```

## HTTP/1.1 vs HTTP/2 vs HTTP/3

```
HTTP/1.1 (1997~):
  - 요청당 TCP 연결 1개
  - 브라우저는 보통 도메인당 6개 연결 병렬 사용
  - Head-of-line blocking (앞 요청 지연 시 뒤 요청도 대기)

HTTP/2 (2015~):
  - 하나의 TCP 연결에서 여러 스트림 다중화
  - 헤더 압축 (HPACK)
  - 서버 푸시 (요청 전에 필요한 리소스 미리 전송)

HTTP/3 (2022~):
  - TCP 대신 QUIC (UDP 기반) 사용
  - 패킷 손실 시 다른 스트림에 영향 없음
  - 0-RTT 연결 재개
```

```bash
# HTTP 버전 확인
curl -I --http2 https://example.com | grep "HTTP/"
curl -I --http3 https://example.com | grep "HTTP/"

# 또는 DevTools Network 탭 → Protocol 컬럼 확인
# h2 = HTTP/2, h3 = HTTP/3
```

## 브라우저 DevTools로 요청 흐름 분석하기

브라우저에서 직접 각 단계의 시간을 측정할 수 있습니다. Chrome DevTools → Network 탭 → 요청 클릭 → Timing 탭을 열면 다음 정보가 나옵니다.

```
Timing 항목          의미
─────────────────────────────────────────────────────
Queueing             브라우저가 요청 대기열에 넣은 시간
Stalled              연결을 기다리는 시간 (HTTP/1.1 병렬 제한)
DNS Lookup           DNS 조회 시간 (캐시 시 거의 0)
Initial connection   TCP 3-way handshake 시간
SSL                  TLS 핸드쉐이크 시간 (HTTPS만)
Request sent         요청 데이터 전송 시간
Waiting (TTFB)       서버 첫 바이트 응답까지 대기 시간
Content Download     응답 본문 수신 시간
─────────────────────────────────────────────────────
```

**TTFB (Time to First Byte)**가 높으면 서버 처리가 느리거나 물리적 거리가 멀다는 신호입니다. CDN을 사용하면 Content Download 시간이 줄고, 서버 최적화로 TTFB를 낮출 수 있습니다.

curl로 같은 정보를 얻으려면 `--write-out` 옵션을 사용합니다.

```bash
curl -o /dev/null -s -w "
    namelookup: %{time_namelookup}s
    connect:    %{time_connect}s
    ssl:        %{time_appconnect}s
    ttfb:       %{time_starttransfer}s
    total:      %{time_total}s
    size:       %{size_download} bytes
" https://example.com
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 이해 |
|------|------|-------------|
| DNS와 HTTP를 같은 단계로 보는 것 | DNS 실패 시 HTTP 오류로 오해 | DNS는 IP 조회, HTTP는 그 후 요청 전송 |
| HTTPS를 완전히 다른 프로토콜로 보는 것 | TLS 오류를 HTTP 오류로 혼동 | HTTPS = HTTP + TLS 암호화 계층 |
| 서버가 화면을 그린다고 생각하는 것 | 서버 응답 문제와 렌더링 문제를 구분 못 함 | 기본 렌더링은 브라우저가 담당 |
| DevTools 없이 감으로 디버깅 | 수십 분 헤맴 | Network 탭이 1분 안에 답 줌 |
| 상태 코드 200이면 문제없다 생각 | JSON 파싱 오류 등을 놓침 | 200이라도 본문과 Content-Type 확인 필요 |

## 직접 검증해 볼 포인트

```bash
# 1. DNS 조회
dig example.com +short

# 2. HTTP 요청/응답 전체 보기
curl -sv https://example.com > /dev/null

# 3. 상태 코드만 확인
curl -o /dev/null -s -w "%{http_code}" https://example.com

# 4. 응답 시간 세분화 (DNS, TCP, TLS, TTFB 별도 측정)
curl -w "DNS: %{time_namelookup}s\nTCP: %{time_connect}s\nTLS: %{time_appconnect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" \
  -o /dev/null -s https://example.com
```

**기대 결과:** DNS 조회가 성공하면 IP가 출력되고, Network 탭에서는 문서 요청 뒤에 추가 리소스 요청이 연쇄적으로 보입니다.

**실패 모드:** DNS 조회가 실패하면 HTTP 요청 자체가 시작되지 않습니다. HTML 응답은 200인데 화면이 깨지면 문제는 서버보다 렌더링 단계에 있을 가능성이 큽니다.

## 실무에서의 디버깅 루틴

```
사이트가 안 열린다 →
  1) ping 또는 dig → DNS 문제인가?
  2) curl -I → TLS 또는 서버 연결 문제인가?
  3) curl -v → HTTP 응답 상태 코드는?
  4) DevTools Network 탭 → 어느 리소스에서 막혔나?
  5) DevTools Console 탭 → JavaScript 오류가 있나?
```

현업에서 문제가 터지면 첫 질문은 늘 같습니다. DNS 문제인가, TLS 문제인가, 서버 문제인가, 렌더링 문제인가. 이 단계 이름을 알고 있으면 30분 걸릴 디버깅이 3분으로 줄어드는 경우가 많습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 단계마다 시간 예산을 둡니다. 예를 들어 DNS 50ms, TLS 100ms처럼 봅니다.
- 캐시 가능한 것은 어디에서 캐시할지 먼저 결정합니다.
- 이 작업이 브라우저에서 돌아야 하는지 서버에서 돌아야 하는지 늘 구분합니다.
- DevTools Network 탭을 뷰어가 아니라 디버거로 씁니다.
- 추측보다 측정을 먼저 믿습니다.

## 운영 체크리스트

- [ ] URL에서 픽셀까지 가는 다섯 단계를 설명할 수 있습니다.
- [ ] DNS와 HTTP의 차이를 설명할 수 있습니다.
- [ ] DevTools Network 탭에서 단일 요청을 분석할 수 있습니다.
- [ ] curl로 상태 코드와 헤더를 읽을 수 있습니다.
- [ ] 캐시가 어느 단계에서 동작하는지 알고 있습니다.

## 연습 문제

1. 자주 가는 사이트 하나를 열고 Network 탭에서 가장 큰 요청을 찾아보세요.
2. `dig` 또는 `nslookup`으로 도메인 세 개를 조회해 TTL 값을 비교해 보세요.
3. `curl -w` 플래그로 같은 URL의 DNS, TCP, TLS, TTFB 시간을 각각 측정해 보세요.

## 정리와 다음 글

웹은 여러 프로토콜이 협력하는 시스템입니다. 이 흐름을 먼저 잡아 두면 이후에 배우는 HTML, CSS, JavaScript, DOM, API, 데이터베이스, 배포가 모두 같은 지도 안에 들어옵니다. 다음 글에서는 브라우저가 실제로 내려받는 세 가지 언어, HTML, CSS, JavaScript를 정리하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- **Web Development 101 (1/10): 웹은 어떻게 동작하는가? (현재 글)**
- [Web Development 101 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [Web Development 101 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [Web Development 101 (4/10): HTTP와 API](./04-http-and-api.md)
- [Web Development 101 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [Web Development 101 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [Web Development 101 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [Web Development 101 (8/10): 배포](./08-deployment.md)
- [Web Development 101 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [How the Web works (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [Chrome DevTools Network features](https://developer.chrome.com/docs/devtools/network/)

### 개념 보강
- [What is DNS? (Cloudflare Learning Center)](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [URI generic syntax (RFC 3986)](https://www.rfc-editor.org/rfc/rfc3986)

- [web-development-101 예제 코드 저장소 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/web-development-101/ko)

Tags: Computer Science, WebDevelopment, HTTP, DNS, Browser, Frontend
