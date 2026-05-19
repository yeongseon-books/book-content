---
series: computer-networks-101
episode: 4
title: DNS
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

# DNS

이 글은 Computer Networks 101 시리즈의 4번째 글입니다.

## 이 글에서 다룰 문제

- DNS 계층 구조는 어떻게 되어 있을까요?
- recursive resolver와 캐시는 어떤 역할을 할까요?
- A, AAAA, CNAME, MX, TXT 레코드는 각각 어디에 쓰일까요?
- TTL은 왜 운영에서 자주 사고를 부를까요?

> DNS는 이름을 주소로 바꾸는 시스템입니다. 하지만 단일 서버 하나가 아니라, 루트 서버부터 TLD, authoritative 서버까지 이어지는 전 세계 계층 구조와 그 앞단의 resolver, 그리고 캐시가 함께 돌아가는 구조입니다. 인터넷이 빠르게 동작하는 이유도 캐시이고, DNS 사고가 반복되는 이유도 대개 캐시입니다.

## 왜 중요한가

"인터넷이 안 된다"는 문제의 상당수는 DNS에서 시작되고, 그중 많은 경우가 TTL과 캐시를 잘못 이해한 탓입니다. DNS를 모르면 배포 후에도 왜 예전 IP로 붙는지 설명하기 어렵고, 서비스 이전이나 리전 failover도 예측하기 힘들어집니다. 게다가 모든 HTTP 요청은 DNS 조회로 시작하기 때문에 성능 분석에서도 빠지지 않습니다.

> "It's always DNS"라는 운영자 농담은 과장이 섞였지만, 생각보다 자주 맞습니다.

## 핵심 그림

> 클라이언트는 운영 체제의 stub resolver에 물어보고, stub resolver는 보통 ISP나 회사의 recursive resolver에 질의를 넘깁니다. recursive resolver는 루트 서버, TLD 서버, authoritative 서버를 순서대로 따라가며 답을 찾고, 그 결과를 TTL 동안 캐시합니다.

![DNS 조회가 루트에서 authoritative까지 내려가는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/computer-networks-101/04/04-01-concept-at-a-glance.ko.png)
*recursive resolver가 위임 체인을 따라 내려가 답을 찾고, TTL 동안 캐시해 다음 조회를 빠르게 만듭니다.*

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| A / AAAA | 도메인을 IPv4 / IPv6 주소로 매핑하는 레코드 |
| CNAME | 도메인을 다른 도메인에 별칭으로 연결하는 레코드 |
| MX | 메일 서버를 가리키는 레코드 |
| TXT | SPF, DKIM, 도메인 검증 등에 쓰는 텍스트 레코드 |
| TTL | 캐시 가능한 수명을 초 단위로 나타낸 값 |

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

resolver가 실제로 어떤 경로를 따라 답을 찾는지 그대로 볼 수 있습니다.

### 3단계: 다양한 레코드 타입 보기

```bash
dig MX gmail.com +short
dig AAAA cloudflare.com +short
dig TXT _dmarc.gmail.com +short
```

하나의 도메인에 여러 종류의 레코드가 동시에 존재할 수 있습니다.

### 4단계: Python에서 조회하기

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
```

### 5단계: `tcpdump`로 DNS 패킷 보기

```bash
sudo tcpdump -i any -nn 'udp port 53'
# A? example.com
# A 93.184.216.34
```

DNS는 기본적으로 UDP 53번 포트를 사용하고, 응답이 크면 TCP로 넘어갑니다.

## 이 코드에서 먼저 볼 점

- DNS 조회는 모든 HTTP 요청의 첫 단계입니다. 캐시가 없으면 지연이 크게 늘 수 있습니다.
- TTL은 절대적인 마감 시간이 아니라 캐시의 유효 기간 힌트에 가깝습니다.
- 하나의 도메인에 여러 A나 AAAA 레코드가 동시에 달릴 수 있습니다.
- CNAME 체인이 길어질수록 조회도 느려집니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| TTL을 하루로 두고 즉시 전환을 기대 | 캐시 때문에 전환이 늦어짐 | 이전 전에 TTL을 60초 등으로 미리 낮춘다 |
| `/etc/hosts`로 임시 조치 후 잊어버림 | 원인 추적이 더 어려워짐 | 테스트 직후 바로 원복한다 |
| `nslookup`만 믿음 | 실제 앱이 다른 resolver를 쓸 수 있음 | 앱 컨테이너 안에서 `dig`를 실행한다 |
| 모든 문제를 DNS로 의심 | 진단 시간이 길어짐 | `ping`, `curl`, `dig`를 함께 써서 분리한다 |
| root 도메인에 CNAME을 직접 연결 | 일부 resolver에서 깨짐 | ALIAS / ANAME 같은 대안을 쓴다 |

## 실무에서는 이렇게 보입니다

- 서비스 이전 전에는 TTL을 미리 낮춘 뒤 IP를 바꿉니다.
- CDN은 사용자 위치에 따라 다른 IP를 응답하는 GeoDNS를 사용합니다.
- failover는 authoritative 서버가 상태에 따라 다른 IP를 돌려주는 식으로 구현되기도 합니다.
- SPF, DKIM, DMARC는 모두 TXT 레코드입니다.
- Kubernetes에서는 CoreDNS가 서비스 이름을 ClusterIP로 바꿔 줍니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 IP를 바꾸기 전에 반드시 TTL부터 확인합니다. DNS 변경은 흔히 "전파"라고 부르지만, 실제 핵심은 캐시 만료입니다. DNS가 실시간 시스템이 아니라는 사실 하나만 제대로 이해해도 자주 겪는 DNS 사고 상당수가 설명됩니다.

또한 `nslookup` 결과만 보고 안심하지 않습니다. 애플리케이션이 실제로 어떤 resolver를 쓰는지, 컨테이너 안의 `resolv.conf`가 무엇인지, Kubernetes의 CoreDNS 정책이 어떤지까지 함께 봅니다. 같은 도메인도 환경마다 다르게 풀릴 수 있기 때문입니다.

## 체크리스트

- [ ] DNS 계층 구조를 말할 수 있다
- [ ] A, AAAA, CNAME, MX, TXT의 용도를 안다
- [ ] `dig`로 위임 경로를 추적할 수 있다
- [ ] TTL이 운영에 미치는 영향을 설명할 수 있다
- [ ] DNS 변경 전에 TTL을 먼저 낮춘다

## 연습 문제

1. 자주 방문하는 사이트의 A, MX, TXT 레코드를 `dig`로 조회하고, 무엇이 보였는지 한 단락으로 설명해 보세요.
2. TTL이 60초인 임시 도메인을 운영한다고 가정하고, IP를 바꿀 때 사용자 영향이 어떻게 달라지는지 설명해 보세요.
3. `tcpdump`로 DNS 질의와 응답을 캡처한 뒤, 두 번째 조회가 왜 더 빠른지 설명해 보세요.

## 정리와 다음 글

DNS는 인터넷의 전화번호부이자, 운영 사고의 상당수를 설명하는 캐시 시스템입니다. 계층 구조와 TTL을 이해하면 배포, 이전, failover가 갑자기 훨씬 예측 가능해집니다.

다음 글에서는 DNS로 찾은 IP에 실제로 어떤 메시지를 보내는지, HTTP와 HTTPS를 다룹니다.

<!-- toc:begin -->
- [네트워크란 무엇인가?](./01-what-is-a-network.md)
- [IP와 subnet](./02-ip-and-subnet.md)
- [TCP와 UDP](./03-tcp-and-udp.md)
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

Tags: Computer Science, 네트워크, DNS, resolver, 캐싱, TTL
