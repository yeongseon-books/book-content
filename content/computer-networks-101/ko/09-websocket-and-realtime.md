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

핵심 전환점은 `101 Switching Protocols`입니다. 응답 전까지는 HTTP였던 연결이, 그 뒤에는 WebSocket 프레임 스트림으로 동작합니다.

## 핵심 용어

- **Upgrade handshake**: `Upgrade: websocket` 헤더를 넣어 프로토콜 전환을 요청하는 HTTP 핸드셰이크
- **Frame**: WebSocket이 주고받는 최소 단위. text, binary, ping, pong, close가 있습니다.
- **SSE**: 긴 HTTP 응답 위에서 서버→클라이언트로만 이벤트를 흘리는 표준 방식
- **Long-polling**: 새 이벤트가 생길 때까지 응답을 일부러 늦추는 기법
- **Backpressure**: 수신자가 느릴 때 송신 큐가 무한히 커지지 않도록 제어하는 메커니즘

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

## 이 코드에서 먼저 볼 점

- 핸드셰이크는 HTTP이지만, 응답 후에는 같은 소켓이 더 이상 HTTP가 아닙니다.
- 프레임은 가볍습니다. 메시지마다 헤더를 새로 보내지 않아 작은 메시지를 자주 보내기에 유리합니다.
- `CLIENTS` 집합은 프로세스 로컬 상태입니다. 서버가 두 대가 되면 메시지가 절반만 도착할 수 있습니다.
- ping과 pong은 사용자 메시지가 아니라 keepalive용 제어 프레임입니다.

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
- 인증 토큰 만료와 권한 회수처럼, 긴 연결이 가지는 별도 보안 경계도 분명히 그립니다.

## 체크리스트

- [ ] 정말 실시간이 필요한가, 아니면 짧은 polling이면 충분한가?
- [ ] WebSocket, SSE, long-polling 중 가장 단순한 선택을 했는가?
- [ ] ping interval과 idle timeout을 의식적으로 정했는가?
- [ ] 재연결과 메시지 재개 전략이 있는가?
- [ ] 인스턴스 수가 늘어나도 메시지가 모든 관련 클라이언트에 도달하는가?
- [ ] 프록시에서 Upgrade 헤더와 충분한 timeout을 설정했는가?

## 연습 문제

1. SSE와 WebSocket이 서로 대체 가능한 경우 두 가지, WebSocket만 적합한 경우 두 가지를 적어 보세요.
2. 5단계 채팅 서버를 두 인스턴스로 띄운 뒤 각각 다른 클라이언트를 붙여 보세요. 왜 메시지가 절반만 도착하는지 설명하고, 어떻게 고칠지 한두 문장으로 적어 보세요.
3. WebSocket 서비스를 NGINX 뒤에 둔다고 할 때 꼭 바꿔야 하는 설정을 세 가지 이상 적어 보세요.

## 정리와 다음 글

WebSocket은 HTTP로 시작하지만, 응답 이후에는 더 이상 HTTP가 아닌 연결입니다. 양방향성과 낮은 메시지 오버헤드를 얻는 대신, 오래 살아 있는 연결을 운영해야 하는 부담을 받아들여야 합니다. 가장 흔한 함정은 필요하지 않은 곳에 쓰는 것과, 공유 상태를 단일 인스턴스 메모리에 두는 것입니다.

다음 글에서는 시리즈를 마무리하며, 네트워크가 평소처럼 동작하지 않을 때 어디서부터 어떤 순서로 봐야 하는지 정리합니다.

## 심화 실습: 패킷 캡처 · 헤더 해석 · 소켓 동작 검증

네트워크 문제를 줄이려면 추상 계층 설명만으로는 부족합니다. 패킷 단위 관찰과 애플리케이션 소켓 로그를 연결해야 원인 구분이 가능합니다. 핵심은 "어느 계층에서 실패했는가"를 증거 기반으로 좁히는 것입니다.

### tcpdump로 최소 증거를 확보하기

```bash
sudo tcpdump -i any -nn "tcp port 443" -c 20
```

이 명령으로 먼저 확인할 항목은 세 가지입니다.
- SYN이 나가고 SYN-ACK가 돌아오는가
- 재전송(retransmission)이 반복되는가
- RST 패킷이 어느 쪽에서 발생하는가

