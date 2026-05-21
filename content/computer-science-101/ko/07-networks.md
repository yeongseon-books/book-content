---
series: computer-science-101
episode: 7
title: "Computer Science 101 (7/10): 네트워크"
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
  - TCP/IP
  - HTTP
  - DNS
  - 소켓
seo_description: TCP/IP, HTTP, DNS가 실제로 어떻게 동작하는지 소켓 예제로 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Science 101 (7/10): 네트워크

브라우저 주소창에 도메인을 입력하고 화면에 응답이 뜨기까지는 하나의 마법 같은 요청이 아니라, 층별로 역할이 나뉜 프로토콜들이 차례로 일을 나눠 갖는 과정입니다. 느림과 오류를 빠르게 좁히는 엔지니어는 이 층을 머릿속에 그릴 수 있습니다.

이 글은 Computer Science 101 시리즈의 7번째 글입니다.

여기서는 TCP/IP 계층, HTTP 요청과 응답, DNS 이름 해석, 그리고 소켓 프로그래밍의 기초를 통해 네트워크를 구조적으로 이해해 보겠습니다.

## 먼저 던지는 질문

- 브라우저에 주소를 입력했을 때 데이터가 내 화면까지 오는 경로는 어떻게 구성될까요?
- IP, TCP, HTTP, DNS는 각각 어느 층에서 어떤 역할을 맡을까요?
- HTTP 요청과 응답은 선 위에서 어떤 형태로 오갈까요?

## 큰 그림

![Computer Science 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/07/07-01-concept-at-a-glance.ko.png)

*Computer Science 101 7장 흐름 개요*

## 이 글에서 배울 것

- TCP/IP 4계층의 역할
- HTTP 요청과 응답의 기본 구조
- DNS가 이름을 IP로 바꾸는 방식
- socket API로 서버와 직접 통신하는 방법

## 왜 중요한가

API 응답이 느릴 때, 인증서 오류가 날 때, 이상한 timeout이 발생할 때 — 모두 네트워크 계층 어딘가에 원인이 있습니다. 계층 구조를 알면 "어느 계층의 문제인가"를 묻고 답할 수 있습니다.

> 네트워크 = 약속의 계층 구조

각 계층은 아래 계층을 신뢰하면서 자기 일에만 집중합니다.

## 한눈에 보는 개념

> 데이터는 위 계층에서 아래 계층으로 내려가며 헤더가 추가되고, 받는 쪽에서는 반대로 헤더를 벗기며 올라갑니다.

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| IP | 패킷을 목적지 호스트까지 전달하는 주소 지정 프로토콜 |
| Port | 호스트 안에서 어느 프로세스가 데이터를 받을지 식별하는 번호 |
| TCP | 연결 지향이며 순서와 재전송을 보장하는 전송 프로토콜 |
| UDP | 가볍지만 신뢰성을 보장하지 않는 비연결형 프로토콜 |
| HTTP | 웹에서 요청과 응답을 교환하는 애플리케이션 계층 프로토콜 |
| DNS | 도메인 이름을 IP 주소로 바꾸는 시스템 |

## Before / After

**Before — HTTP를 마법으로 보는 코드:**

```python
import urllib.request

# You have no idea what is actually exchanged
data = urllib.request.urlopen("https://httpbin.org/get").read()
print(data[:80])
```

**After — HTTP를 한 줄씩 들여다본 코드:**

```python
import socket
import ssl

# HTTPS = TCP + TLS + HTTP
ctx = ssl.create_default_context()
with socket.create_connection(("httpbin.org", 443)) as sock:
    with ctx.wrap_socket(sock, server_hostname="httpbin.org") as tls:
        request = (
            "GET /get HTTP/1.1\r\n"
            "Host: httpbin.org\r\n"
            "Connection: close\r\n\r\n"
        )
        tls.send(request.encode())
        response = b""
        while chunk := tls.recv(4096):
            response += chunk

print(response.split(b"\r\n\r\n", 1)[0].decode())   # response headers
```

## 단계별로 따라하기

### 1단계: DNS 조회 직접 해 보기

```python
import socket

host = "www.python.org"
ip = socket.gethostbyname(host)
print(f"{host} -> {ip}")

# Find every address (IPv4, IPv6)
for info in socket.getaddrinfo(host, 443):
    family, _, _, _, sockaddr = info
    print(family.name, sockaddr)
```

### 2단계: TCP 에코 서버와 클라이언트

