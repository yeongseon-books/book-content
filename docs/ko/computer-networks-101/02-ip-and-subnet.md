---
series: computer-networks-101
episode: 2
title: IP와 subnet
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
  - IP
  - subnet
  - CIDR
  - 라우팅
seo_description: IP 주소가 무엇이고 subnet과 CIDR이 어떻게 네트워크를 분리하는지, 라우팅의 출발점이 되는 개념을 정리합니다.
last_reviewed: '2026-05-04'
---

# IP와 subnet

> Computer Networks 101 시리즈 (2/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: "IP 주소"는 단순히 컴퓨터 한 대에 붙은 번호일까요, 아니면 그 컴퓨터가 어느 동네에 사는지를 함께 말해 주는 좌표일까요?

> IP 주소는 두 부분으로 읽어야 합니다 — 어느 네트워크인지(network), 그 안의 몇 번째 호스트인지(host). 이 분할을 정해 주는 것이 subnet mask이고, 그것을 짧게 쓰는 표기가 CIDR입니다. 라우팅, NAT, 방화벽 규칙, 컨테이너 네트워크가 전부 이 분할 위에서 돌아갑니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- IPv4와 IPv6의 차이
- subnet mask와 CIDR 표기
- 네트워크 주소, 브로드캐스트 주소, 사용 가능한 호스트 수 계산
- 사설 IP와 공인 IP

## 왜 중요한가

IP 주소를 그냥 "컴퓨터 한 대의 번호"로 외우면 라우팅, NAT, 방화벽이 마술처럼 보입니다. 모든 네트워크 장비는 사실 IP를 "네트워크 부분"과 "호스트 부분"으로 잘라 보고, 네트워크 부분만으로 다음 행선지를 결정합니다. subnet을 읽지 못하면 클라우드 VPC, k8s 네트워크 정책, 회사 방화벽 규칙 모두 추측 게임이 됩니다.

> 라우터가 보는 것은 IP 주소가 아니라 IP 주소의 "네트워크 부분"입니다.

## 개념 한눈에 보기

> IP 주소는 32비트(IPv4) 또는 128비트(IPv6)의 숫자입니다. subnet mask는 어디까지가 네트워크이고 어디부터가 호스트인지 알려 주는 자입니다. CIDR(`/24`, `/16` 등)은 그 자의 길이를 비트 수로 적은 짧은 표기입니다.

```text
IP        : 192.168.10.42
CIDR      : 192.168.10.0/24
mask      : 255.255.255.0
network   : 192.168.10.0
broadcast : 192.168.10.255
hosts     : 192.168.10.1 ~ 192.168.10.254 (254개)
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| IPv4 / IPv6 | 32비트 / 128비트 주소 체계 |
| subnet mask | IP의 네트워크 부분과 호스트 부분을 가르는 비트 패턴 |
| CIDR | `192.168.10.0/24`처럼 prefix 길이로 적는 표기 |
| 네트워크 주소 | 호스트 비트가 모두 0인 주소 |
| 브로드캐스트 주소 | 호스트 비트가 모두 1인 주소(IPv4) |
| 사설 IP | 인터넷에서 라우팅되지 않는 대역(10/8, 172.16/12, 192.168/16) |

## Before / After

**Before — "IP는 그냥 번호":**

```text
"192.168.0.5는 내 노트북 번호" — 끝.
```

**After — "IP는 네트워크 + 호스트":**

```text
192.168.0.5/24
└─ network 192.168.0.0/24 의 host 5
같은 /24 안의 노드끼리는 라우터 없이 직접 통신
다른 네트워크로 가려면 라우터를 거친다
```

## 실습: 단계별로 따라하기

### 1단계: 내 IP 확인

```bash
ip addr show       # Linux
ifconfig           # macOS
ipconfig           # Windows
```

`inet 192.168.0.42/24` 같은 줄에서 IP와 prefix를 함께 확인합니다.

### 2단계: 라우팅 테이블 보기

```bash
ip route
# default via 192.168.0.1 dev wlan0
# 192.168.0.0/24 dev wlan0 proto kernel scope link src 192.168.0.42
```

같은 `/24` 안의 목적지는 직접, 그 외는 모두 default gateway(192.168.0.1)로 보낸다는 뜻입니다.

### 3단계: subnet 계산을 코드로

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

### 4단계: 같은 subnet 여부 판정

```python
import ipaddress

a = ipaddress.ip_address('192.168.10.42')
b = ipaddress.ip_address('192.168.10.99')
c = ipaddress.ip_address('192.168.20.1')
net = ipaddress.ip_network('192.168.10.0/24')

print(a in net, b in net, c in net)   # True True False
```

같은 subnet이면 라우터 없이 통신, 아니면 라우터를 거쳐야 합니다.

### 5단계: 사설/공인 IP 구분

```python
import ipaddress

for s in ['10.0.0.5', '172.16.3.4', '192.168.1.1', '8.8.8.8']:
    ip = ipaddress.ip_address(s)
    print(s, 'private' if ip.is_private else 'public')
```

집/회사 안의 단말은 대부분 사설 IP를 쓰고, NAT(7편)을 통해 인터넷으로 나갑니다.

## 이 코드에서 주목할 점

- `ip_network`는 네트워크 단위, `ip_interface`는 "IP + prefix" 한 호스트 단위
- prefix 길이는 단순히 표기 편의가 아니라 라우팅의 기본 단위
- 사설/공인 구분은 `ipaddress` 모듈이 표준으로 제공
- 같은 subnet인지 여부가 곧 "라우터 없이 가는가?"의 답

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| `/24`를 항상 가정 | VPC, k8s에서 충돌 | prefix 길이를 명시 |
| 네트워크/브로드캐스트 주소를 호스트로 사용 | 통신 실패 | `hosts()`로만 사용 가능 IP 추출 |
| 사설 IP를 공인 인터넷에 노출 가능하다고 오해 | 보안/연결 오류 | NAT 또는 공인 IP 필요 |
| IPv4만 고려한 코드 | 듀얼 스택 환경에서 실패 | `ip_address`로 추상화 |
| subnet을 단순 그룹화 도구로 오해 | 라우팅, 보안 정책 무시 | subnet은 라우팅의 기본 |

## 실무에서는 이렇게 쓰입니다

- AWS VPC: `/16` VPC 안에 `/24` subnet 여러 개를 AZ별로 분리
- Kubernetes: pod CIDR, service CIDR이 모두 별도 prefix
- 방화벽: "10.0.0.0/8에서 오는 트래픽 허용" 같은 규칙
- VPN: 회사 사설 대역과 충돌하지 않도록 prefix 설계
- 게임 서버: 같은 subnet의 인접 서버끼리 빠른 내부 통신

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새 인프라를 설계하기 전에 "IP plan"을 먼저 그립니다. 어떤 prefix를 어디에 할당하고, 회사 다른 네트워크와 충돌은 없는지, 향후 N년 동안 호스트 수가 충분한지를 계산합니다. prefix 선택은 한 번 굳어지면 바꾸기가 매우 어렵기 때문입니다.

또한 시니어는 "왜 안 되지?"라는 질문을 들으면 가장 먼저 양쪽의 IP와 subnet, 라우팅 테이블, 방화벽 규칙을 같이 봅니다. 응용 코드 디버깅 전에 네트워크 토폴로지를 머리에 그려야 한다는 사실을 잘 알고 있기 때문입니다.

## 체크리스트

- [ ] CIDR `/24`, `/16`, `/8`이 무엇을 의미하는지 안다
- [ ] 네트워크 주소와 브로드캐스트 주소를 계산할 수 있다
- [ ] 같은 subnet인지 여부를 판단할 수 있다
- [ ] 사설/공인 IP 대역을 안다
- [ ] 새 시스템을 그릴 때 IP plan을 먼저 그린다

## 연습 문제

1. `10.20.0.0/22`의 네트워크 주소, 브로드캐스트 주소, 사용 가능한 호스트 수를 계산하세요.

2. 두 IP `172.16.5.10`와 `172.16.5.130`이 `/25`에서 같은 subnet인지 판정하세요.

3. 회사가 `/16`을 사용한다고 가정하고, 5개 팀에 각각 `/20`을 할당하는 plan을 그리세요.

## 정리 및 다음 단계

IP 주소는 한 컴퓨터의 좌표가 아니라 "어느 네트워크의 몇 번째 호스트"입니다. subnet과 CIDR은 그 분할을 정하는 도구이고, 라우팅·NAT·방화벽·VPC가 모두 이 분할 위에서 돌아갑니다.

다음 글에서는 IP 위에서 동작하는 두 가지 전송 프로토콜 — TCP와 UDP를 비교합니다.

<!-- toc:begin -->
- [네트워크란 무엇인가?](./01-what-is-a-network.md)
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
