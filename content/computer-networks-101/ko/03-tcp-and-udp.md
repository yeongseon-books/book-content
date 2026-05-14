---
series: computer-networks-101
episode: 3
title: TCP와 UDP
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
  - TCP
  - UDP
  - 전송계층
  - 신뢰성
seo_description: 신뢰성의 TCP와 속도의 UDP를 연결, 순서 보장, 재전송 관점에서 비교하고 각 워크로드에 맞는 선택 기준을 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# TCP와 UDP

이 글은 Computer Networks 101 시리즈의 3번째 글입니다.

## 이 글에서 다룰 문제

- TCP가 맡는 책임은 정확히 무엇일까요?
- UDP는 왜 일부 책임을 의도적으로 하지 않을까요?
- 3-way handshake와 연결 종료는 어떤 흐름으로 일어날까요?
- 어떤 워크로드에 TCP를, 어떤 워크로드에 UDP를 골라야 할까요?

> TCP와 UDP는 모두 IP 위에서 동작하는 전송 계층 프로토콜이지만 책임 분담 방식이 완전히 다릅니다. TCP는 연결, 순서, 재전송, 흐름 제어와 혼잡 제어를 운영 체제 쪽에 둡니다. UDP는 그 부담을 애플리케이션에 넘기고 패킷만 보냅니다. 중요한 것은 우열이 아니라 워크로드에 맞는 선택입니다.

## 왜 중요한가

전송 프로토콜 선택은 시스템 성능과 사용자 경험을 직접 좌우합니다. 게임이나 화상 통화에 TCP를 쓰면 한 프레임 손실이 전체 흐름을 멈춰 세울 수 있고, 결제 처리에 UDP를 쓰면 중요한 데이터가 조용히 사라질 수 있습니다. "왜 이 프로토콜을 골랐는가"에 답하지 못하면 설계는 금세 관성에 끌려갑니다.

> 프로토콜 선택은 무엇을 보장받고, 무엇을 포기할지 정하는 트레이드오프입니다.

## 핵심 그림

> TCP는 두 호스트 사이에 가상 회선을 만들고, 데이터가 순서대로 빠짐없이 너무 빠르지 않게 흐르도록 관리합니다. UDP는 그런 회선 없이 데이터그램을 바로 던집니다. 신뢰성이 필요하다면 애플리케이션이 그 위에 따로 얹어야 합니다.

```text
TCP: handshake → stream → retransmit → flow control → close
     "도착했는지 모르겠으면 다시 보낸다"
UDP: just send()
     "보냈다. 도착 여부는 네가 확인해라."
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 3-way handshake | SYN, SYN-ACK, ACK로 TCP 연결을 여는 절차 |
| ACK | 데이터가 도착했음을 알리는 확인 응답 |
| 재전송 | ACK가 오지 않을 때 다시 보내는 동작 |
| 흐름 제어 | 수신자가 감당할 수 없으면 송신 속도를 줄이는 메커니즘 |
| 혼잡 제어 | 네트워크가 막히면 송신 속도를 낮추는 메커니즘 |

## Before / After

**Before — "TCP는 좋고 UDP는 위험하다"**

```text
모든 서비스에 TCP를 쓴다
```

**After — "워크로드마다 선택이 다르다"**

```text
Web / API / file transfer  → TCP (HTTP, HTTPS)
DNS lookup                 → UDP (small and idempotent)
Video calls / games        → UDP + custom reliability
QUIC (HTTP/3)              → New reliability layer on top of UDP
```

## 단계별로 따라하기

### 1단계: TCP echo 서버

```python
# tcp_server.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 5001)); s.listen()
while True:
    c, _ = s.accept()
    data = c.recv(1024)
    c.sendall(data); c.close()
```

```python
# tcp_client.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5001))
s.sendall(b'hello tcp')
print(s.recv(1024))   # b'hello tcp'
```

### 2단계: UDP echo 서버

```python
# udp_server.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 5002))
while True:
    data, addr = s.recvfrom(1024)
    s.sendto(data, addr)
```

```python
# udp_client.py
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'hello udp', ('127.0.0.1', 5002))
print(s.recvfrom(1024))   # (b'hello udp', ('127.0.0.1', 5002))
```

UDP에는 `connect`, `listen`, `accept`가 없습니다. 그냥 보내고 받습니다.

### 3단계: `tcpdump`로 핸드셰이크 보기

```bash
sudo tcpdump -i lo -nn 'port 5001'
# SYN → SYN-ACK → ACK → PSH+ACK(data) → ACK → FIN → FIN+ACK → ACK
```

UDP는 이렇게 보입니다.

```bash
sudo tcpdump -i lo -nn 'port 5002'
# UDP, length 9   (one line and done)
```

### 4단계: 일부러 패킷을 버려 보기

```python
# UDP packet-loss simulation
import socket, random

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 5003))
while True:
    data, addr = s.recvfrom(1024)
    if random.random() < 0.3:
        continue   # 30% drop
    s.sendto(data, addr)
```

UDP에서는 손실이 그냥 손실입니다. TCP였다면 자동 재전송이 일어났겠지만, UDP에서는 애플리케이션이 책임집니다.

### 5단계: 신뢰성을 직접 얹는 맛보기

```python
# Simple ACK + retransmit on top of UDP
import socket, time