```python
# server.py — a simple echo server that accepts one client
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.bind(("127.0.0.1", 5050))
    srv.listen(1)
    print("listening on 127.0.0.1:5050")
    conn, addr = srv.accept()
    with conn:
        print("connected:", addr)
        while data := conn.recv(1024):
            conn.sendall(data)               # echo back exactly what came in
```

```python
# client.py — sends a message to the server above and prints the reply
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cli:
    cli.connect(("127.0.0.1", 5050))
    cli.sendall(b"Hello, network!")
    print(cli.recv(1024).decode())
```

### 3단계: HTTP 요청 직접 만들기

```python
import socket

with socket.create_connection(("example.com", 80)) as sock:
    sock.send(b"GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n")
    raw = b""
    while chunk := sock.recv(4096):
        raw += chunk

header, _, body = raw.partition(b"\r\n\r\n")
print(header.decode())
print("body bytes:", len(body))
```

### 4단계: TCP vs UDP 비교

```python
# UDP sends without a connection and does not guarantee delivery
import socket

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
    udp.sendto(b"ping", ("8.8.8.8", 53))     # just fire a datagram
    udp.settimeout(2)
    try:
        data, addr = udp.recvfrom(1024)
        print("received:", len(data), "bytes from", addr)
    except socket.timeout:
        print("no reply — UDP does not retransmit")
```

### 5단계: 응답 시간을 계층별로 측정

```python
import socket
import time
import urllib.request

host = "www.python.org"

t0 = time.perf_counter()
ip = socket.gethostbyname(host)
t1 = time.perf_counter()

with socket.create_connection((ip, 443)) as sock:
    t2 = time.perf_counter()

t3 = time.perf_counter()
urllib.request.urlopen(f"https://{host}/").read()
t4 = time.perf_counter()

print(f"DNS    : {(t1 - t0) * 1000:6.1f} ms")
print(f"TCP    : {(t2 - t1) * 1000:6.1f} ms")
print(f"HTTPS  : {(t4 - t3) * 1000:6.1f} ms (total)")
```

**Expected output:** `DNS`, `TCP`, `HTTPS` 구간이 각각 별도 시간으로 찍히고, 네트워크 지연을 어느 계층에서 먼저 의심해야 할지 감이 잡혀야 합니다.

## 이 코드에서 먼저 봐야 할 점

- HTTP는 결국 텍스트 한 덩어리이며 헤더와 본문이 빈 줄로 구분됩니다
- TCP는 연결이 필요하고 순서·재전송을 보장합니다 — UDP는 그렇지 않습니다
- DNS 조회는 별도의 비용입니다 — 캐싱이 응답 시간을 크게 좌우합니다
- HTTPS는 TCP 연결 위에서 TLS 핸드셰이크가 추가됩니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| TCP 연결을 매 요청마다 새로 맺음 | 핸드셰이크 비용 누적 | HTTP keep-alive, 커넥션 풀 사용 |
| DNS 조회를 캐싱하지 않음 | 매 요청마다 수십 ms | OS·라이브러리 DNS 캐시 활용 |
| `recv` 한 번으로 전체를 받았다 가정 | 메시지 잘림 | 길이 기반·구분자 기반 파싱 |
| HTTPS 인증서 검증 비활성화 | MITM 공격에 취약 | 검증을 끄지 말고 인증서를 고치기 |
| UDP에 신뢰성을 기대 | 패킷 손실 시 침묵 | 신뢰성이 필요하면 TCP 또는 응용 프로토콜 |

## 실무에서는 이렇게 쓰입니다

- 마이크로서비스 간 통신에서 HTTP/2·gRPC 선택과 keep-alive 튜닝
- DNS 캐싱·CDN으로 글로벌 사용자에게 일정한 응답 시간 제공
- 모니터링에서 P50/P95 응답 시간을 DNS·TCP·TLS·서버로 분해
- API 게이트웨이가 TLS 종단·로드 밸런싱·재시도를 담당
- 게임·실시간 전송에 UDP·QUIC을 사용해 지연을 낮춤

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "느리다"는 말을 들으면 곧바로 시간을 층별로 분해합니다. DNS, TCP 연결, TLS 핸드셰이크, 서버 처리, 응답 본문 다운로드를 각각 따로 재야 해결책도 맞아집니다.

또한 네트워크는 항상 실패한다고 가정하고 코드를 짭니다. 타임아웃, 재시도, 회로 차단기, 멱등성은 선택 옵션이 아니라 기본값입니다. 정상 경로만 가정한 네트워크 코드는 운영에서 반드시 터집니다.


