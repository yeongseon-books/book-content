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


![Computer Networks 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/02/02-01-concept-at-a-glance.ko.png)
*Computer Networks 101 2장 흐름 개요*

## 먼저 던지는 질문

- IPv4와 IPv6는 어떤 차이를 가질까요?
- subnet mask와 CIDR 표기는 무엇을 나눠서 보여 줄까요?
- 네트워크 주소, 브로드캐스트 주소, 사용 가능한 호스트 수는 어떻게 계산할까요?

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
| 게이트웨이 | 다른 네트워크로 나가는 출구 라우터 |
| VLSM | Variable Length Subnet Masking, 서로 다른 크기의 subnet을 만드는 기법 |

## IPv4 주소의 구조

IPv4 주소는 32비트 이진수입니다. 사람이 읽기 쉽도록 8비트씩 끊어 10진수로 표기합니다.

```text
IP 주소:   192.168.10.42
이진 표현:  11000000.10101000.00001010.00101010
           ├── 네트워크 부분 ──┤├─ 호스트 ─┤   (/24일 때)

subnet mask: 255.255.255.0
이진 표현:   11111111.11111111.11111111.00000000
             1이 연속된 구간 = 네트워크 부분 (24비트)
             0이 연속된 구간 = 호스트 부분 (8비트)
```

subnet mask를 IP 주소에 AND 연산하면 네트워크 주소가 나옵니다:

```text
  11000000.10101000.00001010.00101010   (192.168.10.42)
& 11111111.11111111.11111111.00000000   (255.255.255.0)
= 11000000.10101000.00001010.00000000   (192.168.10.0) ← 네트워크 주소
```

## 적용 전후 비교
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
# Linux
ip addr show
# 출력 예:
# 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
#     inet 192.168.0.42/24 brd 192.168.0.255 scope global eth0

# macOS
ifconfig en0
# 출력 예:
# inet 192.168.0.42 netmask 0xffffff00 broadcast 192.168.0.255

# Windows
ipconfig
# 출력 예:
# IPv4 Address. . . . . . . . . : 192.168.0.42
# Subnet Mask . . . . . . . . . : 255.255.255.0
# Default Gateway . . . . . . . : 192.168.0.1
```

`inet 192.168.0.42/24` 같은 줄에서 IP 주소와 prefix 길이를 함께 볼 수 있습니다. Linux의 `brd 192.168.0.255`는 브로드캐스트 주소를 보여줍니다.

### 2단계: 라우팅 테이블 읽기

```bash
ip route
# default via 192.168.0.1 dev wlan0 proto dhcp metric 600
# 192.168.0.0/24 dev wlan0 proto kernel scope link src 192.168.0.42
# 172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1
```

이 출력을 한 줄씩 읽으면:

| 규칙 | 의미 |
| --- | --- |
| `default via 192.168.0.1` | 위 규칙에 안 맞는 모든 패킷은 192.168.0.1로 보냄 |
| `192.168.0.0/24 dev wlan0` | 이 subnet은 wlan0으로 직접 전달 |
| `172.17.0.0/16 dev docker0` | Docker 컨테이너용 subnet은 docker0 브리지로 전달 |

같은 `/24` 안의 목적지는 직접 보내고, 그 밖의 목적지는 기본 게이트웨이인 `192.168.0.1`로 보냅니다. 라우터는 이 과정을 재귀적으로 반복합니다.

### 3단계: 코드로 subnet 계산하기

```python
import ipaddress

net = ipaddress.ip_network('192.168.10.0/24')
print(f"네트워크 주소:     {net.network_address}")     # 192.168.10.0
print(f"브로드캐스트 주소: {net.broadcast_address}")    # 192.168.10.255
print(f"전체 주소 수:      {net.num_addresses}")        # 256
print(f"사용 가능 호스트:  {net.num_addresses - 2}")    # 254
print(f"첫 호스트:         {list(net.hosts())[0]}")     # 192.168.10.1
print(f"마지막 호스트:     {list(net.hosts())[-1]}")    # 192.168.10.254
print(f"subnet mask:       {net.netmask}")             # 255.255.255.0
```

주의: `num_addresses`는 네트워크 주소와 브로드캐스트 주소를 포함합니다. 실제 호스트에 할당할 수 있는 수는 항상 2개 적습니다.

### 4단계: 같은 subnet인지 판정하기

```python
import ipaddress

