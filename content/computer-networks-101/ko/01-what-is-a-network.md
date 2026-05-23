---
series: computer-networks-101
episode: 1
title: "Computer Networks 101 (1/10): 네트워크란 무엇인가?"
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
  - 인터넷
  - 패킷
  - 계층모델
  - OSI
seo_description: 패킷, 프로토콜, 계층 모델을 중심으로 현대 네트워크의 기본 동작 원리와 인터넷 통신 과정을 상세히 설명합니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (1/10): 네트워크란 무엇인가?

이 글은 Computer Networks 101 시리즈의 첫 번째 글입니다.


![Computer Networks 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/01/01-01-concept-at-a-glance.ko.png)
*Computer Networks 101 1장 흐름 개요*

## 먼저 던지는 질문

- 네트워크와 인터넷은 어떻게 다른가요?
- 패킷은 왜 네트워크의 기본 단위로 취급될까요?
- 계층 모델이 없으면 IP, TCP, DNS, HTTP를 왜 함께 이해하기 어려울까요?

## 왜 중요한가

네트워크 책을 처음 펼치면 IP, TCP, UDP, DNS, HTTP, TLS, BGP, NAT 같은 약어가 한꺼번에 쏟아집니다. 머릿속 그림 없이 이 단어들을 외우기만 하면 서로 어떻게 연결되는지 보이지 않고, 결국 오래 남지 않습니다. 계층 모델은 이 단어들을 꽂아 둘 책장입니다. 책장이 없으면 책이 바닥에 쌓이듯, 개념도 금세 뒤엉킵니다.

> 네트워크를 배운다는 것은 새 단어를 외우는 일이 아니라, 각 단어를 어느 층에 놓아야 하는지 정하는 일입니다.

## 핵심 그림

> 데이터는 패킷이라는 작은 단위로 잘려 네트워크를 흐릅니다. 그리고 각 층은 서로 다른 책임을 맡습니다. 물리 신호를 보내는 층, 바로 옆 장비와 프레임을 주고받는 층, 전 세계 경로를 찾는 층, 신뢰성 있는 전송을 맡는 층, 마지막으로 HTTP 같은 의미 있는 메시지를 다루는 층이 나뉘어 있습니다. 이 책임 분리가 바로 계층 모델입니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 패킷 | 네트워크를 흐르는 데이터의 기본 단위 |
| 프로토콜 | 두 노드가 통신하기 위한 형식과 절차의 약속 |
| 계층 모델 | 통신 책임을 여러 층으로 나눈 구조 |
| 호스트 | 통신의 끝점이 되는 장치(컴퓨터, 서버, 휴대폰) |
| 라우터 | 패킷을 다음 네트워크로 넘기는 장치 |
| 캡슐화 | 윗층 데이터를 아랫층 봉투로 감싸는 과정 |
| 프레임 | 링크 계층에서 주고받는 데이터 단위 |
| 세그먼트 | 전송 계층에서 주고받는 데이터 단위 |

## 네트워크와 인터넷의 차이

이 개념을 혼동하는 사람이 많습니다. 차이는 범위와 약속의 수준에 있습니다.

| 구분 | 네트워크 | 인터넷 |
| --- | --- | --- |
| 범위 | 사무실, 가정, 데이터센터 등 국지적 | 전 세계 네트워크의 네트워크 |
| 프로토콜 | 자유(Ethernet, Wi-Fi, TokenRing 등) | IP를 공통 프로토콜로 사용 |
| 주소 | MAC, 내부 IP 등 | 글로벌 IP 주소 체계 |
| 관리 | 단일 조직 | 수천 개의 AS(Autonomous System)가 협력 |

예를 들어 회사 사무실에 스위치와 PC 10대가 연결되어 있으면 이미 네트워크입니다. 이 네트워크가 ISP를 통해 다른 네트워크와 연결되고, BGP로 경로를 교환하면 인터넷의 일부가 됩니다.

