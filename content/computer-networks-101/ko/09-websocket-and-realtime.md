---
series: computer-networks-101
episode: 9
title: "Computer Networks 101 (9/10): WebSocket과 실시간 통신"
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
  - 네트워크
  - WebSocket
  - 실시간
  - SSE
  - 스트리밍
seo_description: WebSocket과 SSE, long-polling의 차이와 운영 포인트를 설명합니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (9/10): WebSocket과 실시간 통신

이 글은 Computer Networks 101 시리즈의 9번째 글입니다.

## 먼저 던지는 질문

- WebSocket 연결은 HTTP에서 어떻게 업그레이드될까요?
- WebSocket, SSE, long-polling 중 언제 무엇을 골라야 할까요?
- ping/pong, 재연결, backpressure는 왜 운영의 핵심일까요?

## 큰 그림

![Computer Networks 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/09/09-01-concept-at-a-glance.ko.png)

*Computer Networks 101 9장 흐름 개요*

## 왜 중요한가

대시보드, 채팅, 게임, 시세 화면, 협업 편집기는 모두 서버가 먼저 이벤트를 밀어 넣을 수 있어야 자연스럽게 동작합니다. 이걸 평범한 HTTP만으로 흉내 내려면 polling이나 long-polling으로 자원을 계속 태워야 합니다. WebSocket을 이해하면 언제 필요한지뿐 아니라, 언제 굳이 쓰지 않아도 되는지도 보이기 시작합니다.

> 실시간은 보통 "사람이 기다리기 전에 도착한다"는 뜻입니다. 5초 새로고침으로 충분한 화면에 WebSocket을 쓰면 운영 비용만 늘어납니다.

## 핵심 그림

```text
┌──────────┐                              ┌──────────┐
│ 클라이언트 │                              │   서버    │
└─────┬────┘                              └─────┬────┘
      │                                         │
      │── GET /chat HTTP/1.1 ──────────────────▶│
      │   Upgrade: websocket                    │
      │   Connection: Upgrade                   │
      │   Sec-WebSocket-Key: dGhlIHNhbXBsZ...  │
      │                                         │
      │◀── HTTP/1.1 101 Switching Protocols ────│
      │    Upgrade: websocket                   │
      │    Sec-WebSocket-Accept: s3pPLM...      │
      │                                         │
      │═══════════ WebSocket 프레임 ════════════│
      │                                         │
      │──── [text frame] "hello" ──────────────▶│
      │◀─── [text frame] "world" ───────────────│
      │──── [ping] ────────────────────────────▶│
      │◀─── [pong] ─────────────────────────────│
      │──── [close] ───────────────────────────▶│
      │◀─── [close] ─────────────────────────────│
```

핵심 전환점은 `101 Switching Protocols`입니다. 응답 전까지는 HTTP였던 연결이, 그 뒤에는 WebSocket 프레임 스트림으로 동작합니다. 같은 TCP 소켓을 재사용하므로 추가 핸드셰이크가 없습니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| Upgrade handshake | `Upgrade: websocket` 헤더를 넣어 프로토콜 전환을 요청하는 HTTP 핸드셰이크 |
| Frame | WebSocket이 주고받는 최소 단위. text, binary, ping, pong, close가 있습니다 |
| Opcode | 프레임 종류를 나타내는 4비트 값 (0x1=text, 0x2=binary, 0x8=close, 0x9=ping, 0xA=pong) |
| SSE | 긴 HTTP 응답 위에서 서버→클라이언트로만 이벤트를 흘리는 표준 방식 |
| Long-polling | 새 이벤트가 생길 때까지 응답을 일부러 늦추는 기법 |
| Backpressure | 수신자가 느릴 때 송신 큐가 무한히 커지지 않도록 제어하는 메커니즘 |
| Heartbeat | ping/pong으로 연결 생존을 확인하는 주기적 프레임 |

## Before/After

**Before — 5초마다 polling**