### TCP 3-Way 핸드셰이크 상세

TCP 연결 수립 과정을 패킷 단위로 추적합니다.

```text
클라이언트                                     서버
    │                                           │
    │── SYN (seq=100) ─────────────────────────→│  ① 연결 요청
    │                                           │
    │←── SYN+ACK (seq=300, ack=101) ───────────│  ② 요청 수락 + 서버 시퀀스
    │                                           │
    │── ACK (seq=101, ack=301) ────────────────→│  ③ 연결 확립
    │                                           │
    │══════════ 데이터 전송 가능 ══════════════════│
    │                                           │
    │── FIN (seq=500) ─────────────────────────→│  ④ 종료 요청
    │←── ACK (seq=700, ack=501) ───────────────│  ⑤ FIN 수신 확인
    │←── FIN (seq=700, ack=501) ───────────────│  ⑥ 서버도 종료
    │── ACK (seq=501, ack=701) ────────────────→│  ⑦ 최종 확인
    │                                           │
    │     [TIME_WAIT 2MSL]                      │
```

각 단계에서 운영상 주의할 점:

- **SYN 큐**: 서버가 SYN을 받고 SYN+ACK를 보낸 뒤 완전한 ACK를 기다리는 반접속(half-open) 상태가 쌓이는 큐입니다. SYN Flood 공격은 이 큐를 가득 채워 정상 연결을 막습니다.
- **TIME_WAIT**: 마지막 ACK가 유실될 경우를 대비해 2×MSL(Maximum Segment Lifetime, 보통 60초) 동안 소켓을 유지합니다. 고빈도 서버에서 `TIME_WAIT` 소켓이 쌓이면 `SO_REUSEADDR`로 포트를 재사용합니다.

### TCP 흐름 제어와 혼잡 제어

TCP는 두 가지 메커니즘으로 네트워크를 보호합니다.

| 구분 | 흐름 제어 (Flow Control) | 혼잡 제어 (Congestion Control) |
|------|--------------------------|-------------------------------|
| 보호 대상 | 수신자의 버퍼 | 네트워크 경로 |
| 신호 | 수신 윈도우(rwnd) | 패킷 손실, RTT 증가 |
| 조절 변수 | 송신 윈도우 ≤ rwnd | cwnd(혼잡 윈도우) |
| 알고리즘 | 슬라이딩 윈도우 | Slow Start → AIMD |

```text
cwnd 변화 (Slow Start + Congestion Avoidance)

cwnd
 ↑
 │            ×  패킷 손실 감지
 │          ╱
 │        ╱   ← Congestion Avoidance (선형 증가)
 │      ╱
 │    ╱
 │  ╱  ← Slow Start (지수 증가)
 │╱
 └─────────────────────────→ 시간
        ssthresh
```

Slow Start에서 cwnd는 매 RTT마다 2배로 증가합니다. ssthresh(임계값)에 도달하면 Congestion Avoidance로 전환되어 매 RTT마다 1 MSS씩만 증가합니다. 패킷 손실이 감지되면 cwnd를 절반으로 줄입니다(AIMD: Additive Increase, Multiplicative Decrease).

### DNS 조회 과정 추적

```python
import socket
import time

def trace_dns(hostname: str) -> None:
    """DNS 조회 시간을 측정합니다."""
    start = time.perf_counter()
    try:
        results = socket.getaddrinfo(hostname, 443, socket.AF_INET, socket.SOCK_STREAM)
        elapsed = (time.perf_counter() - start) * 1000
        ip = results[0][4][0]
        print(f"{hostname} → {ip} ({elapsed:.2f} ms)")
    except socket.gaierror as e:
        print(f"{hostname} → 실패: {e}")

# 첫 번째 조회 (재귀 질의 필요)
trace_dns("example.com")
# 두 번째 조회 (OS DNS 캐시 적중)
trace_dns("example.com")
```

DNS 조회 경로:

```text
브라우저 캐시 → OS 캐시 (/etc/hosts, systemd-resolved)
  → 로컬 DNS 서버 (ISP/회사)
    → 루트 네임서버 (.)
      → TLD 네임서버 (.com)
        → 권한 네임서버 (example.com)
```

각 단계의 캐싱 TTL이 응답 속도를 결정합니다. TTL이 짧으면(30초) 빠른 장애 전환이 가능하지만 DNS 부하가 증가합니다. TTL이 길면(24시간) 부하는 줄지만 IP 변경 시 전파가 느립니다.

