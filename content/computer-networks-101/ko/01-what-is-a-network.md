---
series: computer-networks-101
episode: 1
title: 네트워크란 무엇인가?
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
  - 인터넷
  - 패킷
  - 계층모델
  - OSI
seo_description: 패킷, 프로토콜, 계층 모델을 중심으로 현대 네트워크의 기본 동작 원리와 인터넷 통신 과정을 상세히 설명합니다.
last_reviewed: '2026-05-12'
---

# 네트워크란 무엇인가?

이 글은 Computer Networks 101 시리즈의 첫 번째 글입니다.

## 이 글에서 다룰 문제

- 네트워크와 인터넷은 어떻게 다른가요?
- 패킷은 왜 네트워크의 기본 단위로 취급될까요?
- 계층 모델이 없으면 IP, TCP, DNS, HTTP를 왜 함께 이해하기 어려울까요?
- 프로토콜은 단순한 용어가 아니라 어떤 약속을 뜻할까요?

> 네트워크는 케이블 자체가 아니라 약속의 묶음입니다. 컴퓨터 두 대가 데이터를 주고받을 수 있는 이유는 누가 먼저 말할지, 데이터를 어떻게 잘라 보낼지, 받은 쪽이 어떻게 다시 조립할지에 대한 규칙이 있기 때문입니다. 그 규칙이 프로토콜이고, 그 규칙들이 층층이 쌓인 구조가 계층 모델입니다.

## 왜 중요한가

네트워크 책을 처음 펼치면 IP, TCP, UDP, DNS, HTTP, TLS, BGP, NAT 같은 약어가 한꺼번에 쏟아집니다. 머릿속 그림 없이 이 단어들을 외우기만 하면 서로 어떻게 연결되는지 보이지 않고, 결국 오래 남지 않습니다. 계층 모델은 이 단어들을 꽂아 둘 책장입니다. 책장이 없으면 책이 바닥에 쌓이듯, 개념도 금세 뒤엉킵니다.

> 네트워크를 배운다는 것은 새 단어를 외우는 일이 아니라, 각 단어를 어느 층에 놓아야 하는지 정하는 일입니다.

## 핵심 그림

> 데이터는 패킷이라는 작은 단위로 잘려 네트워크를 흐릅니다. 그리고 각 층은 서로 다른 책임을 맡습니다. 물리 신호를 보내는 층, 바로 옆 장비와 프레임을 주고받는 층, 전 세계 경로를 찾는 층, 신뢰성 있는 전송을 맡는 층, 마지막으로 HTTP 같은 의미 있는 메시지를 다루는 층이 나뉘어 있습니다. 이 책임 분리가 바로 계층 모델입니다.

```text
[애플리케이션] HTTP, DNS, SMTP, gRPC ...
[전송]         TCP / UDP
[네트워크]     IP, ICMP, 라우팅
[링크]         Ethernet, Wi-Fi
[물리]         전기/광/전파 신호
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 패킷 | 네트워크를 흐르는 데이터의 기본 단위 |
| 프로토콜 | 두 노드가 통신하기 위한 형식과 절차의 약속 |
| 계층 모델 | 통신 책임을 여러 층으로 나눈 구조 |
| 호스트 | 통신의 끝점이 되는 장치(컴퓨터, 서버, 휴대폰) |
| 라우터 | 패킷을 다음 네트워크로 넘기는 장치 |

## Before / After

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

## 단계별로 따라하기

### 1단계: `ping`으로 패킷 왕복 보기

```bash
ping -c 3 example.com
# 64 bytes from 93.184.216.34: icmp_seq=1 ttl=53 time=12.3 ms
```

`ping`은 네트워크 계층 프로토콜인 ICMP를 사용합니다. 출력에는 패킷 크기, 왕복 시간, TTL이 보입니다.

### 2단계: `traceroute`로 경로 보기

```bash
traceroute example.com    # or mtr example.com
# 1  router.local  1.1 ms
# 2  isp-gw        5.4 ms
# ...
# N  93.184.216.34 12.3 ms
```

이 명령은 내 장비에서 목적지까지 패킷이 거치는 라우터를 한 줄씩 보여 줍니다. 인터넷이 결국 라우터들의 연쇄라는 사실이 눈에 들어옵니다.

### 3단계: 가장 작은 클라이언트와 서버

```python
# server.py
import socket
s = socket.socket()
s.bind(('127.0.0.1', 5000)); s.listen()
while True:
    c, _ = s.accept()
    c.sendall(b'hello\n'); c.close()
