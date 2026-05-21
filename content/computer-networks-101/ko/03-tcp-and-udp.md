---
series: computer-networks-101
episode: 3
title: "Computer Networks 101 (3/10): TCP와 UDP"
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
  - TCP
  - UDP
  - 전송계층
  - 신뢰성
seo_description: 신뢰성의 TCP와 속도의 UDP를 연결, 순서 보장, 재전송 관점에서 비교하고 각 워크로드에 맞는 선택 기준을 상세히 다룹니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (3/10): TCP와 UDP

이 글은 Computer Networks 101 시리즈의 3번째 글입니다.


![Computer Networks 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/03/03-01-concept-at-a-glance.ko.png)
*Computer Networks 101 3장 흐름 개요*

## 먼저 던지는 질문

- TCP가 맡는 책임은 정확히 무엇일까요?
- UDP는 왜 일부 책임을 의도적으로 하지 않을까요?
- 3-way handshake와 연결 종료는 어떤 흐름으로 일어날까요?

## 왜 중요한가

전송 프로토콜 선택은 시스템 성능과 사용자 경험을 직접 좌우합니다. 게임이나 화상 통화에 TCP를 쓰면 한 프레임 손실이 전체 흐름을 멈춰 세울 수 있고, 결제 처리에 UDP를 쓰면 중요한 데이터가 조용히 사라질 수 있습니다. "왜 이 프로토콜을 골랐는가"에 답하지 못하면 설계는 금세 관성에 끌려갑니다.

> 프로토콜 선택은 무엇을 보장받고, 무엇을 포기할지 정하는 트레이드오프입니다.

## 핵심 그림

> TCP는 두 호스트 사이에 가상 회선을 만들고, 데이터가 순서대로 빠짐없이 너무 빠르지 않게 흐르도록 관리합니다. UDP는 그런 회선 없이 데이터그램을 바로 던집니다. 신뢰성이 필요하다면 애플리케이션이 그 위에 따로 얹어야 합니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 3-way handshake | SYN, SYN-ACK, ACK로 TCP 연결을 여는 절차 |
| ACK | 데이터가 도착했음을 알리는 확인 응답 |
| 재전송 | ACK가 오지 않을 때 다시 보내는 동작 |
| 흐름 제어 | 수신자가 감당할 수 없으면 송신 속도를 줄이는 메커니즘 |
| 혼잡 제어 | 네트워크가 막히면 송신 속도를 낮추는 메커니즘 |
| 세그먼트 | TCP가 다루는 데이터 단위 |
| 데이터그램 | UDP가 다루는 데이터 단위 |
| MSS | Maximum Segment Size, TCP 세그먼트의 최대 페이로드 크기 |

## TCP의 네 가지 책임

TCP가 제공하는 보장을 한 줄씩 분리해 보면:

| 책임 | 동작 방식 | 비용 |
| --- | --- | --- |
| 연결 관리 | 3-way handshake로 열고, FIN으로 닫음 | 연결당 1 RTT 추가 |
| 순서 보장 | Sequence Number로 순서 추적, 재조립 | 수신 버퍼 필요 |
| 신뢰성 (재전송) | ACK 미수신 시 재전송 | 대역폭 + 지연 |
| 흐름/혼잡 제어 | Window Size 조절, AIMD 알고리즘 | 최대 처리량 제한 |

UDP는 이 네 가지를 모두 하지 않습니다. 그래서 헤더가 8바이트밖에 안 됩니다(TCP는 최소 20바이트).

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

## 3-way handshake 상세

TCP 연결은 세 단계로 열립니다. 각 단계에서 교환하는 정보를 정확히 보면:

```text
Client                              Server
  │                                    │
  │─── SYN (seq=100) ────────────────→ │  ← 1. 클라이언트가 연결 요청
  │                                    │
  │←── SYN-ACK (seq=300, ack=101) ──── │  ← 2. 서버가 수락 + 자기 seq 전달
  │                                    │
  │─── ACK (seq=101, ack=301) ───────→ │  ← 3. 클라이언트가 확인
  │                                    │
  │    ← 이제 데이터 전송 가능 →        │
```

**왜 3단계인가?** 양쪽 모두 상대방의 시작 sequence number를 확인해야 하기 때문입니다. 2단계만으로는 클라이언트가 서버의 seq를 확인했는지 서버가 알 수 없습니다.

