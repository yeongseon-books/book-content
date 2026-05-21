---
series: backend-development-101
episode: 2
title: "Backend Development 101 (2/10): HTTP 서버 만들기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Backend
  - HTTP
  - Python
  - FastAPI
  - Networking
seo_description: HTTP 서버의 본질을 소켓부터 FastAPI까지 따라가는 입문 가이드입니다
last_reviewed: '2026-05-15'
---

# Backend Development 101 (2/10): HTTP 서버 만들기

이 글은 Backend Development 101 시리즈의 2번째 글입니다.

프레임워크를 오래 쓰다 보면 HTTP 서버가 실제로 무슨 일을 하는지 잊기 쉽습니다. 하지만 응답이 잘리거나, 헤더가 빠지거나, 프록시 뒤에서 동작이 달라지는 순간에는 결국 요청과 응답의 가장 바닥 구조까지 내려가 봐야 합니다.

여기서는 요청과 응답이 결국 텍스트라는 사실부터 시작해, raw socket과 FastAPI를 함께 보면서 서버의 가장 바닥 구조를 잡아 보겠습니다.

![Backend Development 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/02/02-01-concept-at-a-glance.ko.png)
*Backend Development 101 2장 흐름 개요*

## 먼저 던지는 질문

- HTTP 요청과 응답은 실제로 어떤 모양의 텍스트일까요?
- HTTP는 TCP 위에서 어떻게 동작할까요?
- status code와 header는 왜 단순 장식이 아니라 계약일까요?

## 왜 중요한가

프레임워크가 가려 주는 것을 한 번 직접 보면 이후의 디버깅 속도가 완전히 달라집니다. status code가 왜 이상한지, header가 왜 빠졌는지, 응답이 왜 중간에 끊겼는지를 추측이 아니라 구조로 설명할 수 있게 되기 때문입니다.

시니어 엔지니어가 프레임워크를 덜 쓰기 때문이 아니라, 프레임워크 뒤에 무엇이 있는지 알고 있기 때문에 운영 판단이 빠른 것입니다. 백엔드 입문에서 HTTP의 텍스트 구조를 직접 보는 경험은 그 감각을 만드는 가장 짧은 길입니다.

> HTTP 서버는 소켓에서 요청 텍스트를 읽고, 응답 텍스트를 다시 써 주는 프로그램입니다.

## 한눈에 보는 개념

요청과 응답은 결국 텍스트 블록입니다. 서버는 소켓에서 바이트를 읽고, 그것을 HTTP 요청으로 해석하고, 다시 응답 텍스트를 써 주는 프로그램입니다.

## 핵심 용어

- **Request line**: `GET /path HTTP/1.1`처럼 메서드, 경로, 버전을 담는 첫 줄입니다.
- **Status line**: `HTTP/1.1 200 OK`처럼 응답의 첫 줄입니다.
- **Header**: `Key: Value` 형식의 메타데이터입니다.
- **Body**: JSON, HTML, 파일처럼 실제 데이터를 담는 부분입니다.
- **Method**: GET, POST, PUT, DELETE처럼 요청의 종류를 나타냅니다.

## 개선 전/개선 후

**Before (라이브러리가 모든 것을 감춤)**

```python
import requests
print(requests.get("https://example.com").status_code)
```

**After (바이트를 직접 관찰)**

```python
import socket
s = socket.create_connection(("example.com", 80))
s.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
print(s.recv(4096).decode()[:200])
```

두 코드는 비슷한 일을 하지만, 두 번째 코드는 프로토콜 텍스트가 눈앞에 드러납니다. 이 차이가 나중에 운영 문제를 설명할 수 있는지 없는지를 가릅니다.

## 실습: 다섯 단계로 보는 하이퍼텍스트 전송 프로토콜 서버

### 단계 1 — 로우 소켓 서버

```python
# 1_socket_server.py
import socket
srv = socket.socket()
srv.bind(("127.0.0.1", 9000))
srv.listen()
conn, _ = srv.accept()
data = conn.recv(1024)
print(data.decode())
conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello")
conn.close()
```