연결 실패를 애플리케이션 오류로 단정하기 전에, 3-way handshake가 실제로 성립했는지 먼저 확인해야 합니다.

### IPv4/TCP 헤더를 바이트 단위로 해석하기

```text
IPv4 Header (20B 기본)
- Version/IHL
- Total Length
- Identification
- Flags/Fragment Offset
- TTL
- Protocol (6=TCP, 17=UDP)
- Header Checksum
- Source IP / Destination IP

TCP Header (20B 기본)
- Source Port / Destination Port
- Sequence Number
- Acknowledgment Number
- Data Offset
- Flags (SYN, ACK, FIN, RST, PSH)
- Window Size
- Checksum
- Urgent Pointer
```

예를 들어 SYN 패킷에서 `flags=SYN`, `ack=0`이고, 응답에서 `flags=SYN,ACK`와 함께 `ack=client_seq+1`이 오면 handshake 2단계가 정상입니다. 이 규칙만 알아도 다수의 연결 이슈를 빠르게 분류할 수 있습니다.

### Python 소켓으로 타임아웃과 재시도 경계 분리

```python
import socket

def fetch_banner(host: str, port: int, timeout: float = 2.0) -> bytes:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(b"HEAD / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        return sock.recv(512)

try:
    data = fetch_banner("93.184.216.34", 80)
    print(data.decode(errors="replace"))
except socket.timeout:
    print("timeout: 네트워크 지연 또는 서버 응답 지연")
except OSError as e:
    print(f"os error: {e}")
```

포인트는 connect timeout과 read timeout을 구분하는 것입니다. connect 단계 실패는 라우팅/방화벽/리슨 상태 문제 가능성이 크고, read 단계 실패는 애플리케이션 지연이나 서버 과부하 가능성이 큽니다.

### UDP 손실과 순서 역전 관찰 예시

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)

for i in range(1, 11):
    payload = f"seq={i}".encode()
    sock.sendto(payload, ("127.0.0.1", 9999))
```

UDP는 전달 보장과 순서 보장을 제공하지 않습니다. 따라서 실시간 시스템에서는 애플리케이션 레벨에서 `sequence`, `timestamp`, `dedup` 정책을 설계해야 합니다. 이 지점이 TCP와 UDP 선택의 핵심입니다.

### TLS 핸드셰이크를 계층별로 읽기

HTTPS 문제를 볼 때는 다음 흐름으로 분리하면 진단 속도가 올라갑니다.
1. TCP 연결 성립 여부
2. ClientHello/ServerHello 교환 여부
3. 인증서 체인 검증 성공 여부
4. 애플리케이션 데이터 송수신 여부

즉 "HTTPS 실패"라는 한 문장을 TCP, TLS, HTTP 단계로 쪼개는 습관이 필요합니다. 같은 502/504라도 실제 원인은 완전히 다를 수 있습니다.

### 패킷 캡처와 애플리케이션 로그를 합치는 방법

운영에서는 다음 필드를 공통 키로 맞추면 추적성이 좋아집니다.
- `src_ip`, `src_port`, `dst_ip`, `dst_port`
- `timestamp`(밀리초 단위)
- `request_id` 또는 `trace_id`

이 키로 묶으면 "애플리케이션에서는 timeout, 패킷에서는 SYN 재전송" 같은 상관관계를 바로 찾을 수 있습니다. 결과적으로 네트워크 팀과 애플리케이션 팀이 같은 사실 기반으로 협업할 수 있습니다.

### 점검 체크리스트

- 연결 실패 시 handshake 3단계를 캡처로 확인했는가
- TCP/UDP 선택 이유를 지연, 손실, 순서 보장 관점으로 설명할 수 있는가
- 프로토콜 헤더의 핵심 필드를 보고 상태를 해석할 수 있는가
- 소켓 timeout을 connect/read로 분리해 로깅했는가

이 기준을 적용하면 네트워크 문제는 "감"이 아니라 재현 가능한 관찰 데이터로 다뤄집니다.

## 처음 질문으로 돌아가기

- **WebSocket 연결은 HTTP에서 어떻게 업그레이드될까요?**
  - 본문의 기준은 WebSocket과 실시간 통신를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **WebSocket, SSE, long-polling 중 언제 무엇을 골라야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **ping/pong, 재연결, backpressure는 왜 운영의 핵심일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, 네트워크, WebSocket, 실시간, SSE, 스트리밍
