---
series: computer-networks-101
episode: 4
title: "Computer Networks 101 (4/10): DNS"
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
  - DNS
  - resolver
  - 캐싱
  - TTL
seo_description: 도메인 이름을 IP 주소로 변환하는 DNS의 계층 구조와 동작 원리, TTL 및 캐싱이 시스템 운영에 미치는 영향을 상세히 다룹니다.
last_reviewed: '2026-05-15'
---

# Computer Networks 101 (4/10): DNS

이 글은 Computer Networks 101 시리즈의 4번째 글입니다.

## 먼저 던지는 질문

- DNS 계층 구조는 어떻게 되어 있을까요?
- recursive resolver와 캐시는 어떤 역할을 할까요?
- A, AAAA, CNAME, MX, TXT 레코드는 각각 어디에 쓰일까요?

## 큰 그림

![Computer Networks 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/04/04-01-concept-at-a-glance.ko.png)

*Computer Networks 101 4장 흐름 개요*

## 왜 중요한가

"인터넷이 안 된다"는 문제의 상당수는 DNS에서 시작되고, 그중 많은 경우가 TTL과 캐시를 잘못 이해한 탓입니다. DNS를 모르면 배포 후에도 왜 예전 IP로 붙는지 설명하기 어렵고, 서비스 이전이나 리전 failover도 예측하기 힘들어집니다. 게다가 모든 HTTP 요청은 DNS 조회로 시작하기 때문에 성능 분석에서도 빠지지 않습니다.

> "It's always DNS"라는 운영자 농담은 과장이 섞였지만, 생각보다 자주 맞습니다.

## 핵심 그림

> 클라이언트는 운영 체제의 stub resolver에 물어보고, stub resolver는 보통 ISP나 회사의 recursive resolver에 질의를 넘깁니다. recursive resolver는 루트 서버, TLD 서버, authoritative 서버를 순서대로 따라가며 답을 찾고, 그 결과를 TTL 동안 캐시합니다.

```text
┌──────────┐       ┌──────────────────┐       ┌──────────┐
│ 애플리케이션  │──────▶│ stub resolver     │──────▶│ recursive │
│ (브라우저)  │       │ (/etc/resolv.conf)│       │ resolver  │
└──────────┘       └──────────────────┘       └─────┬────┘
                                                     │
                         ┌───────────────────────────┼───────────────┐
                         ▼                           ▼               ▼
                   ┌──────────┐             ┌──────────┐    ┌──────────────┐
                   │ root (.)  │             │ TLD (.com)│    │ authoritative │
                   └──────────┘             └──────────┘    │ (example.com) │
                                                            └──────────────┘
```

위 그림에서 recursive resolver가 한 번 답을 받으면 TTL 동안 캐시에 저장합니다. 다음에 같은 질의가 오면 authoritative 서버까지 가지 않고 캐시에서 바로 응답합니다. 이것이 DNS가 빠르면서도 동시에 변경이 느린 이유입니다.

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| A / AAAA | 도메인을 IPv4 / IPv6 주소로 매핑하는 레코드 |
| CNAME | 도메인을 다른 도메인에 별칭으로 연결하는 레코드 |
| MX | 메일 서버를 가리키는 레코드 |
| TXT | SPF, DKIM, 도메인 검증 등에 쓰는 텍스트 레코드 |
| NS | 해당 도메인의 authoritative 네임서버를 가리키는 레코드 |
| SOA | 도메인 영역(zone)의 메타 정보를 담는 레코드 |
| TTL | 캐시 가능한 수명을 초 단위로 나타낸 값 |
| stub resolver | OS에 내장된 최소 resolver. 자체 캐시 없이 recursive resolver에 위임 |
| recursive resolver | 클라이언트 대신 root→TLD→auth를 따라가며 답을 찾아주는 서버 |
| authoritative server | 특정 도메인의 레코드를 실제로 보유한 최종 서버 |

## Before / After

**Before — "DNS는 어디선가 찾아 주는 큰 사전"**