a = ipaddress.ip_address('192.168.10.42')
b = ipaddress.ip_address('192.168.10.99')
c = ipaddress.ip_address('192.168.20.1')
net = ipaddress.ip_network('192.168.10.0/24')

print(a in net, b in net, c in net)   # True True False
```

같은 subnet이면 라우터 없이 직접 전달(ARP로 MAC 주소를 찾아 프레임을 보냄)되고, 다른 subnet이면 게이트웨이 라우터를 거쳐야 합니다.

### 5단계: 사설 IP와 공인 IP 구분하기

```python
import ipaddress

for s in ['10.0.0.5', '172.16.3.4', '192.168.1.1', '8.8.8.8', '100.64.0.1']:
    ip = ipaddress.ip_address(s)
    print(f"{s:15s} → {'private' if ip.is_private else 'public'}")
```

RFC 1918에서 정의한 사설 대역:

| 대역 | CIDR | 주소 수 |
| --- | --- | --- |
| 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 | 16,777,216 |
| 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 | 1,048,576 |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | 65,536 |

가정과 사무실의 장비는 대체로 사설 IP를 쓰고, 인터넷으로 나갈 때는 NAT를 거칩니다. 100.64.0.0/10은 CGN(Carrier-Grade NAT) 용도의 공유 주소 공간으로, 사설도 공인도 아닌 특수 대역입니다.

## subnet 계산 실전 연습

subnet 계산은 시험 문제가 아니라 VPC 설계, 방화벽 규칙, IP 계획의 기초입니다.

### /24보다 큰 subnet

```text
192.168.10.0/22  →  호스트 비트 = 32 - 22 = 10비트

네트워크 주소:      192.168.10.0
                    11000000.10101000.000010|10.00000000
                                           └ 여기부터 호스트 (10비트)

브로드캐스트 주소:  192.168.11.255
                    11000000.10101000.000010|11.11111111

전체 주소 수:       2^10 = 1024
사용 가능 호스트:   1022
범위:              192.168.10.1 ~ 192.168.11.254
```

### /24보다 작은 subnet (VLSM)

```text
192.168.10.0/26  →  호스트 비트 = 32 - 26 = 6비트

네트워크 주소:      192.168.10.0
브로드캐스트 주소:  192.168.10.63
사용 가능 호스트:   62

다음 /26 subnet:   192.168.10.64/26 (호스트 64~127)
그 다음:           192.168.10.128/26 (호스트 128~191)
마지막:            192.168.10.192/26 (호스트 192~255)
```

하나의 /24를 4개의 /26으로 나누면 각각 62대의 호스트를 수용할 수 있습니다.

### 빠른 계산 참조표

| prefix | 호스트 비트 | 주소 수 | 사용 가능 호스트 |
| --- | --- | --- | --- |
| /8 | 24 | 16,777,216 | 16,777,214 |
| /16 | 16 | 65,536 | 65,534 |
| /20 | 12 | 4,096 | 4,094 |
| /22 | 10 | 1,024 | 1,022 |
| /24 | 8 | 256 | 254 |
| /25 | 7 | 128 | 126 |
| /26 | 6 | 64 | 62 |
| /27 | 5 | 32 | 30 |
| /28 | 4 | 16 | 14 |
| /30 | 2 | 4 | 2 |
| /32 | 0 | 1 | 1 (단일 호스트) |

/30은 point-to-point 링크(라우터 간 연결)에 자주 쓰입니다. /32는 loopback이나 호스트 라우트에 사용됩니다.

## IPv4 vs IPv6

| 항목 | IPv4 | IPv6 |
| --- | --- | --- |
| 주소 길이 | 32비트 | 128비트 |
| 표기법 | 10진수 점 구분 (192.168.1.1) | 16진수 콜론 구분 (2001:db8::1) |
| 주소 수 | ~43억 | ~340간(3.4×10^38) |
| 헤더 크기 | 20-60바이트 (가변) | 40바이트 (고정) |
| 브로드캐스트 | 있음 | 없음 (멀티캐스트로 대체) |
| NAT 필요성 | 필수 (주소 부족) | 불필요 (주소 풍부) |
| 자동 설정 | DHCP | SLAAC + DHCPv6 |
| 체크섬 | 헤더에 포함 | 없음 (상위 계층에 위임) |

```bash
# IPv6 주소 확인
ip -6 addr show
# 출력 예:
# inet6 fe80::1a2b:3c4d:5e6f:7890/64 scope link
# inet6 2001:db8:1::42/64 scope global