### HTTP 요청-응답 실제 형태

HTTP/1.1 요청과 응답의 선 위 표현을 바이트 수준에서 봅니다.

```text
요청 (클라이언트 → 서버):
────────────────────────────────────
GET /api/users/123 HTTP/1.1\r\n
Host: api.example.com\r\n
Accept: application/json\r\n
Authorization: Bearer eyJhbG...\r\n
Connection: keep-alive\r\n
\r\n
────────────────────────────────────

응답 (서버 → 클라이언트):
────────────────────────────────────
HTTP/1.1 200 OK\r\n
Content-Type: application/json\r\n
Content-Length: 82\r\n
Cache-Control: max-age=60\r\n
\r\n
{"id":123,"name":"홍길동","email":"hong@example.com","created":"2026-01-15T09:30:00Z"}
────────────────────────────────────
```

HTTP/2와 HTTP/3의 차이:

| 버전 | 전송 프로토콜 | 멀티플렉싱 | 헤더 압축 | 특징 |
|------|--------------|-----------|-----------|------|
| HTTP/1.1 | TCP | 불가 (파이프라이닝 제한) | 없음 | 커넥션당 하나의 요청 |
| HTTP/2 | TCP | 스트림 기반 | HPACK | Head-of-line blocking (TCP 수준) |
| HTTP/3 | QUIC (UDP) | 스트림 기반 | QPACK | 스트림 독립 손실 복구 |

### 소켓 프로그래밍 기본 구조

```python
import socket
import threading

def echo_server(host: str = "127.0.0.1", port: int = 9999) -> None:
    """간단한 에코 서버 — 수신한 데이터를 그대로 반환합니다."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(5)
        print(f"서버 시작: {host}:{port}")

        while True:
            conn, addr = srv.accept()
            with conn:
                print(f"연결: {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(data)  # 에코

def echo_client(host: str = "127.0.0.1", port: int = 9999) -> None:
    """에코 서버에 메시지를 보내고 응답을 확인합니다."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        message = "Hello, Network!"
        sock.sendall(message.encode())
        response = sock.recv(1024)
        print(f"송신: {message}")
        print(f"수신: {response.decode()}")
        assert response.decode() == message

# 서버를 백그라운드 스레드로 실행
server_thread = threading.Thread(target=echo_server, daemon=True)
server_thread.start()

import time; time.sleep(0.1)  # 서버 시작 대기
echo_client()
```

이 단순 에코 서버는 연결당 하나의 스레드를 쓰므로 10,000개 동시 연결에는 적합하지 않습니다. 운영 환경에서는 `asyncio`, `epoll`, 또는 이벤트 루프 기반 프레임워크를 사용합니다.

### 네트워크 지연 분해와 측정

웹 요청의 총 시간을 구간별로 분해하면 병목을 정확히 짚을 수 있습니다.

```text
총 응답 시간 = DNS + TCP 연결 + TLS 핸드셰이크 + 요청 전송 + 서버 처리 + 응답 수신

예시: https://api.example.com/users/123
─────────────────────────────────────────────────
DNS 조회:          15 ms  (캐시 미스 시 50-200 ms)
TCP 연결:          25 ms  (1 RTT)
TLS 1.3:          25 ms  (1 RTT, 재연결 시 0-RTT 가능)
요청 전송:          1 ms  (수백 바이트)
서버 처리:         45 ms  (DB 쿼리 + 직렬화)
응답 수신:         10 ms  (1 KB JSON)
─────────────────────────────────────────────────
합계:             121 ms
```

```python
import urllib.request
import time

def measure_http(url: str) -> dict[str, float]:
    """HTTP 요청의 각 단계 시간을 측정합니다."""
    start = time.perf_counter()
    req = urllib.request.Request(url)
    
    dns_start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=5) as resp:
        connect_done = time.perf_counter()
        body = resp.read()
        done = time.perf_counter()
    
    return {
        "total_ms": (done - start) * 1000,
        "body_bytes": len(body),
        "status": resp.status,
    }

result = measure_http("http://example.com")
print(f"상태: {result['status']}, 크기: {result['body_bytes']}B, 시간: {result['total_ms']:.1f}ms")
```

운영에서는 `curl -w` 포맷이나 브라우저 DevTools의 Timing 탭으로 각 구간을 분리합니다.