**tcpdump에서 보이는 실제 모습:**

```bash
sudo tcpdump -i lo -nn 'port 5001' -c 6
```

```text
10:00:01.001 IP 127.0.0.1.54321 > 127.0.0.1.5001: Flags [S], seq 1000000, win 65535, options [mss 65495]
10:00:01.001 IP 127.0.0.1.5001 > 127.0.0.1.54321: Flags [S.], seq 2000000, ack 1000001, win 65535
10:00:01.001 IP 127.0.0.1.54321 > 127.0.0.1.5001: Flags [.], ack 2000001, win 65535
```

Flags 해석: `[S]` = SYN, `[S.]` = SYN+ACK, `[.]` = ACK, `[P.]` = PSH+ACK, `[F.]` = FIN+ACK, `[R]` = RST

## 연결 종료: 4-way close

```text
Client                              Server
  │                                    │
  │─── FIN (seq=500) ────────────────→ │  ← 1. 클라이언트: "나는 더 보낼 데이터 없어"
  │                                    │
  │←── ACK (ack=501) ─────────────── │  ← 2. 서버: "알겠어, 잠깐 기다려"
  │                                    │
  │←── FIN (seq=700) ─────────────── │  ← 3. 서버: "나도 다 보냈어"
  │                                    │
  │─── ACK (ack=701) ────────────────→ │  ← 4. 클라이언트: "확인"
  │                                    │
  │    [TIME_WAIT 2MSL]                │  ← 클라이언트는 2분간 대기
```

**TIME_WAIT가 중요한 이유:** 마지막 ACK가 손실되면 서버가 FIN을 재전송합니다. 클라이언트가 이미 소켓을 닫았다면 RST를 보내게 되므로, 2MSL(보통 60-120초) 동안 소켓을 유지합니다.

**운영에서 TIME_WAIT 문제:**

```bash
# TIME_WAIT 상태 소켓 수 확인
ss -s | grep TIME-WAIT
# 또는
ss -tan state time-wait | wc -l
```

대량의 짧은 연결을 처리하는 서버에서 TIME_WAIT가 수만 개 쌓이면 포트가 고갈될 수 있습니다. 해결책은 connection pooling이나 HTTP keep-alive입니다.

## 단계별로 따라하기

### 1단계: TCP echo 서버

```python
# tcp_server.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.0.1', 5001))
s.listen(5)
print("TCP echo server on :5001")

while True:
    conn, addr = s.accept()
    print(f"connected: {addr}")
    data = conn.recv(1024)
    if data:
        conn.sendall(data)  # echo back
    conn.close()
```

```python
# tcp_client.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5001))
s.sendall(b'hello tcp')
print(s.recv(1024))   # b'hello tcp'
s.close()
```

### 2단계: UDP echo 서버

```python
# udp_server.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 5002))
print("UDP echo server on :5002")

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

UDP에는 `connect`, `listen`, `accept`가 없습니다. 그냥 보내고 받습니다. 연결 상태를 유지하지 않으므로 서버 자원 소비도 적습니다.

### 3단계: `tcpdump`로 핸드셰이크 보기

```bash
# 터미널 1
sudo tcpdump -i lo -nn 'port 5001'

# 터미널 2
python3 tcp_server.py

# 터미널 3
python3 tcp_client.py
```

TCP 출력:
```text
SYN → SYN-ACK → ACK → PSH+ACK(data) → ACK → FIN → FIN+ACK → ACK
```

UDP 출력:
```bash
sudo tcpdump -i lo -nn 'port 5002'
# 127.0.0.1.xxxxx > 127.0.0.1.5002: UDP, length 9
# 127.0.0.1.5002 > 127.0.0.1.xxxxx: UDP, length 9
```

UDP는 단 두 줄입니다. handshake도 FIN도 없습니다.

### 4단계: 일부러 패킷을 버려 보기

```python
# udp_lossy_server.py — 30% 패킷 드롭 시뮬레이션
import socket, random

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 5003))

received = 0
dropped = 0

while True:
    data, addr = s.recvfrom(1024)
    received += 1
    if random.random() < 0.3:
        dropped += 1
        continue   # 30% drop — no response
    s.sendto(data, addr)
    if received % 10 == 0:
        print(f"received={received} dropped={dropped} rate={dropped/received:.1%}")
