---
series: computer-networks-101
episode: 3
title: TCP와 UDP
status: content-ready
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
seo_description: TCP와 UDP의 차이를 신뢰성·순서·연결·속도라는 네 축으로 비교하고, 어떤 상황에서 어느 쪽을 골라야 하는지 정리합니다.
last_reviewed: '2026-05-04'
---

# TCP와 UDP

> Computer Networks 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: TCP와 UDP는 단순히 "신뢰성 있는 것 vs 빠른 것"의 대비일까요, 아니면 서로 다른 책임 분담을 보여 주는 두 가지 설계일까요?

> 둘 다 IP 위에서 동작하는 전송 계층 프로토콜입니다. TCP는 연결, 순서 보장, 재전송, 흐름·혼잡 제어까지 다 처리합니다. UDP는 그 모든 것을 애플리케이션에 떠넘기고 그저 패킷을 던집니다. 정답은 없고 워크로드에 맞는 선택이 있을 뿐입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- TCP의 4가지 책임(연결, 순서, 재전송, 혼잡 제어)
- UDP가 의도적으로 하지 않는 것
- 3-way handshake와 4-way close
- 언제 어느 쪽을 골라야 하는가

## 왜 중요한가

전송 프로토콜 선택은 시스템 성능과 사용자 경험을 직접 좌우합니다. 게임/영상 통화에 TCP를 쓰면 한 프레임의 손실이 전체 흐름을 멈춰 버립니다. 결제 처리에 UDP를 쓰면 트랜잭션이 사라집니다. "왜 이 프로토콜?"을 답하지 못하면 시스템 설계는 카고 컬트가 됩니다.

> 프로토콜 선택은 트레이드오프입니다 — 무엇을 보장받고 무엇을 포기할지.

## 개념 한눈에 보기

> TCP는 두 호스트 사이에 가상 회선을 만들어 데이터가 순서대로, 빠짐없이, 너무 빠르지도 않게 흐르도록 보장합니다. UDP는 회선 없이 패킷 한 개씩을 IP 위에 올려 보냅니다. 신뢰성이 필요하면 애플리케이션이 직접 구현해야 합니다.

```text
TCP: handshake → stream → retransmit → flow control → close
     "도착했는지 모르면 다시 보낸다"
UDP: 그냥 send()
     "보낸다. 도착했는지는 네가 확인해라."
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 3-way handshake | SYN, SYN-ACK, ACK으로 TCP 연결 수립 |
| ACK | 받았다는 확인 응답 |
| 재전송 | ACK이 안 오면 다시 보내는 것 |
| 흐름 제어 | 받는 쪽이 못 따라오면 보내는 속도를 늦춤 |
| 혼잡 제어 | 네트워크가 막히면 보내는 속도를 늦춤 |

## Before / After

**Before — "TCP는 좋은 것, UDP는 위험한 것":**

```text
모든 것에 TCP를 쓴다
```

**After — "워크로드별 선택":**

```text
웹/API/파일 전송   → TCP (HTTP, HTTPS)
DNS 조회           → UDP (작고 idempotent)
영상 통화/게임     → UDP + 자체 신뢰성
QUIC (HTTP/3)      → UDP 위에 새로운 신뢰성 계층
```

## 실습: 단계별로 따라하기

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

UDP에는 `connect`, `listen`, `accept`가 없습니다. 그저 보내고 받습니다.

### 3단계: tcpdump로 핸드셰이크 보기

```bash
sudo tcpdump -i lo -nn 'port 5001'
# SYN → SYN-ACK → ACK → PSH+ACK(data) → ACK → FIN → FIN+ACK → ACK
```

UDP는?

```bash
sudo tcpdump -i lo -nn 'port 5002'
# UDP, length 9   (한 줄로 끝)
```

### 4단계: 일부러 패킷 잃어버리기

```python
# 패킷 손실 시뮬레이션 (UDP)
import socket, random

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 5003))
while True:
    data, addr = s.recvfrom(1024)
    if random.random() < 0.3:
        continue   # 30% drop
    s.sendto(data, addr)