```text
[사무실 LAN] ─── ISP A ─── Internet Exchange ─── ISP B ─── [클라우드 서버]
     │                                                          │
  네트워크(local)                                          네트워크(remote)
                        ← 인터넷(global) →
```

핵심은 인터넷이 "하나의 시스템"이 아니라 "약속(IP)으로 이어진 네트워크의 연합"이라는 사실입니다. RFC 1122에서 정의하는 인터넷 호스트 요구사항도 이 전제에서 출발합니다.

## 적용 전후 비교
**Before — "인터넷은 마법"**

```text
브라우저  →  ???  →  서버
중간은 하나의 거대한 검은 상자
```

**After — "각 층에는 책임이 있다"**

```text
HTTP(메시지) → TCP(신뢰성) → IP(라우팅) → Ethernet(링크) → 신호
각 층은 윗층의 데이터를 자기 봉투에 담아 아래층으로 넘긴다(encapsulation)
```

어느 층이 무슨 책임을 맡는지 알면, 문제가 애플리케이션인지 TCP인지 라우팅인지 훨씬 빨리 분리할 수 있습니다.

## 계층 모델 비교: OSI 7계층 vs TCP/IP 4계층

교과서에서는 OSI 7계층을 먼저 가르치지만, 실무에서 실제로 동작하는 프로토콜은 TCP/IP 4계층에 대응됩니다. 둘 다 알아야 하는 이유는 대화 상대에 따라 기준이 다르기 때문입니다.

```text
OSI 7계층              TCP/IP 4계층           대표 프로토콜
─────────────────────────────────────────────────────────
7. Application  ┐
6. Presentation ├──→   Application            HTTP, DNS, SMTP, FTP
5. Session      ┘
4. Transport    ───→   Transport              TCP, UDP
3. Network      ───→   Internet               IP, ICMP, ARP
2. Data Link    ┐
1. Physical     ┘──→   Network Access         Ethernet, Wi-Fi, PPP
```

실무에서는 TCP/IP 모델을 더 자주 사용합니다. 하지만 "이 문제는 세션 계층 문제다"처럼 OSI 용어로 소통하는 팀도 있으므로, 대응 관계를 머릿속에 두면 됩니다.

**각 층의 핵심 질문:**

| 계층 | 이 층이 답하는 질문 |
| --- | --- |
| Application | "무슨 의미의 메시지를 주고받을까?" |
| Transport | "데이터가 순서대로, 빠짐없이 도착하는가?" |
| Internet | "목적지까지 어떤 경로로 갈까?" |
| Network Access | "바로 옆 장비에 비트를 어떻게 전달할까?" |

## 단계별로 따라하기

### 1단계: `ping`으로 패킷 왕복 보기

```bash
ping -c 3 example.com
# PING example.com (93.184.216.34) 56(84) bytes of data.
# 64 bytes from 93.184.216.34: icmp_seq=1 ttl=53 time=12.3 ms
# 64 bytes from 93.184.216.34: icmp_seq=2 ttl=53 time=12.1 ms
# 64 bytes from 93.184.216.34: icmp_seq=3 ttl=53 time=12.4 ms
#
# --- example.com ping statistics ---
# 3 packets transmitted, 3 received, 0% packet loss, time 2003ms
# rtt min/avg/max/mdev = 12.1/12.3/12.4/0.1 ms
```

`ping`은 네트워크 계층 프로토콜인 ICMP를 사용합니다. 출력에서 확인할 항목은 세 가지입니다.

- **64 bytes**: 패킷 크기. ICMP echo request의 기본 페이로드 56바이트에 IP 헤더 20바이트, ICMP 헤더 8바이트가 붙어 84바이트가 됩니다.
- **ttl=53**: Time To Live. 패킷이 몇 홉을 더 거칠 수 있는지 나타냅니다. 초기값이 64였다면 11개 라우터를 거쳤다는 의미입니다.
- **time=12.3 ms**: 왕복 시간(RTT). 패킷이 목적지까지 갔다가 돌아오는 데 걸린 시간입니다.