```text
example.com → 어떻게 IP가 되는지 모름
```

**After — "DNS는 분산 트리와 캐시의 조합"**

```text
. → com → example.com → A 93.184.216.34
각 단계는 다른 서버가 맡고, resolver가 위임을 따라간다
```

## 단계별로 따라하기

### 1단계: `dig`로 단일 조회하기

```bash
dig example.com +noall +answer
# example.com.  86400  IN  A  93.184.216.34
```

`86400`은 TTL입니다. 최대 24시간 동안 캐시에 남겨 둘 수 있다는 말입니다.

### 2단계: 위임 체인 따라가기

```bash
dig example.com +trace
# .                ← root
# com.             ← TLD
# example.com.     ← authoritative
```

실제 출력을 좀 더 자세히 보겠습니다.

```bash
dig example.com +trace +nodnssec
;; Received 239 bytes from 127.0.0.53#53(127.0.0.53) in 0 ms
; . 518400 IN NS a.root-servers.net.

;; Received 828 bytes from 198.41.0.4#53(a.root-servers.net) in 24 ms
; com. 172800 IN NS a.gtld-servers.net.

;; Received 460 bytes from 192.5.6.30#53(a.gtld-servers.net) in 18 ms
; example.com. 172800 IN NS a.iana-servers.net.

;; Received 56 bytes from 199.43.135.53#53(a.iana-servers.net) in 32 ms
; example.com. 86400 IN A 93.184.216.34
```

resolver가 실제로 어떤 경로를 따라 답을 찾는지 그대로 볼 수 있습니다. 총 네 번의 질의가 필요했고, 각 단계에서 "나는 모르지만 여기에 물어봐"라는 위임(delegation)이 일어납니다.

### 3단계: 다양한 레코드 타입 보기

```bash
dig MX gmail.com +short
# 5 gmail-smtp-in.l.google.com.
# 10 alt1.gmail-smtp-in.l.google.com.
# 20 alt2.gmail-smtp-in.l.google.com.

dig AAAA cloudflare.com +short
# 2606:4700::6810:84e5
# 2606:4700::6810:85e5

dig TXT _dmarc.gmail.com +short
# "v=DMARC1; p=none; sp=quarantine; rua=mailto:..."
```

하나의 도메인에 여러 종류의 레코드가 동시에 존재할 수 있습니다. MX 레코드의 숫자(5, 10, 20)는 우선순위이며 낮을수록 먼저 시도합니다.

### 4단계: NS와 SOA 레코드 확인하기

```bash
dig NS example.com +short
# a.iana-servers.net.
# b.iana-servers.net.

dig SOA example.com +short
# sns.dns.icann.org. noc.dns.icann.org. 2024120101 7200 3600 1209600 3600
```

SOA 레코드의 각 필드는 순서대로 primary NS, 관리자 이메일(`.`은 `@`), 시리얼 번호, refresh, retry, expire, negative TTL입니다. 시리얼 번호가 바뀌면 secondary 서버가 zone 전송을 시작합니다.

### 5단계: Python에서 조회하기

```python
import socket

print(socket.gethostbyname('example.com'))   # 93.184.216.34
print(socket.getaddrinfo('example.com', 443, type=socket.SOCK_STREAM))
# Uses the OS stub resolver
```

더 정밀하게 보려면 이렇게도 할 수 있습니다.

```python
import dns.resolver   # pip install dnspython

ans = dns.resolver.resolve('example.com', 'A')
for r in ans:
    print(r.to_text(), 'TTL', ans.rrset.ttl)

# CNAME 체인 추적
try:
    cname = dns.resolver.resolve('www.github.com', 'CNAME')
    for r in cname:
        print(f"CNAME → {r.target}")
except dns.resolver.NoAnswer:
    print("No CNAME record")

# MX 우선순위 확인
mx_ans = dns.resolver.resolve('gmail.com', 'MX')
for r in sorted(mx_ans, key=lambda x: x.preference):
    print(f"priority={r.preference} server={r.exchange}")
```