# IPv6로 ping
ping6 -c 3 2001:db8::1
```

IPv6가 NAT 없이 동작하는 이유는 주소 공간이 충분하기 때문입니다. 하지만 현실에서는 IPv4와 IPv6가 공존하는 듀얼 스택 환경이 대부분이므로, 둘 다 이해해야 합니다.

## 이 코드에서 먼저 볼 점

- `ip_network`는 네트워크 단위이고, `ip_interface`는 "호스트 IP + prefix" 단위입니다.
- prefix 길이는 단순한 축약 표기가 아니라 라우팅의 기본 단위입니다.
- 사설/공인 여부는 `ipaddress` 모듈이 직접 판단해 줍니다.
- "같은 subnet인가"는 곧 "라우터 없이 갈 수 있는가"와 같은 질문입니다.
- subnet mask와 IP의 AND 연산이 라우터의 핵심 판단 로직입니다.

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
- Kubernetes는 pod CIDR과 service CIDR을 별도 prefix로 가집니다. 예: pod `10.244.0.0/16`, service `10.96.0.0/12`.
- 방화벽은 `10.0.0.0/8`처럼 prefix 단위로 규칙을 씁니다. 개별 IP보다 prefix로 묶어야 규칙 수가 관리 가능합니다.
- VPN은 다른 조직의 사설 대역과 충돌하지 않도록 prefix를 미리 설계해야 합니다. 양쪽 모두 `10.0.0.0/24`를 쓰면 라우팅이 모호해집니다.
- 게임 서버처럼 인접한 장비끼리 빠른 내부 통신이 필요한 경우에도 subnet 설계가 중요합니다.

```text
[실무 VPC 설계 예시 — AWS]

VPC: 10.0.0.0/16 (65,534 hosts)
├── public-subnet-az-a:  10.0.0.0/24   (웹 서버, ALB)
├── public-subnet-az-b:  10.0.1.0/24   (웹 서버, ALB)
├── private-subnet-az-a: 10.0.10.0/24  (앱 서버)
├── private-subnet-az-b: 10.0.11.0/24  (앱 서버)
├── db-subnet-az-a:      10.0.20.0/24  (RDS)
├── db-subnet-az-b:      10.0.21.0/24  (RDS)
└── reserved:            10.0.100.0/22 (향후 확장용)
```

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새 인프라를 설계할 때 가장 먼저 IP 계획부터 그립니다. 어느 prefix를 어디에 줄지, 다른 조직 네트워크와 충돌하지 않는지, 앞으로 몇 년 동안 호스트 수가 충분한지부터 봅니다. prefix 결정은 한 번 굳어지면 되돌리기 매우 어렵기 때문입니다.

또한 "왜 이 연결이 안 되지"라는 질문을 받으면 양 끝점의 IP, subnet, 라우팅 테이블, 방화벽 규칙을 먼저 함께 봅니다. 애플리케이션 디버깅보다 먼저 네트워크 지형도를 머릿속에 세웁니다.

IP 계획에서 자주 쓰는 원칙:
- 팀별로 /20 이상을 통째로 할당해 향후 확장에 대비합니다.
- public subnet과 private subnet을 주소 범위로 명확히 구분합니다.
- 번호 체계에 의미를 부여합니다(예: 10.{환경}.{서비스}.{호스트}).
- 문서화를 반드시 병행합니다. IP 계획은 코드보다 오래 살아남습니다.

## IP 주소 고갈과 NAT의 등장

IPv4 주소는 약 43억 개입니다. 1980년대에 인터넷을 설계할 때는 충분해 보였지만, 2011년 IANA의 마지막 /8 블록이 배분되면서 공식적으로 고갈되었습니다.

주소 고갈에 대응하는 방법은 크게 세 가지입니다:

1. **NAT (Network Address Translation)**: 사설 IP를 공인 IP로 변환해 여러 장비가 하나의 공인 IP를 공유합니다. 가정용 공유기가 하는 일이 바로 이것입니다.
2. **CIDR**: 클래스 기반 할당(A/B/C)을 폐지하고 prefix 단위로 유연하게 할당합니다.
3. **IPv6 전환**: 근본적 해결책이지만 전환 비용이 커서 아직 완료되지 않았습니다.

```text
NAT 동작 예시:

[PC-A 10.0.0.2:50001] ─┐
[PC-B 10.0.0.3:50002] ─┼─→ [NAT Router] ─→ [Internet]
[PC-C 10.0.0.4:50003] ─┘    203.0.113.1:10001~10003

내부 사설 IP:port  →  외부 공인 IP:port (변환 테이블 관리)
```

NAT 덕분에 하나의 공인 IP로 수백 대의 장비가 인터넷을 사용할 수 있습니다. 하지만 NAT는 양방향 연결을 어렵게 만들고, P2P 통신이나 VoIP에서 추가 기술(STUN, TURN)이 필요해지는 원인이기도 합니다.

## 특수 목적 IP 대역

인터넷에는 일반 통신에 사용하지 않는 특수 대역이 여러 개 있습니다.

| 대역 | 용도 |
| --- | --- |
| 0.0.0.0/8 | 현재 네트워크 (소스로만 사용) |
| 127.0.0.0/8 | 루프백 (자기 자신) |
| 169.254.0.0/16 | 링크-로컬 (DHCP 실패 시 자동 할당) |
| 224.0.0.0/4 | 멀티캐스트 |
| 255.255.255.255/32 | 제한 브로드캐스트 |
| 100.64.0.0/10 | CGN 공유 주소 (ISP 내부) |

운영 중에 `169.254.x.x` 주소가 보이면 DHCP 서버 연결에 실패했다는 신호입니다. 이 주소로는 같은 링크 안의 장비끼리만 통신할 수 있고, 라우터를 넘을 수 없습니다.

## subnet 설계 실전 시나리오

스타트업이 AWS에서 인프라를 시작한다고 가정합니다. 현재 엔지니어 5명, 서버 20대이지만 2년 내 10배 성장을 예상합니다.

```text
설계 원칙:
1. VPC는 /16 (65,534 호스트) — 확장 여유 확보
2. 환경별 분리: prod, staging, dev → 각각 /18 이상
3. AZ별 분리: 각 환경을 2개 AZ에 나눔
4. 역할별 분리: public, private, DB, cache

결과:
VPC: 10.0.0.0/16

prod  (10.0.0.0/18)
├── public-az-a:  10.0.0.0/24   (ALB, Bastion)
├── public-az-b:  10.0.1.0/24
├── app-az-a:     10.0.10.0/24  (ECS/EKS)
├── app-az-b:     10.0.11.0/24
├── db-az-a:      10.0.20.0/24  (RDS)
└── db-az-b:      10.0.21.0/24

staging (10.0.64.0/18)
├── public-az-a:  10.0.64.0/24
├── app-az-a:     10.0.74.0/24
└── db-az-a:      10.0.84.0/24

dev (10.0.128.0/18)
└── (단일 AZ로 비용 절약)

