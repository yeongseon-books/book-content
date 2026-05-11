---
series: computer-networks-101
episode: 1
title: 네트워크란 무엇인가?
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
  - 인터넷
  - 패킷
  - 계층모델
  - OSI
seo_description: 네트워크가 무엇이고 인터넷이 어떻게 동작하는지, 패킷·계층 모델·프로토콜이라는 세 단어로 정리합니다.
last_reviewed: '2026-05-11'
---

# 네트워크란 무엇인가?

> Computer Networks 101 시리즈 (1/10)


## 이 글에서 다룰 문제

네트워크 책을 처음 펼치면 IP, TCP, UDP, DNS, HTTP, TLS, BGP, NAT 같은 약어가 동시에 쏟아집니다. 머릿속 그림 없이 이 단어들을 외우면 서로 어떻게 연결되는지 보이지 않고 결국 다 잊어버립니다. 계층 모델은 이 단어들을 정리해 두는 책장입니다. 책장 없이 책을 사면 바닥에 쌓인 채 영영 못 꺼내게 됩니다.

> 네트워크 학습은 새 단어를 외우는 것이 아니라, 이미 있는 단어를 어느 층에 놓을지 정리하는 일입니다.

## 전체 흐름
> 데이터는 패킷이라는 작은 단위로 잘려 네트워크를 통해 전달됩니다. 각 단계마다 다른 종류의 약속(프로토콜)이 일을 분담합니다. 물리적인 신호, 인접 장비 사이의 프레임, 전 세계로 라우팅되는 패킷, 신뢰성 있는 연결, 마지막으로 의미 있는 메시지(HTTP 요청 등). 이 분담 구조가 계층 모델입니다.

```text
[애플리케이션] HTTP, DNS, SMTP, gRPC ...
[전송]         TCP / UDP
[네트워크]     IP, ICMP, 라우팅
[링크]         Ethernet, Wi-Fi
[물리]         전기/광/전파 신호
```

## Before / After

**Before — "인터넷은 마법":**

```text
브라우저 → ??? → 서버
중간이 모두 검은 상자
```

**After — "층마다 책임이 있다":**

```text
HTTP(메시지) → TCP(신뢰성) → IP(라우팅) → Ethernet(인접 전송) → 신호
각 층은 윗층의 데이터를 자신의 봉투에 담아 다음 층으로 넘긴다 (encapsulation)
```

층의 책임을 알면 어떤 문제가 어디서 생겼는지(앱? TCP? 라우팅?)를 분리해 볼 수 있습니다.

## 단계별로 따라하기

### 1단계: ping으로 패킷 왕복 보기

```bash
ping -c 3 example.com
# 출력 예시: 64 bytes from 93.184.216.34: icmp_seq=1 ttl=53 time=12.3 ms
```

ping은 ICMP라는 네트워크층 프로토콜을 씁니다. 출력에는 패킷 크기, 응답 시간, TTL이 나옵니다.

### 2단계: traceroute로 경로 보기

```bash
traceroute example.com    # 또는 mtr example.com
# 출력 예시: 1  router.local  1.1 ms
# 출력 예시: 2  isp-gw        5.4 ms
# 출력 예시: ...
# 출력 예시: N  93.184.216.34 12.3 ms
```

내 컴퓨터에서 목적지까지 패킷이 통과하는 라우터들을 한 줄씩 보여줍니다. 인터넷이 "라우터의 라우터의 라우터"라는 사실이 한눈에 보입니다.

### 3단계: 가장 작은 클라이언트/서버

```python
# server.py 예제
import socket
s = socket.socket()
s.bind(('127.0.0.1', 5000)); s.listen()
while True:
    c, _ = s.accept()
    c.sendall(b'hello\n'); c.close()
```

```python
# client.py 예제
import socket
s = socket.socket(); s.connect(('127.0.0.1', 5000))
print(s.recv(1024))
```

소켓은 OS가 제공하는 네트워크 인터페이스입니다. 시리즈에서 자주 다시 등장합니다.

### 4단계: 패킷 캡처

```bash
sudo tcpdump -i lo -nn -c 5 'port 5000'
# 위 server/client를 실행하면 SYN, SYN-ACK, ACK, PSH+ACK, FIN 시퀀스가 보임
```

tcpdump/Wireshark는 모든 네트워크 학습의 X선입니다. 4편(DNS), 5편(HTTP)에서도 다시 사용합니다.

### 5단계: 계층 인식하며 다시 보기

위 흐름을 계층별로 정리해 보세요.

```text
client.recv() ↔ server.sendall()    ← 애플리케이션 층 (메시지)
TCP            ↔ TCP                ← 전송 층 (연결, 순서, 재전송)
IP(loopback)   ↔ IP(loopback)       ← 네트워크 층 (라우팅)
loopback driver                      ← 링크 + 물리 층
```

같은 한 줄의 코드가 다섯 층의 협업을 만들어 냅니다.

## 이 코드에서 주목할 점

- 데이터는 항상 패킷 단위로 자르고 합쳐집니다
- 각 층은 윗층 데이터를 자신의 봉투에 넣고(encapsulation) 다음 층에 넘깁니다
- ICMP, TCP, IP는 책에서 본 추상이 아니라 ping/tcpdump 출력에 보이는 실체
- "내 컴퓨터에서 서버까지"는 항상 여러 라우터의 협업

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 인터넷을 단일 시스템으로 가정 | 라우팅, AS, 지연 무시 | traceroute로 실체 확인 |
| HTTP만 알고 TCP/IP 모름 | 연결, 재전송, NAT 문제 진단 불가 | 계층 모델로 정리 |
| 모든 연결 문제를 "DNS 탓" | 진단 시간 낭비 | ping → curl → tcpdump 순서로 절단 |
| 패킷이 항상 같은 경로로 간다는 가정 | 흐름 추적 실패 | 인터넷은 패킷 단위 라우팅 |
| TCP는 항상 신뢰성, UDP는 항상 손실 | 부정확 | 신뢰성/속도 트레이드오프(3편 참조) |

## 실무에서는 이렇게 쓰입니다

- 백엔드 API: HTTP/HTTPS over TCP, 종종 HTTP/2 또는 HTTP/3
- 게임/영상 통화: UDP 위에서 자체 프로토콜
- 컨테이너: 네트워크 namespace로 가상 네트워크 구성
- CDN: 사용자에 가장 가까운 라우팅 + 캐시
- 모니터링: 계층별 메트릭(패킷 손실, RTT, HTTP 5xx)을 분리해 관찰

## 체크리스트

- [ ] 네트워크와 인터넷의 차이를 안다
- [ ] 패킷, 프로토콜, 계층 모델의 의미를 안다
- [ ] ping, traceroute, tcpdump를 한 번 이상 써 봤다
- [ ] HTTP가 어느 층 위에서 도는지 안다
- [ ] 사고가 나면 "어느 층 문제?"라고 먼저 묻는다

## 정리 및 다음 단계

네트워크는 케이블이 아니라 약속의 묶음입니다. 패킷, 프로토콜, 계층 모델이라는 세 단어가 시리즈 전체의 책장이 됩니다. 새 단어가 나올 때마다 이 책장 위 어디에 꽂힐지 의식하는 습관이 학습 속도를 결정합니다.

다음 글에서는 인터넷에서 가장 기본이 되는 주소 체계 — IP와 subnet으로 넘어갑니다.

<!-- toc:begin -->
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

Tags: Computer Science, 네트워크, 인터넷, 패킷, 계층모델, OSI