### 2단계: `traceroute`로 경로 보기

```bash
traceroute example.com
# traceroute to example.com (93.184.216.34), 30 hops max, 60 byte packets
#  1  router.local (192.168.1.1)  1.123 ms  0.987 ms  0.912 ms
#  2  isp-gw-1.example-isp.net (10.0.0.1)  5.432 ms  5.301 ms  5.198 ms
#  3  core-rtr.example-isp.net (10.0.1.1)  8.765 ms  8.654 ms  8.543 ms
#  4  * * *
#  5  peer-rtr.cdn-network.net (198.51.100.1)  10.234 ms  10.123 ms  10.012 ms
#  6  93.184.216.34 (93.184.216.34)  12.345 ms  12.234 ms  12.123 ms
```

이 명령은 내 장비에서 목적지까지 패킷이 거치는 라우터를 한 줄씩 보여 줍니다. 각 줄은 TTL을 1씩 증가시키며 ICMP Time Exceeded 응답을 받아 만듭니다. `* * *`은 해당 라우터가 ICMP 응답을 차단한다는 의미이며, 경로 자체가 끊긴 것은 아닙니다.

인터넷이 결국 라우터들의 연쇄라는 사실이 눈에 들어옵니다.

### 3단계: 가장 작은 클라이언트와 서버

```python
# server.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.0.1', 5000))
s.listen(1)
print("listening on 127.0.0.1:5000")

while True:
    conn, addr = s.accept()
    print(f"connected: {addr}")
    conn.sendall(b'hello from server\n')
    conn.close()
```

```python
# client.py
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5000))
data = s.recv(1024)
print(f"received: {data.decode()}")
s.close()
```

소켓은 운영 체제가 제공하는 네트워크 인터페이스입니다. `socket.AF_INET`은 IPv4를, `socket.SOCK_STREAM`은 TCP를 의미합니다. 이 두 줄만으로도 계층 모델의 상위 3개 층(application, transport, internet)이 협력하고 있음을 알 수 있습니다.

### 4단계: 패킷 캡처하기

```bash
# 터미널 1: 서버 실행
python3 server.py

# 터미널 2: tcpdump 실행
sudo tcpdump -i lo -nn -c 10 'port 5000'

# 터미널 3: 클라이언트 실행
python3 client.py
```

캡처 결과:

```text
10:01:03.001 IP 127.0.0.1.54321 > 127.0.0.1.5000: Flags [S], seq 1000, win 65535
10:01:03.001 IP 127.0.0.1.5000 > 127.0.0.1.54321: Flags [S.], seq 2000, ack 1001, win 65535
10:01:03.001 IP 127.0.0.1.54321 > 127.0.0.1.5000: Flags [.], ack 2001, win 65535
10:01:03.002 IP 127.0.0.1.5000 > 127.0.0.1.54321: Flags [P.], seq 2001:2019, ack 1001
10:01:03.002 IP 127.0.0.1.54321 > 127.0.0.1.5000: Flags [.], ack 2019, win 65535
10:01:03.002 IP 127.0.0.1.5000 > 127.0.0.1.54321: Flags [F.], seq 2019, ack 1001
10:01:03.002 IP 127.0.0.1.54321 > 127.0.0.1.5000: Flags [F.], seq 1001, ack 2020
10:01:03.002 IP 127.0.0.1.5000 > 127.0.0.1.54321: Flags [.], ack 1002, win 65535
```

이 캡처에서 TCP 연결의 전체 생명주기가 보입니다:
- **3-way handshake**: SYN → SYN-ACK → ACK (처음 3줄)
- **데이터 전송**: PSH+ACK로 "hello from server\n" 18바이트 전송
- **연결 종료**: FIN → FIN → ACK (4-way 종료의 축약형)