```

```python
# client.py
import socket
s = socket.socket(); s.connect(('127.0.0.1', 5000))
print(s.recv(1024))
```

소켓은 운영 체제가 제공하는 네트워크 인터페이스입니다. 시리즈 전체에서 계속 다시 등장합니다.

### 4단계: 패킷 캡처하기

```bash
sudo tcpdump -i lo -nn -c 5 'port 5000'
# Run server/client above and you will see SYN, SYN-ACK, ACK, PSH+ACK, FIN
```

`tcpdump`와 Wireshark는 네트워크 학습의 X선 같은 도구입니다. 4편과 5편에서도 다시 사용합니다.

### 5단계: 계층을 머릿속에 두고 다시 보기

위 흐름을 계층에 대응해 보면 이렇게 정리됩니다.

```text
client.recv() ↔ server.sendall()    ← application layer (message)
TCP            ↔ TCP                ← transport layer (connection, order, retransmission)
IP(loopback)   ↔ IP(loopback)       ← network layer (routing)
loopback driver                      ← link + physical layer
```

한 줄의 코드 뒤에 다섯 층의 협업이 숨어 있다는 점이 중요합니다.

## 이 코드에서 먼저 볼 점

- 데이터는 항상 패킷으로 잘리고 다시 조립됩니다.
- 각 층은 윗층 데이터를 자기 봉투로 감싸 아래층에 넘깁니다.
- ICMP, TCP, IP는 교과서 안의 추상이 아니라 `ping`과 `tcpdump`에서 직접 보이는 실체입니다.
- "내 컴퓨터에서 저 서버까지"는 언제나 여러 라우터의 협업입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 인터넷을 하나의 시스템으로 생각 | 라우팅, AS, 지연을 놓침 | `traceroute`로 실제 경로를 본다 |
| HTTP만 알고 TCP/IP를 모름 | 연결, 재전송, NAT 문제를 진단 못 함 | 용어를 계층별로 정리한다 |
| 모든 실패를 DNS 탓으로 돌림 | 진단 시간이 길어짐 | `ping` → `curl` → `tcpdump` 순서로 자른다 |
| 패킷이 항상 같은 길을 간다고 가정 | 추적이 엇나감 | 인터넷은 패킷 단위로 라우팅된다는 점을 기억한다 |
| TCP는 늘 신뢰 가능하고 UDP는 늘 손실된다고 믿음 | 선택 기준이 흐려짐 | 신뢰성과 속도의 균형으로 본다 |

## 실무에서는 이렇게 보입니다

- 백엔드 API는 대개 TCP 위의 HTTP/HTTPS로 동작합니다.
- 게임과 영상 통화는 UDP 위에 자체 프로토콜을 얹는 경우가 많습니다.
- 컨테이너는 네트워크 네임스페이스로 가상 네트워크를 만듭니다.
- CDN은 사용자와 가까운 경로 선택과 캐시를 함께 사용합니다.
- 모니터링은 패킷 손실, RTT, HTTP 5xx처럼 계층별 지표를 따로 봅니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 네트워크 장애 이야기를 들으면 가장 먼저 "어느 층 문제인가"를 묻습니다. 서비스의 5xx인지, TCP 재전송 폭주인지, DNS 조회 실패인지, 라우팅 문제인지부터 나눠 보지 않으면 논의가 끝없이 맴돕니다. 계층 모델은 교과서 그림이 아니라, 장애를 처음 분류하는 표입니다.

또한 HTTP 요청 하나에도 DNS 조회, TCP 핸드셰이크, TLS 핸드셰이크, HTTP 헤더 전송, 여러 홉의 라우팅 비용이 숨어 있다는 사실을 항상 의식합니다. 평소에는 추상화가 이 비용을 감추지만, 장애가 나면 청구서처럼 하나씩 드러납니다.

## 체크리스트

- [ ] 네트워크와 인터넷의 차이를 설명할 수 있다
- [ ] 패킷, 프로토콜, 계층 모델이 무엇인지 안다
- [ ] `ping`, `traceroute`, `tcpdump`를 직접 한 번 써 봤다
- [ ] HTTP가 어느 층에서 동작하는지 안다
- [ ] 문제가 생기면 먼저 "어느 층인가"를 묻는다

## 연습 문제

1. 자주 방문하는 사이트에 `traceroute`를 실행하고, 라우터 수와 평균 RTT를 한 단락으로 정리해 보세요.
2. 위 클라이언트/서버 예제를 실행한 뒤 `tcpdump`로 캡처하고, SYN / SYN-ACK / ACK 순서를 직접 찾아 보세요.
3. HTTP 요청이 실패했다고 가정하고, 어느 층부터 어떤 도구로 확인할지 5단계 절차를 적어 보세요.

## 정리와 다음 글

네트워크는 케이블이 아니라 약속의 묶음입니다. 패킷, 프로토콜, 계층 모델이라는 세 단어가 이 시리즈 전체를 정리하는 책장이 됩니다. 앞으로 새로운 용어가 나올 때마다 "이 단어는 어느 층에 놓이는가"를 먼저 묻는 습관이 학습 속도를 크게 바꿉니다.

다음 글에서는 인터넷의 가장 기본적인 주소 체계인 IP와 subnet을 다룹니다.

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
