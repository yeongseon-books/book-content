---
series: computer-science-101
episode: 7
title: 네트워크
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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

# 네트워크

브라우저 주소창에 도메인을 입력하고 화면에 응답이 뜨기까지는 하나의 마법 같은 요청이 아니라, 층별로 역할이 나뉜 프로토콜들이 차례로 일을 나눠 갖는 과정입니다. 느림과 오류를 빠르게 좁히는 엔지니어는 이 층을 머릿속에 그릴 수 있습니다.

이 글은 Computer Science 101 시리즈의 7번째 글입니다.

여기서는 TCP/IP 계층, HTTP 요청과 응답, DNS 이름 해석, 그리고 소켓 프로그래밍의 기초를 통해 네트워크를 구조적으로 이해해 보겠습니다.

## 이 글에서 다룰 문제

- 브라우저에 주소를 입력했을 때 데이터가 내 화면까지 오는 경로는 어떻게 구성될까요?
- IP, TCP, HTTP, DNS는 각각 어느 층에서 어떤 역할을 맡을까요?
- HTTP 요청과 응답은 선 위에서 어떤 형태로 오갈까요?
- DNS 조회 시간과 TLS 핸드셰이크는 왜 전체 지연 시간에 포함될까요?
- TCP와 UDP는 어떤 워크로드에서 다르게 선택해야 할까요?

> 네트워크는 층별 약속의 집합입니다. 각 층이 자기 책임만 정확히 이해하면, 문제도 어느 층에서 시작됐는지 훨씬 빨리 좁힐 수 있습니다.

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

```text
Layer (TCP/IP)        Example protocols          Unit
────────────────────────────────────────────────────────
Application           HTTP, DNS, SMTP, SSH       message
Transport             TCP, UDP                   segment
Internet              IP, ICMP                   packet
Network Access        Ethernet, Wi-Fi            frame
```

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

<!-- toc:begin -->
- [Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [계산과 프로그램](./02-computation-and-programs.md)
- [데이터 표현](./03-data-representation.md)
- [알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [컴퓨터 구조](./05-computer-architecture.md)
- [운영체제](./06-operating-systems.md)
- **네트워크 (현재 글)**
- [데이터베이스](./08-databases.md)
- [소프트웨어 엔지니어링](./09-software-engineering.md)
- [AI와 데이터사이언스까지의 연결](./10-ai-and-data-science.md)
<!-- toc:end -->

## 참고 자료

- [HTTP/1.1 RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [High Performance Browser Networking — Ilya Grigorik](https://hpbn.co/)
- [Cloudflare Learning Center — DNS](https://www.cloudflare.com/learning/dns/what-is-dns/)

Tags: Computer Science, 네트워크, TCP/IP, HTTP, DNS, 소켓