```

UDP에서는 손실이 그냥 손실입니다. 클라이언트는 응답이 안 오면 타임아웃으로 알 수 있을 뿐, 프로토콜이 알려주지 않습니다.

### 5단계: 신뢰성을 직접 얹는 맛보기

```python
# Simple ACK + retransmit on top of UDP
import socket, time, struct

def send_reliable(sock, data: bytes, addr, retries=3, timeout=0.5):
    """시퀀스 번호 + ACK + 재전송으로 최소 신뢰성 확보."""
    seq = int(time.time() * 1000) % 65536
    packet = struct.pack('!H', seq) + data  # 2바이트 seq + payload

    for attempt in range(retries):
        sock.sendto(packet, addr)
        sock.settimeout(timeout)
        try:
            ack_data, _ = sock.recvfrom(1024)
            ack_seq = struct.unpack('!H', ack_data[:2])[0]
            if ack_seq == seq:
                return True
        except socket.timeout:
            print(f"  retry {attempt + 1}/{retries}")
            continue
    return False
```

QUIC, RTP, 게임 프로토콜은 모두 이런 패턴을 훨씬 정교하게 확장한 형태입니다. 선택적 ACK(SACK), 적응형 타임아웃, FEC(Forward Error Correction) 등을 조합합니다. 예를 들어 RTP(Real-time Transport Protocol)는 타임스탬프와 시퀀스 번호를 제공하되 재전송은 하지 않고, 대신 jitter buffer로 네트워크 변동을 흡수합니다. 게임에서는 서버 권위(server authority) 모델과 클라이언트 예측(client prediction)을 결합해 UDP 손실을 보상합니다.


## TCP 재전송 관찰 실습

TCP 재전송을 실제로 볼 수 있는 방법:

```bash
# Wireshark 필터로 재전송 패킷만 보기
tcp.analysis.retransmission

# tcpdump로 재전송 확인 (동일 seq가 두 번 나오는지 관찰)
sudo tcpdump -i eth0 -nn 'tcp port 443' -v | grep -i retransmit

# netstat으로 재전송 통계 확인
cat /proc/net/snmp | grep Tcp
# Tcp: ... RetransSegs ...
# 일정 시간 간격으로 읽어 매초 재전송 수를 계산
```

재전송 비율이 1%를 넘으면 사용자 경험에 눈에 띄는 영향이 시작됩니다. 5%를 넘으면 대부분의 애플리케이션에서 심각한 성능 저하가 발생합니다. 이 수치를 모니터링 대시보드에 올려 두면 네트워크 문제를 조기에 감지할 수 있습니다. 특히 클라우드 환경에서는 AZ 간 통신 시 재전송이 급증하는 이벤트를 알림으로 설정하는 것이 좋습니다.

## TCP 재전송과 혼잡 제어

TCP의 가장 복잡한 부분은 혼잡 제어입니다. 핵심 아이디어는 단순합니다: 네트워크가 막히면 천천히 보내고, 여유가 있으면 빠르게 보냅니다.

```text
혼잡 윈도우(cwnd) 변화:

Slow Start (지수 증가)
cwnd: 1 → 2 → 4 → 8 → 16 → ... → ssthresh 도달

Congestion Avoidance (선형 증가)
cwnd: 16 → 17 → 18 → 19 → ... → 패킷 손실 감지

패킷 손실 시:
  - 3 duplicate ACK → Fast Retransmit, cwnd = cwnd/2
  - Timeout → cwnd = 1, 다시 Slow Start
```

**실무에서의 영향:**

```bash
# 현재 TCP 혼잡 제어 알고리즘 확인
sysctl net.ipv4.tcp_congestion_control
# cubic (Linux 기본), bbr (Google), reno 등