```python
# client.py — naive polling for new messages
import time, requests

last_id = 0
while True:
    resp = requests.get(f"https://api.example.com/messages?since={last_id}")
    for msg in resp.json():
        print(msg["text"])
        last_id = max(last_id, msg["id"])
    time.sleep(5)
```

아무 일도 없는데 5초마다 요청이 나가고, 새 메시지는 최대 5초 늦게 보입니다.

**After — WebSocket으로 즉시 수신**

```python
# client.py — uses the websockets library
import asyncio
import websockets

async def listen():
    async with websockets.connect("wss://api.example.com/messages") as ws:
        async for raw in ws:  # arrives the moment the server sends it
            print(raw)

asyncio.run(listen())
```

이제 클라이언트가 계속 묻지 않아도, 서버가 이벤트가 생기는 순간 바로 밀어 넣을 수 있습니다.

## WebSocket vs SSE vs Long-polling 비교

| 기준 | WebSocket | SSE | Long-polling |
| --- | --- | --- | --- |
| 방향 | 양방향 | 서버→클라이언트 | 서버→클라이언트 (요청 단위) |
| 프로토콜 | ws:// / wss:// | HTTP (text/event-stream) | HTTP |
| 연결 유지 | 하나의 TCP 연결 상시 유지 | 하나의 HTTP 응답이 계속 열림 | 요청마다 새 연결 (또는 keep-alive) |
| 브라우저 지원 | 거의 모든 최신 브라우저 | IE 제외 모든 브라우저 | 모든 브라우저 |
| 자동 재연결 | 직접 구현 필요 | EventSource API 내장 | 직접 구현 필요 |
| HTTP/2 호환 | 별도 연결 필요 | 멀티플렉싱 가능 | 완전 호환 |
| 프록시 통과 | Upgrade 설정 필요 | 일반 HTTP로 통과 | 문제 없음 |
| 적합한 경우 | 채팅, 게임, 협업 편집기 | 알림, 대시보드, 실시간 피드 | 업데이트 빈도 낮고 단순함 우선 |

SSE 서버 예시:

```python
# sse_server.py — Flask
from flask import Flask, Response
import time

app = Flask(__name__)

@app.get('/events')
def events():
    def generate():
        event_id = 0
        while True:
            event_id += 1
            yield f"id: {event_id}\ndata: tick {event_id}\n\n"
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')
```

클라이언트(브라우저):

```javascript
const source = new EventSource('/events');
source.onmessage = (e) => console.log(e.data);
// 연결이 끊기면 EventSource가 자동으로 재연결합니다
```

## WebSocket 에코 서버를 단계별로 만들기

### 1단계 — 의존성 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install websockets
```

`websockets`는 `asyncio` 기반으로 널리 쓰이는 Python WebSocket 라이브러리입니다.

### 2단계 — 가장 단순한 에코 서버

```python
# server.py
import asyncio
import websockets

async def echo(ws):
    async for message in ws:
        await ws.send(f"echo: {message}")

async def main():
    async with websockets.serve(echo, "127.0.0.1", 8765):
        print("listening on ws://127.0.0.1:8765")
        await asyncio.Future()  # run forever

asyncio.run(main())
```

`async for message in ws`가 핵심입니다. 프레임이 들어올 때마다 코루틴이 깨어납니다.

### 3단계 — 직접 메시지 보내 보기

다른 터미널에서 `websocat`이나 짧은 Python 클라이언트로 테스트합니다.

```python
# client.py
import asyncio, websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        await ws.send("hello")
        print(await ws.recv())  # → echo: hello
        await ws.send("world")
        print(await ws.recv())  # → echo: world

asyncio.run(main())
```

두 번의 주고받기가 같은 연결 안에서 일어난다는 점이 중요합니다. 메시지마다 새 TCP 핸드셰이크를 하지 않습니다.

### 4단계 — ping/pong으로 죽은 연결 감지

```python
# server.py — add keepalive options
async with websockets.serve(
    echo, "127.0.0.1", 8765,
    ping_interval=20,   # send a ping every 20 s
    ping_timeout=20,    # close if no pong within 20 s
):
    await asyncio.Future()