### 6단계: `tcpdump`로 DNS 패킷 보기

```bash
sudo tcpdump -i any -nn 'udp port 53' -c 10
# 10:01:03.123 IP 10.0.1.5.41234 > 8.8.8.8.53: A? example.com. (29)
# 10:01:03.145 IP 8.8.8.8.53 > 10.0.1.5.41234: A 93.184.216.34 (45)
```

DNS는 기본적으로 UDP 53번 포트를 사용하고, 응답이 512바이트를 초과하면 TCP로 넘어갑니다. DNSSEC이나 대형 TXT 레코드가 포함된 경우에 TCP fallback이 자주 발생합니다.

### 7단계: 캐시 동작 직접 관찰하기

```bash
# 첫 번째 조회 — TTL이 최댓값
dig example.com +noall +answer
# example.com. 86400 IN A 93.184.216.34

# 30초 후 다시 조회 — TTL이 줄어 있음
dig example.com +noall +answer
# example.com. 86370 IN A 93.184.216.34
```

TTL이 줄어드는 것을 직접 관찰할 수 있습니다. 이 값이 0에 도달하면 resolver는 다시 authoritative 서버에 질의합니다.

## 이 코드에서 먼저 볼 점

- DNS 조회는 모든 HTTP 요청의 첫 단계입니다. 캐시가 없으면 지연이 크게 늘 수 있습니다.
- TTL은 절대적인 마감 시간이 아니라 캐시의 유효 기간 힌트에 가깝습니다.
- 하나의 도메인에 여러 A나 AAAA 레코드가 동시에 달릴 수 있습니다.
- CNAME 체인이 길어질수록 조회도 느려집니다.
- negative caching도 존재합니다. NXDOMAIN 응답도 SOA의 minimum TTL 동안 캐시됩니다.
- `getaddrinfo()`는 OS 캐시를 사용하고, `dns.resolver`는 자체적으로 질의합니다. 같은 프로세스에서도 경로가 다를 수 있습니다.
- Round-Robin DNS에서는 같은 도메인을 조회할 때마다 IP 순서가 바뀔 수 있습니다. 클라이언트가 항상 첫 번째 IP를 사용한다면 부하 분산이 고르지 않습니다.

### DNS 질의 패킷 구조

DNS 메시지는 UDP 위에서 다음 구조로 전송됩니다.

```text
┌────────────────────────────────────────────────┐
│ Header (12 bytes)                              │
│  ID: 0xAB12  (질의/응답 매칭용)                 │
│  Flags: QR=0(질의), OPCODE=0, RD=1            │
│  QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0   │
├────────────────────────────────────────────────┤
│ Question Section                               │
│  QNAME: 07 example 03 com 00                  │
│  QTYPE: 0x0001 (A)                            │
│  QCLASS: 0x0001 (IN)                          │
└────────────────────────────────────────────────┘

응답 메시지:
┌────────────────────────────────────────────────┐
│ Header (12 bytes)                              │
│  ID: 0xAB12  (동일 ID)                         │
│  Flags: QR=1(응답), AA=1, RCODE=0(No Error)   │
│  QDCOUNT=1, ANCOUNT=1                          │
├────────────────────────────────────────────────┤
│ Answer Section                                 │
│  NAME: example.com.                            │
│  TYPE: A, CLASS: IN, TTL: 86400               │
│  RDLENGTH: 4, RDATA: 93.184.216.34            │
└────────────────────────────────────────────────┘
```

