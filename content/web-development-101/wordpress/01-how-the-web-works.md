---
series: web-development-101
episode: 1
title: "바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - 웹개발
  - HTTP
  - DNS
  - 브라우저
  - 프론트엔드
seo_description: AI에게 웹앱을 만들어달라고 하기 전에 꼭 알아야 할 웹의 동작 원리를 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가?

이 글은 **바이브코딩을 위한 웹 개발 기초** 시리즈의 첫 번째 글입니다. AI에게 웹앱을 만들어달라고 요청하기 전에, 웹이 실제로 어떻게 동작하는지 알아야 합니다. 이 시리즈는 그 기초를 10편에 걸쳐 정리합니다.

---

AI 도구로 웹앱을 빠르게 만들 수 있는 시대입니다. 그런데 막상 AI가 코드를 생성해 줘도 "왜 이게 안 되지?"라는 순간은 반드시 찾아옵니다. 그 순간 버텨 주는 것이 바로 웹의 기본 원리입니다. URL을 입력하고 화면이 보일 때까지 어떤 일이 벌어지는지 모르면, AI가 만들어준 코드도 고치지 못합니다.

바이브코딩을 할 때 가장 자주 막히는 지점이 있습니다. "서버가 응답을 안 한다", "API가 연결이 안 된다", "화면이 왜 안 바뀌지"처럼 느껴지는 문제들입니다. 이 모두는 웹의 흐름을 모르면 어디를 봐야 하는지조차 알 수 없습니다. 반대로 DNS, HTTP, 브라우저 렌더링이라는 다섯 단계가 머릿속에 들어오면, AI가 만들어준 코드를 읽고 수정하는 속도가 완전히 달라집니다.

이 글에서는 주소창에 URL을 입력한 뒤 화면이 보이기까지의 흐름을 단계별로 정리합니다. 바이브코딩을 할 때 이 흐름이 "아, 지금 DNS 단계에서 문제구나"처럼 읽히도록 돕는 것이 목표입니다.

> URL을 입력하고 화면이 보이기까지의 흐름은 브라우저·DNS·HTTP·서버·렌더링이 한 줄로 맞물린 파이프라인입니다. 이 흐름을 알아야 AI가 만들어준 코드의 어디가 문제인지 추측 대신 단계 단위로 끊어서 읽을 수 있습니다.

## 이 글에서 다룰 문제

- URL을 입력한 뒤 화면이 보일 때까지 어떤 단계가 지나갈까요?
- DNS와 HTTP는 각각 어떤 역할을 맡을까요?
- 서버가 응답을 보내면 브라우저는 그 데이터를 어떻게 화면으로 바꿀까요?
- 바이브코딩 중에 이 개념을 잘못 적용하면 어떤 문제가 생길까요?
- 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 바이브코딩 관점: 왜 웹 흐름을 알아야 하는가

AI에게 "웹앱 만들어줘"라고 하면 코드가 나옵니다. 그런데 그 코드를 실행하면 에러가 납니다. "왜 에러가 나지?"를 AI에게 다시 물을 수도 있지만, AI가 에러를 보지 못한다면 여러분이 직접 읽어야 합니다. 그때 필요한 것이 바로 웹의 흐름입니다.

"DNS resolution failed"라는 에러를 봤을 때 이것이 무슨 뜻인지 모르면, AI에게 전달할 컨텍스트도 없습니다. 반대로 "아, DNS 단계에서 도메인을 IP로 변환하지 못했구나"라고 읽힌다면, AI와의 대화가 훨씬 빠르고 정확해집니다.

바이브코딩은 AI를 잘 활용하는 방법이지, AI가 모든 것을 대신해 주는 방법이 아닙니다. 기초 원리를 알아야 AI와 더 잘 협력할 수 있습니다.

## 먼저 알아둘 용어

- **URL**: 리소스의 주소입니다. scheme, host, path 같은 요소로 구성됩니다.
- **DNS**: 도메인 이름을 IP 주소로 바꾸는 시스템입니다.
- **HTTP**: 요청과 응답을 주고받는 프로토콜입니다.
- **서버**: 요청을 받아 응답으로 바꾸는 프로그램입니다.
- **브라우저**: 응답 데이터를 읽어 화면의 픽셀로 바꾸는 프로그램입니다.

## Before / After: DNS를 쓰는 이유

**Before — IP 직접 입력**

```python
# 외우기 어렵고, 서버가 바뀌면 코드도 바꿔야 합니다
ip = "93.184.216.34"
```

**After — 도메인 사용**

```python
import socket
ip = socket.gethostbyname("example.com")
print(ip)  # 93.184.216.34
```

DNS는 사람이 읽는 이름과 기계가 읽는 주소 사이를 이어 줍니다. 바이브코딩으로 만든 앱도 결국 이 변환 과정을 거칩니다.

## 웹 요청을 다섯 단계로 따라가기

### 1단계 — DNS 조회

브라우저는 먼저 `example.com`이 어떤 IP를 가리키는지 확인합니다.

```python
import socket
print(socket.gethostbyname("example.com"))
# 출력: 93.184.216.34
```

### 2단계 — HTTP 요청

IP를 알게 된 브라우저는 서버에 요청을 보냅니다.

```python
import requests
r = requests.get("https://example.com")
print(r.status_code, len(r.text))
# 출력: 200 1256
```

### 3단계 — 응답 헤더 읽기

서버는 본문과 함께 메타데이터(헤더)를 돌려줍니다.

```python
import requests
r = requests.get("https://example.com")
for k, v in r.headers.items():
    print(k, ":", v)
```