```

이 설정은 NAT나 로드밸런서가 idle 연결을 조용히 끊는 상황을 줄이고, 깨진 peer를 서버가 빨리 알아차리게 해 줍니다.

### 5단계 — 브로드캐스트로 작은 채팅 만들기

```python
# server.py
import asyncio, websockets

CLIENTS = set()

async def chat(ws):
    CLIENTS.add(ws)
    try:
        async for message in ws:
            await asyncio.gather(*[c.send(message) for c in CLIENTS])
    finally:
        CLIENTS.discard(ws)

async def main():
    async with websockets.serve(chat, "127.0.0.1", 8765):
        await asyncio.Future()

asyncio.run(main())
```

클라이언트를 두 개 띄우고 한쪽에서 보내면 다른 쪽에서도 메시지가 보입니다. 다만 `CLIENTS` 집합은 **이 프로세스 메모리 안에서만** 유지됩니다. 이 한계가 곧 운영 이야기로 이어집니다.

### 6단계 — 재연결과 지수 백오프

클라이언트는 연결이 끊길 수 있다는 것을 항상 가정해야 합니다.

```python
# client_with_reconnect.py
import asyncio, websockets, random

async def listen_with_reconnect(url: str):
    backoff = 1.0
    while True:
        try:
            async with websockets.connect(url) as ws:
                backoff = 1.0  # 연결 성공하면 백오프 초기화
                async for message in ws:
                    print(message)
        except (websockets.ConnectionClosed, OSError) as e:
            jitter = random.uniform(0, backoff * 0.3)
            wait = backoff + jitter
            print(f"disconnected: {e}, reconnecting in {wait:.1f}s")
            await asyncio.sleep(wait)
            backoff = min(backoff * 2, 60.0)  # 최대 60초