QNAME의 `07 example 03 com 00`은 길이-접두사 인코딩입니다. `07`은 다음 7바이트가 "example"이라는 뜻이고, `00`이 이름의 끝을 표시합니다. 이 구조 덕분에 DNS는 점(`.`)을 구분자로 명시하지 않아도 됩니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| TTL을 하루로 두고 즉시 전환을 기대 | 캐시 때문에 전환이 늦어짐 | 이전 전에 TTL을 60초 등으로 미리 낮춘다 |
| `/etc/hosts`로 임시 조치 후 잊어버림 | 원인 추적이 더 어려워짐 | 테스트 직후 바로 원복한다 |
| `nslookup`만 믿음 | 실제 앱이 다른 resolver를 쓸 수 있음 | 앱 컨테이너 안에서 `dig`를 실행한다 |
| 모든 문제를 DNS로 의심 | 진단 시간이 길어짐 | `ping`, `curl`, `dig`를 함께 써서 분리한다 |
| root 도메인에 CNAME을 직접 연결 | 일부 resolver에서 깨짐 | ALIAS / ANAME 같은 대안을 쓴다 |

## DNS 레코드 설계 실무 예시

실제 서비스를 운영할 때 DNS 레코드를 어떻게 구성하는지 구체적 사례를 보겠습니다.

### 웹 서비스 기본 구성

```text
; Zone: myapp.io
$TTL 300

; root 도메인 — A 레코드 (CNAME 사용 불가)
myapp.io.           300  IN  A      203.0.113.10
myapp.io.           300  IN  A      203.0.113.11
myapp.io.           300  IN  AAAA   2001:db8::10

; www — CNAME으로 CDN 연결
www.myapp.io.       300  IN  CNAME  myapp.io.cdn.cloudflare.net.

; API 서버
api.myapp.io.       60   IN  A      203.0.113.20

; 메일 관련
myapp.io.           3600 IN  MX     10 mail1.myapp.io.
myapp.io.           3600 IN  MX     20 mail2.myapp.io.
myapp.io.           3600 IN  TXT    "v=spf1 include:_spf.google.com ~all"
_dmarc.myapp.io.    3600 IN  TXT    "v=DMARC1; p=reject; rua=mailto:dmarc@myapp.io"
```

주목할 점은 다음과 같습니다.

- root 도메인(`myapp.io`)에는 CNAME을 쓸 수 없으므로 A 레코드를 직접 사용합니다.
- API 서버의 TTL은 60초로 짧게 잡아서 빠른 전환이 가능하도록 합니다.
- 메일 관련 레코드(MX, SPF, DMARC)의 TTL은 3600초로 넉넉하게 둡니다. 메일 설정은 자주 바뀌지 않기 때문입니다.

### 서비스 이전 시나리오

```text
; D-7: TTL을 미리 낮춤
api.myapp.io.   60  IN  A  203.0.113.20   ; 기존 IP, TTL 60초

; D-day: IP 변경
api.myapp.io.   60  IN  A  198.51.100.50  ; 새 IP

; D+1: 안정화 확인 후 TTL 복원
api.myapp.io.  300  IN  A  198.51.100.50  ; TTL 5분으로 복원
```

핵심은 IP를 바꾸기 **최소 기존 TTL 시간 전**에 TTL을 낮추는 것입니다. 기존 TTL이 86400(하루)이었다면 하루 전에 60초로 낮추고, 캐시가 모두 만료된 다음 날 IP를 변경합니다.

## 실무에서는 이렇게 보입니다

- 서비스 이전 전에는 TTL을 미리 낮춘 뒤 IP를 바꿉니다.
- CDN은 사용자 위치에 따라 다른 IP를 응답하는 GeoDNS를 사용합니다.
- failover는 authoritative 서버가 상태에 따라 다른 IP를 돌려주는 식으로 구현되기도 합니다.
- SPF, DKIM, DMARC는 모두 TXT 레코드입니다.
- Kubernetes에서는 CoreDNS가 서비스 이름을 ClusterIP로 바꿔 줍니다.

### Kubernetes DNS 동작 예시

```bash
# Pod 안에서 서비스 이름으로 조회
dig my-service.default.svc.cluster.local +short
# 10.96.45.12

# CoreDNS 설정 확인
kubectl get configmap coredns -n kube-system -o yaml
```