브라우저에서 `http://127.0.0.1:9000/`를 열면 `hello`가 보입니다. 프레임워크 없이도 서버가 본질적으로 하는 일은 요청을 읽고 응답을 쓰는 것뿐이라는 사실을 여기서 직접 확인할 수 있습니다.

### 단계 2 — 파이썬 웹 프레임워크로 같은 서버 만들기

```python
# 2_fastapi.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return "hello"
```

```bash
uvicorn 2_fastapi:app --port 9000
```

FastAPI는 같은 일을 훨씬 편하게 하게 해 줍니다. 하지만 편해졌다고 해서 서버의 본질이 바뀌는 것은 아닙니다.

### 단계 3 — 상태 코드 선택

```python
# 3_status.py
from fastapi import FastAPI, HTTPException
app = FastAPI()

@app.get("/items/{i}")
def get_item(i: int):
    if i < 0:
        raise HTTPException(400, "i must be >= 0")
    return {"i": i}
```

상태 코드는 단순한 숫자가 아니라 서버와 클라이언트 사이의 의미 계약입니다. 어떤 실패였는지를 코드로 분명히 구분해야 로그, 모니터링, 재시도 전략이 모두 맞게 동작합니다.

### 단계 4 — 사용자 정의 헤더

```python
# 4_headers.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
app = FastAPI()

@app.get("/")
def root():
    return JSONResponse({"ok": True}, headers={"X-App": "demo"})
```

헤더는 의도와 맥락을 전달합니다. Content-Type, Cache-Control, Authorization처럼 운영에서 중요한 정보는 대부분 헤더를 통해 오갑니다.

### 단계 5 — 명령줄 하이퍼텍스트 전송 프로토콜 도구로 관찰하기

```bash
curl -i http://127.0.0.1:9000/
```

`-i` 옵션은 body뿐 아니라 status line과 header까지 함께 보여 줍니다. 브라우저가 가리는 것을 보려면 결국 이런 도구로 다시 내려가야 합니다.

## 검증 포인트

**Expected output:** raw socket 서버에서는 터미널에 요청 텍스트가 찍히고, 브라우저나 `curl -i`에서는 `HTTP/1.1 200 OK`와 `hello`가 보여야 합니다.

### 먼저 확인할 실패 지점

- 브라우저가 계속 대기하면 `Content-Length`와 연결 종료가 빠지지 않았는지 확인합니다.
- 응답 파싱이 이상하면 줄바꿈이 `
`인지 먼저 봅니다.
- FastAPI 예제가 안 뜨면 `uvicorn 2_fastapi:app --port 9000`처럼 import 경로를 다시 확인합니다.

## 이 코드에서 먼저 볼 점

- `Content-Length`가 없으면 클라이언트는 body의 끝을 알 수 없습니다.
- HTTP는 `\r\n` 줄바꿈을 기대하므로 plain `\n`만 쓰면 파서가 깨질 수 있습니다.
- 같은 URL이라도 메서드가 다르면 다른 동작입니다.

이 세 가지는 문법보다 더 중요합니다. HTTP를 텍스트 프로토콜로 본다는 감각이 생기면, 프레임워크의 동작도 훨씬 덜 신비롭게 느껴집니다.

## 자주 하는 실수 5가지

1. **오류인데도 200을 반환하는 실수**입니다. 모니터링이 깨집니다.
2. **`Content-Type`을 빼먹는 실수**입니다. 클라이언트가 JSON을 해석할 수 없습니다.
3. **응답 body 종료를 제대로 처리하지 않는 실수**입니다. 연결이 새어 나갑니다.
4. **GET에 body를 보내는 실수**입니다. 캐시와 프록시가 무시할 수 있습니다.
5. **200과 500만 쓰는 실수**입니다. 4xx 계열이 가진 의미를 모두 잃습니다.

## 운영에서는 이렇게 드러납니다

