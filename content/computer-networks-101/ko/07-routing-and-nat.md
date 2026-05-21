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

```text
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌─────────────┐
│ 호스트 A     │────▶│ 라우터 1  │────▶│ 라우터 2  │────▶│ 호스트 B     │
│192.168.0.10 │     │(GW)      │     │(ISP)     │     │93.184.216.34│
└─────────────┘     └──────────┘     └──────────┘     └─────────────┘
       │                  │                                    ▲
       │   src 변환       │                                    │
       ▼                  ▼                                    │
  사설 IP 출발      NAT: 192.168.0.10:54321                    │
                   → 203.0.113.5:30001                         │
                         │                                     │
                         └─────────────────────────────────────┘
                              응답: dst 203.0.113.5:30001
                              → 역변환 → 192.168.0.10:54321
```

패킷은 호스트 A에서 출발할 때 사설 IP를 달고 있습니다. 첫 번째 라우터(default gateway)가 NAT를 수행해 공인 IP로 바꾸고, 이후 라우터들은 공인 IP 기준으로 다음 홉을 결정합니다. 응답이 돌아올 때는 NAT 테이블을 역으로 참조해 원래 사설 IP로 되돌립니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 라우팅 테이블 | "이 prefix는 이 인터페이스/다음 홉으로"라는 매핑 |
| default gateway | 더 구체적인 규칙이 없을 때 쓰는 다음 홉 |
| longest-prefix match | 더 긴 prefix 규칙이 우선하는 원칙 |
| NAT | 사설 IP와 포트를 공인 IP와 포트로 변환하는 동작 |
| SNAT (Source NAT) | 출발지 주소를 변환 — 내부에서 외부로 나갈 때 |
| DNAT (Destination NAT) | 목적지 주소를 변환 — 외부에서 내부로 들어올 때 |
| conntrack | Linux 커널의 연결 추적 테이블, NAT 상태를 유지 |
| AS, BGP | 인터넷 전역에서 경로를 교환하는 단위와 프로토콜 |
| metric | 같은 목적지에 여러 경로가 있을 때 우선순위를 결정하는 비용 값 |

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
# default via 192.168.0.1 dev wlan0  proto dhcp  metric 600
# 10.0.0.0/8 via 10.0.1.1 dev tun0  metric 50
# 172.17.0.0/16 dev docker0  proto kernel  scope link  src 172.17.0.1
# 192.168.0.0/24 dev wlan0  proto kernel  scope link  src 192.168.0.10
```

각 줄이 하나의 라우팅 규칙입니다. 읽는 방법은 다음과 같습니다.

| 필드 | 의미 | 위 예시에서 |
| --- | --- | --- |
| destination prefix | 이 대역에 해당하는 패킷을 | `10.0.0.0/8` |
| via | 이 다음 홉으로 보내라 | `10.0.1.1` |
| dev | 이 인터페이스를 통해 | `tun0` |
| metric | 비용(낮을수록 우선) | `50` |
| proto | 이 규칙을 누가 만들었나 | `kernel`, `dhcp` |

가장 긴 prefix가 이깁니다. `192.168.0.0/24` 규칙은 `/24`가 `/0`(default)보다 구체적이므로 해당 대역 패킷에 대해 default route보다 우선 적용됩니다.

### 2단계: longest-prefix match 동작 원리

목적지 IP가 `10.0.5.3`인 패킷이 있다고 합시다. 라우팅 테이블에 다음 규칙이 있습니다.

```text
10.0.0.0/8      via 10.0.1.1   dev tun0     metric 50
10.0.5.0/24     via 10.0.5.1   dev eth1     metric 100
0.0.0.0/0       via 192.168.0.1 dev wlan0   metric 600
```

매칭 과정:

1. `10.0.5.3`은 `10.0.5.0/24`에 속합니다 → prefix 길이 24
2. `10.0.5.3`은 `10.0.0.0/8`에도 속합니다 → prefix 길이 8
3. `10.0.5.3`은 `0.0.0.0/0`에도 속합니다 → prefix 길이 0

가장 긴 prefix인 `/24` 규칙이 선택됩니다. metric은 같은 prefix 길이의 규칙이 여러 개일 때만 비교합니다.

```bash
# 특정 목적지에 어떤 규칙이 적용되는지 확인
ip route get 10.0.5.3
# 10.0.5.3 via 10.0.5.1 dev eth1 src 10.0.5.100
```

### 3단계: `traceroute`로 중간 라우터 보기

```bash
traceroute -n 1.1.1.1
# traceroute to 1.1.1.1, 30 hops max, 60 byte packets
#  1  192.168.0.1    1.234 ms  0.987 ms  1.102 ms
#  2  10.200.0.1     5.432 ms  5.201 ms  5.678 ms
#  3  72.14.215.85   8.901 ms  8.765 ms  9.012 ms
#  4  * * *
#  5  1.1.1.1       12.345 ms  12.123 ms  12.456 ms
```

출력의 각 줄이 다음 홉 라우터입니다. `* * *`는 해당 라우터가 ICMP TTL exceeded 응답을 보내지 않는 것이며, 경로 단절을 의미하지 않습니다.

`mtr`을 사용하면 연속 측정으로 패킷 손실률과 지터까지 확인할 수 있습니다.

```bash
mtr -n --report -c 100 1.1.1.1
# HOST                   Loss%   Snt   Last   Avg  Best  Wrst StDev
# 1. 192.168.0.1          0.0%   100    1.2   1.1   0.8   2.1   0.3
# 2. 10.200.0.1           0.0%   100    5.4   5.2   4.8   7.1   0.5
# 3. 72.14.215.85         2.0%   100    9.0   8.8   8.2  12.3   0.9
# 4. ???                  100.0   100    0.0   0.0   0.0   0.0   0.0
# 5. 1.1.1.1              0.0%   100   12.3  12.1  11.8  14.2   0.4
```

hop 4에서 100% 손실이지만 hop 5는 정상입니다. 이는 hop 4 라우터가 ICMP를 차단한 것이지 경로가 끊긴 것이 아닙니다.

### 4단계: 내 공인 IP 확인하기

```bash
curl -s ifconfig.me
# 203.0.113.5
```

내 장비는 `192.168.0.10` 같은 사설 IP를 쓰지만, 외부 세상은 다른 공인 IP를 봅니다. 그 중간 변환이 NAT입니다.

사설 IP 대역은 RFC 1918에 정의되어 있습니다.

| 대역 | CIDR | 주소 수 |
| --- | --- | --- |
| 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 | 16,777,216 |
| 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 | 1,048,576 |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | 65,536 |

### 5단계: NAT 동작 원리 — conntrack 테이블 읽기

NAT는 단순히 IP를 바꾸는 것이 아니라, 연결 상태를 추적합니다.

```bash
# NAT 규칙 확인
sudo iptables -t nat -L -n -v
# Chain POSTROUTING (policy ACCEPT)
# pkts bytes target     prot opt in     out     source      destination
# 1234 98765 MASQUERADE  all  --  *      eth0   192.168.0.0/24  0.0.0.0/0
```

`MASQUERADE`가 대표적인 source NAT 규칙입니다. 이 규칙은 "192.168.0.0/24에서 출발해 eth0으로 나가는 모든 패킷의 출발지 IP를 eth0의 IP로 바꿔라"는 뜻입니다.

```bash
# conntrack 테이블로 현재 NAT 세션 보기
sudo conntrack -L -n
# tcp  6 117 TIME_WAIT src=192.168.0.10 dst=93.184.216.34 sport=54321 dport=443
#                      src=93.184.216.34 dst=203.0.113.5 sport=443 dport=30001 [ASSURED]
```

이 출력은 하나의 NAT 세션을 보여줍니다.

| 방향 | src | dst | sport | dport |
| --- | --- | --- | --- | --- |
| 원래 (내부→외부) | 192.168.0.10 | 93.184.216.34 | 54321 | 443 |
| 응답 (외부→내부) | 93.184.216.34 | 203.0.113.5 | 443 | 30001 |

NAT가 한 일: 출발지 `192.168.0.10:54321` → `203.0.113.5:30001`로 변환. 응답이 `203.0.113.5:30001`로 돌아오면 conntrack 테이블을 참조해 `192.168.0.10:54321`로 역변환합니다.

### 6단계: DNAT와 포트 포워딩

외부에서 내부 서버로 접근하려면 DNAT(Destination NAT)가 필요합니다.

```bash
# 외부에서 203.0.113.5:8080으로 오는 요청을 내부 192.168.0.20:80으로 전달
sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 \
  -j DNAT --to-destination 192.168.0.20:80