```text
; CoreDNS가 관리하는 레코드 예시
my-service.default.svc.cluster.local.  5  IN  A  10.96.45.12
my-pod.default.pod.cluster.local.      5  IN  A  10.244.1.23
```

Pod에서 `curl http://my-service:8080`을 호출하면 CoreDNS가 `my-service.default.svc.cluster.local`을 `10.96.45.12`로 변환합니다. TTL은 기본 5초입니다. Service가 삭제되면 NXDOMAIN을 반환합니다.

### DNS 기반 서비스 디스커버리 패턴

```python
import dns.resolver

def discover_backends(service_domain: str) -> list[str]:
    """DNS SRV 레코드로 백엔드 목록 조회"""
    backends = []
    try:
        answers = dns.resolver.resolve(f"_http._tcp.{service_domain}", "SRV")
        for rdata in sorted(answers, key=lambda r: (r.priority, -r.weight)):
            backends.append(f"{rdata.target}:{rdata.port}")
    except dns.resolver.NXDOMAIN:
        pass
    return backends

# 사용 예
hosts = discover_backends("api.myapp.io")
# ['backend1.myapp.io:8080', 'backend2.myapp.io:8080']
```

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 IP를 바꾸기 전에 반드시 TTL부터 확인합니다. DNS 변경은 흔히 "전파"라고 부르지만, 실제 핵심은 캐시 만료입니다. DNS가 실시간 시스템이 아니라는 사실 하나만 제대로 이해해도 자주 겪는 DNS 사고 상당수가 설명됩니다.

또한 `nslookup` 결과만 보고 안심하지 않습니다. 애플리케이션이 실제로 어떤 resolver를 쓰는지, 컨테이너 안의 `resolv.conf`가 무엇인지, Kubernetes의 CoreDNS 정책이 어떤지까지 함께 봅니다. 같은 도메인도 환경마다 다르게 풀릴 수 있기 때문입니다.

DNS 장애 대응에서 가장 먼저 하는 일은 "어느 레벨의 캐시가 문제인가"를 분리하는 것입니다.

```text
계층별 캐시 체크 순서:
1. 브라우저 캐시    → chrome://net-internals/#dns
2. OS 캐시         → systemd-resolve --statistics (Linux)
3. 로컬 resolver   → /etc/resolv.conf 확인
4. upstream DNS    → dig @8.8.8.8 vs dig @1.1.1.1 비교
5. authoritative   → dig @ns1.example.com example.com
```

## DNS 보안: 알아야 할 위협과 대응

| 위협 | 설명 | 대응 |
| --- | --- | --- |
| DNS spoofing | 위조된 응답을 캐시에 주입 | DNSSEC 검증 활성화 |
| DNS amplification DDoS | 작은 질의로 큰 응답을 유도해 피해자에게 반사 | Response Rate Limiting, BCP38 |
| DNS tunneling | DNS 질의/응답에 데이터를 숨겨 방화벽 우회 | 비정상 질의 패턴 모니터링 |
| Domain hijacking | 등록 기관 계정 탈취로 NS 레코드 변경 | Registrar Lock, 2FA |

```bash
# DNSSEC 검증 상태 확인
dig example.com +dnssec +short
# 93.184.216.34
# A 13 2 86400 ... (RRSIG)

# DNSSEC 체인 검증
dig +sigchase +trusted-key=./root.keys example.com
```

## DNS 성능 측정과 트러블슈팅

DNS 문제를 진단할 때 가장 중요한 것은 "어디서 느린지"를 수치로 확인하는 것입니다.

### 응답 시간 측정

```bash
# 단일 질의 응답 시간 측정
dig example.com | grep "Query time"
# ;; Query time: 23 msec

# 여러 DNS 서버 비교
for ns in 8.8.8.8 1.1.1.1 208.67.222.222; do
  echo -n "$ns: "
  dig @$ns example.com +noall +stats | grep "Query time"
done
# 8.8.8.8: ;; Query time: 12 msec
# 1.1.1.1: ;; Query time: 8 msec
# 208.67.222.222: ;; Query time: 31 msec
```