`Content-Type`, `Cache-Control` 같은 헤더가 브라우저 동작을 결정합니다.

### 4단계 — HTML 파싱

브라우저는 받은 HTML을 구조(DOM)로 변환합니다.

```python
import re, requests
html = requests.get("https://example.com").text
title = re.search(r"<title>(.*?)</title>", html).group(1)
print(title)
```

### 5단계 — DevTools에서 관찰

```text
F12 → Network 탭 → example.com 새로고침
```

요청별 시간, 상태 코드, 크기, 헤더를 모두 볼 수 있습니다. 바이브코딩 디버깅에서 가장 자주 쓰게 됩니다.

## 바이브코딩에서 자주 나오는 실수

| 실수 | 원인 | 올바른 이해 |
|------|------|-------------|
| "API가 안 돼요"라고만 설명 | 어느 단계인지 모름 | DNS, HTTP, 서버 중 어느 단계인지 먼저 구분 |
| HTTPS와 HTTP를 다른 프로토콜로 봄 | TLS 개념 부재 | HTTP 메시지를 TLS로 감싼 것이 HTTPS |
| 서버가 화면을 그린다고 생각 | 렌더링 단계 모름 | 화면 렌더링은 기본적으로 브라우저가 담당 |
| DevTools 없이 감으로 디버깅 | 도구 미숙지 | Network 탭이 가장 빠른 진단 도구 |
| DNS 오류를 HTTP 오류로 혼동 | 단계 혼동 | DNS 실패 시 HTTP 요청 자체가 시작 안 됨 |

## AI 팁: 웹 흐름 관련 좋은 질문 방법

바이브코딩 중 웹 흐름 관련 문제가 생겼을 때 AI에게 이렇게 질문하면 더 정확한 답변을 받을 수 있습니다.

```
"브라우저 Network 탭에서 이런 에러가 보입니다: [에러 메시지]
요청 URL은 [URL]이고, 상태 코드는 [상태 코드]입니다.
이 문제가 DNS 단계인지, HTTP 단계인지, 서버 응답 단계인지 알고 싶습니다."
```

구체적인 단계 이름과 DevTools 정보를 포함하면 AI가 훨씬 정확하게 진단할 수 있습니다.

## 체크리스트

- [ ] URL에서 픽셀까지 가는 다섯 단계를 설명할 수 있습니다.
- [ ] DNS와 HTTP의 차이를 설명할 수 있습니다.
- [ ] DevTools Network 탭에서 단일 요청을 분석할 수 있습니다.
- [ ] 응답에서 상태 코드를 읽을 수 있습니다.
- [ ] 캐시가 어느 단계에서 동작하는지 알고 있습니다.

## 처음 질문으로 돌아가기

- **URL을 입력한 뒤 화면이 보일 때까지 어떤 단계가 지나갈까요?**
  DNS 조회 → TCP/TLS 연결 → HTTP 요청 → 서버 응답 → 브라우저 렌더링의 다섯 단계가 순서대로 이어집니다.

- **DNS와 HTTP는 각각 어떤 역할을 맡을까요?**
  DNS는 도메인 이름을 IP 주소로 바꾸는 전화번호부 역할을 하고, HTTP는 그 IP로 연결된 서버와 요청/응답을 주고받는 규칙입니다.

- **서버가 응답을 보내면 브라우저는 그 데이터를 어떻게 화면으로 바꿀까요?**
  브라우저는 HTML을 파싱해 DOM 트리를 만들고, CSS로 스타일을 계산한 뒤, 픽셀을 화면에 그립니다.

## 정리

웹은 여러 프로토콜이 협력하는 시스템입니다. 이 흐름을 머릿속에 넣어 두면 바이브코딩으로 만든 앱에서 문제가 생겼을 때 "어느 단계에서 문제인지"를 빠르게 파악할 수 있습니다. 다음 글에서는 브라우저가 내려받는 세 가지 언어, HTML·CSS·JavaScript를 정리합니다.

## 참고 자료

- [How the Web works (MDN)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [Chrome DevTools Network features](https://developer.chrome.com/docs/devtools/network/)
- [What is DNS? (Cloudflare Learning Center)](https://www.cloudflare.com/learning/dns/what-is-dns/)

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 웹 개발 기초 (1/10): 웹은 어떻게 동작하는가? (현재 글)**
- [바이브코딩을 위한 웹 개발 기초 (2/10): HTML, CSS, JavaScript](./02-html-css-javascript.md)
- [바이브코딩을 위한 웹 개발 기초 (3/10): 브라우저와 DOM](./03-browser-and-dom.md)
- [바이브코딩을 위한 웹 개발 기초 (4/10): HTTP와 API](./04-http-and-api.md)
- [바이브코딩을 위한 웹 개발 기초 (5/10): Frontend와 Backend](./05-frontend-and-backend.md)
- [바이브코딩을 위한 웹 개발 기초 (6/10): 인증과 세션](./06-auth-and-sessions.md)
- [바이브코딩을 위한 웹 개발 기초 (7/10): 데이터베이스 연결](./07-connecting-to-database.md)
- [바이브코딩을 위한 웹 개발 기초 (8/10): 배포](./08-deployment.md)
- [바이브코딩을 위한 웹 개발 기초 (9/10): 성능과 캐싱](./09-performance-and-caching.md)
- [바이브코딩을 위한 웹 개발 기초 (10/10): 작은 웹앱 만들기](./10-building-a-small-web-app.md)

<!-- toc:end -->

Tags: 바이브코딩, 웹개발, HTTP, DNS, 브라우저, 프론트엔드
