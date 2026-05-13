---
series: backend-development-101
episode: 2
title: HTTP 서버 만들기
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
last_reviewed: '2026-05-12'
---

# HTTP 서버 만들기

이 글은 Backend Development 101 시리즈의 두 번째 글입니다. 프레임워크를 쓰다 보면 HTTP 서버가 실제로 무엇을 하는지 잊기 쉽습니다. 여기서는 요청과 응답이 결국 텍스트라는 사실부터 시작해, raw socket과 FastAPI를 함께 보면서 서버의 가장 바닥 구조를 잡아 보겠습니다.

## 이 글에서 다룰 문제

- HTTP 요청과 응답은 실제로 어떤 모양의 텍스트일까요?
- HTTP는 TCP 위에서 어떻게 동작할까요?
- status code와 header는 왜 단순 장식이 아니라 계약일까요?
- raw socket 서버와 FastAPI 서버는 무엇이 같고 무엇이 다를까요?
- 운영 장애가 났을 때 왜 다시 헤더와 소켓으로 내려가야 할까요?

## 왜 중요한가

프레임워크가 가려 주는 것을 한 번 직접 보면 이후의 디버깅 속도가 완전히 달라집니다. status code가 왜 이상한지, header가 왜 빠졌는지, 응답이 왜 중간에 끊겼는지를 추측이 아니라 구조로 설명할 수 있게 되기 때문입니다.

시니어 엔지니어가 프레임워크를 덜 쓰기 때문이 아니라, 프레임워크 뒤에 무엇이 있는지 알고 있기 때문에 운영 판단이 빠른 것입니다. 백엔드 입문에서 HTTP의 텍스트 구조를 직접 보는 경험은 그 감각을 만드는 가장 짧은 길입니다.

> HTTP 서버는 소켓에서 요청 텍스트를 읽고, 응답 텍스트를 다시 써 주는 프로그램입니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Client["Client"] -->|"GET / HTTP/1.1"| Sock["TCP socket"]
    Sock --> Parser["Parser"]
    Parser --> App["Handler"]
    App --> Resp["Response builder"]
    Resp --> Sock2["TCP socket"]
    Sock2 -->|"HTTP/1.1 200 OK"| Client
```

요청과 응답은 결국 텍스트 블록입니다. 서버는 소켓에서 바이트를 읽고, 그것을 HTTP 요청으로 해석하고, 다시 응답 텍스트를 써 주는 프로그램입니다.

## 핵심 용어

- **Request line**: `GET /path HTTP/1.1`처럼 메서드, 경로, 버전을 담는 첫 줄입니다.
- **Status line**: `HTTP/1.1 200 OK`처럼 응답의 첫 줄입니다.
- **Header**: `Key: Value` 형식의 메타데이터입니다.
- **Body**: JSON, HTML, 파일처럼 실제 데이터를 담는 부분입니다.
- **Method**: GET, POST, PUT, DELETE처럼 요청의 종류를 나타냅니다.

## Before/After

**Before (the library hides everything)**

```python
import requests
print(requests.get("https://example.com").status_code)
```

**After (you watch the bytes)**

```python
import socket
s = socket.create_connection(("example.com", 80))
s.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
print(s.recv(4096).decode()[:200])
```

두 코드는 비슷한 일을 하지만, 두 번째 코드는 프로토콜 텍스트가 눈앞에 드러납니다. 이 차이가 나중에 운영 문제를 설명할 수 있는지 없는지를 가릅니다.

## 실습: 다섯 단계로 보는 HTTP 서버

### Step 1 — Raw socket server

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

### Step 2 — Same thing with FastAPI

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

### Step 3 — Choose your status code

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

### Step 4 — Custom headers

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

### Step 5 — Inspect with curl

```bash
curl -i http://127.0.0.1:9000/
```

`-i` 옵션은 body뿐 아니라 status line과 header까지 함께 보여 줍니다. 브라우저가 가리는 것을 보려면 결국 이런 도구로 다시 내려가야 합니다.

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

<!-- toc:begin -->
- [백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
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

- [HTTP messages (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages)
- [HTTP status codes (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [FastAPI responses](https://fastapi.tiangolo.com/advanced/response-directly/)
- [curl manual](https://curl.se/docs/manual.html)

Tags: Backend, HTTP, Python, FastAPI, Networking