# 내부에서 나가는 응답도 올바르게 처리되도록 MASQUERADE 확인
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

이것이 "포트 포워딩"의 실체입니다. 공유기 설정 화면에서 포트 포워딩을 설정하면 내부적으로 이와 동일한 DNAT 규칙이 만들어집니다.

### 7단계: 정적 라우트 추가와 삭제 실험하기

```bash
# 192.168.50.0/24 대역을 특정 게이트웨이로 보내기
sudo ip route add 192.168.50.0/24 via 192.168.0.254 dev eth0

# 확인
ip route show | grep 192.168.50
# 192.168.50.0/24 via 192.168.0.254 dev eth0

# 해당 대역으로 패킷이 어떻게 라우팅되는지 확인
ip route get 192.168.50.100
# 192.168.50.100 via 192.168.0.254 dev eth0 src 192.168.0.10

# 삭제
sudo ip route del 192.168.50.0/24
```

라우팅 테이블이 바뀌면 패킷의 목적지 처리 방식도 즉시 달라진다는 점을 직접 볼 수 있습니다.

## 이 코드에서 먼저 볼 점

- 라우팅 결정은 매 홉마다 독립적으로 내려집니다. 각 라우터는 자기 테이블만 보고 다음 홉을 결정합니다.
- longest-prefix match가 기본 원칙입니다. 더 좁은 규칙이 default보다 우선합니다.
- NAT는 나가는 연결을 추적해 응답이 올바른 사설 IP로 돌아오게 합니다.
- 외부에서 시작되는 새 연결은 DNAT나 포트 포워딩 같은 추가 설정이 필요합니다.
- conntrack 테이블이 가득 차면 새 연결이 실패합니다. 고트래픽 환경에서 흔한 문제입니다.