reserved: 10.0.192.0/18 (향후 새 환경용)
```

이렇게 설계하면 환경 간 subnet이 절대 겹치지 않고, VPN으로 다른 VPC와 연결해도 충돌이 없습니다. prefix를 넉넉하게 잡는 것이 핵심입니다. 나중에 subnet을 넓히는 것은 불가능하지만, 처음부터 크게 잡아두면 사용하지 않는 주소는 비용이 들지 않습니다. 이 원칙은 AWS뿐 아니라 GCP, Azure, 온프레미스 환경 모두에 동일하게 적용됩니다.


## 심화: IP 관련 진단 명령 모음

### ARP 테이블 확인

같은 subnet 내 통신이 안 될 때, ARP 캐시를 확인하면 MAC 주소 해석 문제를 찾을 수 있습니다.

```bash
# ARP 캐시 보기
ip neigh show
# 192.168.0.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE
# 192.168.0.100 dev eth0 FAILED    ← MAC 해석 실패 = 대상 down 또는 subnet 불일치

# ARP 캐시 비우기 (재해석 강제)
sudo ip neigh flush dev eth0
```

### IP 충돌 탐지

같은 subnet에서 두 장비가 같은 IP를 사용하면 간헐적 연결 장애가 발생합니다.

```bash
# arping으로 중복 IP 확인
arping -D -I eth0 192.168.0.42
# 응답이 오면 충돌 존재
```

### tcpdump로 IP 계층 문제 진단

```bash
# 특정 subnet의 트래픽만 캡처
sudo tcpdump -i eth0 -nn 'net 192.168.10.0/24'

# ARP 요청/응답만 보기
sudo tcpdump -i eth0 -nn arp

# ICMP (ping) 트래픽만 보기
sudo tcpdump -i eth0 -nn icmp
```

### Longest Prefix Match — 라우터의 핵심 알고리즘

라우터는 라우팅 테이블에 여러 prefix가 있을 때, 목적지 IP와 가장 길게 일치하는 prefix를 선택합니다. 이것을 Longest Prefix Match라 합니다.

```text
라우팅 테이블:
  10.0.0.0/8      → gateway A
  10.0.10.0/24    → gateway B
  10.0.10.128/25  → gateway C
  0.0.0.0/0       → gateway D (default)

목적지: 10.0.10.200
  /8  일치 (10.*)
  /24 일치 (10.0.10.*)
  /25 일치? 10.0.10.128~255 → 200은 해당 → 일치!
  → 가장 긴 /25를 선택 → gateway C로 전달

목적지: 10.0.10.50
  /25 일치? 10.0.10.0~127 → 아님 (128~255만 해당)
  /24 일치 → gateway B로 전달
```

이 원리를 알면 방화벽 규칙이나 VPC 라우팅에서 "왜 이 규칙이 저 규칙보다 우선하는가"를 이해할 수 있습니다. 더 구체적인 prefix가 항상 이깁니다.

### IP 통신 문제의 계층별 진단 절차

```text
1. ip addr show → IP/prefix가 올바른가?
   └─ subnet 불일치 → 통신 불가

2. ip route → default gateway가 있는가?
   └─ gateway 없음 → 외부 통신 불가

3. ping gateway → gateway에 도달하는가?
   └─ 실패 → 링크/스위치 문제

4. ping 외부 IP (8.8.8.8) → 라우팅 동작하는가?
   └─ 실패 → ISP/방화벽 문제

5. nslookup example.com → DNS 해석 되는가?
   └─ 실패 → DNS 설정 문제 (→ 4편에서 상세)
```


이 순서로 아래에서 위로 올라가면, IP/subnet 계층의 문제를 애플리케이션 계층과 혼동하지 않고 빠르게 식별할 수 있습니다. 실무에서는 이 5단계를 30초 안에 실행할 수 있도록 스크립트화해 두는 팀이 많습니다.

### Python으로 subnet 분할 자동화

```python
import ipaddress

# /16을 /24로 나누기
parent = ipaddress.ip_network('10.0.0.0/16')
subnets_24 = list(parent.subnets(new_prefix=24))
print(f"/16을 /24로 나누면: {len(subnets_24)}개")  # 256개
print(f"첫 subnet: {subnets_24[0]}")               # 10.0.0.0/24
print(f"마지막:    {subnets_24[-1]}")               # 10.0.255.0/24