asyncio.run(listen_with_reconnect("ws://127.0.0.1:8765"))
```

핵심 포인트:
- 연결 성공 시 백오프를 초기화합니다.
- 지수 백오프에 jitter를 추가해 thundering herd를 방지합니다.
- 최대 백오프를 설정해 너무 오래 기다리지 않게 합니다.

## NGINX에서 WebSocket 프록시 설정

WebSocket을 reverse proxy 뒤에 두려면 추가 설정이 필요합니다.

```nginx
# nginx.conf
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 443 ssl;
    server_name ws.example.com;

    location /ws/ {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # WebSocket idle timeout (기본 60s는 너무 짧음)
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

빠뜨리기 쉬운 세 가지:
1. `proxy_http_version 1.1` — HTTP/1.0은 Upgrade를 지원하지 않습니다.
2. `Upgrade`와 `Connection` 헤더 전달 — 없으면 101 응답이 클라이언트에 도달하지 않습니다.
3. `proxy_read_timeout` 연장 — 기본 60초가 지나면 nginx가 연결을 끊습니다.

## 이 코드에서 먼저 볼 점

- 핸드셰이크는 HTTP이지만, 응답 후에는 같은 소켓이 더 이상 HTTP가 아닙니다.
- 프레임은 가볍습니다. 메시지마다 헤더를 새로 보내지 않아 작은 메시지를 자주 보내기에 유리합니다.
- `CLIENTS` 집합은 프로세스 로컬 상태입니다. 서버가 두 대가 되면 메시지가 절반만 도착할 수 있습니다.
- ping과 pong은 사용자 메시지가 아니라 keepalive용 제어 프레임입니다.
- close 프레임도 양쪽이 교환해야 깔끔하게 종료됩니다.

## Backpressure와 메시지 큐 관리

느린 클라이언트가 있을 때 서버의 송신 큐가 무한히 커지면 메모리가 고갈됩니다.

```python
# backpressure 전략 예시
async def chat_with_backpressure(ws):
    CLIENTS.add(ws)
    try:
        async for message in ws:
            for client in list(CLIENTS):
                try:
                    # 큐가 너무 크면 해당 클라이언트 연결을 끊음
                    if client.transport.get_write_buffer_size() > 65536:
                        await client.close(1008, "slow consumer")
                        CLIENTS.discard(client)
                    else:
                        await client.send(message)
                except websockets.ConnectionClosed:
                    CLIENTS.discard(client)
    finally:
        CLIENTS.discard(ws)
```

운영 수준에서 backpressure를 다루는 방법:

| 전략 | 동작 | 적합한 경우 |
| --- | --- | --- |
| Drop oldest | 큐가 가득 차면 오래된 메시지부터 버림 | 시세, 센서 데이터 (최신만 중요) |
| Drop newest | 큐가 가득 차면 새 메시지를 버림 | 드물게 사용 |
| Disconnect | 느린 클라이언트 연결을 강제 종료 | 채팅 (재연결 후 히스토리 로드) |
| Throttle | 전송 속도를 제한 | 스트리밍 (프레임 스킵) |

## 다중 인스턴스와 메시지 버스

```text
┌────────────┐     ┌────────────┐
│ WS Gateway │     │ WS Gateway │
│ Instance 1 │     │ Instance 2 │
│ (clients   │     │ (clients   │
│  A, B, C)  │     │  D, E, F)  │
└──────┬─────┘     └──────┬─────┘
       │                   │
       └─────────┬─────────┘
                 │
         ┌───────┴───────┐
         │  Redis Pub/Sub │
         │  (또는 NATS,   │
         │   Kafka)       │
         └───────────────┘
```

클라이언트 A가 메시지를 보내면:
1. Gateway 1이 수신
2. Redis에 publish
3. Gateway 1과 2 모두 subscribe로 수신
4. 각 gateway가 자기에게 연결된 클라이언트에게 전달

이 구조 없이는 인스턴스를 늘릴 수 없습니다.

Redis pub/sub을 사용한 구현 예시:

```python
# gateway.py — Redis pub/sub 기반 브로드캐스트
import asyncio, websockets, redis.asyncio as redis

CLIENTS = set()
r = redis.Redis()

async def subscriber():
    pubsub = r.pubsub()
    await pubsub.subscribe('chat')
    async for message in pubsub.listen():
        if message['type'] == 'message':
            data = message['data'].decode()
            await asyncio.gather(*[c.send(data) for c in CLIENTS])

async def handler(ws):
    CLIENTS.add(ws)
    try:
        async for message in ws:
            await r.publish('chat', message)  # 모든 gateway에 전파
    finally:
        CLIENTS.discard(ws)

async def main():
    asyncio.create_task(subscriber())
    async with websockets.serve(handler, '0.0.0.0', 8765):
        await asyncio.Future()

asyncio.run(main())
```

이 패턴이면 Gateway 1에 연결된 클라이언트가 보낸 메시지가 Redis를 통해 Gateway 2에도 전달되어, Gateway 2에 연결된 클라이언트도 메시지를 받을 수 있습니다.

## WebSocket 보안 고려사항

긴 연결은 HTTP 요청/응답과 다른 보안 경계를 가집니다.

| 위협 | 대응 |
| --- | --- |
| 인증 토큰 만료 후에도 연결 유지 | 서버에서 주기적으로 토큰 유효성 검증, 만료 시 close frame 전송 |
| CSRF (Cross-Site WebSocket Hijacking) | 연결 시 Origin 헤더 검증, 또는 handshake에 토큰 포함 |
| DoS (대량 연결) | 클라이언트당 연결 수 제한, rate limiting |
| 메시지 인젝션 | 모든 수신 메시지를 서버에서 검증 후 브로드캐스트 |
| 암호화되지 않은 전송 | 반드시 wss:// (TLS) 사용 |

```python
# handshake 시 토큰 검증 예시
async def handler(ws):
    # 첫 메시지로 인증 토큰을 받음
    try:
        auth_msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
        token = json.loads(auth_msg).get('token')
        if not verify_token(token):
            await ws.close(4001, 'unauthorized')
            return
    except asyncio.TimeoutError:
        await ws.close(4002, 'auth timeout')
        return
    
    # 인증 성공 후 정상 처리
    CLIENTS.add(ws)
    try:
        async for message in ws:
            await broadcast(message)
    finally:
        CLIENTS.discard(ws)
```

## 자주 하는 실수 5가지

1. **polling이면 충분한 곳에 WebSocket을 붙입니다.** 30초 단위 갱신이면 plain HTTP가 더 싸고 디버깅도 쉽습니다.
2. **공유 상태를 인스턴스 메모리에만 둡니다.** 서버가 두 대가 되는 순간 브로드캐스트가 조용히 깨집니다. Redis pub/sub, NATS, Kafka 같은 메시지 버스를 처음부터 고려해야 합니다.
3. **재연결 전략이 없습니다.** 모바일 네트워크는 자주 끊깁니다. 지수 백오프와 마지막 이벤트 ID 기준 재개 전략이 필요합니다.
4. **backpressure를 무시합니다.** 느린 클라이언트 때문에 송신 큐가 계속 커지면 결국 프로세스 메모리가 무너집니다.
5. **L7 프록시 설정을 잊습니다.** NGINX 같은 프록시는 idle timeout이 짧습니다. `Upgrade`, `Connection`, 충분한 `proxy_read_timeout`이 필요합니다.

## 실무에서는 이렇게 보입니다

대규모 실시간 시스템은 보통 **WebSocket gateway 계층**과 **메시지 버스**를 분리합니다. gateway는 연결 유지와 수신 이벤트 publish만 담당하고, 메시지 버스가 다른 gateway 인스턴스에 붙어 있는 클라이언트까지 이벤트를 전파합니다. 이 구조가 있어야 gateway를 안전하게 오토스케일할 수 있습니다.

배포 방식도 일반 HTTP와 다릅니다. WebSocket 서비스는 **기존 연결을 끊지 않고 새 버전을 도입**해야 합니다. 보통은 graceful drain으로 새 연결만 새 버전으로 보내고, 기존 연결은 자연스럽게 종료되게 둡니다.

선택 기준은 단순합니다. 서버가 **자주, 양방향으로** 이벤트를 주고받아야 하면 WebSocket을 씁니다. 한 방향 스트리밍이면 SSE가 더 단순하고 HTTP/2와도 잘 맞습니다. 업데이트 빈도가 낮다면 polling이면 충분합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 먼저 "정말 실시간이 필요한가"를 묻습니다. WebSocket의 큰 비용은 코드보다 운영에 있습니다.
- "연결이 잠깐 흔들린 것"과 "연결이 완전히 죽은 것"을 구분합니다. 재연결과 resume 전략이 설계의 절반입니다.
- 인스턴스 메모리를 절대 신뢰하지 않습니다. 처음부터 메시지 버스를 상정합니다.
- backpressure를 사용자가 느끼기 전에 시스템이 먼저 감지해야 한다고 봅니다.
- 인증 토큰 만료와 권한 회수처럼, 긴 연결이 가지는 별도 보안 경계도 분명히 그립니다. WebSocket은 연결 시점에만 인증하므로, 토큰이 만료된 후에도 연결이 살아 있을 수 있습니다.

## 체크리스트

- [ ] 정말 실시간이 필요한가, 아니면 짧은 polling이면 충분한가?
- [ ] WebSocket, SSE, long-polling 중 가장 단순한 선택을 했는가?
- [ ] ping interval과 idle timeout을 의식적으로 정했는가?
- [ ] 재연결과 메시지 재개 전략이 있는가?
- [ ] 인스턴스 수가 늘어나도 메시지가 모든 관련 클라이언트에 도달하는가?
- [ ] 프록시에서 Upgrade 헤더와 충분한 timeout을 설정했는가?
- [ ] backpressure 정책을 정했는가?
- [ ] 인증 토큰 만료 시 연결을 어떻게 처리할지 정했는가?

## 연습 문제

1. SSE와 WebSocket이 서로 대체 가능한 경우 두 가지, WebSocket만 적합한 경우 두 가지를 적어 보세요.
2. 5단계 채팅 서버를 두 인스턴스로 띄운 뒤 각각 다른 클라이언트를 붙여 보세요. 왜 메시지가 절반만 도착하는지 설명하고, 어떻게 고칠지 한두 문장으로 적어 보세요.
3. WebSocket 서비스를 NGINX 뒤에 둔다고 할 때 꼭 바꿔야 하는 설정을 세 가지 이상 적어 보세요.
4. 지수 백오프 재연결에서 jitter를 넣는 이유를 한 문장으로 설명해 보세요.
5. backpressure가 없으면 어떤 순서로 장애가 확대되는지 3단계로 적어 보세요.

## 정리와 다음 글

WebSocket은 HTTP로 시작하지만, 응답 이후에는 더 이상 HTTP가 아닌 연결입니다. 양방향성과 낮은 메시지 오버헤드를 얻는 대신, 오래 살아 있는 연결을 운영해야 하는 부담을 받아들여야 합니다. 가장 흔한 함정은 필요하지 않은 곳에 쓰는 것과, 공유 상태를 단일 인스턴스 메모리에 두는 것입니다.

다음 글에서는 시리즈를 마무리하며, 네트워크가 평소처럼 동작하지 않을 때 어디서부터 어떤 순서로 봐야 하는지 정리합니다.

## 처음 질문으로 돌아가기

- **WebSocket 연결은 HTTP에서 어떻게 업그레이드될까요?**
  - 클라이언트가 `Upgrade: websocket`과 `Sec-WebSocket-Key` 헤더를 포함한 HTTP GET 요청을 보내면, 서버가 `101 Switching Protocols`로 응답합니다. 이 시점부터 같은 TCP 소켓이 HTTP가 아닌 WebSocket 프레임 프로토콜로 동작합니다. 추가 TCP 핸드셰이크 없이 기존 연결을 그대로 전환하는 것이 핵심입니다.
- **WebSocket, SSE, long-polling 중 언제 무엇을 골라야 할까요?**
  - 양방향 통신(채팅, 게임, 협업 편집기)이면 WebSocket이 유일한 선택입니다. 서버→클라이언트 단방향이면 SSE가 더 단순하고 자동 재연결까지 내장되어 있습니다. 업데이트 빈도가 낮고(30초+) 인프라 단순함이 우선이면 polling이면 충분합니다.
- **ping/pong, 재연결, backpressure는 왜 운영의 핵심일까요?**
  - ping/pong 없이는 NAT 타임아웃이나 네트워크 장애로 끊긴 연결을 서버가 감지하지 못해 리소스가 누수됩니다. 재연결 전략 없이는 일시적 네트워크 불안정에도 사용자가 수동으로 새로고침해야 합니다. backpressure 없이는 느린 클라이언트 하나가 서버 메모리를 고갈시켜 전체 서비스를 무너뜨릴 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Networks 101 (1/10): 네트워크란 무엇인가?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP와 subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP와 UDP](./03-tcp-and-udp.md)
- [Computer Networks 101 (4/10): DNS](./04-dns.md)
- [Computer Networks 101 (5/10): HTTP와 HTTPS](./05-http-and-https.md)
- [Computer Networks 101 (6/10): TLS 기초](./06-tls-basics.md)
- [Computer Networks 101 (7/10): 라우팅과 NAT](./07-routing-and-nat.md)
- [Computer Networks 101 (8/10): Load Balancer](./08-load-balancer.md)
- **WebSocket과 실시간 통신 (현재 글)**
- 네트워크 문제 디버깅 (예정)

<!-- toc:end -->

## 참고 자료

- [RFC 6455 — The WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [MDN — Writing WebSocket servers](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers)
- [websockets (Python) Documentation](https://websockets.readthedocs.io/)
- [NGINX — WebSocket Proxying](https://nginx.org/en/docs/http/websocket.html)
- [book-examples: computer-networks-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, WebSocket, 실시간, SSE, 스트리밍