`tcpdump`와 Wireshark는 네트워크 학습의 X선 같은 도구입니다. 이 시리즈에서 계속 다시 사용합니다.

### 5단계: 계층을 머릿속에 두고 다시 보기

위 흐름을 계층에 대응해 보면 이렇게 정리됩니다.

```text
Layer           client 측                    server 측
─────────────────────────────────────────────────────────────
Application     client.py connect+recv       server.py accept+sendall
Transport       TCP: port 54321              TCP: port 5000
Internet        IP: 127.0.0.1               IP: 127.0.0.1
Network Access  loopback driver              loopback driver
```

한 줄의 코드 뒤에 네 층의 협업이 숨어 있다는 점이 중요합니다.

## 캡슐화: 봉투 안의 봉투

계층 모델에서 가장 중요한 동작 원리는 캡슐화(encapsulation)입니다. 데이터가 위에서 아래로 내려갈 때마다 각 층이 자기 헤더를 붙입니다.

```text
Application Data:  "GET / HTTP/1.1\r\n..."                       (가변)
                   ↓ TCP가 감싸기
TCP Segment:      [TCP Header 20B][HTTP Data]                   (+20B)
                   ↓ IP가 감싸기
IP Packet:        [IP Header 20B][TCP Segment]                  (+20B)
                   ↓ Ethernet이 감싸기
Ethernet Frame:   [ETH Header 14B][IP Packet][FCS 4B]           (+18B)
```

수신 측에서는 이 과정이 역순으로 일어납니다. 각 층이 자기 헤더를 벗겨내고 위층에 전달합니다. 이것을 역캡슐화(decapsulation)라 합니다.

**실제 크기를 계산해 봅시다.** "hello"라는 5바이트 HTTP 응답을 보내려면:

| 계층 | 추가되는 헤더 | 누적 크기 |
| --- | --- | --- |
| Application | HTTP 응답 헤더 ~200B | 205B |
| Transport | TCP 20B | 225B |
| Internet | IP 20B | 245B |
| Network Access | Ethernet 14B + FCS 4B | 263B |

5바이트를 보내기 위해 263바이트가 필요합니다. 이것이 "작은 HTTP 요청을 많이 보내면 비효율적"인 이유입니다. 헤더 오버헤드가 페이로드보다 클 수 있습니다.

## 패킷 교환 vs 회선 교환

인터넷이 패킷 교환(packet switching)을 선택한 이유를 이해하면, "왜 패킷이 기본 단위인가"에 대한 답이 나옵니다.

| 방식 | 회선 교환 (전화망) | 패킷 교환 (인터넷) |
| --- | --- | --- |
| 자원 할당 | 통화 시작 시 경로 독점 | 패킷 단위로 공유 |
| 유휴 시간 | 자원 낭비 | 다른 패킷이 사용 |
| 장애 복구 | 회선 끊기면 통화 끊김 | 다른 경로로 우회 가능 |
| 지연 | 일정(예측 가능) | 변동(큐잉 지연) |

웹 브라우징은 요청-응답 패턴이라 대부분의 시간이 유휴 상태입니다. 회선 교환으로 설계하면 유휴 시간에도 자원을 독점하므로 비용이 기하급수적으로 늘어납니다. 패킷 교환은 이 유휴 자원을 다른 통신이 쓸 수 있게 하므로, 같은 물리 인프라에서 훨씬 많은 사용자를 수용할 수 있습니다.

실제 숫자로 보면, 1Gbps 링크에 100명이 동시에 접속해도 각 사용자가 활발히 데이터를 주고받는 시간은 전체의 5-10%에 불과합니다. 패킷 교환은 나머지 90%의 유휴 시간을 다른 사용자에게 즉시 양보합니다. 이 통계적 다중화(statistical multiplexing)가 인터넷의 경제성을 만듭니다.

## 이 코드에서 먼저 볼 점