```

UDP에서 drop은 그대로 손실입니다. TCP였다면 자동으로 재전송했겠지만 UDP는 애플리케이션이 처리해야 합니다.

### 5단계: 신뢰성 직접 구현 맛보기

```python
# UDP 위에 단순한 ACK + 재전송
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

QUIC, RTP, 게임 프로토콜이 모두 이런 구조의 정교한 버전입니다.

## 이 코드에서 주목할 점

- TCP는 stream 추상(순서, 경계 없음), UDP는 datagram 추상(경계 있음, 순서 없음)
- TCP의 `recv(1024)`가 항상 정확히 1024바이트를 주지 않음(boundary 없음)
- UDP의 `recvfrom`은 한 datagram을 통째로 받음
- 신뢰성은 "공짜"가 아니라 핸드셰이크/ACK/재전송이라는 비용

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| TCP `recv`가 메시지 단위라고 가정 | 메시지가 잘리거나 합쳐짐 | 길이 prefix나 delimiter로 framing |
| UDP가 항상 손실된다고 오해 | 실시간 워크로드에서 무리하게 TCP 사용 | UDP + 자체 신뢰성 도입 |
| TCP가 "느리다"고 일반화 | HTTP/2, HTTP/3 비교 누락 | 실제 RTT/throughput 측정 |
| 양쪽 close를 잊음 | TIME_WAIT, 리소스 누수 | with 문/try-finally로 close 보장 |
| 혼잡 제어를 무시 | 낮은 throughput, 패킷 폭주 | TCP 기본 알고리즘(BBR/CUBIC) 이해 |

## 실무에서는 이렇게 쓰입니다

- 웹/API: HTTP/HTTPS over TCP, 점차 HTTP/3(QUIC over UDP)로 이동
- DNS: 기본 UDP, 응답이 크면 TCP로 fallback
- 영상 회의(Zoom, Meet): 미디어는 UDP(RTP), 시그널링은 TCP
- 게임: 위치/입력은 UDP, 채팅/결제는 TCP
- 데이터베이스: 거의 모두 TCP(트랜잭션 무결성)

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "TCP vs UDP"를 종교 전쟁으로 다루지 않습니다. 두 가지 모두 도구일 뿐이고, 워크로드의 요구(지연, 손실 허용도, 메시지 크기, 보안)에 맞는 쪽을 고릅니다. 그리고 두 프로토콜의 비용 모형 — 핸드셰이크 RTT, 재전송 시간, MTU/단편화 — 을 머릿속에 들고 다니며 설계 단계에서 미리 따져 봅니다.

QUIC의 등장은 시니어들에게 의미가 큽니다. "TCP는 운영체제 커널이라 바꾸기 어렵고, UDP 위에서 신뢰성을 다시 짜면 더 빠르게 진화할 수 있다"는 통찰이 만든 설계이기 때문입니다.

## 체크리스트

- [ ] TCP의 4가지 책임(연결, 순서, 재전송, 혼잡 제어)을 안다
- [ ] UDP가 일부러 안 하는 것을 안다
- [ ] 3-way handshake를 그릴 수 있다
- [ ] 워크로드별로 TCP/UDP를 고를 수 있다
- [ ] HTTP/3가 왜 UDP 위에 있는지 안다

## 연습 문제

1. tcpdump로 TCP 연결 종료(4-way close)를 캡처하고 FIN과 ACK의 순서를 정리하세요.

2. 위 5단계의 ACK + 재전송을 확장해 sequence number를 추가하고, 중복 패킷을 거르는 로직을 작성하세요.

3. "내 서비스는 TCP인가 UDP인가? 왜?"를 한 문단으로 답해 보세요.

## 정리 및 다음 단계

TCP와 UDP는 같은 IP 위에 올라타지만 서로 다른 책임 분담을 보여 줍니다. TCP는 운영체제가 신뢰성을 책임지고, UDP는 애플리케이션이 책임집니다. 워크로드에 맞춰 고르는 것이 본질입니다.

다음 글에서는 사람이 보는 도메인 이름이 IP로 변환되는 과정 — DNS를 다룹니다.

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