### 연속 조회로 캐시 효과 확인

```bash
# 캐시 플러시 후 첫 조회
sudo systemd-resolve --flush-caches
dig example.com | grep "Query time"
# ;; Query time: 45 msec

# 즉시 재조회 — 캐시 히트
dig example.com | grep "Query time"
# ;; Query time: 0 msec
```

### 대량 조회 성능 테스트

```bash
# 100개 도메인을 순차 조회해 평균 응답 시간 측정
cat domains.txt | while read domain; do
  dig +noall +stats "$domain" | grep "Query time"
done | awk -F: '{sum += $2; n++} END {print "avg:", sum/n, "msec"}'
```

### Python으로 DNS 응답 시간 모니터링

```python
import dns.resolver
import time

def measure_dns(domain: str, rdtype: str = "A", server: str = None) -> float:
    resolver = dns.resolver.Resolver()
    if server:
        resolver.nameservers = [server]
    start = time.perf_counter()
    resolver.resolve(domain, rdtype)
    elapsed = (time.perf_counter() - start) * 1000
    return round(elapsed, 2)

# 여러 resolver 비교
servers = {"Google": "8.8.8.8", "Cloudflare": "1.1.1.1", "Quad9": "9.9.9.9"}
for name, ip in servers.items():
    ms = measure_dns("example.com", server=ip)
    print(f"{name:12s} ({ip:15s}): {ms:6.2f} ms")
```

### DNS 장애 진단 플로우차트

```text
문제: 도메인이 풀리지 않는다
│
├─ dig @127.0.0.53 실패?
│   ├─ Yes → 로컬 resolver 문제
│   │        → systemctl status systemd-resolved
│   │        → /etc/resolv.conf 확인
│   └─ No  → 다음 단계
│
├─ dig @8.8.8.8 실패?
│   ├─ Yes → 네트워크 연결 또는 방화벽 문제
│   │        → ping 8.8.8.8 (ICMP 확인)
│   │        → iptables -L -n | grep 53
│   └─ No  → 로컬 resolver 설정 문제
│
├─ dig @authoritative-ns 실패?
│   ├─ Yes → authoritative 서버 다운 또는 zone 설정 오류
│   │        → whois로 NS 레코드 확인
│   └─ No  → 캐시 문제 (TTL 만료 대기)
│
└─ NXDOMAIN vs SERVFAIL 구분
    ├─ NXDOMAIN → 도메인 미등록 또는 zone에 레코드 없음
    └─ SERVFAIL → DNSSEC 검증 실패 또는 서버 내부 오류
```

### resolv.conf 설정과 ndots 옵션

Kubernetes Pod에서 자주 발생하는 DNS 지연 문제 중 하나가 `ndots` 설정입니다.

```bash
# Pod 안에서 resolv.conf 확인
cat /etc/resolv.conf
# nameserver 10.96.0.10
# search default.svc.cluster.local svc.cluster.local cluster.local
# options ndots:5
```

`ndots:5`는 "도메인에 점이 5개 미만이면 search 도메인을 먼저 붙여서 시도한다"는 뜻입니다. 즉 `api.external.com`(점 2개)을 조회하면 다음 순서로 시도합니다.

```text
1. api.external.com.default.svc.cluster.local  → NXDOMAIN
2. api.external.com.svc.cluster.local          → NXDOMAIN
3. api.external.com.cluster.local              → NXDOMAIN
4. api.external.com.                           → 성공!
```

외부 도메인 하나를 풀기 위해 불필요한 질의가 3번 더 발생합니다. 해결 방법은 두 가지입니다.

```yaml
# 방법 1: Pod spec에서 dnsConfig 조정
spec:
  dnsConfig:
    options:
    - name: ndots
      value: "2"

# 방법 2: 코드에서 FQDN 사용 (trailing dot)
# api.external.com.  ← 마지막 점이 있으면 search 도메인을 건너뜀
```

