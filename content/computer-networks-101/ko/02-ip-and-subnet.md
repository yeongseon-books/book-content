---
series: computer-networks-101
episode: 2
title: "Computer Networks 101 (2/10): IP와 subnet"
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
  - IP
  - subnet
  - CIDR
  - 라우팅
seo_description: IP와 subnet, CIDR이 라우팅의 출발점이 되는 이유를 설명합니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (2/10): IP와 subnet

이 글은 Computer Networks 101 시리즈의 2번째 글입니다.

## 먼저 던지는 질문

- IPv4와 IPv6는 어떤 차이를 가질까요?
- subnet mask와 CIDR 표기는 무엇을 나눠서 보여 줄까요?
- 네트워크 주소, 브로드캐스트 주소, 사용 가능한 호스트 수는 어떻게 계산할까요?

## 큰 그림

![Computer Networks 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/02/02-01-concept-at-a-glance.ko.png)

*Computer Networks 101 2장 흐름 개요*

## 왜 중요한가

IP 주소를 그냥 "장비 하나의 번호"로만 외우면 라우팅, NAT, 방화벽 규칙이 모두 마법처럼 보입니다. 실제 네트워크 장비는 IP 주소에서 네트워크 부분과 호스트 부분을 나눠 보고, 네트워크 부분만으로 다음 홉을 결정합니다. subnet을 읽을 줄 모르면 클라우드 VPC, Kubernetes 네트워크 정책, 사내 방화벽 규칙이 전부 추측 게임이 됩니다.

> 라우터가 실제로 보는 것은 IP 주소 전체가 아니라 그중 네트워크 부분입니다.

## 핵심 그림

> IP 주소는 IPv4에서는 32비트, IPv6에서는 128비트 숫자입니다. subnet mask는 어디까지가 네트워크이고 어디부터가 호스트인지 알려 주는 비트 기준선입니다. CIDR(`/24`, `/16`)은 그 기준선의 길이를 비트 수로 적는 방식입니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| IPv4 / IPv6 | 32비트 / 128비트 주소 공간 |
| subnet mask | 네트워크 부분과 호스트 부분을 나누는 비트 패턴 |
| CIDR | `192.168.10.0/24` 같은 prefix 길이 표기 |
| 네트워크 주소 | 호스트 비트를 모두 0으로 둔 주소 |
| 브로드캐스트 주소 | 호스트 비트를 모두 1로 둔 주소(IPv4) |
| 사설 IP | 인터넷에 직접 라우팅되지 않는 대역 |

## Before / After

**Before — "IP는 그냥 숫자다"**

```text
"192.168.0.5는 내 노트북 번호" — 끝.
```

**After — "IP는 네트워크 + 호스트다"**

```text
192.168.0.5/24
└─ network 192.168.0.0/24 안의 host 5
같은 /24 안의 노드끼리는 라우터 없이 직접 통신
다른 네트워크로 가려면 라우터를 지나야 함
```

## 단계별로 따라하기

### 1단계: 내 IP 확인하기

```bash
ip addr show       # Linux
ifconfig           # macOS
ipconfig           # Windows
```

`inet 192.168.0.42/24` 같은 줄에서 IP 주소와 prefix 길이를 함께 볼 수 있습니다.

### 2단계: 라우팅 테이블 읽기

```bash
ip route
# default via 192.168.0.1 dev wlan0
# 192.168.0.0/24 dev wlan0 proto kernel scope link src 192.168.0.42
```

같은 `/24` 안의 목적지는 직접 보내고, 그 밖의 목적지는 기본 게이트웨이인 `192.168.0.1`로 보냅니다.

### 3단계: 코드로 subnet 계산하기

```python
import ipaddress

net = ipaddress.ip_network('192.168.10.0/24')
print(net.network_address)   # 192.168.10.0
print(net.broadcast_address) # 192.168.10.255
print(net.num_addresses)     # 256
print(list(net.hosts())[:3]) # [192.168.10.1, .2, .3]

ip = ipaddress.ip_interface('192.168.10.42/24')
print(ip.network)            # 192.168.10.0/24
```

### 4단계: 같은 subnet인지 판정하기

```python
import ipaddress

a = ipaddress.ip_address('192.168.10.42')
b = ipaddress.ip_address('192.168.10.99')
c = ipaddress.ip_address('192.168.20.1')
net = ipaddress.ip_network('192.168.10.0/24')

print(a in net, b in net, c in net)   # True True False
```

같은 subnet이면 라우터 없이 직접 전달되고, 아니면 라우터를 거쳐야 합니다.

### 5단계: 사설 IP와 공인 IP 구분하기

```python
import ipaddress

for s in ['10.0.0.5', '172.16.3.4', '192.168.1.1', '8.8.8.8']:
    ip = ipaddress.ip_address(s)
    print(s, 'private' if ip.is_private else 'public')
```

가정과 사무실의 장비는 대체로 사설 IP를 쓰고, 인터넷으로 나갈 때는 NAT를 거칩니다.

## 이 코드에서 먼저 볼 점

- `ip_network`는 네트워크 단위이고, `ip_interface`는 "호스트 IP + prefix" 단위입니다.
- prefix 길이는 단순한 축약 표기가 아니라 라우팅의 기본 단위입니다.
- 사설/공인 여부는 `ipaddress` 모듈이 직접 판단해 줍니다.
- "같은 subnet인가"는 곧 "라우터 없이 갈 수 있는가"와 같은 질문입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 언제나 `/24`라고 가정 | VPC와 Kubernetes에서 충돌 발생 | prefix 길이를 항상 명시한다 |
| 네트워크 주소나 브로드캐스트 주소를 호스트로 사용 | 통신 실패 | `hosts()` 범위에서만 고른다 |
| 사설 IP가 인터넷에서 바로 보인다고 생각 | 연결과 보안 오류 발생 | NAT 또는 공인 IP를 사용한다 |
| IPv4만 고려해 코드 작성 | 듀얼 스택 환경에서 실패 | `ip_address` 추상화를 사용한다 |
| subnet을 단순 그룹으로만 이해 | 라우팅과 보안 정책을 놓침 | subnet을 라우팅 단위로 본다 |

