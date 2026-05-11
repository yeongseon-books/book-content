---
series: backend-development-101
episode: 2
title: HTTP 서버 만들기
status: content-ready
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
seo_description: HTTP 서버를 직접 만들며 요청/응답 구조와 status code/header를 손에 익히는 입문 가이드.
last_reviewed: '2026-05-11'
---

# HTTP 서버 만들기

> Backend Development 101 시리즈 (2/10)


## 이 글에서 다룰 문제

프레임워크가 가려주는 부분을 한 번이라도 직접 보면 이후 디버깅이 훨씬 빨라집니다. status code가 왜 그렇게 나왔는지, header가 왜 붙지 않았는지 본질을 모르면 결국 추측에 머물게 됩니다.

> 프레임워크는 편리하지만, 그 아래에서 무슨 일이 일어나는지 알아야 운영 판단이 정확해집니다.

## 전체 흐름
```mermaid
flowchart LR
    Client["Client"] -->|"GET / HTTP/1.1"| Sock["TCP socket"]
    Sock --> Parser["Parser"]
    Parser --> App["Handler"]
    App --> Resp["Response builder"]
    Resp --> Sock2["TCP socket"]
    Sock2 -->|"HTTP/1.1 200 OK"| Client
```

요청도 응답도 결국 텍스트 한 덩어리입니다.

## Before/After

**Before (라이브러리 안에 다 숨어 있다)**

```python
import requests
print(requests.get("https://example.com").status_code)
```

**After (요청을 직접 본다)**

```python
import socket
s = socket.create_connection(("example.com", 80))
s.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
print(s.recv(4096).decode()[:200])
```

같은 일이지만 프로토콜 텍스트가 직접 보입니다.

## 서버 5단계

### 1단계 — raw socket 서버

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

브라우저에서 `http://127.0.0.1:9000/`에 접속하면 `hello`가 보입니다.

### 2단계 — FastAPI로 같은 일

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

### 3단계 — status code 직접 지정

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

### 4단계 — 커스텀 header

```python
# 4_headers.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
app = FastAPI()

@app.get("/")
def root():
    return JSONResponse({"ok": True}, headers={"X-App": "demo"})
```

### 5단계 — curl로 응답 보기

```bash
curl -i http://127.0.0.1:9000/
```

`-i`는 응답의 헤더와 status까지 함께 보여줍니다.

## 이 코드에서 주목할 점

- `Content-Length`가 없으면 클라이언트는 본문이 어디서 끝나는지 모릅니다.
- `\r\n` 줄바꿈은 HTTP 사양입니다. `\n`만 쓰면 파서가 깨질 수 있습니다.
- 같은 URL이라도 method가 다르면 다른 동작입니다.

## 자주 하는 실수 5가지

1. **에러도 200으로 응답한다.** 모니터링이 망가집니다.
2. **`Content-Type` 을 빠뜨린다.** 클라이언트가 JSON으로 못 읽습니다.
3. **응답 본문을 안 닫는다.** 연결이 영원히 살아있게 됩니다.
4. **GET에 body를 보낸다.** 캐시와 프록시가 무시합니다.
5. **status code를 200과 500만 쓴다.** 4xx가 주는 구체적인 의미를 잃습니다.

## 실무에서는 이렇게 쓰입니다

운영 환경에서는 FastAPI 같은 프레임워크가 raw socket 처리를 대신 맡습니다. 그래도 장애가 나면 응답이 왜 끊겼는지, 어디서 잘렸는지 확인하려고 결국 socket과 header 수준까지 내려가야 합니다. tcpdump, Wireshark, curl은 그때 가장 기본이 되는 도구입니다.

## 체크리스트

- [ ] HTTP 요청의 첫 줄을 읽을 수 있다.
- [ ] status code 4xx와 5xx를 구분할 수 있다.
- [ ] curl `-i` 로 헤더를 볼 수 있다.
- [ ] FastAPI에서 status code를 직접 지정할 수 있다.
- [ ] raw socket 서버를 한 번이라도 띄워 봤다.

## 정리 및 다음 단계

HTTP 서버는 텍스트 프로토콜을 다루는 프로그램입니다. 다음 글에서는 그 위에서 어떤 함수가 어떤 path를 처리하는지 결정하는 라우터를 봅니다.

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