- 데이터는 항상 패킷으로 잘리고 다시 조립됩니다.
- 각 층은 윗층 데이터를 자기 봉투로 감싸 아래층에 넘깁니다.
- ICMP, TCP, IP는 교과서 안의 추상이 아니라 `ping`과 `tcpdump`에서 직접 보이는 실체입니다.
- "내 컴퓨터에서 저 서버까지"는 언제나 여러 라우터의 협업입니다.
- 소켓 API는 계층 모델의 application-transport 경계에 위치합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 인터넷을 하나의 시스템으로 생각 | 라우팅, AS, 지연을 놓침 | `traceroute`로 실제 경로를 본다 |
| HTTP만 알고 TCP/IP를 모름 | 연결, 재전송, NAT 문제를 진단 못 함 | 용어를 계층별로 정리한다 |
| 모든 실패를 DNS 탓으로 돌림 | 진단 시간이 길어짐 | `ping` → `curl` → `tcpdump` 순서로 자른다 |
| 패킷이 항상 같은 길을 간다고 가정 | 추적이 엇나감 | 인터넷은 패킷 단위로 라우팅된다는 점을 기억한다 |
| TCP는 늘 신뢰 가능하고 UDP는 늘 손실된다고 믿음 | 선택 기준이 흐려짐 | 신뢰성과 속도의 균형으로 본다 |

## 실무에서는 이렇게 보입니다

- 백엔드 API는 대개 TCP 위의 HTTP/HTTPS로 동작합니다. 하나의 HTTP/2 연결에 여러 요청을 multiplexing합니다.
- 게임과 영상 통화는 UDP 위에 자체 프로토콜을 얹는 경우가 많습니다. 패킷 하나가 손실되어도 전체 스트림을 멈추지 않기 위해서입니다.
- 컨테이너는 네트워크 네임스페이스로 가상 네트워크를 만듭니다. 같은 호스트 위의 컨테이너끼리도 IP와 라우팅 테이블이 분리됩니다.
- CDN은 사용자와 가까운 경로 선택과 캐시를 함께 사용합니다. DNS 기반 또는 Anycast 기반으로 가장 가까운 엣지를 찾습니다.
- 모니터링은 패킷 손실, RTT, HTTP 5xx처럼 계층별 지표를 따로 봅니다. "느리다"라는 증상을 어느 층에서 먼저 확인할지가 진단 속도를 결정합니다.

```text
[실무 진단 흐름]
1. ping → ICMP 응답 없음? → 라우팅/방화벽 문제
2. telnet host port → TCP 연결 안 됨? → 포트 막힘/서비스 미기동
3. curl -v → HTTP 5xx? → 애플리케이션 로직 문제
4. tcpdump → 재전송 폭주? → 네트워크 혼잡/MTU 문제
```

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 네트워크 장애 이야기를 들으면 가장 먼저 "어느 층 문제인가"를 묻습니다. 서비스의 5xx인지, TCP 재전송 폭주인지, DNS 조회 실패인지, 라우팅 문제인지부터 나눠 보지 않으면 논의가 끝없이 맴돕니다. 계층 모델은 교과서 그림이 아니라, 장애를 처음 분류하는 표입니다.

또한 HTTP 요청 하나에도 DNS 조회, TCP 핸드셰이크, TLS 핸드셰이크, HTTP 헤더 전송, 여러 홉의 라우팅 비용이 숨어 있다는 사실을 항상 의식합니다. 평소에는 추상화가 이 비용을 감추지만, 장애가 나면 청구서처럼 하나씩 드러납니다.

```text
HTTP GET https://api.example.com/users 의 숨은 비용

1. DNS lookup         → 50ms (캐시 미스 시)
2. TCP handshake      → 1 RTT = 30ms
3. TLS handshake      → 1-2 RTT = 30-60ms
4. HTTP request/resp  → 1 RTT + server processing = 50ms
─────────────────────────────────────────────
총 최초 요청 비용     → 160-190ms (keep-alive 없을 때)
```

