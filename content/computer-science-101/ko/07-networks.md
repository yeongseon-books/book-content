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
  - 본문의 기준은 네트워크를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **IP, TCP, HTTP, DNS는 각각 어느 층에서 어떤 역할을 맡을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **HTTP 요청과 응답은 선 위에서 어떤 형태로 오갈까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, 네트워크, TCP/IP, HTTP, DNS, 소켓
