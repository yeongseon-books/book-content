---
series: computer-networks-101
episode: 7
title: 라우팅과 NAT
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
  - 라우팅
  - NAT
  - default gateway
  - 사설IP
seo_description: 패킷이 인터넷을 가로질러 가는 라우팅 원리와, 사설 네트워크가 공인 인터넷으로 나가는 NAT를 한 번에 정리합니다.
last_reviewed: '2026-05-11'
---

# 라우팅과 NAT

> Computer Networks 101 시리즈 (7/10)


## 이 글에서 다룰 문제

라우팅을 모르면 "왜 우리 회사에서만 안 되지?" 같은 질문에 답할 수 없습니다. NAT를 모르면 "왜 외부에서 우리 서버에 접속이 안 되지?", "왜 같은 회사 네트워크에서는 잘 되는데 집에서는 막히지?" 같은 사고가 미스터리로 남습니다. VPN, 컨테이너 네트워크, 클라우드 VPC도 결국 라우팅 + NAT 변형입니다.

> 라우터는 한 번에 한 홉만 봅니다. 인터넷은 그 작은 결정의 합입니다.

## 전체 흐름
```text
my laptop (192.168.0.10/24)
  └─ same /24? yes  → 직접 전송
  └─ same /24? no   → default gateway (192.168.0.1)
                        └─ ISP router → ... → destination AS
NAT는 발신지 (192.168.0.10:54321)을 (203.0.113.5:60000) 같은 공인 주소/포트로 바꿔 보냄
```

## Before / After

**Before — "인터넷은 마법 케이블":**

```text
패킷이 어떻게 도착하는지 모름
```

**After — "라우터들의 협업 + NAT":**

```text
hop 1 → hop 2 → ... → hop N
NAT는 outbound는 자동, inbound는 명시적 포트 포워딩 필요
```

## 단계별로 따라하기

### 1단계: 내 라우팅 테이블 보기

```bash
ip route
# 출력 예시: default via 192.168.0.1 dev wlan0
# 출력 예시: 10.0.0.0/8 via 10.0.1.1 dev tun0
# 출력 예시: 192.168.0.0/24 dev wlan0 proto kernel scope link src 192.168.0.10
```

가장 긴 prefix가 우선 — `192.168.0.0/24`가 default보다 우선 적용됩니다.

### 2단계: traceroute로 라우터들 보기

```bash
traceroute 1.1.1.1
# 1  192.168.0.1   1 ms
# 2  isp-gw        5 ms
# 3  ...
# 출력 예시: N  one.one.one.one  12 ms
```

각 줄이 다음 홉 라우터입니다.

### 3단계: 공인 IP 확인

```bash
curl -s ifconfig.me
# 203.0.113.5
```

내 사설 IP는 `192.168.0.10`인데 외부에서 보이는 IP는 다릅니다. 둘 사이의 변환이 NAT입니다.

### 4단계: NAT 확인 (Linux iptables)

```bash
sudo iptables -t nat -L -n -v
# 출력 예시: Chain POSTROUTING (policy ACCEPT)
# 출력 예시: MASQUERADE  all  --  192.168.0.0/24  0.0.0.0/0
```

`MASQUERADE`가 source NAT 규칙입니다.

### 5단계: 정적 라우트 추가/삭제 (실험용)

```bash
# 192.168.50.0/24를 특정 게이트웨이로 보내기
sudo ip route add 192.168.50.0/24 via 192.168.0.254
ip route show
sudo ip route del 192.168.50.0/24
```

라우팅 테이블이 즉시 반영되고 패킷의 행선지가 바뀌는 것을 직접 봅니다.

## 이 코드에서 주목할 점

- 라우팅 결정은 매 홉마다 독립적
- longest-prefix match가 우선 — 그래서 더 좁은 규칙이 default를 덮음
- NAT는 outbound 연결을 추적해 응답을 원래 사설 IP로 되돌림
- 외부에서 들어오는 새 연결은 명시적 포트 포워딩(DNAT)이 필요

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| NAT 뒤에서 외부 인바운드 가능하다고 가정 | 접속 실패 | 포트 포워딩, reverse tunnel, public LB |
| 회사·집 양쪽이 같은 사설 대역 | VPN 라우팅 충돌 | prefix 분리 |
| traceroute UDP/ICMP 차단으로 빈 줄 → 경로 끊겼다고 오해 | 잘못된 진단 | mtr, TCP traceroute 활용 |
| longest-prefix match를 모름 | "default로 가야 하는데?" | 더 좁은 규칙이 우선 |
| NAT 세션 타임아웃 무시 | 장시간 idle 연결 끊김 | keepalive 설정 |

## 실무에서는 이렇게 쓰입니다

- 클라우드 VPC: subnet별 라우팅 테이블 + NAT 게이트웨이
- 컨테이너: docker0/CNI가 호스트의 NAT 규칙으로 외부와 연결
- VPN: 추가 라우트가 라우팅 테이블에 삽입됨
- BGP: 인터넷 백본이 AS 간 경로를 협의
- IoT/모바일: 일반적으로 carrier-grade NAT 뒤

## 체크리스트

- [ ] 라우팅 테이블을 읽을 수 있다
- [ ] longest-prefix match를 안다
- [ ] NAT가 발신지 IP/포트를 어떻게 바꾸는지 안다
- [ ] traceroute로 경로를 진단할 수 있다
- [ ] 외부 인바운드 연결이 왜 추가 설정이 필요한지 안다

## 정리 및 다음 단계

라우터는 매 홉의 결정자이고, NAT는 사설 IP가 공인 인터넷으로 나가는 다리입니다. 둘만 잘 알아도 인터넷의 절반이 보입니다.

다음 글에서는 그 라우팅의 끝에 자주 만나는 장치 — Load Balancer로 넘어갑니다.

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
