---
series: computer-networks-101
episode: 7
title: 라우팅과 NAT
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
  - 라우팅
  - NAT
  - default gateway
  - 사설IP
seo_description: 라우팅 테이블과 NAT가 패킷 이동을 어떻게 결정하는지 설명합니다.
last_reviewed: '2026-05-12'
---

# 라우팅과 NAT

이 글은 Computer Networks 101 시리즈의 7번째 글입니다.

## 이 글에서 다룰 문제

- 라우팅 테이블은 어떻게 읽어야 할까요?
- default gateway와 longest-prefix match는 어떻게 동작할까요?
- NAT는 출발지 IP와 포트를 어떻게 바꿀까요?
- AS와 BGP는 인터넷 규모에서 어떤 역할을 할까요?

> 라우터는 패킷마다 다음 홉 하나만 결정합니다. 라우팅 테이블은 그 결정을 위한 규칙집입니다. 사설 IP에서 공인 인터넷으로 나갈 때는 NAT가 출발지 IP와 포트를 라우터의 공인 주소로 바꿉니다. 인터넷의 절반은 라우팅이고, 나머지 절반은 NAT라고 생각해도 크게 틀리지 않습니다.

## 왜 중요한가

라우팅을 모르면 "왜 회사 네트워크에서만 안 되지?"라는 질문에 답하기 어렵습니다. NAT를 모르면 "왜 집에서는 안 되고 사무실에서는 되지?", "왜 외부에서 우리 서버로 바로 못 들어오지?" 같은 문제가 설명되지 않습니다. VPN, 컨테이너 네트워크, 클라우드 VPC 역시 결국 라우팅과 NAT의 변형입니다.

> 라우터는 전체 경로를 한 번에 아는 것이 아니라, 그 순간 필요한 다음 홉만 봅니다. 인터넷은 그 작은 결정들의 합입니다.

## 핵심 그림

```text
my laptop (192.168.0.10/24)
  └─ same /24? yes  → direct delivery
  └─ same /24? no   → default gateway (192.168.0.1)
                        └─ ISP router → ... → destination AS
NAT rewrites source (192.168.0.10:54321) to (203.0.113.5:60000)
```

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

<!-- toc:begin -->
- [네트워크란 무엇인가?](./01-what-is-a-network.md)
- [IP와 subnet](./02-ip-and-subnet.md)
- [TCP와 UDP](./03-tcp-and-udp.md)
- [DNS](./04-dns.md)
- [HTTP와 HTTPS](./05-http-and-https.md)
- [TLS 기초](./06-tls-basics.md)
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

Tags: Computer Science, 네트워크, 라우팅, NAT, default gateway, 사설IP