배포 직전까지는 정상처럼 보이던 서버가 운영 트래픽에서만 흔들리는 경우가 있습니다. 이때 원인을 빨리 찾는 팀은 예외 메시지보다 먼저 요청 경계를 확인합니다. 어떤 프록시를 거쳤는지, 원래 메서드가 유지됐는지, 본문 길이와 헤더가 실제로 일치하는지를 체크하면 문제를 훨씬 빠르게 좁힐 수 있습니다.

특히 HTTP/1.1 keep-alive 구간에서는 이전 요청의 흔적이 다음 요청에 영향을 주는 것처럼 보이는 착시가 생길 수 있습니다. 실제로는 연결 재사용 과정에서 파서가 읽어야 할 바이트 수를 잘못 판단한 경우가 많습니다. 그래서 `Content-Length`, `Transfer-Encoding`, 연결 종료 조건을 함께 보는 습관이 중요합니다.

실무에서 많이 쓰는 점검 순서는 단순합니다. 첫째, 같은 요청을 로컬과 운영에서 `curl -v`로 각각 기록합니다. 둘째, 응답 상태 코드와 헤더를 한 줄씩 비교합니다. 셋째, 애플리케이션 로그와 리버스 프록시 로그를 같은 요청 식별자로 묶어 확인합니다. 이 세 단계만 지켜도 문제를 네트워크 계층, 애플리케이션 계층, 설정 계층 중 어디에서 먼저 봐야 할지 명확해집니다.

실제 운영에서는 FastAPI가 소켓 처리 대부분을 대신합니다. 그래도 장애가 나면 결국 tcpdump, Wireshark, curl 같은 도구로 내려가 헤더와 연결 상태를 봐야 합니다. 응답이 잘렸는지, 중간 프록시가 무엇을 바꿨는지, 서버가 어떤 코드를 돌려줬는지는 그 레벨에서만 명확해집니다.

그래서 HTTP 서버를 배운다는 것은 FastAPI 문법을 하나 더 익히는 일이 아니라, 프레임워크 아래에서 무슨 일이 일어나는지 설명할 수 있게 되는 일입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 상태 코드는 장식이 아니라 계약입니다.
- 헤더는 의도를 전달하므로 명확하게 설정합니다.
- timeout과 keep-alive는 추측하지 않고 설정합니다.
- 응답 크기에는 항상 상한이 있습니다.
- raw HTTP를 자주 읽어 본 경험이 실제 장애 때 큰 차이를 만듭니다.

## 체크리스트

- [ ] HTTP 요청 첫 줄을 읽을 수 있습니다.
- [ ] 4xx와 5xx의 차이를 설명할 수 있습니다.
- [ ] `curl -i`로 헤더를 확인할 수 있습니다.
- [ ] FastAPI에서 상태 코드를 지정할 수 있습니다.
- [ ] raw socket 서버를 한 번이라도 실행해 보았습니다.

## 연습 문제

1. raw socket 서버가 `Content-Type: application/json` 헤더와 JSON body를 반환하도록 바꿔 보세요.
2. FastAPI에 `503`을 반환하는 `/error` 경로를 추가해 보세요.
3. `curl -v`로 서버에 요청을 보내고 요청/응답 전체 텍스트를 캡처해 보세요.

## 정리와 다음 글

HTTP 서버는 텍스트 프로토콜을 읽고 쓰는 프로그램입니다. 다음 글에서는 그 위에 라우터를 올려, 어떤 경로를 어떤 함수가 처리할지 정하는 구조를 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **HTTP 요청과 응답은 실제로 어떤 모양의 텍스트일까요?**
  - 본문의 기준은 HTTP 서버 만들기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **HTTP는 TCP 위에서 어떻게 동작할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **status code와 header는 왜 단순 장식이 아니라 계약일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- **HTTP 서버 만들기 (현재 글)**
- Routing과 Controller (예정)
- Service Layer (예정)
- Database Layer (예정)
- 인증과 권한 (예정)
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [HTTP messages (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages)
- [HTTP status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [FastAPI responses](https://fastapi.tiangolo.com/advanced/response-directly/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [curl manual](https://curl.se/docs/manual.html)

Tags: Backend, HTTP, Python, FastAPI, Networking