def send_reliable(sock, data, addr, retries=3, timeout=0.5):
    for _ in range(retries):
        sock.sendto(data, addr)
        sock.settimeout(timeout)
        try:
            ack, _ = sock.recvfrom(1024)
            if ack == b'ACK':
                return True
        except socket.timeout:
            continue
    return False
```

QUIC, RTP, 게임 프로토콜은 모두 이런 패턴을 훨씬 정교하게 확장한 형태입니다.

## 이 코드에서 먼저 볼 점

- TCP는 스트림 추상입니다. 순서는 보장하지만 메시지 경계는 없습니다.
- UDP는 데이터그램 추상입니다. 데이터그램 경계는 유지하지만 순서와 재전송은 보장하지 않습니다.
- TCP의 `recv(1024)`는 항상 1024바이트를 돌려주는 함수가 아닙니다.
- 신뢰성은 공짜가 아니라 핸드셰이크, ACK, 재전송 비용을 동반합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| TCP `recv`가 메시지 하나를 그대로 준다고 생각 | 메시지가 합쳐지거나 잘림 | 길이 prefix나 구분자로 프레이밍한다 |
| UDP는 무조건 손실된다고 오해 | 실시간 워크로드에 TCP를 억지로 씀 | UDP 위에 필요한 만큼의 신뢰성을 올린다 |
| TCP를 무조건 느리다고 일반화 | HTTP/2, HTTP/3 진화를 놓침 | RTT와 처리량을 실제로 측정한다 |
| 양쪽에서 close를 깜빡함 | TIME_WAIT와 리소스 누수 발생 | `with` 또는 `try/finally`를 쓴다 |
| 혼잡 제어를 고려하지 않음 | 처리량 저하나 패킷 폭주 발생 | 기본 TCP 알고리즘을 이해한다 |

## 실무에서는 이렇게 보입니다

- 웹과 API는 대체로 TCP 위의 HTTP/HTTPS를 사용합니다.
- DNS는 기본적으로 UDP를 쓰고, 응답이 크면 TCP로 넘어갑니다.
- 화상 회의는 미디어를 UDP로, 시그널링을 TCP로 나누는 경우가 많습니다.
- 게임은 위치와 입력을 UDP로, 채팅과 결제를 TCP로 보내는 식으로 섞어 씁니다.
- 데이터베이스는 트랜잭션 무결성 때문에 거의 항상 TCP를 사용합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 TCP와 UDP를 종교 전쟁처럼 보지 않습니다. 둘 다 도구이고, 정답은 워크로드 요구사항에 달려 있다고 봅니다. 지연 시간, 손실 허용도, 메시지 크기, 보안 요구사항을 설계 단계에서 함께 따져 봅니다.

또한 QUIC가 왜 중요한지도 이해합니다. TCP는 운영 체제 커널 안에 있어 바꾸기 어렵지만, UDP 위에 신뢰성을 다시 쌓으면 더 빠른 속도로 진화할 수 있기 때문입니다.

## 체크리스트

- [ ] TCP의 네 가지 책임을 설명할 수 있다
- [ ] UDP가 의도적으로 하지 않는 일을 안다
- [ ] 3-way handshake를 그릴 수 있다
- [ ] 워크로드에 따라 TCP와 UDP를 고를 수 있다
- [ ] HTTP/3가 왜 UDP 위에 놓이는지 안다

## 연습 문제

1. `tcpdump`로 TCP 연결 종료(4-way close)를 캡처하고 FIN과 ACK의 순서를 적어 보세요.
2. 위 ACK + 재전송 예제에 시퀀스 번호를 추가하고, 중복 패킷을 버리는 로직을 넣어 보세요.
3. "내 서비스는 TCP를 써야 하는가, UDP를 써야 하는가"를 한 단락으로 설명해 보세요.

## 정리와 다음 글

TCP와 UDP는 같은 IP 위에서 서로 다른 책임 분담 철학을 보여 줍니다. TCP는 신뢰성을 운영 체제에 두고, UDP는 그 책임을 애플리케이션에 둡니다. 핵심은 어떤 프로토콜이 더 좋으냐가 아니라 어떤 워크로드에 더 맞느냐입니다.

다음 글에서는 사람이 읽는 도메인 이름이 IP 주소로 바뀌는 과정, DNS를 다룹니다.

<!-- toc:begin -->
- [네트워크란 무엇인가?](./01-what-is-a-network.md)
- [IP와 subnet](./02-ip-and-subnet.md)
- **TCP와 UDP (현재 글)**
- DNS (예정)
- HTTP와 HTTPS (예정)
- TLS 기초 (예정)
- 라우팅과 NAT (예정)
- Load Balancer (예정)
- WebSocket과 실시간 통신 (예정)
- 네트워크 문제 디버깅 (예정)
<!-- toc:end -->

## 참고 자료

- [RFC 9293 — Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 768 — User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
- [RFC 9000 — QUIC](https://www.rfc-editor.org/rfc/rfc9000)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)

Tags: Computer Science, 네트워크, TCP, UDP, 전송계층, 신뢰성
