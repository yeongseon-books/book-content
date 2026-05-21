---
series: computer-networks-101
episode: 7
title: "Computer Networks 101 (7/10): 라우팅과 NAT"
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
  - 라우팅
  - NAT
  - default gateway
  - 사설IP
seo_description: 라우팅 테이블의 결정 원리와 NAT가 사설 IP와 공인 IP 사이를 연결하는 방식을 통해 패킷이 목적지까지 도달하는 과정을 상세히 다룹니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (7/10): 라우팅과 NAT

이 글은 Computer Networks 101 시리즈의 7번째 글입니다.

## 먼저 던지는 질문

- 라우팅 테이블은 어떻게 읽어야 할까요?
- default gateway와 longest-prefix match는 어떻게 동작할까요?
- NAT는 출발지 IP와 포트를 어떻게 바꿀까요?

## 큰 그림

![Computer Networks 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/07/07-01-concept-at-a-glance.ko.png)

*Computer Networks 101 7장 흐름 개요*

## 왜 중요한가

라우팅을 모르면 "왜 회사 네트워크에서만 안 되지?"라는 질문에 답하기 어렵습니다. NAT를 모르면 "왜 집에서는 안 되고 사무실에서는 되지?", "왜 외부에서 우리 서버로 바로 못 들어오지?" 같은 문제가 설명되지 않습니다. VPN, 컨테이너 네트워크, 클라우드 VPC 역시 결국 라우팅과 NAT의 변형입니다.

> 라우터는 전체 경로를 한 번에 아는 것이 아니라, 그 순간 필요한 다음 홉만 봅니다. 인터넷은 그 작은 결정들의 합입니다.

## 핵심 그림

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 라우팅 테이블 | "이 prefix는 이 인터페이스/다음 홉으로"라는 매핑 |
| default gateway | 더 구체적인 규칙이 없을 때 쓰는 다음 홉 |
| longest-prefix match | 더 긴 prefix 규칙이 우선하는 원칙 |
| NAT | 사설 IP와 포트를 공인 IP와 포트로 변환하는 동작 |
| AS, BGP | 인터넷 전역에서 경로를 교환하는 단위와 프로토콜 |

## Before / After

**Before — "인터넷은 마법의 케이블"**

```text
패킷이 어떻게 거기까지 가는지 모른다
```

**After — "라우터가 협업하고 NAT가 다리를 놓는다"**

```text
hop 1 → hop 2 → ... → hop N
밖으로 나가는 것은 NAT가 자동으로 처리하지만,
밖에서 새로 들어오는 연결은 명시적 포트 포워딩이 필요하다
```

## 단계별로 따라하기

### 1단계: 라우팅 테이블 읽기

```bash
ip route
# default via 192.168.0.1 dev wlan0
# 10.0.0.0/8 via 10.0.1.1 dev tun0
# 192.168.0.0/24 dev wlan0 proto kernel scope link src 192.168.0.10
```

가장 긴 prefix가 이깁니다. 그래서 `192.168.0.0/24` 규칙은 default route보다 우선 적용됩니다.

### 2단계: `traceroute`로 중간 라우터 보기

```bash
traceroute 1.1.1.1
# 1  192.168.0.1   1 ms
# 2  isp-gw        5 ms
# 3  ...
# N  one.one.one.one  12 ms
```

출력의 각 줄이 다음 홉 라우터입니다.

### 3단계: 내 공인 IP 확인하기

```bash
curl -s ifconfig.me
# 203.0.113.5
```

내 장비는 `192.168.0.10` 같은 사설 IP를 쓰지만, 외부 세상은 다른 공인 IP를 봅니다. 그 중간 변환이 NAT입니다.

### 4단계: NAT 규칙 보기

```bash
sudo iptables -t nat -L -n -v
# Chain POSTROUTING (policy ACCEPT)
# MASQUERADE  all  --  192.168.0.0/24  0.0.0.0/0
```

`MASQUERADE`가 대표적인 source NAT 규칙입니다.

### 5단계: 정적 라우트 추가와 삭제 실험하기

```bash
# Send 192.168.50.0/24 through a specific gateway
sudo ip route add 192.168.50.0/24 via 192.168.0.254
ip route show
sudo ip route del 192.168.50.0/24
```

라우팅 테이블이 바뀌면 패킷의 목적지 처리 방식도 즉시 달라진다는 점을 직접 볼 수 있습니다.

## 6단계: longest-prefix와 NAT 상태를 함께 읽기

같은 증상처럼 보여도, 라우팅 오류와 NAT 오류는 출력 모양이 다릅니다.

| 관찰한 현상 | 먼저 의심할 것 | 왜 그렇게 보이는가 |
| --- | --- | --- |
| `ip route get 1.1.1.1`이 예상과 다른 인터페이스를 고름 | longest-prefix match 충돌 | 더 구체적인 prefix 규칙이 default route를 이겼기 때문입니다 |
| 내부에서 외부로는 연결되지만, 오래 idle 뒤 응답이 끊김 | NAT 세션 타임아웃 | 출발지 변환 상태가 사라져 돌아오는 패킷을 원래 호스트에 매핑하지 못합니다 |
| 특정 원격 대역만 VPN으로 가야 하는데 전부 로컬 게이트웨이로 나감 | 정적 라우트 누락 | 더 구체적인 기업망 prefix가 라우팅 테이블에 없기 때문입니다 |

```bash
ip route get 1.1.1.1
# 1.1.1.1 via 192.168.0.1 dev wlan0 src 192.168.0.10
```