# BBR로 변경 (처리량 개선 목적)
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr
```

장거리 연결(예: 한국-미국 서버 간)에서 TCP 처리량이 낮은 이유의 대부분은 혼잡 제어 때문입니다. RTT가 길면 cwnd가 증가하는 속도가 느려지고, 손실 하나에 크게 감소합니다.

## TCP vs UDP 비교 정리

| 항목 | TCP | UDP |
| --- | --- | --- |
| 연결 | 있음 (stateful) | 없음 (stateless) |
| 순서 보장 | 있음 | 없음 |
| 재전송 | 자동 | 없음 |
| 흐름 제어 | 있음 (Window) | 없음 |
| 혼잡 제어 | 있음 | 없음 |
| 헤더 크기 | 20-60 바이트 | 8 바이트 |
| 지연 | handshake + 재전송 대기 | 최소 |
| 메시지 경계 | 없음 (byte stream) | 있음 (datagram) |
| Head-of-line blocking | 있음 | 없음 |

**Head-of-line blocking**: TCP에서 패킷 하나가 손실되면, 그 뒤의 패킷들도 애플리케이션에 전달되지 못하고 대기합니다. 이것이 HTTP/2가 TCP 위에서 여전히 겪는 문제이며, HTTP/3이 QUIC(UDP 기반)으로 이동한 핵심 이유입니다.

## QUIC: UDP 위의 새로운 전송 계층

QUIC는 Google이 설계하고 RFC 9000으로 표준화된 프로토콜입니다. UDP 위에 TCP의 장점(신뢰성, 순서 보장)을 다시 구현하되, 몇 가지 핵심 문제를 해결합니다.

```text
TCP + TLS 1.3:         QUIC:
  1 RTT (TCP handshake)    0-1 RTT (통합 handshake)
+ 1 RTT (TLS handshake)
= 2 RTT minimum            = 0 RTT (재연결 시)

TCP: 하나의 스트림         QUIC: 독립된 여러 스트림
  → HOL blocking 발생        → 스트림 간 영향 없음
```


## TCP 메시지 프레이밍

TCP는 바이트 스트림이므로 메시지 경계를 보존하지 않습니다. 애플리케이션이 직접 경계를 정해야 합니다.

```python
# 방법 1: 길이 prefix (가장 일반적)
import struct

def send_message(sock, data: bytes):
    length = struct.pack('!I', len(data))  # 4바이트 big-endian 길이
    sock.sendall(length + data)

def recv_message(sock) -> bytes:
    raw_len = recv_exact(sock, 4)
    length = struct.unpack('!I', raw_len)[0]
    return recv_exact(sock, length)

def recv_exact(sock, n: int) -> bytes:
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError('connection closed')
        buf += chunk
    return buf
```

```python
# 방법 2: 구분자 (\n)
def recv_line(sock) -> str:
    buf = b''
    while not buf.endswith(b'\n'):
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError('connection closed')
        buf += chunk
    return buf.decode().strip()
```

방법 1(길이 prefix)이 더 안전합니다. 구분자 방식은 페이로드 안에 구분자가 들어가면 깨집니다. HTTP/1.1은 `Content-Length` 헤더로 길이 prefix를 사용하고, chunked encoding은 각 chunk에 길이를 붙입니다.

## TCP 상태 전이와 `ss` 명령

TCP 연결은 여러 상태를 거칩니다. 운영에서 중요한 상태들:

```text
LISTEN      → 서버가 연결 대기 중
SYN_SENT    → 클라이언트가 SYN 보냄
SYN_RECV    → 서버가 SYN-ACK 보냄
ESTABLISHED → 연결 완료, 데이터 전송 가능
FIN_WAIT_1  → FIN 보냄, ACK 대기
FIN_WAIT_2  → ACK 받음, 상대 FIN 대기
TIME_WAIT   → 2MSL 대기 (지연된 패킷 처리)
CLOSE_WAIT  → 상대가 FIN 보냄, 내가 아직 닫지 않음
LAST_ACK    → FIN 보냄, 마지막 ACK 대기
```

```bash
# 상태별 소켓 수 확인
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn
#  152 ESTAB
#   47 TIME-WAIT
#    8 LISTEN
#    3 CLOSE-WAIT    ← 이것이 쌓이면 애플리케이션이 close()를 안 하는 것

# CLOSE_WAIT가 많으면 애플리케이션 버그 (소켓 누수)
# TIME_WAIT가 많으면 연결 회전이 빠른 것 (정상이지만 관리 필요)
```

## 실전 성능 측정: `iperf3`

TCP/UDP 처리량을 실제로 측정하려면 `iperf3`를 사용합니다.

```bash
# 서버 측
iperf3 -s