# 두 subnet이 겹치는지 확인
a = ipaddress.ip_network('10.0.0.0/22')
b = ipaddress.ip_network('10.0.2.0/24')
print(f"겹침: {a.overlaps(b)}")  # True — b는 a의 부분집합
```

## 체크리스트

- [ ] CIDR `/24`, `/16`, `/8`이 뜻하는 범위를 안다
- [ ] subnet mask를 이진수로 변환해 AND 연산을 수행할 수 있다
- [ ] 네트워크 주소와 브로드캐스트 주소를 계산할 수 있다
- [ ] 두 IP가 같은 subnet인지 판단할 수 있다
- [ ] 사설 IP와 공인 IP 대역을 안다
- [ ] IPv4와 IPv6의 핵심 차이를 설명할 수 있다
- [ ] 라우팅 테이블을 읽고 패킷의 다음 홉을 판단할 수 있다
- [ ] 새 시스템을 설계할 때 IP 계획부터 그린다

## 연습 문제

1. `10.20.0.0/22`의 네트워크 주소, 브로드캐스트 주소, 사용 가능한 호스트 수를 계산해 보세요.
2. `172.16.5.10`과 `172.16.5.130`이 같은 `/25` subnet에 있는지 판단해 보세요.
3. 회사가 `/16` 대역 하나를 갖고 있다고 가정하고, 다섯 팀에 각각 `/20`을 배정하는 계획을 그려 보세요.
4. `ip route` 출력을 보고, 목적지 `8.8.8.8`로 가는 패킷이 어떤 규칙에 매칭되는지 설명해 보세요.
5. IPv6 주소 `2001:db8:abcd:0012::1/64`에서 네트워크 부분과 인터페이스 ID를 분리해 보세요.

## 정리와 다음 글

IP 주소는 한 컴퓨터의 번호가 아니라 "어느 네트워크의 몇 번째 호스트인가"를 함께 담은 좌표입니다. subnet과 CIDR은 그 경계를 정의하고, 라우팅, NAT, 방화벽, VPC는 모두 그 위에서 동작합니다. subnet mask의 AND 연산 한 번이 라우터의 가장 기본적인 판단이라는 점을 기억하면, 이후의 라우팅과 NAT도 자연스럽게 이어집니다.

다음 글에서는 IP 위에서 동작하는 두 전송 프로토콜, TCP와 UDP를 비교합니다.

## 처음 질문으로 돌아가기

- **IPv4와 IPv6는 어떤 차이를 가질까요?**
  - IPv4는 32비트(약 43억 개)로 주소가 부족해 NAT가 필수이고, IPv6는 128비트로 사실상 무한한 주소 공간을 제공해 NAT 없이 엔드투엔드 통신이 가능합니다. 헤더 구조도 IPv6가 더 단순(고정 40바이트)하며, 브로드캐스트 대신 멀티캐스트를 사용합니다.
- **subnet mask와 CIDR 표기는 무엇을 나눠서 보여 줄까요?**
  - 32비트 IP 주소에서 어디까지가 "네트워크를 식별하는 부분"이고 어디부터가 "그 네트워크 안의 호스트를 식별하는 부분"인지를 나눕니다. /24는 상위 24비트가 네트워크, 하위 8비트가 호스트라는 뜻입니다. 라우터는 이 경계를 기준으로 "같은 네트워크인지, 다른 네트워크로 포워딩해야 하는지"를 판단합니다.
- **네트워크 주소, 브로드캐스트 주소, 사용 가능한 호스트 수는 어떻게 계산할까요?**
  - 호스트 비트를 모두 0으로 두면 네트워크 주소, 모두 1로 두면 브로드캐스트 주소입니다. 사용 가능한 호스트 수는 2^(호스트 비트 수) - 2입니다. 예를 들어 /24는 호스트 비트가 8개이므로 2^8 - 2 = 254대를 수용합니다.

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
- [RFC 1918 — Private Address Space](https://www.rfc-editor.org/rfc/rfc1918)
- [Python `ipaddress` 모듈 문서](https://docs.python.org/3/library/ipaddress.html)
- [Cloudflare Learning — What is an IP address?](https://www.cloudflare.com/learning/dns/glossary/what-is-my-ip-address/)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, IP, subnet, CIDR, 라우팅