## NAT 세션 타임아웃과 운영 이슈

NAT 세션에는 타임아웃이 있습니다. Linux 기본값:

```bash
# 현재 conntrack 타임아웃 확인
sysctl net.netfilter.nf_conntrack_tcp_timeout_established
# net.netfilter.nf_conntrack_tcp_timeout_established = 432000  (5일)

sysctl net.netfilter.nf_conntrack_tcp_timeout_time_wait
# net.netfilter.nf_conntrack_tcp_timeout_time_wait = 120  (2분)

# conntrack 테이블 최대 크기
sysctl net.netfilter.nf_conntrack_max
# net.netfilter.nf_conntrack_max = 262144
```

운영에서 자주 발생하는 문제:

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| "nf_conntrack: table full, dropping packet" | 동시 연결 수가 conntrack_max 초과 | `nf_conntrack_max` 증가, 불필요한 추적 제외 |
| idle 연결이 5분 후 끊김 | 중간 NAT 장비의 타임아웃이 짧음 | TCP keepalive 간격을 NAT 타임아웃보다 짧게 설정 |
| 비대칭 라우팅 시 패킷 드롭 | conntrack이 요청을 못 본 상태에서 응답이 도착 | 라우팅 대칭성 확보 또는 `nf_conntrack_tcp_loose=1` |

```bash
# conntrack 테이블 사용량 확인
sudo conntrack -C
# 15234

# 특정 목적지에 대한 세션만 보기
sudo conntrack -L -d 93.184.216.34
```