이 명령은 "이 목적지로 지금 패킷을 보내면 어떤 인터페이스와 어떤 출발지 주소를 쓸까"를 바로 보여 줍니다. `traceroute`보다 앞에서, 운영 체제가 첫 번째 결정을 어떻게 내리는지 확인할 때 특히 유용합니다.

## 이 코드에서 먼저 볼 점

- 라우팅 결정은 매 홉마다 독립적으로 내려집니다.
- longest-prefix match가 기본 원칙입니다. 더 좁은 규칙이 default보다 우선합니다.
- NAT는 나가는 연결을 추적해 응답이 올바른 사설 IP로 돌아오게 합니다.
- 외부에서 시작되는 새 연결은 DNAT나 포트 포워딩 같은 추가 설정이 필요합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| NAT 뒤에서도 외부 인바운드가 자동으로 된다고 생각 | 연결 실패 | 포트 포워딩, reverse tunnel, public LB를 사용한다 |
| 회사와 집이 같은 사설 대역을 씀 | VPN 라우팅 충돌 | prefix를 분리한다 |
| `traceroute`의 빈 홉을 경로 단절로 단정 | 잘못된 진단 | `mtr`이나 TCP traceroute로 교차 확인한다 |
| longest-prefix match를 잊음 | 예상과 다른 경로 사용 | 더 구체적인 규칙이 우선함을 기억한다 |
| NAT 세션 타임아웃을 무시 | idle 연결이 끊김 | keepalive를 넣는다 |

## 실무에서는 이렇게 보입니다

- 클라우드 VPC는 subnet별 라우팅 테이블과 NAT gateway를 조합합니다.
- 컨테이너 네트워크는 `docker0`나 CNI를 통해 호스트 NAT 규칙을 사용합니다.
- VPN은 라우팅 테이블에 추가 경로를 주입합니다.
- 인터넷 백본은 BGP로 AS 간 경로를 협상합니다.
- 모바일과 IoT는 carrier-grade NAT 뒤에 있는 경우가 많습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 네트워크 사고가 나면 양 끝점의 라우팅 테이블, NAT 정책, 방화벽 규칙을 한꺼번에 펼쳐 봅니다. 패킷은 나가는데 응답이 안 돌아오는 문제는 대개 비대칭 라우팅이나 NAT 세션 만료에서 시작하기 때문입니다.

또한 IPv6와 NAT의 관계도 함께 생각합니다. IPv6는 주소 공간이 넓어 NAT가 기술적으로 필수가 아니므로, 공인 IP 부족을 전제로 한 운영 습관이 어떻게 달라질지까지 내다봅니다.

## 체크리스트

- [ ] 라우팅 테이블을 읽을 수 있다
- [ ] longest-prefix match를 설명할 수 있다
- [ ] NAT가 출발지 IP와 포트를 어떻게 바꾸는지 안다
- [ ] `traceroute`로 경로를 진단할 수 있다
- [ ] 외부 인바운드 연결에 왜 추가 설정이 필요한지 안다

## 연습 문제

1. 자신의 라우팅 테이블을 저장하고, default route와 가장 구체적인 규칙 하나를 설명해 보세요.
2. 같은 LAN에 있는 두 호스트와 다른 네트워크에 있는 호스트를 각각 `ping`, `traceroute` 해 보고, 라우터를 지났는지 판단해 보세요.
3. "회사에서는 SSH가 되는데 집에서는 안 되는 이유"를 NAT와 방화벽 관점에서 한 단락으로 설명해 보세요.

## 정리와 다음 글

라우터는 한 홉씩 경로를 결정하고, NAT는 사설 IP가 공인 인터넷과 통신할 수 있게 다리를 놓습니다. 이 둘을 이해하면 인터넷 동작의 상당 부분이 눈에 보이기 시작합니다.

다음 글에서는 그 경로 끝에서 자주 만나는 장치, Load Balancer를 다룹니다.

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

## 처음 질문으로 돌아가기

- **라우팅 테이블은 어떻게 읽어야 할까요?**
  - 본문의 기준은 라우팅과 NAT를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **default gateway와 longest-prefix match는 어떻게 동작할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **NAT는 출발지 IP와 포트를 어떻게 바꿀까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Networks 101 (1/10): 네트워크란 무엇인가?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP와 subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP와 UDP](./03-tcp-and-udp.md)
- [Computer Networks 101 (4/10): DNS](./04-dns.md)
- [Computer Networks 101 (5/10): HTTP와 HTTPS](./05-http-and-https.md)
- [Computer Networks 101 (6/10): TLS 기초](./06-tls-basics.md)
- **라우팅과 NAT (현재 글)**
- Load Balancer (예정)
- WebSocket과 실시간 통신 (예정)
- 네트워크 문제 디버깅 (예정)

<!-- toc:end -->

## 참고 자료

- [RFC 1631 — Network Address Translator](https://www.rfc-editor.org/rfc/rfc1631)
- [Cloudflare Learning — What is BGP?](https://www.cloudflare.com/learning/security/glossary/what-is-bgp/)
- [Linux ip-route(8) man page](https://man7.org/linux/man-pages/man8/ip-route.8.html)
- [Tanenbaum & Wetherall — Computer Networks](https://www.pearson.com/store/p/computer-networks/P100000875375)
- [RFC 4271 — Border Gateway Protocol 4 (BGP-4)](https://www.rfc-editor.org/rfc/rfc4271)

Tags: Computer Science, 네트워크, 라우팅, NAT, default gateway, 사설IP