## 실무에서는 이렇게 보입니다

- AWS VPC는 `/16` 대역을 여러 `/24` subnet으로 나눠 AZ별로 배치합니다.
- Kubernetes는 pod CIDR과 service CIDR을 별도 prefix로 가집니다.
- 방화벽은 `10.0.0.0/8`처럼 prefix 단위로 규칙을 씁니다.
- VPN은 다른 조직의 사설 대역과 충돌하지 않도록 prefix를 미리 설계해야 합니다.
- 게임 서버처럼 인접한 장비끼리 빠른 내부 통신이 필요한 경우에도 subnet 설계가 중요합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새 인프라를 설계할 때 가장 먼저 IP 계획부터 그립니다. 어느 prefix를 어디에 줄지, 다른 조직 네트워크와 충돌하지 않는지, 앞으로 몇 년 동안 호스트 수가 충분한지부터 봅니다. prefix 결정은 한 번 굳어지면 되돌리기 매우 어렵기 때문입니다.

또한 "왜 이 연결이 안 되지"라는 질문을 받으면 양 끝점의 IP, subnet, 라우팅 테이블, 방화벽 규칙을 먼저 함께 봅니다. 애플리케이션 디버깅보다 먼저 네트워크 지형도를 머릿속에 세웁니다.

## 체크리스트

- [ ] CIDR `/24`, `/16`, `/8`이 뜻하는 범위를 안다
- [ ] 네트워크 주소와 브로드캐스트 주소를 계산할 수 있다
- [ ] 두 IP가 같은 subnet인지 판단할 수 있다
- [ ] 사설 IP와 공인 IP 대역을 안다
- [ ] 새 시스템을 설계할 때 IP 계획부터 그린다

## 연습 문제

1. `10.20.0.0/22`의 네트워크 주소, 브로드캐스트 주소, 사용 가능한 호스트 수를 계산해 보세요.
2. `172.16.5.10`과 `172.16.5.130`이 같은 `/25` subnet에 있는지 판단해 보세요.
3. 회사가 `/16` 대역 하나를 갖고 있다고 가정하고, 다섯 팀에 각각 `/20`을 배정하는 계획을 그려 보세요.

## 정리와 다음 글

IP 주소는 한 컴퓨터의 번호가 아니라 "어느 네트워크의 몇 번째 호스트인가"를 함께 담은 좌표입니다. subnet과 CIDR은 그 경계를 정의하고, 라우팅, NAT, 방화벽, VPC는 모두 그 위에서 동작합니다.

다음 글에서는 IP 위에서 동작하는 두 전송 프로토콜, TCP와 UDP를 비교합니다.

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

### 운영 로그와 패킷 증거를 함께 읽는 연습

문서만 보면 개념은 이해되지만, 운영 문제는 보통 "같은 시간대의 서로 다른 증거"를 묶어야 해결됩니다. 다음과 같이 최소 공통 포맷을 맞추면 진단 속도가 크게 올라갑니다.

```text
2026-05-21T10:01:03.120Z src=10.0.1.24:51432 dst=10.0.2.11:443 event=connect_start req_id=ab12
2026-05-21T10:01:03.341Z src=10.0.1.24:51432 dst=10.0.2.11:443 event=connect_timeout req_id=ab12
2026-05-21T10:01:03.350Z pcap src=10.0.1.24:51432 dst=10.0.2.11:443 flag=SYN retransmit=3
```

위처럼 애플리케이션 로그와 캡처 로그의 키를 맞추면, "코드 버그"와 "네트워크 경로 문제"를 같은 화면에서 분리할 수 있습니다. 특히 재전송 카운트, RTT 변화, RST 발생 위치를 함께 보면 문제 책임 경계가 명확해집니다.

### 최소 재현 시나리오 템플릿

1. 동일 요청을 10회 반복해 성공/실패 비율 기록
2. 실패 시점의 소켓 예외 타입(`timeout`, `connection reset`) 집계
3. 같은 시점의 패킷에서 SYN, ACK, RST, FIN 비율 확인

이 과정을 습관화하면 "가끔 느리다" 같은 모호한 제보를 수치화된 진단 리포트로 바꿀 수 있습니다.

## 처음 질문으로 돌아가기

- **IPv4와 IPv6는 어떤 차이를 가질까요?**
  - 본문의 기준은 IP와 subnet를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **subnet mask와 CIDR 표기는 무엇을 나눠서 보여 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **네트워크 주소, 브로드캐스트 주소, 사용 가능한 호스트 수는 어떻게 계산할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Networks 101 (1/10): 네트워크란 무엇인가?](./01-what-is-a-network.md)
- **IP와 subnet (현재 글)**
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

- [RFC 791 — Internet Protocol](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 4632 — CIDR](https://www.rfc-editor.org/rfc/rfc4632)
- [Python `ipaddress` 모듈 문서](https://docs.python.org/3/library/ipaddress.html)
- [Cloudflare Learning — What is an IP address?](https://www.cloudflare.com/learning/dns/glossary/what-is-my-ip-address/)

Tags: Computer Science, 네트워크, IP, subnet, CIDR, 라우팅