## NAT traversal과 P2P 연결

NAT 뒤에 있는 두 호스트가 서로 직접 연결하려면 NAT traversal 기술이 필요합니다. 대표적인 방법 세 가지를 비교합니다.

| 기술 | 동작 원리 | 성공률 | 사용 사례 |
| --- | --- | --- | --- |
| STUN | 외부 서버에 요청을 보내 자신의 공인 IP:포트를 알아낸 뒤, 상대방에게 알려줌 | ~70% (symmetric NAT 제외) | WebRTC, VoIP |
| TURN | 중계 서버를 통해 모든 트래픽을 전달 | ~100% | STUN 실패 시 fallback |
| UDP hole punching | 양쪽이 동시에 상대의 공인 IP:포트로 UDP를 보내 NAT 매핑을 생성 | ~60-80% | 게임, 파일 공유 |

```text
클라이언트 A (192.168.0.10)          STUN 서버          클라이언트 B (10.0.0.5)
       │                              │                        │
       │── 요청: 내 공인 주소는? ──────▶│                        │
       │◀─ 응답: 203.0.113.5:30001 ────│                        │
       │                              │                        │
       │                              │◀── 요청: 내 공인 주소는? ──│
       │                              │── 응답: 198.51.100.2:40001 ▶│
       │                              │                        │
       │◀────── 시그널링 서버를 통해 서로의 공인 주소 교환 ────────▶│
       │                              │                        │
       │◀═══════════ 직접 UDP 통신 (hole punching) ═══════════════▶│
```

WebRTC의 ICE(Interactive Connectivity Establishment) 프레임워크는 STUN → TURN 순서로 시도하며, 가능한 한 직접 연결을 우선합니다. 이 과정을 이해하면 화상 회의에서 "연결 중..."이 오래 걸리는 이유를 설명할 수 있습니다.
## longest-prefix match 실전 시나리오

같은 증상처럼 보여도, 라우팅 오류와 NAT 오류는 출력 모양이 다릅니다.

| 관찰한 현상 | 먼저 의심할 것 | 왜 그렇게 보이는가 |
| --- | --- | --- |
| `ip route get 1.1.1.1`이 예상과 다른 인터페이스를 고름 | longest-prefix match 충돌 | 더 구체적인 prefix 규칙이 default route를 이겼기 때문입니다 |
| 내부에서 외부로는 연결되지만, 오래 idle 뒤 응답이 끊김 | NAT 세션 타임아웃 | 출발지 변환 상태가 사라져 돌아오는 패킷을 원래 호스트에 매핑하지 못합니다 |
| 특정 원격 대역만 VPN으로 가야 하는데 전부 로컬 게이트웨이로 나감 | 정적 라우트 누락 | 더 구체적인 기업망 prefix가 라우팅 테이블에 없기 때문입니다 |
| Docker 컨테이너에서 호스트 네트워크 대역에 접근 불가 | docker0 브릿지 라우팅 | 컨테이너의 default route가 docker0이고 호스트 대역 규칙이 없음 |

```bash
# VPN 연결 후 라우팅 테이블이 어떻게 바뀌었는지 확인
ip route show table all | grep -c "via"
# VPN이 주입한 경로 수를 확인

# 특정 IP가 어떤 경로를 타는지 즉시 확인
ip route get 10.100.0.5
# 10.100.0.5 via 10.8.0.1 dev tun0 src 10.8.0.2
```

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| NAT 뒤에서도 외부 인바운드가 자동으로 된다고 생각 | 연결 실패 | 포트 포워딩, reverse tunnel, public LB를 사용한다 |
| 회사와 집이 같은 사설 대역을 씀 | VPN 라우팅 충돌 | prefix를 분리하거나 NAT-on-NAT를 사용한다 |
| `traceroute`의 빈 홉을 경로 단절로 단정 | 잘못된 진단 | `mtr`이나 TCP traceroute로 교차 확인한다 |
| longest-prefix match를 잊음 | 예상과 다른 경로 사용 | `ip route get <dst>`로 실제 매칭 규칙을 확인한다 |
| NAT 세션 타임아웃을 무시 | idle 연결이 끊김 | TCP keepalive 간격을 NAT 타임아웃보다 짧게 넣는다 |