연결을 재사용(keep-alive)하면 2-3번이 사라집니다. HTTP/2 multiplexing은 여기서 한 단계 더 나아가 하나의 TCP 연결에 수십 개 요청을 동시에 보냅니다. 이런 최적화의 근거도 결국 계층 모델에서 나옵니다.

## 심화: 실제 패킷을 Wireshark로 읽기

CLI의 `tcpdump`는 빠르지만, 패킷 내부를 계층별로 펼쳐 보려면 Wireshark가 더 직관적입니다.

### Wireshark 필터 예시

```text
# 특정 포트의 TCP 통신만 보기
tcp.port == 5000

# 3-way handshake만 보기
tcp.flags.syn == 1

# 재전송 패킷만 보기
tcp.analysis.retransmission

# DNS 쿼리만 보기
dns

# 특정 호스트와의 통신
ip.addr == 93.184.216.34
```

### 하나의 패킷을 계층별로 읽기

Wireshark에서 패킷 하나를 클릭하면 다음과 같이 계층별로 펼쳐집니다:

```text
Frame 1: 74 bytes on wire (592 bits)
├── Ethernet II, Src: aa:bb:cc:dd:ee:ff, Dst: 11:22:33:44:55:66
│   ├── Type: IPv4 (0x0800)
├── Internet Protocol Version 4
│   ├── Source: 192.168.1.100
│   ├── Destination: 93.184.216.34
│   ├── TTL: 64
│   ├── Protocol: TCP (6)
│   ├── Total Length: 60
├── Transmission Control Protocol
│   ├── Source Port: 54321
│   ├── Destination Port: 80
│   ├── Flags: SYN
│   ├── Sequence Number: 0 (relative)
│   ├── Window Size: 65535
```

이렇게 한 패킷 안에 Ethernet → IP → TCP가 순서대로 쌓여 있는 것이 캡슐화의 실체입니다. 각 헤더는 자기 층의 정보만 담고 있으며, 상위 층의 내용은 payload로 취급합니다.

### 연습: loopback에서 캡처 후 분석

```bash
# 1. Wireshark에서 loopback 인터페이스 선택
# 2. 필터: tcp.port == 5000
# 3. server.py 실행 → client.py 실행
# 4. 캡처된 패킷에서 다음을 확인:
#    - SYN 패킷의 seq number
#    - SYN-ACK의 ack = client seq + 1 인지
#    - PSH+ACK 패킷의 payload에 "hello from server" 문자열이 보이는지
#    - FIN 패킷이 양쪽에서 각각 발생하는지
```

## 네트워크 진단의 계층별 도구 정리

| 계층 | 확인 대상 | 도구 | 대표 명령 |
| --- | --- | --- | --- |
| Application | HTTP 응답, API 동작 | curl, httpie | `curl -v https://example.com` |
| Transport | 포트 열림, TCP 상태 | netstat, ss, telnet | `ss -tnlp` |
| Internet | IP 연결성, 경로 | ping, traceroute, mtr | `mtr example.com` |
| Network Access | 인터페이스 상태, ARP | ip, arp, ethtool | `ip link show` |

문제가 생기면 아래층부터 위로 올라가며 확인하는 것이 정석입니다. IP 연결이 안 되는데 HTTP를 디버깅하면 시간만 낭비합니다.

## 체크리스트

- [ ] 네트워크와 인터넷의 차이를 설명할 수 있다
- [ ] 패킷, 프로토콜, 계층 모델이 무엇인지 안다
- [ ] OSI 7계층과 TCP/IP 4계층의 대응 관계를 그릴 수 있다
- [ ] 캡슐화(encapsulation)의 동작을 설명할 수 있다
- [ ] `ping`, `traceroute`, `tcpdump`를 직접 한 번 써 봤다
- [ ] HTTP가 어느 층에서 동작하는지 안다
- [ ] 문제가 생기면 먼저 "어느 층인가"를 묻는다
- [ ] 패킷 교환이 회선 교환보다 유리한 이유를 설명할 수 있다