```bash
curl -o /dev/null -s -w "DNS: %{time_namelookup}s\nTCP: %{time_connect}s\nTLS: %{time_appconnect}s\nTotal: %{time_total}s\n" https://example.com
```

CDN은 DNS와 TCP 연결 구간을 줄이고, HTTP/2 멀티플렉싱은 여러 요청을 하나의 연결에서 처리해 TCP 핸드셰이크 반복을 제거합니다. Keep-Alive가 중요한 이유도 같은 맥락입니다.
## 체크리스트

- [ ] TCP/IP 계층의 역할을 한 줄씩 설명할 수 있는가
- [ ] HTTP 요청·응답의 형식을 외우고 있는가
- [ ] DNS 조회 비용이 응답 시간에 포함된다는 점을 의식하는가
- [ ] TCP와 UDP를 적절한 상황에 골라 쓰는가
- [ ] 모든 네트워크 호출에 타임아웃을 걸어 두는가

## 연습 문제

1. `socket`만 사용해 여러 클라이언트를 동시에 처리하는 echo 서버를 작성해 보세요.
2. 같은 URL을 `urllib.request`와 `requests`로 100번씩 호출해 keep-alive 효과를 비교해 보세요.
3. 도메인을 입력받아 DNS, TCP, TLS, HTTP 시간을 따로 출력하는 작은 프로파일러를 만들어 보세요.

## 정리 및 다음 단계

네트워크는 계층의 약속이며, 각 계층은 아래 계층을 신뢰하면서 자기 일에 집중합니다. HTTP는 TCP 위의 텍스트 프로토콜이고, TCP는 IP 위의 신뢰성 계층입니다. 응답 시간을 계층별로 분해해 보는 습관이 시니어 디버깅의 시작입니다.

다음 글에서는 이 네트워크 너머에서 데이터를 영구적으로 보관하고 효율적으로 조회하는 방법 — 데이터베이스 — 를 다룹니다.


## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

네트워크 단원에서는 지연 시간, 처리량, 혼잡 제어를 애플리케이션 재시도 정책과 함께 묶어 이해해야 실무 의사결정에 적용됩니다.


## 처음 질문으로 돌아가기

- **브라우저에 주소를 입력했을 때 데이터가 내 화면까지 오는 경로는 어떻게 구성될까요?**
  - DNS 조회로 도메인을 IP로 변환하고, TCP 3-Way 핸드셰이크로 연결을 수립한 뒤, HTTP 요청을 전송합니다. 서버 응답은 TCP 세그먼트로 쪼개져 IP 패킷에 실려 라우터들을 거쳐 돌아오고, 브라우저가 이를 재조합해 렌더링합니다.
- **IP, TCP, HTTP, DNS는 각각 어느 층에서 어떤 역할을 맡을까요?**
  - DNS는 응용 계층에서 이름을 IP로 변환하고, HTTP도 응용 계층에서 요청/응답 형식을 정의합니다. TCP는 전송 계층에서 신뢰성(순서 보장, 재전송)을 담당하고, IP는 네트워크 계층에서 패킷을 목적지까지 라우팅합니다.
- **HTTP 요청과 응답은 선 위에서 어떤 형태로 오갈까요?**
  - 메서드, 경로, 헤더가 텍스트 줄로 구성되고 빈 줄 뒤에 본문이 옵니다. `GET /api/users HTTP/1.1\r\n` 같은 시작 줄, 키-값 헤더들, `\r\n\r\n` 구분자, 그리고 JSON/HTML 본문으로 이루어진 구조입니다.
<!-- toc:begin -->
## 시리즈 목차

- [Computer Science 101 (1/10): Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): 계산과 프로그램](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): 데이터 표현](./03-data-representation.md)
- [Computer Science 101 (4/10): 알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [Computer Science 101 (5/10): 컴퓨터 구조](./05-computer-architecture.md)
- [Computer Science 101 (6/10): 운영체제](./06-operating-systems.md)
- **네트워크 (현재 글)**
- 데이터베이스 (예정)
- 소프트웨어 엔지니어링 (예정)
- AI와 데이터사이언스까지의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [HTTP/1.1 RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [High Performance Browser Networking — Ilya Grigorik](https://hpbn.co/)
- [Cloudflare Learning Center — DNS](https://www.cloudflare.com/learning/dns/what-is-dns/)

- [이 시리즈의 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)
Tags: Computer Science, 네트워크, TCP/IP, HTTP, DNS, 소켓