## 실무에서는 이렇게 보입니다

- 클라우드 VPC는 subnet별 라우팅 테이블과 NAT gateway를 조합합니다. AWS의 경우 private subnet은 NAT Gateway를 통해 외부와 통신하고, public subnet은 Internet Gateway를 직접 사용합니다.
- 컨테이너 네트워크는 `docker0`나 CNI를 통해 호스트 NAT 규칙을 사용합니다. Kubernetes에서는 kube-proxy가 iptables 또는 IPVS 규칙을 동적으로 관리합니다.
- VPN은 라우팅 테이블에 추가 경로를 주입합니다. split tunneling은 회사 대역만 VPN으로 보내고 나머지는 로컬 게이트웨이를 쓰게 하는 라우팅 설정입니다.
- 인터넷 백본은 BGP로 AS 간 경로를 협상합니다. 한 AS가 잘못된 prefix를 광고하면 대규모 장애가 발생합니다(2021년 Facebook 장애 사례).
- 모바일과 IoT는 carrier-grade NAT(CGNAT) 뒤에 있는 경우가 많습니다. 이 경우 사설 IP가 이중으로 NAT되므로 P2P 연결이 어렵고, STUN/TURN 같은 NAT traversal 기술이 필요합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 네트워크 사고가 나면 양 끝점의 라우팅 테이블, NAT 정책, 방화벽 규칙을 한꺼번에 펼쳐 봅니다. 패킷은 나가는데 응답이 안 돌아오는 문제는 대개 비대칭 라우팅이나 NAT 세션 만료에서 시작하기 때문입니다.

또한 IPv6와 NAT의 관계도 함께 생각합니다. IPv6는 주소 공간이 넓어 NAT가 기술적으로 필수가 아니므로, 공인 IP 부족을 전제로 한 운영 습관이 어떻게 달라질지까지 내다봅니다.

디버깅 순서도 정형화되어 있습니다.

1. `ip route get <dst>` — 내 호스트가 어디로 보내려 하는지
2. `traceroute` / `mtr` — 실제로 어떤 경로를 타는지
3. `conntrack -L` — NAT 세션이 생겼는지, 타임아웃은 얼마나 남았는지
4. `tcpdump` — 패킷이 실제로 나가고 돌아오는지

이 네 단계를 순서대로 밟으면 "감"이 아니라 증거 기반으로 문제를 좁힐 수 있습니다.

## 클라우드 환경의 라우팅과 NAT

온프레미스와 클라우드의 라우팅/NAT 차이를 정리합니다.

| 구분 | 온프레미스 | 클라우드 (AWS/Azure/GCP) |
| --- | --- | --- |
| 라우팅 테이블 | 물리 라우터 또는 Linux ip route | VPC Route Table (소프트웨어 정의) |
| NAT | iptables MASQUERADE | NAT Gateway (관리형 서비스) |
| 포트 포워딩 | iptables DNAT | Load Balancer + Security Group |
| BGP | 물리 라우터 간 직접 피어링 | VPN Gateway 또는 Direct Connect |
| conntrack 제한 | sysctl 튜닝 | 인스턴스 타입별 연결 추적 제한 |

클라우드에서는 라우팅 테이블을 직접 편집하지 않고 콘솔이나 IaC(Terraform)로 선언합니다. 하지만 동작 원리는 동일합니다. subnet 단위로 라우팅 테이블을 연결하고, 0.0.0.0/0 → NAT Gateway 또는 Internet Gateway로 default route를 설정합니다.