## 연습 문제

1. 자주 방문하는 사이트에 `traceroute`를 실행하고, 라우터 수와 평균 RTT를 한 단락으로 정리해 보세요.
2. 위 클라이언트/서버 예제를 실행한 뒤 `tcpdump`로 캡처하고, SYN / SYN-ACK / ACK 순서를 직접 찾아 보세요.
3. HTTP 요청이 실패했다고 가정하고, 어느 층부터 어떤 도구로 확인할지 5단계 절차를 적어 보세요.
4. "hello"라는 5바이트를 TCP로 보낼 때, Ethernet 프레임까지 포함한 총 바이트 수를 계산해 보세요.
5. 패킷 교환과 회선 교환의 차이를 동료에게 30초 안에 설명하는 문장을 만들어 보세요.

## 정리와 다음 글

네트워크는 케이블이 아니라 약속의 묶음입니다. 패킷, 프로토콜, 계층 모델이라는 세 단어가 이 시리즈 전체를 정리하는 책장이 됩니다. 앞으로 새로운 용어가 나올 때마다 "이 단어는 어느 층에 놓이는가"를 먼저 묻는 습관이 학습 속도를 크게 바꿉니다.

이 글에서 다룬 핵심을 한 문장으로 요약하면: 인터넷은 패킷 교환 방식으로 동작하고, 계층 모델은 각 층의 책임을 분리해 복잡도를 관리합니다.

다음 글에서는 인터넷의 가장 기본적인 주소 체계인 IP와 subnet을 다룹니다.

## 처음 질문으로 돌아가기

- **네트워크와 인터넷은 어떻게 다른가요?**
  - 네트워크는 장치들이 연결된 국지적 단위이고, 인터넷은 이 네트워크들이 IP라는 공통 프로토콜로 연결된 글로벌 연합입니다. 사무실 LAN은 네트워크이고, 그 LAN이 ISP를 통해 다른 AS와 연결되면 인터넷의 일부가 됩니다.
- **패킷은 왜 네트워크의 기본 단위로 취급될까요?**
  - 인터넷은 패킷 교환 방식을 채택했기 때문입니다. 회선 교환과 달리 패킷 단위로 자원을 공유하므로, 유휴 시간에 다른 통신이 같은 링크를 사용할 수 있고, 장애 시 다른 경로로 우회할 수 있습니다.
- **계층 모델이 없으면 IP, TCP, DNS, HTTP를 왜 함께 이해하기 어려울까요?**
  - 계층 모델은 각 프로토콜의 책임 범위를 정합니다. IP는 경로, TCP는 신뢰성, DNS는 이름 해석, HTTP는 메시지 의미를 담당합니다. 이 구분 없이 배우면 모든 개념이 한 덩어리로 뒤섞여, 장애가 발생했을 때 어디서부터 봐야 할지 판단할 수 없습니다.

<!-- toc:begin -->
## 시리즈 목차

- **네트워크란 무엇인가? (현재 글)**
- IP와 subnet (예정)
- TCP와 UDP (예정)
- DNS (예정)
- HTTP와 HTTPS (예정)
- TLS 기초 (예정)
- 라우팅과 NAT (예정)
- Load Balancer (예정)
- WebSocket과 실시간 통신 (예정)
- 네트워크 문제 디버깅 (예정)

<!-- toc:end -->

## 참고 자료

- [Tanenbaum & Wetherall — Computer Networks](https://www.pearson.com/store/p/computer-networks/P100000875375)
- [Kurose & Ross — Computer Networking: A Top-Down Approach](https://gaia.cs.umass.edu/kurose_ross/)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [Cloudflare Learning — What is the Internet?](https://www.cloudflare.com/learning/network-layer/what-is-the-internet/)
- [RFC 1122 — Internet Host Requirements](https://www.rfc-editor.org/rfc/rfc1122)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, 인터넷, 패킷, 계층모델, OSI