# TCP 측정 (클라이언트)
iperf3 -c server-ip -t 10
# [ ID] Interval       Transfer    Bitrate        Retr  Cwnd
# [  5] 0.00-10.00 sec  1.10 GBytes  943 Mbits/sec  0     428 KBytes

# UDP 측정 (클라이언트, 100Mbps 제한)
iperf3 -c server-ip -u -b 100M -t 10
# [ ID] Interval       Transfer    Bitrate        Jitter   Lost/Total
# [  5] 0.00-10.00 sec  119 MBytes  100 Mbits/sec  0.05ms   12/85000 (0.014%)
```

UDP 측정에서 `Lost/Total`이 높으면 네트워크 경로에 문제가 있는 것입니다. Jitter(지터)가 높으면 실시간 워크로드에 문제가 될 수 있습니다.

## 이 코드에서 먼저 볼 점

- TCP는 스트림 추상입니다. 순서는 보장하지만 메시지 경계는 없습니다.
- UDP는 데이터그램 추상입니다. 데이터그램 경계는 유지하지만 순서와 재전송은 보장하지 않습니다.
- TCP의 `recv(1024)`는 항상 1024바이트를 돌려주는 함수가 아닙니다. 1바이트만 올 수도 있습니다.
- 신뢰성은 공짜가 아니라 핸드셰이크, ACK, 재전송 비용을 동반합니다.
- TIME_WAIT는 버그가 아니라 프로토콜이 의도한 안전장치입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| TCP `recv`가 메시지 하나를 그대로 준다고 생각 | 메시지가 합쳐지거나 잘림 | 길이 prefix나 구분자로 프레이밍한다 |
| UDP는 무조건 손실된다고 오해 | 실시간 워크로드에 TCP를 억지로 씀 | UDP 위에 필요한 만큼의 신뢰성을 올린다 |
| TCP를 무조건 느리다고 일반화 | HTTP/2, HTTP/3 진화를 놓침 | RTT와 처리량을 실제로 측정한다 |
| 양쪽에서 close를 깜빡함 | TIME_WAIT와 리소스 누수 발생 | `with` 또는 `try/finally`를 쓴다 |
| 혼잡 제어를 고려하지 않음 | 처리량 저하나 패킷 폭주 발생 | 기본 TCP 알고리즘을 이해한다 |

## 실무에서는 이렇게 보입니다

- 웹과 API는 대체로 TCP 위의 HTTP/HTTPS를 사용합니다. keep-alive로 연결을 재사용해 handshake 비용을 줄입니다.
- DNS는 기본적으로 UDP를 쓰고, 응답이 512바이트를 넘으면 TCP로 넘어갑니다(EDNS0 확장 시 더 큼).
- 화상 회의는 미디어를 UDP(RTP)로, 시그널링을 TCP(SIP/WebSocket)로 나눕니다.
- 게임은 위치와 입력을 UDP로, 채팅과 결제를 TCP로 보내는 식으로 섞어 씁니다.
- 데이터베이스는 트랜잭션 무결성 때문에 거의 항상 TCP를 사용합니다.
- 마이크로서비스 간 gRPC는 HTTP/2(TCP) 위에서 동작합니다.

```text
[프로토콜 선택 의사결정 트리]

데이터 손실이 허용되는가?
├── 예 → 지연이 중요한가?
│       ├── 예 → UDP + 애플리케이션 레벨 처리 (게임, VoIP)
│       └── 아니오 → TCP도 가능 (로그 수집 등)
└── 아니오 → TCP 또는 QUIC
              ├── 연결 설정 지연을 줄여야 하나? → QUIC (0-RTT)
              └── 호환성이 중요한가? → TCP