```text
# AWS VPC Route Table 예시 (private subnet)
Destination      Target          Status
10.0.0.0/16      local           active
0.0.0.0/0        nat-gw-abc123   active

# AWS VPC Route Table 예시 (public subnet)
Destination      Target          Status
10.0.0.0/16      local           active
0.0.0.0/0        igw-xyz789      active
```

## 체크리스트

- [ ] 라우팅 테이블을 읽고 각 필드의 의미를 설명할 수 있다
- [ ] longest-prefix match의 동작 원리를 예시로 보여줄 수 있다
- [ ] `ip route get`으로 특정 목적지의 실제 매칭 규칙을 확인할 수 있다
- [ ] NAT가 출발지 IP와 포트를 어떻게 바꾸는지 conntrack으로 확인할 수 있다
- [ ] SNAT와 DNAT의 차이를 설명할 수 있다
- [ ] `traceroute`와 `mtr`로 경로를 진단할 수 있다
- [ ] 외부 인바운드 연결에 왜 추가 설정이 필요한지 설명할 수 있다
- [ ] NAT 세션 타임아웃이 운영에 미치는 영향을 안다

## 연습 문제

1. 자신의 라우팅 테이블을 저장하고, default route와 가장 구체적인 규칙 하나를 설명해 보세요.
2. 같은 LAN에 있는 두 호스트와 다른 네트워크에 있는 호스트를 각각 `ping`, `traceroute` 해 보고, 라우터를 지났는지 판단해 보세요.
3. "회사에서는 SSH가 되는데 집에서는 안 되는 이유"를 NAT와 방화벽 관점에서 한 단락으로 설명해 보세요.
4. `sudo conntrack -L`로 현재 NAT 세션을 확인하고, 가장 오래된 세션의 프로토콜과 상태를 기록해 보세요.
5. VPN을 연결하기 전과 후에 `ip route`를 비교해 어떤 경로가 추가되었는지 확인해 보세요.

## 정리와 다음 글

라우터는 한 홉씩 경로를 결정하고, NAT는 사설 IP가 공인 인터넷과 통신할 수 있게 다리를 놓습니다. 이 둘을 이해하면 인터넷 동작의 상당 부분이 눈에 보이기 시작합니다. longest-prefix match는 라우팅의 핵심 원칙이고, conntrack은 NAT의 핵심 메커니즘입니다.

다음 글에서는 그 경로 끝에서 자주 만나는 장치, Load Balancer를 다룹니다.

## 처음 질문으로 돌아가기

- **라우팅 테이블은 어떻게 읽어야 할까요?**
  - 각 줄은 "이 destination prefix에 해당하는 패킷을, 이 인터페이스(dev)를 통해, 이 다음 홉(via)으로 보내라"는 규칙입니다. `ip route` 출력에서 destination, via, dev, metric 네 필드를 읽으면 됩니다. `ip route get <IP>`로 특정 목적지에 실제 적용되는 규칙을 바로 확인할 수 있습니다.
- **default gateway와 longest-prefix match는 어떻게 동작할까요?**
  - default gateway는 `0.0.0.0/0` 규칙, 즉 "다른 어떤 규칙에도 매칭되지 않는 모든 패킷"을 받는 마지막 수단입니다. longest-prefix match는 여러 규칙이 동시에 매칭될 때 prefix 길이가 가장 긴(가장 구체적인) 규칙을 선택하는 원칙입니다. `/24`는 `/8`보다 우선하고, `/8`은 `/0`보다 우선합니다.
- **NAT는 출발지 IP와 포트를 어떻게 바꿀까요?**
  - SNAT(MASQUERADE)는 나가는 패킷의 출발지 IP를 공인 IP로, 출발지 포트를 새 포트로 바꾸고, 이 매핑을 conntrack 테이블에 기록합니다. 응답이 돌아오면 conntrack을 역으로 참조해 원래 사설 IP:포트로 되돌립니다. 이 상태 추적 덕분에 하나의 공인 IP로 수만 개의 내부 연결을 동시에 처리할 수 있습니다.

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
- [book-examples: computer-networks-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, 라우팅, NAT, default gateway, 사설IP