이 차이만 알아도 Kubernetes 환경에서 외부 API 호출 지연의 상당수를 해결할 수 있습니다.

## 체크리스트

- [ ] DNS 계층 구조를 말할 수 있다
- [ ] A, AAAA, CNAME, MX, TXT, NS, SOA의 용도를 안다
- [ ] `dig`로 위임 경로를 추적할 수 있다
- [ ] TTL이 운영에 미치는 영향을 설명할 수 있다
- [ ] DNS 변경 전에 TTL을 먼저 낮춘다
- [ ] negative caching의 존재를 인지하고 있다
- [ ] Kubernetes에서 서비스 이름이 어떻게 풀리는지 안다

## 연습 문제

1. 자주 방문하는 사이트의 A, MX, TXT 레코드를 `dig`로 조회하고, 무엇이 보였는지 한 단락으로 설명해 보세요.
2. TTL이 60초인 임시 도메인을 운영한다고 가정하고, IP를 바꿀 때 사용자 영향이 어떻게 달라지는지 설명해 보세요.
3. `tcpdump`로 DNS 질의와 응답을 캡처한 뒤, 두 번째 조회가 왜 더 빠른지 설명해 보세요.
4. `dig +trace`로 세 개의 서로 다른 도메인을 추적하고, 위임 체인의 깊이가 어떻게 다른지 비교해 보세요.

## 정리와 다음 글

DNS는 인터넷의 전화번호부이자, 운영 사고의 상당수를 설명하는 캐시 시스템입니다. 계층 구조와 TTL을 이해하면 배포, 이전, failover가 갑자기 훨씬 예측 가능해집니다.

다음 글에서는 DNS로 찾은 IP에 실제로 어떤 메시지를 보내는지, HTTP와 HTTPS를 다룹니다.

## 처음 질문으로 돌아가기

- **DNS 계층 구조는 어떻게 되어 있을까요?**
  - root(`.`) → TLD(`.com`) → authoritative(`example.com`)의 트리 구조이며, recursive resolver가 이 위임 체인을 따라 답을 찾습니다. `dig +trace`로 직접 관찰할 수 있습니다.
- **recursive resolver와 캐시는 어떤 역할을 할까요?**
  - recursive resolver는 클라이언트 대신 root부터 authoritative까지 따라가며 답을 구하고, 그 결과를 TTL 동안 캐시합니다. 덕분에 대부분의 질의는 authoritative 서버까지 가지 않고 끝나지만, TTL 만료 전에는 변경이 반영되지 않는 트레이드오프가 있습니다.
- **A, AAAA, CNAME, MX, TXT 레코드는 각각 어디에 쓰일까요?**
  - A/AAAA는 도메인→IP 매핑, CNAME은 도메인→도메인 별칭, MX는 메일 라우팅, TXT는 SPF/DKIM/DMARC 같은 도메인 검증과 메일 보안에 쓰입니다. 하나의 도메인에 여러 타입이 동시에 존재할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Networks 101 (1/10): 네트워크란 무엇인가?](./01-what-is-a-network.md)
- [Computer Networks 101 (2/10): IP와 subnet](./02-ip-and-subnet.md)
- [Computer Networks 101 (3/10): TCP와 UDP](./03-tcp-and-udp.md)
- **DNS (현재 글)**
- HTTP와 HTTPS (예정)
- TLS 기초 (예정)
- 라우팅과 NAT (예정)
- Load Balancer (예정)
- WebSocket과 실시간 통신 (예정)
- 네트워크 문제 디버깅 (예정)

<!-- toc:end -->

## 참고 자료

- [RFC 1035 — Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035)
- [Cloudflare Learning — What is DNS?](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [dnspython 문서](https://www.dnspython.org/)
- [Julia Evans — How DNS works (zine)](https://wizardzines.com/zines/dns/)
- [시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/computer-networks-101/ko)

Tags: Computer Science, 네트워크, DNS, resolver, 캐싱, TTL