```

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 TCP와 UDP를 종교 전쟁처럼 보지 않습니다. 둘 다 도구이고, 정답은 워크로드 요구사항에 달려 있다고 봅니다. 지연 시간, 손실 허용도, 메시지 크기, 보안 요구사항을 설계 단계에서 함께 따져 봅니다.

또한 QUIC가 왜 중요한지도 이해합니다. TCP는 운영 체제 커널 안에 있어 바꾸기 어렵지만, UDP 위에 신뢰성을 다시 쌓으면 사용자 공간에서 훨씬 더 민첩하게 발전시킬 수 있습니다.

성능 진단에서는 다음을 먼저 확인합니다:
- `ss -ti`로 TCP 연결의 재전송 횟수, RTT, cwnd를 봅니다.
- 재전송이 많으면 네트워크 경로 문제를 의심합니다.
- cwnd가 작은 채로 멈춰 있으면 혼잡 제어 알고리즘이나 수신 윈도우 제한을 봅니다.

```bash
# TCP 연결 상세 정보 확인
ss -ti dst 93.184.216.34
# 출력 예:
# cubic wscale:7,7 rto:204 rtt:12.5/6.2 ato:40 mss:1448
# pmtu:1500 rcvmss:1448 advmss:1448
# cwnd:10 bytes_sent:1024 bytes_acked:1024
# bytes_received:4096 segs_out:15 segs_in:20
# data_segs_out:5 data_segs_in:10
# delivery_rate 927744bps
# retrans:0/0    ← 재전송 없음 = 건강한 연결
```

## 체크리스트

- [ ] TCP의 네 가지 책임(연결, 순서, 재전송, 흐름/혼잡 제어)을 설명할 수 있다
- [ ] UDP가 의도적으로 하지 않는 일을 안다
- [ ] 3-way handshake와 4-way close를 그릴 수 있다
- [ ] 워크로드에 따라 TCP와 UDP를 고를 수 있다
- [ ] TIME_WAIT의 존재 이유를 안다
- [ ] Head-of-line blocking이 무엇인지 설명할 수 있다
- [ ] HTTP/3가 왜 UDP 위에 놓이는지 안다

## 연습 문제

1. `tcpdump`로 TCP 연결 종료(4-way close)를 캡처하고 FIN과 ACK의 순서를 적어 보세요.
2. 위 ACK + 재전송 예제에 시퀀스 번호를 추가하고, 중복 패킷을 버리는 로직을 넣어 보세요.
3. "내 서비스는 TCP를 써야 하는가, UDP를 써야 하는가"를 한 단락으로 설명해 보세요.
4. `ss -ti`로 현재 TCP 연결의 cwnd와 rtt를 확인하고, 그 숫자가 의미하는 바를 해석해 보세요.
5. TCP의 Head-of-line blocking 문제를 그림으로 그리고, QUIC가 이를 어떻게 해결하는지 설명해 보세요.

## 정리와 다음 글

TCP와 UDP는 같은 IP 위에서 서로 다른 책임 분담 철학을 보여 줍니다. TCP는 신뢰성을 운영 체제에 두고, UDP는 그 책임을 애플리케이션에 둡니다. 핵심은 어떤 프로토콜이 더 좋으냐가 아니라 어떤 워크로드에 더 맞느냐입니다.

다음 글에서는 사람이 읽는 도메인 이름이 IP 주소로 바뀌는 과정, DNS를 다룹니다.

## 처음 질문으로 돌아가기

- **TCP가 맡는 책임은 정확히 무엇일까요?**
  - 연결 관리(3-way handshake/4-way close), 순서 보장(sequence number), 신뢰성(ACK + 재전송), 흐름/혼잡 제어(window size 조절). 이 네 가지가 TCP의 핵심 책임이며, 각각 비용(RTT, 버퍼, 대역폭)을 동반합니다.
- **UDP는 왜 일부 책임을 의도적으로 하지 않을까요?**
  - 실시간 워크로드에서는 재전송으로 인한 지연이 손실보다 더 나쁩니다. 화상 통화에서 0.5초 전 프레임을 재전송받아도 이미 무의미합니다. UDP는 이런 워크로드에 불필요한 오버헤드를 제거하고, 필요한 신뢰성만 애플리케이션이 선택적으로 구현할 수 있게 합니다.
- **3-way handshake와 연결 종료는 어떤 흐름으로 일어날까요?**
  - 연결 설정: 클라이언트 SYN(seq=x) → 서버 SYN-ACK(seq=y, ack=x+1) → 클라이언트 ACK(ack=y+1). 연결 종료: 한쪽이 FIN → ACK → 반대쪽 FIN → ACK. 종료 후 TIME_WAIT(2MSL)으로 지연된 패킷이 새 연결을 방해하지 않도록 보호합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Networks 101 (1/10): 네트워크란 무엇인가?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP와 subnet](./02-ip-and-subnet.md)
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
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, TCP, UDP, 전송계층, 신뢰성
